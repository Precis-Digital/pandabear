import argparse
import os
import shutil
import sys
import tempfile
from distutils import dir_util
from typing import List

import yaml
from cookiecutter.main import cookiecutter

PACKAGE_CONFIG_FILE_PATH = "./gcp_package_config.yaml"

COOKIECUTTER_CONFIG_FILE_PATH = "./.cookiecutter.yaml"

COOKIECUTTER_TEMPLATE_URI = "git+ssh://git@github.com/Precis-Digital/precis-python-package.git"

with open("./scripts/VERSION", "r") as f:
    VERSION = f.read()


def parse_cli_list_input(input_str: str, delimiter: str = ",") -> List[str]:
    """
    Parse a string input from a command line argument into a list of strings
    :param input_str: input string with values to be parsed
    :param delimiter: delimiter to use to split string, defaults to a comma (",")
    :return: Parsed list of strings
    """
    input_str = input_str or ""
    return [x.strip().replace('"', "").replace('"', "") for x in input_str.split(delimiter)]


def load_cookiecutter_config(config_file_path: str) -> dict:
    """
    Read in the cookiecutter config file and load as a dictionary.
    :return: dict of loaded cookiecutter config file
    """
    try:
        with open(config_file_path, "r") as cookiecutter_file:
            cookiecutter_config = yaml.safe_load(cookiecutter_file)
    except FileNotFoundError as e:
        sys.exit(f"Unable to find {cookiecutter_file} in project root - {e}")

    # Filter out values starting with "_" as these are non-rendered template values, will break rendering in cookiecutter >V2
    # Keep values starting with "__" as these are hidden template values we want to keep
    hidden_rendered_keys = {k for k in cookiecutter_config["default_context"].keys() if k.startswith("__")}
    return {
        k: v
        for k, v in cookiecutter_config["default_context"].items()
        if not k.startswith("_") or k in hidden_rendered_keys
    }


def load_package_config(file_path: str) -> dict:
    """
    Read in the project's service config yaml file and load as a dictionary.
    :return: dict of loaded service config yaml file
    """
    try:
        with open(file_path, "r") as service_config_file:
            service_config = yaml.safe_load(service_config_file)
    except FileNotFoundError as e:
        sys.exit(f"Unable to find {file_path} in project root - {e}")
    return service_config


def generate_temp_cookiecutter_project(
    cookiecutter_template_uri: str,
    cookiecutter_config_data: dict,
    output_dir: str,
    template_version: str = None,
) -> None:
    """
    Generate a cookiecutter project based on a given cookiecutter template URI and config inputs
    :param cookiecutter_template_uri: URI path to the cookiecutter template (ex. a git url, or zip file path, etc.)
    :param template_version: cookiecutter template version (ie. the branch, tag or commit ID), defaults to latest
    :param cookiecutter_config_data: File path to the cookiecutter template values to populate the template with
    :param output_dir: Destination location for the cookiecutter project
    :return: None
    """
    print(f"Generating temporary cookiecutter output")

    # Note: currently not using cookiecutter's native "replay" arg as it does not allow passing dynamic config values,
    # as of V2.1.1 (instead generating a new project in a temp dir, using a dict of loaded template options passed in extra_context arg
    cookiecutter(
        template=cookiecutter_template_uri,
        checkout=template_version,
        output_dir=output_dir,
        overwrite_if_exists=True,
        no_input=True,
        extra_context=cookiecutter_config_data,
    )

    print("Finished generating temporary cookiecutter output")
    return


def update_folders(folders: List[str], source_dir: str) -> None:
    """
    Copy/replace  a list of folders from a source directory to into the current working directory
    :param folders: List of folder names or paths relative to current working directory
    :param source_dir: Source directory to copy/replace
    :return: None
    """
    # ignore blank values
    folders = [x for x in folders if x != ""]

    for folder in folders:
        source_dir_path = os.path.join(source_dir, f"{folder}")

        if not os.path.isdir(source_dir_path):
            print(f"Warning: could not find source folder {source_dir_path}")
            continue

        copied_files = dir_util.copy_tree(src=source_dir_path, dst=f"./{folder}")
        print(f"Updated {folder} package folder ({len(copied_files)} files)")
    return


def update_files(relative_file_paths: List[str], source_dir: str) -> None:
    """
    Copy/replace  a list of files from a source directory to into the current working directory
    :param relative_file_paths:
    :param source_dir:
    :return:
    """
    # ignore blank values
    relative_file_paths = [x for x in relative_file_paths if x != ""]

    # always update certain files
    relative_file_paths.extend([".cookiecutter.yaml"])

    for file_path in relative_file_paths:
        source_file_path = os.path.join(source_dir, file_path)

        if not os.path.isfile(source_file_path):
            print(f"Warning: could not find source file {source_file_path}")
            continue

        copied_file = shutil.copy(src=source_file_path, dst=f"./{file_path}")
        print(f"Updated {copied_file} package file")
    return


def main():

    # Load project's cookiecutter and service config
    cookiecutter_config = load_cookiecutter_config(config_file_path=COOKIECUTTER_CONFIG_FILE_PATH)
    package_dir = cookiecutter_config["__package_dir"]
    package_config = load_package_config(file_path=PACKAGE_CONFIG_FILE_PATH)

    # Setup CLI
    update_package_cli = argparse.ArgumentParser(
        description=f"""
        CLI to update specified folders and/or files of a Precis Python Package. Run from the source project root.
        """
    )
    update_package_cli.add_argument(
        "--folders",
        type=str,
        help="Folders to update/overwrite. Can pass in multiple as comma delimited list (ex. '--folders=cloudbuild' or '--folders=cloudbuild,scripts'",
    )
    update_package_cli.add_argument(
        "--files",
        type=str,
        help="File paths to update/overwrite. Can pass in multiple as comma delimited list (ex. '--file-paths=cloudbuild/cloudbuild.yaml' or '--file-paths=scripts/build_publish_package.sh,setup.cfg'",
    )
    update_package_cli.add_argument(
        "--template-version",
        type=str,
        help="Cookiecutter template version to fetch (ie. the branch, tag or commit ID), defaults to latest",
        default=None,
    )
    update_package_cli.version = VERSION
    update_package_cli.add_argument("--version", action="version")

    # Parse and validate inputs
    args = update_package_cli.parse_args()
    folders = parse_cli_list_input(input_str=args.folders)
    file_paths = parse_cli_list_input(input_str=args.files)
    template_version = args.template_version

    # Override cookiecutter config with any changes from the service config file
    cookiecutter_config = {
        k: v for k, v in {**cookiecutter_config, **package_config}.items() if k in cookiecutter_config
    }

    # Generate cookiecutter into temp dir, first copy/replace files, then folders
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Created temporary directory {temp_dir}")

        new_source_dir = os.path.join(temp_dir, package_dir)

        generate_temp_cookiecutter_project(
            cookiecutter_template_uri=COOKIECUTTER_TEMPLATE_URI,
            cookiecutter_config_data=cookiecutter_config,
            output_dir=temp_dir,
            template_version=template_version,
        )

        update_files(relative_file_paths=file_paths, source_dir=new_source_dir)

        update_folders(folders=folders, source_dir=new_source_dir)

    return sys.exit(0)


if __name__ == "__main__":
    main()

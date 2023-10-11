# CI/CD with Cloud Build

Continuous Integration (CI) and Continuous Delivery (CD) automates the process of building, testing, and deployment of a service or application. 
It automates the process of moving code from your local machine, to a git repository, and finally to the deployment target (GCP for ex.).
CI/CD flows can be used to ensure code updates are linted, tested, reach a coverage threshold, etc. - before being deployed to a production instance.

[Cloud Build](https://cloud.google.com/build/docs/overview) is a service that executes your builds on Google Cloud Platform's infrastructure.
Cloud Build executes your build as a series of build steps, where each build step is run in a Docker container.
Cloud Build executes a set of build steps defined in a yaml or json file and can be triggered manually via API, schedule, PubSub, or through triggers such as a Push to a specific branch in a git repo or opening of a Pull Request.

The Precis Python Package template comes with a default `cloudbuild` directory with everything needed to setup a CI/CD flow with Cloud Build and GitHub build triggers.
This README walks through setting it up along with the details of the files and assumptions made.
Will setup two build triggers, one for run-tests that will execute a build with the cloudbuild_test.yaml file that validate code formatting and run tests - and another one for build-publish that will build the python package and publish to GCP's Artifact Registry, where the package can be installed from.
The default Cloud Build steps utilizes many of the same scripts in the scripts directory of the template (`run_tests.sh` and `build_publish_package.sh`), to ensure testing and deployment are done in the same way.


### Contents
- [Docs/Resources](#docs--resources)
- [Usage](#usage)
- [Folder Contents](#folder-contents)


### Docs / Resources
- [Cloud Build docs](https://cloud.google.com/build/docs/overview)
- [Building and debugging locally](https://cloud.google.com/build/docs/build-debug-locally)
- [Triggering from GitHub](https://cloud.google.com/build/docs/automating-builds/build-repos-from-github)


### Usage
GitHub Actions are used to automatically bump the version and update the [CHANGELOG.md](CHANGELOG.md) based on the commit messages since the last version (no action needed to enable or configure, settings in [.github/workflows/bumpversion.yaml](.github/workflows/bumpversion.yaml)).
Cloud Build can be used to automatically update your package version and publish to GCP [Artifact Registry](https://cloud.google.com/artifact-registry/docs), where the package can be installed from (must run two commands noted below to setup the build triggers).

- For adding CI/CD run below commands (note, you may be prompted to click a link to connect your repo to Cloud Build, one-time task):
    - `make enable-update-cloudbuild` (will create or update the Cloud Build triggers doing the automated tests and building-publishing of the package)
      - Optionally can manually run the two scripts below:
    - `./cloudbuild/create_update_run_tests_build_trigger.sh` create/updates GitHub Build trigger on Pull Request to master (or main) and will run tests and linting checks.
    - `./cloudbuild/create_update_build_publish_trigger.sh` create/updates GitHub Build trigger on pushes to version tags and will build and publish the package to GCP Artifact Registry
    - Configuration for the test and build/publish GitHub Cloud Build triggers are in `cloudbuild/run_tests_build_trigger.yaml` and `cloudbuild/publish_build_trigger.yaml`
    - Cloud Build makes use of same `build_publish_package.sh` and `run_tests.sh` scripts in scripts directory
- Files at [cloudbuild](cloudbuild) - for adding CI/CD to project, or using Cloud Build to deploy:
   - [run_tests_cloudbuild.yaml](cloudbuild/run_tests_cloudbuild.yaml) - Cloud Build configuration / steps for running tests and linting checks
   - [publish_build_cloudbuild.yaml](cloudbuild/publish_build_cloudbuild.yaml) - Cloud Build configuration / steps for building the python package and uploading to Artifact Registry
- NOTE:
    - The steps run as the Cloud Build Service Account for whatever GCP Project the build is running in.
    - You can grant the Cloud Build Service Account permission to impersonate another (or all) Service Accounts to allow it to run integration tests and act as a specific Service Account (this is done by default in tech-managed Projects).


### Folder Contents
Description of all files in this directory.

- [cloudbuild.yaml](./cloudbuild.yaml) - the main Cloud Build file with the specified default build steps.
    - Includes automated testing, code format tests, and a deploy prod/dev step.
    - Can comment out or add/edit certain steps to meet needs of a given service.
    - Makes use of many of the same scripts in scripts directory (`run_tests.sh`, `deploy_prod.sh` when on master (or main) branch, and `deploy_dev.sh` on others).
- [prod_build_trigger.yaml](./publish_build_trigger.yaml) - a yaml configuration of the 'prod' trigger that will trigger a build and deployment to 'prod'.
    - Specifies certain files to ignore, meaning changes made to certain files or in certain folders won't trigger a build.
- [create_update_prod_build_trigger.sh](./create_update_build_publish_trigger.sh) - create/updates GitHub Build trigger on pushes to master (or main).
    - Setup to trigger on Pushes to "master" or "main" branch.
    - NOTE: if you edit the prod_build_trigger.yaml trigger configuration you need to manually re-run this script to update the trigger.
- [dev_build_trigger.yaml](./run_tests_build_trigger.yaml) - a yaml configuration of the 'dev' trigger that will trigger a build and deployment to 'dev'.
    - Specifies certain files to ignore, meaning changes made to certain files or in certain folders won't trigger a build.
- [create_update_dev_build_trigger.sh](./create_update_run_tests_build_trigger.sh) - create/updates GitHub Build trigger on Pull Request to master (or main).
    - Setup to trigger on Pull Requests targeting "master" or "main" branch.
    - NOTE: if you edit the dev_build_trigger.yaml trigger configuration you need to manually re-run this script to update the trigger.

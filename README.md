# pandabear


[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
![Coverage](static/images/coverage-badge.svg)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

A runtime schema validator for Pandas DataFrames.

When you have a code that passes `pandas.DataFrame`s around, it can become difficult to keep track of the *state* of the data at any given point in the pipeline.

### In a nutshell

When you have a function like

``` python
def foo(df: pd.DataFrame) -> pd.DataFrame:
    # change `df` somehow
    return df
```

somewhere deep in your code, you can only know the state of `df` by running a debugger, or scrutinizing the code. This is especially true when you have a large codebase with many developers. `pandabear` solves this problem by allowing you to define schemas for your `pandas.DataFrame`s, and validate them at runtime. This way, you can be sure that the `pandas.DataFrame` you're passing around is in the state you expect it to be.

## Example

```python
import pandas as pd
import pandabear as pb

# define your input and output schemas
class InputDFSchema(pb.DataFrameModel):
    col1: int
    col2: str
    col3: float = pb.Field(gt=0)

class OutputDFSchema(pb.DataFrameModel):
    col1: int
    col3: float = pb.Field(lt=0)

# decorate your function with `check_schemas` and pass the schemas to your function as type hints.
@pb.check_schemas
def foo(df: pb.DataFrame[InputDFSchema]) -> pb.DataFrame[OutputDFSchema]:
    df = df.drop('col2', axis=1)
    df.col3 *= -1
    return df
```

Now, **whenever `foo` is called**, validation triggers and you can be sure that the data follows your predefined schemas at input and return. If it does not, an exception will be raised.

*This package is heavily inspired by the [`pandera`](https://github.com/unionai-oss/pandera) Python package. Pandera is a fantastic Python library for statistical data testing, that offers a lot more functionality than `pandabear`. Consider this a lighter, `pandas`-only version of `pandera`. If you're looking for a more comprehensive solution that supports other backends than just `pandas` (like `spark`, `polars`, etc.), we highly recommend you check it out.*

**See package level [README.md](src/pandabear/README.md) for documentation and usage examples**

### Usage
- See the [examples](../../examples) directory for detailed demo

### Installation
- Install globally or to a given environment:
    - Activate virtual environment (optional)
    - `pip install pandabear`

## Prerequisites:
- [python](https://www.python.org/downloadss/) and virtual environment manager of your choice
    - pip version > 21.0.0
- [docker](https://docs.docker.com/get-docker/)


## Setup:
- Create/activate a virtual environment
- Run `make help` to see various helper commands to interact with the project
- Run `make setup` to install dependencies and setup the local package
- To make commits: run `make commit` or `make commit-all` (adds all changed files to git staged)


## Commitizen and Automated Versioning and Changelog
- A python package must have a version, here we use [semantic versioning](https://semver.org/) format (ex. 1.1.1)
- Instead of manually bumping a version, this template uses [commitizen](https://commitizen-tools.github.io/commitizen/) to auto-update the package version and auto-generate a CHANGELOG.md
- This automation is done by parsing commit history as you apply changes, using the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) format of commit messages
- To auto-bump the version and generate a change log, [GitHub Actions](https://docs.github.com/en/actions/learn-github-actions/understanding-github-actions) is used on pushes to main/master branch, defined in [.github/workflows/bumpversion.yaml](.github/workflows/bumpversion.yaml). See CI/CD section for more details
- To enforce this commit message, commitizen is used as a pre-commit hook, and we highly recommend you use the commitizen CLI to make commits, you can run `make commit` or `make commit-all` helper commands, or can run things manually in below example
```bash
# Can run `make commit` or `make commit-all` helper command, or each command manually, listed below: 
# Optionally run pre-commit checks to ensure code formatting/linting is good
pre-commit run --all-files -v

# First add your specific files to git staged changes, or add all via '.'
git add .

# Then run cz commit and follow prompt to generate a good commit message
gz commit
```
![Commitizen Demo](static/images/commitizen_demo.gif)


## Misc.
- Author names and emails are specified in [setup.cfg](setup.cfg), the package template initially fills in these values from the git user who created the package, if a user doesn't have a git name specified a placeholder value is used and should be updated.
  - Multiple author names and emails can be specified, as a comma-separated list (ex. `author = John Doe,Jane Doe`)
- Specifying dependencies:
  - You must specify what dependencies your project needs to work in [setup.cfg (install_requires)](setup.cfg), preferably with wider-scope version constraints (eg. requests>=2.0.0 instead of requests==2.1.3)

## CI/CD:
GitHub Actions are used to automatically bump the version and update the [CHANGELOG.md](CHANGELOG.md) based on the commit messages since the last version (no action needed to enable or configure, settings in [.github/workflows/bumpversion.yaml](.github/workflows/bumpversion.yaml)).
Cloud Build is used to automatically package version and publish to PyPI

## Notes / Docs:
- Uses:
    - [pre-commit](https://pre-commit.com/) for Git pre-commit hooks
    - [Black](https://github.com/psf/black) for python code formatting
    - [isort](https://github.com/PyCQA/isort) to sort imports
    - [gitleaks](https://github.com/zricethezav/gitleaks) for secrets scanning in pre-commit hooks and CI/CD
    - [pytest](https://pytest.org/) as test runner (can run both pytests and unittests)
        - [Unittest](https://docs.python.org/3/library/unittest.html)
    - [Coverage](https://coverage.readthedocs.io/en/coverage-5.3.1/) for assessing test coverage
    - [Commitizen](https://commitizen-tools.github.io/commitizen/) for enforcing correct git commit message format, auto-bumping versions, and auto-generating the change log

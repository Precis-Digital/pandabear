all:
	@echo "Run `make help` to see available commands"

setup: ## Setups up local package, installs dependencies, and installs/runs pre-commit
	python -m pip install -r requirements-dev.txt
	python -m pip install -e .
	python -m pre_commit run --all-files -v
	python -m pre_commit install --hook-type commit-msg

test: ## Runs tests via bash script at scripts/run_tests.sh, for more flags and options call this script directly
	bash scripts/run_tests.sh

commit: ## First runs pre-commit checks, before opening the commitizen prompt for making a commit with valid message. NOTE: must first stage files via `git add FILE,FILE2` to automatically add all files with changes use `make commit-all`.
	@python -m pre_commit run --all-files -v || (echo "Pre-commit checks failed, try again! $$?"; exit 1)
	cz commit

commit-all: ## Stages any changed files via `git add .`, then runs pre-commit checks before opening the commitizen prompt for making a commit with valid message.
	@python -m pre_commit run --all-files -v || (echo "Pre-commit checks failed, try again! $$?"; exit 1)
	git add .
	cz commit

enable-update-cloudbuild:  ## Setups up or updates the Cloud Build triggers used in CI/CD for automated building and publishing of the package.
	bash cloudbuild/create_update_run_tests_build_trigger.sh
	@echo ""
	@echo "======================================================="
	@echo ""
	bash cloudbuild/create_update_build_publish_trigger.sh

build-publish-package:  ## Manually runs the build/publish script at scripts/build_publish_package.sh
	bash scripts/build_publish_package.sh

update-from-template: ## Update components (files and/or folders) from the source template. NOTE: must run this script directly with python, ie `python scripts/update_template_components.py --help`
	python scripts/update_template_components.py --help

.PHONY: help

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

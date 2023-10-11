#!/usr/bin/env bash

# Builds and publishes python package

set -e
set -o pipefail

source ./scripts/set_env.sh

# Create/build dist wheel, removing any existing build files
rm --force dist/*.gz || true
rm --force dist/*.whl || true
python -m build --outdir dist/

# Upload to GCP Artifact Registry via twine, using settings defined in gcp_package_config.yaml
REPO_URL="https://${GCP_REGION}-python.pkg.dev/${GCP_PROJECT}/${AR_REPO}/"

python -m twine upload --verbose --repository-url=${REPO_URL} dist/*

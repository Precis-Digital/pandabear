#!/usr/bin/env bash

source ./scripts/set_env.sh

read -p "WARNING - this will remove the entire package (all versions) from the package repository - Proceed? Y/N " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
  echo "Tearing down package!"

  gcloud artifacts packages delete $PACKAGE_NAME --repository=$AR_REPO --location=$GCP_REGION --project=$GCP_PROJECT

  source ./cloudbuild/delete_build_triggers.sh

else
  echo "Tear down aborted by user"
fi

#!/usr/bin/env bash

source ./scripts/set_env.sh

read -p "WARNING - this will delete the Cloud Build Triggers - Proceed? Y/N " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
  echo "Tearing down Cloud Build Triggers!"

  gcloud builds triggers delete pandabear-prod-push-to-master --project=$GCP_PROJECT

  gcloud builds triggers delete pandabear-pull-request-to-master --project=$GCP_PROJECT

else
  echo "Cloud Build Triggers tear down aborted by user"
fi


#!/usr/bin/env bash

source ./scripts/set_env.sh

# Temp file for loading Build Trigger config
TRIGGER_CONFIG="cloudbuild/publish_build_trigger.yaml"

# Import trigger (create/update)
# https://cloud.google.com/sdk/gcloud/reference/beta/builds/triggers/import
gcloud beta builds triggers import --source=$TRIGGER_CONFIG --project=$GCP_PROJECT

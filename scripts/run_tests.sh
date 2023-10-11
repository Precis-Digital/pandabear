#!/usr/bin/env bash

source ./scripts/set_env.sh

export SERVICE_INSTANCE=test

# NOTE: pytest and coverage are configured in pyproject.toml

eval "python -m pytest"
TEST_OUTPUT=$?

coverage-badge -o ./static/images/coverage-badge.svg -f

echo "TEST_OUTPUT:" $TEST_OUTPUT
exit $TEST_OUTPUT
# pandabear

An runtime schema validator for Pandas DataFrames.


### Prerequisites
- [python](https://www.python.org/downloads/) and virtual environment manager of your choice
- [Google Cloud SDK (gcloud)](https://cloud.google.com/sdk/docs/install)
- Configure authentication to GCP [Artifact Registry](https://cloud.google.com/artifact-registry/docs):
    - `pip install keyrings.google-artifactregistry-auth`
    - Once the keyrings python packge is installed pip should pick up yur Application Default Credentials set from the Google Cloud SDK (gcloud)
    - [Docs page](https://cloud.google.com/artifact-registry/docs/python/authentication#keyring-setup)
    - NOTE: The environment installing the package must have read access to the Artifact Registry (all user accounts and approved Cloud Build Service Accounts should already have this access)


### Usage
- See the [examples](../../examples) directory for detailed demo 
- Install to a repo/project:
    - In your `requirements.txt` file add a line specifying the `--extra-index-url` value followed by the python package and version as usual:
  ```
  ...requirements.txt
  
  --extra-index-url=https://europe-west1-python.pkg.dev/precis-artifacts/pd-core/simple/
  pandabear==0.0.0 (NOTE: specify the version to install here!)
  
  ```
- Install globally or to a given environment:
    - Activate virtual environment (optional)
    - `pip install pandabear --extra-index-url=https://europe-west1-python.pkg.dev/precis-artifacts/pd-core/simple/`
    - To update: `pip install pandabear --extra-index-url=https://europe-west1-python.pkg.dev/precis-artifacts/pd-core/simple/ --upgrade`
- NOTE: As with other pip packages, you can specify a version to install
    - `pip install pandabear==0.1.0 --extra-index-url=https://europe-west1-python.pkg.dev/precis-artifacts/pd-core/simple/`
- NOTE: you can omit the `--extra-index-url` arg if you setup a [pip.conf](https://pip.pypa.io/en/stable/topics/configuration/) file and have installed the package `keyrings.google-artifactregistry-auth`

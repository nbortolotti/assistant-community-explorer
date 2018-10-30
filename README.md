# Community Assistant Explorer


## Deploy solution

The initial step should be check the dependencies for the project.

``
pip install -r requirements.txt -t lib
``

To check in local the behavior of the service

``
dev_appserver.py app.yaml
``

Note: check the SDK installing recommendations.

``
export PYTHONPATH="${PYTHONPATH}:/path/to/google/app/engine/sdk/"
``


To deploy the solution directly on Google Cloud Platform,  you could use *gcloud* tool, you can follow the official documentation [here](https://cloud.google.com/sdk/gcloud/reference/app/deploy)

``
gcloud app deploy app.yaml
``

## Agent


## Modules


# Community Assistant Explorer

## Description of the project
The motivation of this project proposes highlight the flexibility of interacting in a conversational way with community information. Following this concept we propose use Actions [Google Assistant] to access community information, interact and represent some of the most important use cases of communities around the world.

### Demo

![demo](https://github.com/nbortolotti/assistant-community-explorer/wiki/pictures/assistant_community_explorer_demo_01.gif)

### Initial Community Component
The project will initially integrate the community information, [GDG-Google Developers Group](https://developers.google.com/programs/community/gdg/). 

## Architecture Overview
check the wiki section, [Architecture Overview](https://github.com/nbortolotti/assistant-community-explorer/wiki/Architecture)

## Technology Used
* App Engine traditional-environment:  responsible to extract the information and create assistant responses.
* Dialogflow, [link](https://dialogflow.com/)
* Actions Google Assistant, [link](https://developers.google.com/actions/)

### Components
* flask, [link](http://flask.pocoo.org)
* google-api-python-client, [link](https://github.com/googleapis/google-api-python-client)
* requests, [link](https://pypi.org/project/requests/)
* meetup-api, [link](https://pypi.org/project/meetup-api/)
* pycountry-convert, [link](https://pypi.org/project/pycountry-convert/)

## Deploy solution
component: core community explorer

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
In the **agent-folder** is possible visualize the initial version of the **intents** used for the initial version of the project.

## Modules
Currently, the community module in which we are working is for the GDG [Google Developers Group](https://developers.google.com/programs/community/gdg/) community. 


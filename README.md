# OrderQualityTool
Order Quality Tool and Dashboard, to connect to DHIS2 data

[![Build Status](https://travis-ci.org/CHAIUganda/OrderQualityTool.svg?branch=develop)](https://travis-ci.org/CHAIUganda/OrderQualityTool)
## Developer Setup


- Make sure python is installed preferably with a virtualenv

- Install the required python packages

        $ pip install -r requirements.txt

- Install the node packages

        $ npm install

- Install bower

        $ npm install -g bower

- Install bower packages

        $ bower install

- Run the python dev server

        $ python manage.py runserver


- Run the python unit tests

        $ python manage.py test

## DEPLOYMENT
The core technologies needed to run this project are:

- Python 2.7 and the project dependencies in [the requirements file](requirements/prod.txt)
- Gunicorn as an application server
- Nginx as a web server
- Celery as a background worker
- Postgresql as the database
- npm and bower to build the static assets



### Docker
If you are using docker, this project has a [Dockerfile](./Dockerfile) and a
[docker-compose configuration](./docker-compose.yml) as an example of how this application can
be deployed.



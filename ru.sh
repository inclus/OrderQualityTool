#! /bin/sh
coverage run --branch --source=dashboard,orderqualitytool,qdbauth,locations ./manage.py test --with-timer
coverage report
coverage html -d reports/coverage

# CrowdClick

[![contributions](https://img.shields.io/badge/contributions-welcome-brightgreen)](https://github.com/crowd-tools/CrowdClick/pulls)
[![Build Status](https://travis-ci.com/crowd-tools/CrowdClick.svg?branch=master)](https://travis-ci.com/crowd-tools/CrowdClick)
[![codecov](https://codecov.io/gh/crowd-tools/CrowdClick/branch/master/graph/badge.svg)](https://codecov.io/gh/crowd-tools/CrowdClick)
[![apiary](https://img.shields.io/badge/apiary-doc-blue)](https://crowdclick.docs.apiary.io/)

Backend of affordable solution that combines traffic and quantitative data to the advertiser
through a crowd-sourcing click to view reward model


## Install and run project

```bash
# Create virtual environment
# https://virtualenvwrapper.readthedocs.io/en/latest/
mkvirtualenv -p python3.6 -a . crowdclick

# Install dependencies
pip install -r requirements.txt

# Initialize local settings
echo 'from .defaults import *' > crowdclick/settings/local.py

# Run migrations
python manage.py migrate

# Load initial data
python manage.py loaddata ad_source/fixtures/*

# Run server
python manage.py runserver 0.0.0.0:8000
```

You should see API endpoints on [http://localhost:8000/api/](http://localhost:8000/api/)

## Check code quality

```bash
# Run tests
python manage.py test

# Flake8
pip install flake8 && flake8 .
```

## Contributions

Contributions are welcome. Be sure to check our
[Code of conduct](https://github.com/CrowdClick/.github/blob/master/CODE_OF_CONDUCT.md)

## Licence

[MIT](https://github.com/CrowdClick/CrowdClick/blob/master/LICENCE)

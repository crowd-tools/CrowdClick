#!/bin/bash

# This script runs automatically only on stage environment

set -x  # Output entering commands

# Activate env, change directory to project root
source ~/.virtualenvs/crowdclick_stage/bin/activate
cd ~/crowd_click_stage/

# Pull updates
git checkout stage -f
git pull

# Pip dependencies
pip install -U pip
pip install -r requirements.txt

# Go Django!
python manage.py migrate
python manage.py collectstatic --no-input

# Restart supervisor
supervisorctl restart crowdclick_stage
supervisorctl restart crowdclick_celery_stage
supervisorctl restart crowdclick_celerybeat_stage

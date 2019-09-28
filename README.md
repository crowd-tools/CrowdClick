# CrowdClick


## Install/Run project

```
git clone ...
cd CrowdClick
mkvirtualenv -p python3.6 -a . crowdclick
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata ad_source/fixtures/*
python manage.py runserver 0.0.0.0:8000
```

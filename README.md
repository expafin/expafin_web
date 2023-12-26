# Django site structure
Fast prototyping Django sites


## Host Setup
Configuration details here: https://github.com/expafin/expafin_web/blob/main/host_settings.md  
The secret variables are stored into a .env file  
The static files and the database are excluded from this repo.


## Django settings
Files customised:  
* settings.py
* urls.py
* models.py
* views.py
* templates
See https://github.com/expafin/expafin_web/blob/main/django_settings.md for details  

## Site updates
Each site update requires a gunicorn restart:  
`sudo systemctl restart gunicorn`  
and collectstatic  

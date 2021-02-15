# ExpaFin site structure

## DigitalOcean Setup
Used DigitalOcean tutorial  
https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-20-04  
The secret variables are stored into a .env file  
The static files and the database are excluded from the repository  


## Django settings
Update:  
* settings.py


* urls.py
* templates


## Site updates
Each site update requires a gunicorn restart:  
`sudo systemctl restart gunicorn`  
and collectstatic  

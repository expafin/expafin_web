# DigitalOcean Setup
Used DigitalOcean tutorial  
https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-20-04  
The secret variables are stored into a .env file  
The static files and the database are excluded from the repository  

``` shell
sudo apt update
sudo apt install python3-pip python3-dev libpq-dev postgresql postgresql-contrib nginx curl
sudo apt update && sudo apt upgrade -y
sudo -H pip3 install --upgrade pip
sudo -H pip3 install virtualenv
cd ~

git clone https://github.com/expafin/expafin_web
cd ~/expafin_web
virtualenv venv
source venv/bin/activate
pip install django gunicorn psycopg2-binary django-environ pillow
django-admin.py startproject expafin_web
cd expafin_web
python3 manage.py startapp expafin

sudo -u postgres psql
CREATE DATABASE DATABASE_NAME;   
CREATE USER [USER_NAME] WITH PASSWORD 'PASSWORD';
ALTER ROLE [USER_NAME] SET client_encoding TO 'utf8';
ALTER ROLE [USER_NAME] SET default_transaction_isolation TO 'read committed';
ALTER ROLE [USER_NAME] SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE [DATABASE_NAME] TO [USER_NAME];
\q

nano .env # set secret variables
name settings.py # set ALLOWED_HOSTS, database parameters, STATIC_ROOT, MEDIA_URL, MEDIA_ROOT

manage.py makemigrations
manage.py migrate
manage.py createsuperuser
manage.py collectstatic

sudo ufw allow 8000
manage.py runserver 0.0.0.0:8000 #check if server is running properly

cd ~/venv
gunicorn --bind 0.0.0.0:8000 expafin_com.wsgi
CTRL-C
deactivate

sudo nano /etc/systemd/system/gunicorn.socket
    [Unit]
    Description=gunicorn socket

    [Socket]
    ListenStream=/run/gunicorn.sock

    [Install]
    WantedBy=sockets.target

sudo nano /etc/systemd/system/gunicorn.service
    [Unit]
    Description=gunicorn daemon
    Requires=gunicorn.socket
    After=network.target

    [Service]
    User=USER_MAME
    Group=www-data
    WorkingDirectory=/home/USER_MAME/myprojectdir
    ExecStart=/home/USER_MAME/myprojectdir/venv/bin/gunicorn \
            --access-logfile - \
            --workers 3 \
            --bind unix:/run/gunicorn.sock \
            myproject.wsgi:application

    [Install]
    WantedBy=multi-user.target

sudo systemctl start gunicorn.socket
sudo systemctl enable gunicorn.socket
sudo systemctl status gunicorn.socket
file /run/gunicorn.sock
sudo systemctl status gunicorn
sudo systemctl daemon-reload
sudo systemctl restart gunicorn

sudo nano /etc/nginx/sites-available/expafin_web
    server {
        listen 80;
        server_name expafin_web;

        location = /favicon.ico { access_log off; log_not_found off; }
        location /static/ {
            root /home/sm/expafin_web/expafin_com;
        }

        location / {
            include proxy_params;
            proxy_pass http://unix:/run/gunicorn.sock;
        }
    }

sudo certbot -d expafin.com,www.expafin.com --expand

sudo ln -s /etc/nginx/sites-available/expafin_web /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
sudo ufw delete allow 8000
sudo ufw allow 'Nginx Full'

sudo systemctl restart gunicorn
sudo systemctl daemon-reload
sudo systemctl restart gunicorn.socket gunicorn.service
sudo nginx -t && sudo systemctl restart nginx
```


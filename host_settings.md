# Host Setup

Inspiration: https://www.howtoforge.com/how-to-install-django-with-postgres-nginx-and-gunicorn-on-rocky-linux-9/

https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-20-04  
Hosted now on Hetzner on AlmaLinux, the tutorial still works with some adjustments.

Prerequisites:

## 0. Point DNS to server

CNAME @ IP

Updating takes time, continue next steps in the meantime.

## 1. Firewall with http and https open

``` shell
sudo dnf update -y && sudo dnf upgrade -y
sudo firewall-cmd --add-service=http --permanent
sudo firewall-cmd --add-service=https --permanent
sudo firewall-cmd --reload
sudo firewall-cmd --permanent --list-services
```

Last command should show something like "cockpit dhcpv6-client http https ssh"

## 2. Python 3 latest (or almost)

Not detailed here. Python 3.12 installed.

## 3. Postgres latest (or almost)

Not detailed here. Postgres 16 installed. Check installation:

``` console
sudo systemctl status postgresql-16
```

## 4. Configure PostgreSQL

Add Postgresql path at the end of bashrc file and export home path.

``` console
nano ~/.bashrc
export PATH=$PATH:/usr/pgsql-16/bin
export HOME='/home/user/'
```

Configure Postgres.

``` console
sudo -i -u postgres psql
CREATE DATABASE djangoapp;
CREATE USER djangouser WITH ENCRYPTED PASSWORD 'dbpassword';
GRANT ALL PRIVILEGES ON DATABASE djangoapp TO djangouser;
\q
```

Export connection parameters into ~/.bashrc.

``` shell
# Postgres
export DB_USER='user'
export DB_PASS='pass'
export DB_PORT='5432'
export DB_HOST='localhost'
export DB_DJANGO='djangoapp'
source ~/.bashrc
```

## 5. Install Django and create project

``` shell
mkdir ~/sampleproject
cd ~/sampleproject
python3.12 -m venv venv
source ./venv/bin/activate
pip install django wheel psycopg2 psycopg2-binary dotenv
django-admin --version
django-admin startproject demoproject .
```

Django uses SECRET_KEY variable to provide cryptographic signing. It generates a default value during installation. You should replace it with a secure value. Run the following command to generate the key and copy it for later.

``` shell
python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
nano demoproject/settings.py
```

Create a .env file in the project root. Add the file in .gitignore. Add the ecrets there:  DB_USER DB_PASS DB_PORT DB_HOST DB_DJANGO.
Put the key you generated into a .env as DJANGO_KEY. Replace the current value of the SECRET_KEY variable with DJANGO_KEY.
```SECRET_KEY = DJANGO_KEY```

Change the settings for the DATABASES section as follows.

``` python
import os

from dotenv import load_dotenv
load_dotenv() 
DJANGO_KEY = str(os.environ.get('DJANGO_KEY'))
DB_USER = os.environ.get('DB_USER')
DB_PASS = os.environ.get('DB_PASS')
DB_PORT = os.environ.get('DB_PORT')
DB_HOST = os.environ.get('DB_HOST')
DB_DJANGO = os.environ.get('DB_DJANGO')
HOME = os.environ.get('HOME')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': DB_DJANGO,
        'USER': DB_USER,
        'PASSWORD': DB_PASS,
        'HOST': DB_HOST,
        'PORT': DB_PORT,
    },
}
```

Next, move to the bottom of the file and add a setting for the location of static files. This is important for Nginx to work and handle requests for these files. Add the following line above the STATIC_URL variable.

``` python
STATIC_ROOT = os.path.join(BASE_DIR, "static/")
```

Verify the database settings.

``` shell
python manage.py check --database default
```

Migrate the database using the migrate command. Migrations in Django propagate changes you make to your models into your database schema.

``` shell
python manage.py makemigrations
python manage.py migrate
```

Create an administrative user to access Django's admin interface.

``` shell
python manage.py createsuperuser
```

Copy the static files into the static directory. Enter yes when prompted.

``` shell
python manage.py collectstatic
```

## 6. Test the Development Server

Edit demoproject/settings.py

``` python
ALLOWED_HOSTS = ['<yourserver_ip_address>']
```

Before you test the development server, you need to configure the firewall to allow Django to work. Django uses port 8000 by default.

``` shell
sudo firewall-cmd --add-port=8000/tcp --permanent
sudo firewall-cmd --reload
```

Start the development server.

``` shell
python manage.py runserver 0.0.0.0:8000
```

Close the development server using ^C

## 7. Install and Test Gunicorn

Inside virtual environment

```pip install gunicorn```

Test Gunicorn's ability to serve the project. 

```gunicorn --bind 0.0.0.0:8000 demoproject.wsgi:application```

To verify, open the URL http://<yourserver_ip_address>:8000

Press ^C when done.

Deactivate the virtual environment to go back to your regular shell.

```deactivate```

## 8. Create a Socket and Service file for Gunicorn

Create and open the Gunicorn socket file for editing.

```sudo nano /etc/systemd/system/gunicorn.socket```

Paste the following code in it.

``` shell
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
```

Save the file by pressing Ctrl + X and entering Y when prompted.

Create and open the Gunicorn service file for editing.

```sudo nano /etc/systemd/system/gunicorn.service```

Paste the following code in it.

``` shell
[Unit]
Description=django gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=user
Group=nginx
WorkingDirectory=/home/user/django_root
ExecStart=/home/user/django_root/venv/bin/gunicorn \
          -t 3000 \
          --access-logfile - \
          --workers 3 \
          --bind unix:/run/gunicorn.sock \
          project.wsgi:application -w 2

[Install]
WantedBy=multi-user.target
```

Save the file by pressing Ctrl + X and entering Y when prompted.

Reload the system daemon to refresh the systemd files.

```sudo systemctl daemon-reload```

Enable and start the Gunicorn socket file.

```sudo systemctl start gunicorn.socket```

```sudo systemctl enable gunicorn.socket```

Check the status of the Gunicorn socket.

```sudo systemctl status gunicorn.socket```

The Gunicorn service is still not running as you can check.

```sudo systemctl status gunicorn.service```

To test the socket activation mechanism, run the following command.

```curl --unix-socket /run/gunicorn.sock localhost```

## 9. Install Nginx

Create and open the /etc/yum.repos.d/nginx.repo file for creating the official Nginx repository.

```sudo nano /etc/yum.repos.d/nginx.repo```

Paste the following code in it.

``` shell
[nginx-stable]
name=nginx stable repo
baseurl=http://nginx.org/packages/centos/$releasever/$basearch/
gpgcheck=1
enabled=1
gpgkey=https://nginx.org/keys/nginx_signing.key
module_hotfixes=true

[nginx-mainline]
name=nginx mainline repo
baseurl=http://nginx.org/packages/mainline/centos/$releasever/$basearch/
gpgcheck=1
enabled=0
gpgkey=https://nginx.org/keys/nginx_signing.key
module_hotfixes=true
```

Save the file by pressing Ctrl + X and entering Y when prompted.

Install the Nginx server.

```sudo dnf install nginx -y```

Verify the installation.

```nginx -v```

Enable and start the Nginx server.

```sudo systemctl enable nginx --now```

Check the status of the server.

```sudo systemctl status nginx```

## 10. Install SSL

So far, your Django application is being served over a plaintext HTTP connection. It is highly recommended that you protect it via an SSL certificate. For this, use the Certbot tool using the Snapd tool. It requires the EPEL repository to work.

``sudo dnf install epel-release``

We will use Snapd to install Certbot. Install Snapd.

```sudo dnf install snapd```

Enable and Start the Snap service.

```sudo systemctl enable snapd.socket --now```

Create necessary links for Snapd to work.

``` shell
sudo ln -s /var/lib/snapd/snap /snap
echo 'export PATH=$PATH:/var/lib/snapd/snap/bin'
sudo tee -a /etc/profile.d/snapd.sh
```

Install the core Snapd repository.

``` shell
sudo snap install core
sudo snap refresh core
```

Install Certbot.

```sudo snap install --classic certbot```
```sudo ln -s /snap/bin/certbot /usr/bin/certbot```

Generate the certificate. The following command will also automatically configure Nginx.

```sudo certbot certonly --nginx --agree-tos --no-eff-email --staple-ocsp --preferred-challenges http -m name@domain.com -d domain.com```

The above command will download a certificate to the /etc/letsencrypt/live/domain.com directory on your server.

Generate a Diffie-Hellman group certificate.

```sudo openssl dhparam -dsaparam -out /etc/ssl/certs/dhparam.pem 4096```

To check whether the SSL renewal is working fine, do a dry run of the process.

```sudo certbot renew --dry-run```

If you see no errors, you are all set. Your certificate will renew automatically.

## 11. Configure Nginx

Create and open the file /etc/nginx/conf.d/django-gunicorn.conf for editing.

```sudo nano /etc/nginx/conf.d/django-gunicorn.conf```

Paste the following code in it.

``` shell
# enforce HTTPS
server {
  listen 80 default_server;
  server_name WEBSITE.com;
  return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name WEBSITE.com;

    access_log  /var/log/nginx/django.access.log;
    error_log   /var/log/nginx/django.error.log;

    http2_push_preload on; # Enable HTTP/2 Server Push

    ssl_certificate /etc/letsencrypt/live/WEBSITE.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/WEBSITE.com/privkey.pem;
    ssl_trusted_certificate /etc/letsencrypt/live/WEBSITE.com/chain.pem;
    ssl_session_timeout 1d;

    # Enable TLS versions (TLSv1.3 is required upcoming HTTP/3 QUIC).
    ssl_protocols TLSv1.2 TLSv1.3;

    # Enable TLSv1.3's 0-RTT. Use $ssl_early_data when reverse proxying to
    # prevent replay attacks.
    #
    # @see: https://nginx.org/en/docs/http/ngx_http_ssl_module.html#ssl_early_data
    ssl_early_data on;

    ssl_ciphers 'ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA384';
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:50m;

    # OCSP Stapling ---
    # fetch OCSP records from URL in ssl_certificate and cache them
    ssl_stapling on;
    ssl_stapling_verify on;
    ssl_dhparam /etc/ssl/certs/dhparam.pem;

    add_header X-Early-Data $tls1_3_early_data;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /home/USER/PROJECT;
    }

    location / {
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_pass http://unix:/run/gunicorn.sock;
    }
}

# This block is useful for debugging TLS v1.3. Please feel free to remove this
# and use the `$ssl_early_data` variable exposed by NGINX directly should you
# wish to do so.
map $ssl_early_data $tls1_3_early_data {
  "~." $ssl_early_data;
  default "";
}
```

Replace WEBSITE USER PROJECT as needed.

Save the file by pressing Ctrl + X and entering Y when prompted.

Open the file /etc/nginx/nginx.conf for editing.

```sudo nano /etc/nginx/nginx.conf```

Add the following line before the line include /etc/nginx/conf.d/*.conf;.

```server_names_hash_bucket_size  64;```

Save the file by pressing Ctrl + X and entering Y when prompted.

Verify your Nginx configuration.

```sudo nginx -t```

Add the domain name to your ALLOWED_HOSTS directive. Open the settings.py file.

You will also need to add the domain name to your ALLOWED_HOSTS directive. Open the settings.py file.

Change the value for ALLOWED_HOSTS variable.

```ALLOWED_HOSTS = ['<yourserver_ip_address>','WEBSITE.com']```

Restart Gunicorn Socket and Service.

```sudo systemctl restart gunicorn.socket```
```sudo systemctl restart gunicorn.service```

Reload the Nginx server.

```sudo systemctl reload nginx```

Open the HTTP port. You can also delete the 8000 port if you are not going to use it anymore.

```sudo firewall-cmd --remove-port=8000/tcp --permanent```
```sudo firewall-cmd --reload```

## 12. Debug stuff

``` shell
sudo systemctl status gunicorn.service
sudo systemctl status gunicorn.socket
sudo systemctl status gunicorn

sudo systemctl status nginx
```

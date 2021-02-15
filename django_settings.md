# Django settings

## project_folder/settings.py
``` python
import os
from environs import Env

# Read environment variables
env = Env()
env.read_env()  # read .env file, if it exists

SECRET_KEY = env('SECRET_KEY')

DEBUG = env('DEBUG')

ALLOWED_HOSTS =  env("ALLOWED_HOSTS").split(",")

INSTALLED_APPS = [
    'expafin',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env('DATABASE_NAME'),
        'USER': env('DATABASE_USER'),
        'PASSWORD': env('DATABASE_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

LANGUAGE_CODE = 'en-gb'

TIME_ZONE = 'UTC'

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR
```

## project_folder/urls.py
``` python
from expafin import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('portfolio/<int:port_id>', views.detail, name='detail'),
] 
urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
```

## Create project_folder/models.py
``` python
from django.db import models

# Create your models here.
class Portfolio(models.Model):
    # Images 
    image = models.ImageField(upload_to='images/')
    # Title 
    title = models.CharField(max_length=50, default="insert title")
    # Summary 
    summary = models.CharField(max_length=200)
    # Details
    details = models.CharField(max_length=500)

    def __str__(self):
        return self.title

```

## Migrate model into database
``` shell
python3 manage.py makemigrations
python3 manage.py migrate
```


## Create project_folder/views.py
``` python
from django.shortcuts import render, get_object_or_404
from .models import Portfolio

# Create your views here.
def home(request):
    jobs = Portfolio.objects
    return render(request,'expafin/home.html', {'jobs': jobs})

def detail(request, port_id):
    port_detail = get_object_or_404(Portfolio, pk=port_id)
    return render(request,'expafin/detail.html', {'port_detail': port_detail})
```

## Create project_folder/apps.py
```
from django.apps import AppConfig

class ExpafinConfig(AppConfig):
    name = 'expafin'
```

``` python
from django.contrib import admin
from .models import Portfolio

# Register your models here.
admin.site.register(Portfolio)
```

## Write a few tests in project_folder/tests.py
```
from django.test import TestCase
from selenium import webdriver
from time import sleep

class FunctionalTestCase(TestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()

    def test_there_is_homepage(self):
        self.browser.get('http://localhost:8000')
        self.assertIn('Hello', self.browser.page_source)

    def test_can_login_to_admin(self):
        pass_file = "../admin.pass"
        with open(pass_file) as f:
            password = f.read().strip()

        user_file = "../username.pass"
        with open(user_file) as f:
            username = f.read().strip()

        self.browser.get('http://localhost:8000/admin/')

        self.browser.find_element_by_name('username').send_keys(username)
        self.browser.find_element_by_name('password').send_keys(password , '\n')
        self.browser.find_element_by_name('next').click()

        self.assertIn('Groups', self.browser.page_source)

    def tearDown(self):
        self.browser.quit()

class UnitTestCase(TestCase):

    def test_home_homepage_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'expafin/home.html')
```

## Add folder project_folder/templates/project_folder
### Add home.html in project_folder/templates/project_folder
### Add detail.html in project_folder/templates/project_folder
### Add static content in project_folder/static
* site images
* bootstrap css
* bootstrap js
* collectstatic


## Site updates
Each site update requires a gunicorn restart:  
`sudo systemctl restart gunicorn`  
and collectstatic  

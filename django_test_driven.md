# Setup Django test driven development backend with a Bootstrap frontend 

## Resources
Awesome Django\
https://github.com/shahraizali/awesome-django\
https://github.com/wsvincent/awesome-django\
https://awesomedjango.org

Gitignore: use Toptal generator\
https://www.toptal.com/developers/gitignore
gitignore for Django:\
https://www.toptal.com/developers/gitignore/api/django


## Create virtual environment
Download Gecko Driver: https://github.com/mozilla/geckodriver/releases
```
cd expafin_com
pip3 install virtualenv
virtualenv venv
source venv/bin/activate
pip install selenium
```
Move the downloaded and unzipped Gecko driver into venv/bin folder  
Test Selenium:
```python
from selenium import webdriver
browser = webdriver.Firefox()
browser.get('http://localhost:8000')
```


## Install Django locally  
```
pip install django
django-admin startproject expafin_com
cd expafin_com
django-admin startapp expafin
python manage.py runserver
```

## Add first functional test
In expafin/tests.py add first test
```python
from django.test import TestCase
from selenium import webdriver

class FunctionalTestCase(TestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()

    def test_there_is_homepage(self):
        browser.get('http://localhost:8000')
        self.assertIn('install', self.browser.page_source)

    def tearDown(self):
        self.browser.quit()
```
Run test
``` python
python manage.py test`
```

## Add first unit test
``` python
class UnitTestCase(TestCase):

    def test_home_homepage_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'expafin/home.html')
```
Run test
``` python
python manage.py test`
```

## Add home page
in expafin_com/**settings.py** add "'expafin'," to INSTALLED_APPS
``` python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'expafin',
]
```
In expafin_com/**urls.py**:
* add "path('',views.home, name='home')," to urlpatterns
* add "from expafin import views" to functions imports
``` python
from django.contrib import admin
from django.urls import path
from expafin import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home, name='home'),
]
```
In _expafin/_**views.py**:
Define homepage view
``` python
def home(request):
    return render(request,'expafin/home.html')
```
Create template directory `expafin/templates/`
Create project template sub-directory `expafin/templates/expafin/`

Create homepage template `expafin/templates/expafin/home.html` with the text 'Hello!'\
_Run test again_

## Produce the project locally  

## Work in process


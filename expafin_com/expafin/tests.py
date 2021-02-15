from django.test import TestCase

# Create your tests here.
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

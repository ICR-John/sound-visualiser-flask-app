import pytest
from selenium.webdriver import ChromeOptions
import unittest
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
import sqlite3


class TestSignUp(unittest.TestCase):
    """Tests whether signup succeeds"""
    def setUp(self):
        # Based on
        # https://stackoverflow.com/questions/29858752/error-message-chromedriver-executable-needs-to-be-available-in-the-path
        # Sets up driver
        self.driver = webdriver.Chrome(ChromeDriverManager().install())
        self.driver.get("http://127.0.0.1:5000/signup")
        # Deletes Previous User test entry from database
        conn = sqlite3.connect("../../data/example.sqlite")
        conn.execute("Delete From User where email like '%user%'")
        conn.commit()

    def tearDown(self):
        # Closes driver
        self.driver.close()

    def test_a_signup(self):
        # Test data
        first_name = "First"
        last_name = "Last"
        email = "user@ucl.ac.uk"
        password = "password1"
        repeat_password = "password1"
        # Fills registration form
        self.driver.find_element_by_id("first_name").send_keys(first_name)
        self.driver.find_element_by_id("last_name").send_keys(last_name)
        self.driver.find_element_by_id("email").send_keys(email)
        self.driver.find_element_by_id("password").send_keys(password)
        self.driver.find_element_by_id("password_repeat").send_keys(repeat_password)
        self.driver.find_element_by_id("submit").click()
        assert self.driver.current_url == 'http://127.0.0.1:5000/menu/'


class TestLogin(unittest.TestCase):
    """Tests whether user can login and logout"""
    def setUp(self):
        # Sets up driver
        self.driver = webdriver.Chrome(ChromeDriverManager().install())
        self.driver.get("http://127.0.0.1:5000/login")
        # Test data
        email = "user@ucl.ac.uk"
        password = "password1"
        # Fills in login form
        self.driver.find_element_by_id("email").send_keys(email)
        self.driver.find_element_by_id("password").send_keys(password)
        self.driver.find_element_by_id("remember").click()
        self.driver.find_element_by_id("login-btn").click()

    def tearDown(self):
        # Closes driver
        self.driver.close()

    def test_a_login(self):
        # Tests if user is logged in
        assert self.driver.current_url == "http://127.0.0.1:5000/menu/"

    def test_b_logout(self):
        # Tests if user is redirected out if they log out
        self.driver.find_element_by_xpath("/html/body/header/nav/div/div/ul[2]/li[2]/a").click()
        assert self.driver.current_url == "http://127.0.0.1:5000/"

    def test_c_remember_me(self):
        # Tests if user is remembered if they leave page for 60 seconds
        self.driver.get("https://www.google.com/")
        sleep(60)
        self.driver.get("http://127.0.0.1:5000/menu/")
        assert self.driver.current_url == "http://127.0.0.1:5000/menu/"


class TestInvalidLogin(unittest.TestCase):
    """Checks if login doesnt accept invalid password or username"""
    def setUp(self):
        # Sets up driver
        self.driver = webdriver.Chrome(ChromeDriverManager().install())
        self.driver.get("http://127.0.0.1:5000/login")

    def tearDown(self):
        # Closes driver
        self.driver.close()

    def test_a_invalid_password(self):
        # Test Data
        email = "user@ucl.ac.uk"
        password = "password"
        # Fills in login form
        self.driver.find_element_by_id("email").send_keys(email)
        self.driver.find_element_by_id("password").send_keys(password)
        self.driver.find_element_by_id("login-btn").click()
        # Checks if error occurs
        error = self.driver.find_element_by_class_name("errors").text
        assert error == "Incorrect password."

    def test_b_invalid_email(self):
        # Test Data
        email = "user@wrong.ac.uk"
        password = "password1"
        # Fills in login form
        self.driver.find_element_by_id("email").send_keys(email)
        self.driver.find_element_by_id("password").send_keys(password)
        self.driver.find_element_by_id("login-btn").click()
        # Checks if error occurs
        error = self.driver.find_element_by_class_name("errors").text
        assert error == "No account found with that email address."


class TestRedirects(unittest.TestCase):
    """Checks if user is redirected to the right login page
    if they are not logged in"""
    def setUp(self):
        # Sets up driver
        self.driver = webdriver.Chrome(ChromeDriverManager().install())

    def tearDown(self):
        # Closes driver
        self.driver.close()

    def test_a_forum_redirect(self):
        # Checks if redirected from forum if not logged in
        self.driver.get("http://127.0.0.1:5000/forum/")
        assert self.driver.current_url == "http://127.0.0.1:5000/login"

    def test_b_plot_redirect(self):
        # Checks if redirected from dash app if not logged in
        self.driver.get("http://127.0.0.1:5000/dash_app/")
        assert self.driver.current_url == "http://127.0.0.1:5000/login"

    def test_b_search_redirect(self):
        # Checks if redirected to login if user tries to search while not logged in
        self.driver.get("http://127.0.0.1:5000")
        self.driver.find_element_by_name("search_term").send_keys("a")
        self.driver.find_element_by_xpath("//*[@id='collapseNavbar']/form/button").click()
        assert self.driver.current_url == "http://127.0.0.1:5000/login"


class TestApp(unittest.TestCase):
    def setUp(self):
        # Sets up driver
        self.driver = webdriver.Chrome(ChromeDriverManager().install())

    def test_app_is_running(self):
        # Checks if the app is running
        self.driver.get("http://127.0.0.1:5000/")
        text = self.driver.find_element_by_class_name("card-text").text
        assert text == 'Become a master sonic sculptor by discovering features of sound'

    def tearDown(self):
        # Closes driver
        self.driver.close()


class TestProfile(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome((ChromeDriverManager()).install())
        self.driver.get("http://127.0.0.1:5000/login")
        # Enter user login details
        email = "user@ucl.ac.uk"
        password = "password1"
        self.driver.find_element_by_id("email").send_keys(email)
        self.driver.find_element_by_id("password").send_keys(password)
        self.driver.find_element_by_id("login-btn").click()
        self.driver.implicitly_wait(10)
        # Deletes Previous User test entry from database
        conn = sqlite3.connect("../../data/example.sqlite")
        conn.execute("Delete From Profile where username like '%user%'")
        conn.commit()

    def test_profile_is_created(self):
        # Go to create profile form
        self.driver.get('http://127.0.0.1:5000/profile/create_profile')
        # Enter profile form details
        username = "user1"
        bio = "blah"
        self.driver.find_element_by_id("username").send_keys(username)
        self.driver.find_element_by_id("bio").send_keys(bio)
        self.driver.find_element_by_id("profile-btn").click()
        self.driver.implicitly_wait(10)
        # Redirect to user's profile
        assert self.driver.current_url == 'http://127.0.0.1:5000/profile/display_profiles/user1/'

    def tearDown(self):
        # Close driver
        self.driver.close()




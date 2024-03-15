import pytest


@pytest.mark.usefixtures('chrome_driver', 'selenium')
class TestMyAppBrowser:
    def test_app_is_running(self, app):
        self.driver.get("http://127.0.0.1:5000/")
        assert self.driver.title == 'Home page'


#Refernce: Lecture notes for testing.

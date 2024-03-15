""" Created by Barraath Jeganathan"""
from my_app.tests.conftest import login


def test_invalid_login_password(client):
    response = login(client, flaskr.app.config['username'], flaskr.app.config['password'] + '$')
    assert b'Incorrect password.' in response.data


##Reference for this code: https://flask.palletsprojects.com/en/1.1.x/testing/
## Given a user is not logged in, When they try and login with an invalid password, Then an error message will be displayed

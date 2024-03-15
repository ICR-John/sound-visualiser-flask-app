""" Created by Barraath Jeganathan"""
from my_app.tests.conftest import login


def test_login(client):
    response = login(client, flaskr.app.config['username'], flaskr.app.config['password'])
    assert b'' in response.data


##Reference for this code: https://flask.palletsprojects.com/en/1.1.x/testing/
#Tests that login works

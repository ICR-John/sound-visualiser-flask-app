""" Created by Barraath Jeganathan"""
from my_app.auth.routes import logout

def test_logout(client):
    response = logout(client)
    assert b'/' in response.data

##Reference for this code: https://flask.palletsprojects.com/en/1.1.x/testing/
#Tests that logout works

""" Created by Barraath Jeganathan"""

def test_redirect_when_login(client):

    response = client.get('/login', follow_redirects=True)
    assert response.status_code == 200
    assert b'/menu' in response.data

##Reference: 1_unit_testing.pdf (lecture notes)
##  Given a user is not logged in, When they try and search a username, Then they will be redirected to the login page

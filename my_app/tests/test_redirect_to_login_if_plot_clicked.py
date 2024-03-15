""" Created by Barraath Jeganathan"""

def test_redirect_to_login_if_plot_clicked(client):
    """
    Given a user is not logged in
    When they try and access the plot page
    Then they will be redirected to the login page
    """
    response = client.get('/dash_app', follow_redirects=True)
    assert response.status_code == 200
    assert b'Login' in response.data


##Reference: 1_unit_testing.pdf (lecture notes)

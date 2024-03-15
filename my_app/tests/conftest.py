""" Created by Ahmed Mohamud, Barraath Jeganathan, Saeeda Doolan """
## Reference for fixture below: https://flask.palletsprojects.com/en/1.1.x/testing/ and ##Reference: 1_unit_testing.pdf (lecture notes)
import os
import tempfile

import pytest
#from flaskr import flaskr

from my_app import create_app
from my_app import db as _db
from my_app.config import TestingConfig


@pytest.fixture(scope='session')
def app(request):
    """ Returns a session wide Flask app (lasts for a session) """
    _app = create_app(TestingConfig)
    ctx = _app.app_context()
    ctx.push()

    yield _app

    ctx.pop()


@pytest.fixture(scope='session')
def client(app):
    """ Exposes the Werkzeug test client for use in the tests. """
    return app.test_client()


@pytest.fixture(scope='session')
def db(app):
    """
    Returns a session wide database using a Flask-SQLAlchemy database connection.
    """
    _db.app = app
    _db.create_all()
    # Add the local authority data to the database (this is a workaround you don't need this for your coursework!)
    yield _db

    # _db.drop_all()


@pytest.fixture(scope='function', autouse=True)
def session(db):
    """ Rolls back database changes at the end of each test """
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session_ = db.create_scoped_session(options=options)

    db.session = session_

    yield session_

    transaction.rollback()
    connection.close()
    session_.remove()


@pytest.fixture(scope='function')
def user(db):
    """ Creates a user without a profile. """
    from my_app.models import User
    user = User(firstname="Person", lastname='One', email='person1@people.com')
    user.set_password('password1')
    db.session.add(user)
    db.session.commit()
    return user

## Reference for fixture below: https://flask.palletsprojects.com/en/1.1.x/testing/
@pytest.fixture
def client():
    db_fd, flaskr.app.config['database'] = tempfile.mkstemp()
    flaskr.app.config['Testing'] = True

    with flaskr.app.test_client()as client:
        with flaskr.app.app_context():
            flaskr.init_db()
        yield client

    os.close(db_fd)
    os.nlink(flaskr.app.config['database'])

## Reference for fixture below: https://flask.palletsprojects.com/en/1.1.x/testing/
def login(client, username, password):
    return client.post('/login', data=dict(
        username= username,
        password= password
    ), follow_redirects=True)

"""Flask config class."""
""" Created by Ahmed Mohamud, Barraath Jeganathan, Beatrix Popa, Isaiah John, Saeeda Doolan """

from pathlib import Path


class Config(object):

    DEBUG = False
    SECRET_KEY = 'abzLMQ6Quf4R6D9HBXCAUA'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DATA_PATH = Path(__file__).parent.parent.joinpath("data")
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + str(DATA_PATH.joinpath('example.sqlite'))  # THIS IS FOR SQLITE
    UPLOADED_PHOTOS_DEST = Path(__file__).parent.joinpath("static/Photos")


class ProductionConfig(Config):
    ENV = 'production'


class DevelopmentConfig(Config):
    ENV = 'development'
    DEBUG = True
    SQLALCHEMY_ECHO = True


class TestingConfig(Config):
    ENV = 'testing'
    TESTING = True
    DATA_PATH = Path(__file__).parent.parent.joinpath("data")
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + str(DATA_PATH.joinpath('example_test.sqlite'))
    SQLALCHEMY_ECHO = True
    WTF_CSRF_ENABLED = False

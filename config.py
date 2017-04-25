import dotenv
import os

dotenv.load()

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = dotenv.get('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SITE_URL = dotenv.get('SITE_URL')


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = dotenv.get('DEV_DATABASE_URL').format(basedir)


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = dotenv.get('TEST_DATABASE_URL').format(basedir)


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL').format(basedir)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

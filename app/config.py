
import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    PROJECT_NAME = 'vietnews'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'very secret key'

    CACHE_TYPE = 'redis'
    CACHE_DEFAULT_TIMEOUT = 60
    CACHE_REDIS_URL = os.environ.get('REDISCLOUD_URL') \
        or 'redis://localhost:6379'


    @staticmethod
    def init_app(app):
        pass

class ProductionConfig(Config):
    MONGO_URI = os.environ.get('MONGOLAB_URI')

class TestingConfig(Config):
    TESTING = True
    DEBUG = os.environ.get('DEBUG')
    MONGO_URI = 'mongodb://localhost:27017/vietnews_test'

class DevelopmentConfig(Config):
    DEBUG = True
    MONGO_URI = 'mongodb://localhost:27017/vietnews'

class HerokuConfig(ProductionConfig):
    @classmethod
    def init_app(cls, app):
        pass

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'heroku': HerokuConfig,

    'default': DevelopmentConfig,
}

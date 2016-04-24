from swing import ConfigBase
import logging

class CommonConfig(ConfigBase):

    SECRET_KEY = "the secret key (you should change this!)"
    DEBUG = True
    DB_CONNECTION = "sqlite:///flask.db"

    DEFAULT_ACCESS_LOG = "./access.log"
    DEFAULT_ERROR_LOG = "./error.log"
    ROOT_LOG = "./app.log"
    ROOT_LOG_LEVEL = logging.DEBUG
    LOG_BASE_FORMAT = "%(asctime)s %(levelname)s (%(filename)s:%(lineno)s) - %(message)s"
    LOG_APP_LEVEL = logging.WARNING

class DevelopmentConfig(CommonConfig):
    
    __confname__ = "dev"

class ProductionConfig(CommonConfig):

    __confname__ = "prod"
    DEBUG = False
    DB_CONNECTION = "sqlite:///flask.prod.db"

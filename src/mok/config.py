"""Config settings for for development, testing and production environments."""


import os
import logging


MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "set the key")
    SCSS_STATIC_DIR = "static"
    SCSS_ASSET_DIR = "assets"
    SESSION_TYPE = "filesystem"
    # Logging details
    LOGGING_NAME = "gunicorn.error"
    LOGGING_DIR = "logs/"
    LOGGING_LEVEL = logging.DEBUG
    LOGGING_FORMAT = "%(asctime)s: %(levelname)s: %(process)d: %(message)s"
    BABEL_DEFAULT_LOCALE = "fr"
    BABEL_TRANSLATION_DIRECTORIES = "translations"
    LANGUAGES = ["fr", "en"]
    API_KEY = os.getenv("API_KEY")


class TestingConfig(Config):
    TESTING = True
    LOGGING_FILE_NAME = "testing" + "-electricity.log"
    API_BASE_URL = os.getenv("TEST_API_BASE_URL", "http://localhost:5000")


class DevelopmentConfig(Config):
    LOGGING_FILE_NAME = "development" + "-electricity.log"
    API_BASE_URL = os.getenv("DEV_API_BASE_URL")


class ProductionConfig(Config):
    LOGGING_FILE_NAME = "production" + "-electricity.log"
    API_BASE_URL = os.getenv("PROD_API_BASE_URL")


ENV_CONFIG_DICT = dict(
    development=DevelopmentConfig, testing=TestingConfig, production=ProductionConfig
)


def get_config(config_name):
    return ENV_CONFIG_DICT.get(config_name, ProductionConfig)

import logging
import os
import sys


# logging.getLogger().setLevel(logging.DEBUG)


class Logger:
    # Here will be the instance stored.
    __instance = None

    @staticmethod
    def get_instance():
        """Static access method."""
        if Logger.__instance is None:
            raise Exception("Logger not initialised!")
        return Logger.__instance

    @staticmethod
    def init_logger(app):
        if Logger.__instance is None:
            Logger.__instance = Logger.__setup_logger(app)

    def __init__(self):
        """Virtually private constructor."""
        if Logger.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            Logger.__instance = self

    @staticmethod
    def __setup_logger(app):
        try:
            logger = logging.getLogger(app.config["LOGGING_NAME"])

            os.makedirs(app.config["LOGGING_DIR"], exist_ok=True)
            file_handler = logging.FileHandler(
                os.path.join(
                    app.config["LOGGING_DIR"],
                    app.config["LOGGING_FILE_NAME"],
                )
            )
            file_handler.setFormatter(logging.Formatter(app.config["LOGGING_FORMAT"]))

            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(logging.Formatter(app.config["LOGGING_FORMAT"]))

            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
            logger.setLevel(app.config["LOGGING_LEVEL"])

            app.logger.handlers = logger.handlers
            app.logger.setLevel(app.config["LOGGING_LEVEL"])

            return app.logger
        except KeyError:
            return None

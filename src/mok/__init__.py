from flask_scss import Scss
from flask import Flask
from flask_material import Material

# from flask_materialize import Material
from flask_session import Session
from flask_bootstrap import Bootstrap
from flask_babel import Babel
from flask import session

from mok.config import get_config
from mok.utils.logger import Logger
from mok.core.main import main_bp
from mok.auth.auth import auth_bp
from mok.auth.auth_bo import auth_bo_bp
from mok.auth.auth_corporate import auth_corp_bp
from mok.core.corp_dashboard import corporate_bp

babel = Babel()


def create_app(config_name):
    app = Flask("Mok Portals", template_folder="./templates")
    app.config.from_object(get_config(config_name))

    Logger.init_logger(app)
    # blueprint for auth routes in our app
    app.register_blueprint(auth_bp)
    # blueprint for back office auth routes in our app
    app.register_blueprint(auth_bo_bp)
    # blueprint for corporate auth routes in our app
    app.register_blueprint(auth_corp_bp)

    # blueprint for non-auth parts of app
    app.register_blueprint(main_bp)
    # blueprint for corporate dashboard
    app.register_blueprint(corporate_bp)

    Session(app)
    Scss(app)
    Material(app)
    Bootstrap(app)
    babel.init_app(app)
    return app


@babel.localeselector
def get_locale():
    try:
        return session["platform_language"]
    except KeyError:
        return "en"

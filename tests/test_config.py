"""Unit tests for environment config settings."""
import os
import pytest


from mok import create_app


def test_config_development():
    app = create_app("development")
    if os.getenv("SECRET_KEY") is None:
        pytest.skip("unsupported configuration")
    assert app.config["SECRET_KEY"] != "set the key"
    assert not app.config["TESTING"]
    # assert app.config["API_BASE_URL"] != "http://localhost:5000"


def test_config_testing():
    app = create_app("testing")
    if os.getenv("SECRET_KEY") is None:
        pytest.skip("unsupported configuration")
    assert app.config["SECRET_KEY"] != "set the key"
    assert app.config["TESTING"]
    assert app.config["API_BASE_URL"] == "http://localhost:5000"


def test_config_production():
    app = create_app("production")
    if os.getenv("SECRET_KEY") is None:
        pytest.skip("unsupported configuration")
    assert app.config["SECRET_KEY"] != "set the key"
    assert not app.config["TESTING"]
    # assert app.config["API_BASE_URL"] != "http://localhost:5000"

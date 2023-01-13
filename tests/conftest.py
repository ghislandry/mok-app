import pytest

from mok import create_app


@pytest.fixture
def app():
    """Returns an instance of the flask test client"""
    app = create_app("testing")
    return app

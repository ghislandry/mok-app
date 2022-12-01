"""Installation script for flask-api-tutorial application."""

from pathlib import Path
from setuptools import setup, find_packages


DESCRIPTION = "Mok Portal"
APP_ROOT = Path(__file__).parent
README = (APP_ROOT / "README.md").read_text()
print(README)
AUTHOR = "Ghislain Landry"
AUTHOR_EMAIL = "ghislain@gmail.com"
PROJECT_URLS = {
    "Documentation": "https://sight-techgroup.com/series/mok-app/",
    "Bug Tracker": "https://bitbucket.org/elementalconcept/mok-app/issues",
    "Source Code": "https://bitbucket.org/elementalconcept/mok-app",
}


INSTALL_REQUIRES = [
    "Flask==2.1.0",
    "Flask-Bcrypt",
    "Flask-Cors",
    "python-dateutil",
    "python-dotenv",
    "requests",
    "urllib3",
    "gunicorn",
    "cryptography",
    "werkzeug<2.1",
    "markupsafe==2.0.1",
    "flask_language",
    "Flask-Scss",
    "flask-material",
    "flask_session",
    "flask_bootstrap",
    "flask-babel",
]


EXTRAS_REQUIRE = {
    "dev": [
        "black",
        "flake8",
        "pre-commit",
        "pydocstyle",
        "pytest",
        "pytest-black",
        "pytest-clarity",
        "pytest-dotenv",
        "pytest-flake8",
        "pytest-flask",
        "tox",
        "pybuilder",
        "gitpython",
        "moto",
        "markupsafe",
    ]
}


setup(
    name="mok",
    description=DESCRIPTION,
    long_description=README,
    long_description_content_type="text/markdown",
    version="0.1",
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    maintainer=AUTHOR,
    maintainer_email=AUTHOR_EMAIL,
    license="MIT",
    url="https://ai.mok.com/admin",
    project_urls=PROJECT_URLS,
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.6",
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
)

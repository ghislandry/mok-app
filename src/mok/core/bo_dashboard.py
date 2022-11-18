from http import HTTPStatus
from flask import (
    Blueprint,
    redirect,
    url_for,
    request,
    current_app,
    session,
    render_template,
    flash,
)
from flask_babel import _
import requests
import json
import copy
import ast

from mok.platform_config import get_platform_language
from mok.auth import error_map
from mok.utils.error_codes import EMPLOYEE_NOT_FOUND

backoffice_bp = Blueprint("backoffice_bp", __name__)


@backoffice_bp.route("/bo/assets")
def bo_assets():
    api_base_url = current_app.config.get('API_BASE_URL')
    access_token = session["access_token"]
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    authorization = "Bearer {access_token}".format(access_token=access_token)
    headers = {"Authorization": authorization}
    response = requests.get(
        f"{api_base_url}/api/v1/assets?page={page}&per_page={per_page}",
        headers=headers,
    )
    logged_in_employee = session["logged_in_employee"]
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        error = _("Your session has expired. Please log in again")
        # Get the configuration for the platform
        flash(error, "error")
        p_language, portal = get_platform_language()
        return render_template(
            "bo_login.html", p_language=p_language, portal=portal,
        )
    # store the fact that we are looking
    return render_template(
        "bo_assets.html",
        assets=response.json(),
        logged_in_employee=logged_in_employee,
    )


@backoffice_bp.route("/bo/customers")
def bo_customers():
    api_base_url = current_app.config.get('API_BASE_URL')
    access_token = session["access_token"]
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    authorization = "Bearer {access_token}".format(access_token=access_token)
    headers = {"Authorization": authorization}
    response = requests.get(
        f"{api_base_url}/api/v1/customers?page={page}&per_page={per_page}",
        headers=headers,
    )
    logged_in_employee = session["logged_in_employee"]
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        error = _("Your session has expired. Please log in again")
        # Get the configuration for the platform
        flash(error, "error")
        p_language, portal = get_platform_language()
        return render_template(
            "bo_login.html", p_language=p_language, portal=portal,
        )
    # store the fact that we are looking
    return render_template(
        "bo_customers.html",
        users=response.json(),
        logged_in_employee=logged_in_employee,
    )

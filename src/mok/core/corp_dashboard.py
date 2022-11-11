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

corporate_bp = Blueprint("corporate_bp", __name__)


@corporate_bp.route("/corp/profile")
def corp_profile():
    access_token = session["access_token"]

    authorization = "Bearer {access_token}".format(access_token=access_token)
    headers = {"Authorization": authorization, "Content-Type": "application/json"}
    logged_in_employee = session["logged_in_employee"]
    api_base_url = current_app.config.get('API_BASE_URL')
    response = requests.get(
        f"{api_base_url}/api/v1/employees/{logged_in_employee['employee_number']}",
        headers=headers,
    )
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        error = _("Your session has expired. Please log in again")
        p_language, portal = get_platform_language()
        return render_template(
            "corporate_login.html",
            p_language=p_language,
            portal=portal,
            error=error,
        )
    if (
        "ErrorCode" in response.json()
        and response.json()["ErrorCode"] == EMPLOYEE_NOT_FOUND
    ):
        # the user does not have a profile yet!
        return redirect(url_for("corporate_bp.corp_dashboard"))
    return render_template("corporate_profile.html", user=response.json())


@corporate_bp.route("/update_profile/<data_dict>", methods=["post"])
def update_profile_post(data_dict):
    access_token = session["access_token"]
    data = copy.deepcopy(data_dict)
    city = request.form.get("city")
    phone_number = request.form.get("phone_number")
    email_address = request.form.get("email")
    data = ast.literal_eval(data)
    #
    data.update(
        {
            "city": city,
            "phone_number": phone_number,
            "email_address": email_address,
        }
    )
    corporate_id = data.pop("corporate_id")

    authorization = "Bearer {access_token}".format(access_token=access_token)
    headers = {
        "Content-Type": "application/json",
        "Authorization": authorization,
    }
    response = requests.put(
        f"{current_app.config.get('API_BASE_URL')}/api/v1/employees/{corporate_id}",
        headers=headers,
        data=json.dumps(data),
    )
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        error = _("Your session has expired. Please log in again")
        return redirect(url_for("auth_corp_bp.corp_login", error=error))
    # return render_template("login.html", error=error)
    # flash(
    #     _("Role of user %(corporate_id)s successfully changed to %(role)s!").format(
    #         corporate_id=corporate_id, role=role
    #     ),
    #     "success"
    # )
    return redirect(url_for("corporate_bp.corp_profile"))


@corporate_bp.route("/corp/dashboard")
def corp_dashboard():
    access_token = session["access_token"]
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    authorization = "Bearer {access_token}".format(access_token=access_token)
    headers = {"Authorization": authorization}
    api_base_url = current_app.config.get('API_BASE_URL')
    response = requests.get(
        f"{api_base_url}/api/v1/employees?page={page}&per_page={per_page}",
        headers=headers,
    )
    logged_in_employee = session["logged_in_employee"]
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        error = _("Your session has expired. Please log in again")
        # Get the configuration for the platform
        p_language, portal = get_platform_language()
        return render_template(
            "corporate_login.html", p_language=p_language, portal=portal, error=error
        )
    return render_template(
        "corporate_dashboard.html",
        users=response.json(),
        logged_in_employee=logged_in_employee,
    )


@corporate_bp.route("/corp/dashboard", methods=["post"])
def corp_dashboard_post():
    access_token = session["access_token"]
    # page = request.args.get('page', 1, type=int)
    # per_page = request.args.get('per_page', 10, type=int)
    corporate_id = request.form.get("corporate_id")
    phone_number = request.form.get("phone_number")
    last_name = request.form.get("last_name")
    data = {
        "corporate_id": corporate_id if len(corporate_id) > 0 else None,
        "phone_number": phone_number if len(phone_number) > 0 else None,
        "last_name": last_name if len(last_name) > 0 else None,
    }
    if all(i is None for i in data.values()):
        return redirect(url_for("corporate_bp.corp_dashboard"))
    authorization = "Bearer {access_token}".format(access_token=access_token)
    headers = {
        "Content-Type": "application/json",
        "Authorization": authorization,
    }
    response = requests.get(
        f"{current_app.config.get('API_BASE_URL')}/api/v1/employees/search",
        headers=headers,
        data=json.dumps(data),
    )
    logged_in_employee = session["logged_in_employee"]
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        error = _("Your session has expired. Please log in again")
        # Get the configuration for the platform
        p_language, portal = get_platform_language()
        return render_template(
            "corporate_login.html", p_language=p_language, portal=portal, error=error
        )
    elif "ErrorCode" in response.json():
        users = None
    else:
        users = response.json()
    return render_template(
        "corporate_dashboard.html",
        users=users,
        logged_in_employee=logged_in_employee,
    )


@corporate_bp.route("/corp/edit_employee_details/<employee_number>", methods=["post"])
def corp_edit_employee_details(employee_number):
    access_token = session["access_token"]
    api_base_url = current_app.config.get('API_BASE_URL')
    data = {
        "last_name": request.form.get("last_name"),
        "phone_number": request.form.get("phone_number"),
        "first_name": request.form.get("first_name"),
        "date_of_birth": request.form.get("date_of_birth"),
        "gender": request.form.get("gender"),
        "city": request.form.get("city"),
        "email_address": request.form.get("email_address"),
    }
    authorization = "Bearer {access_token}".format(access_token=access_token)
    headers = {
        "Content-Type": "application/json",
        "Authorization": authorization,
    }
    response = requests.put(
        f"{api_base_url}/api/v1/employees/{employee_number}",
        headers=headers,
        data=json.dumps(data),
    )
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        error = _("Your session has expired. Please log in again.")
        return redirect(url_for("auth_corp_bp.corp_login", error=error))
    elif response.status_code in [
        HTTPStatus.CONFLICT,
        HTTPStatus.INTERNAL_SERVER_ERROR,
        HTTPStatus.BAD_REQUEST,
    ]:
        try:
            error = error_map[f"{response.json()['ErrorCode']}"]
        except KeyError:
            error = _("Input payload validation failed")
        flash(error, "error")
        return render_template(
            "corporate_register_employee.html",
            error=error_map[f"{response.json()['ErrorCode']}"],
        )
    return redirect(url_for("corporate_bp.corp_dashboard"))


@corporate_bp.route("/corp/register_employee")
def corp_register_employee():
    logged_in_employee = session["logged_in_employee"]
    return render_template(
        "corporate_register_employee.html", logged_in_employee=logged_in_employee
    )


@corporate_bp.route("/corp/register_employee", methods=["post"])
def corp_register_employee_post():
    access_token = session["access_token"]
    data = {
        "employee_number": request.form.get("corporate_id"),
        "first_name": request.form.get("first_name"),
        "last_name": request.form.get("last_name"),
        "gender": request.form.get("gender"),
        "date_of_birth": request.form.get("date_of_birth"),
        "city": request.form.get("city"),
        "phone_number": request.form.get("phone_number"),
        "email_address": request.form.get("email_address"),
    }
    authorization = "Bearer {access_token}".format(access_token=access_token)
    headers = {
        "Content-Type": "application/json",
        "Authorization": authorization,
    }
    response = requests.post(
        f"{current_app.config.get('API_BASE_URL')}/api/v1/employees",
        headers=headers,
        data=json.dumps(data),
    )
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        error = _("Your session has expired. Please log in again.")
        return redirect(url_for("auth_corp_bp.corp_login", error=error))
    elif response.status_code in [
        HTTPStatus.CONFLICT,
        HTTPStatus.INTERNAL_SERVER_ERROR,
        HTTPStatus.BAD_REQUEST,
    ]:
        try:
            error = error_map[f"{response.json()['ErrorCode']}"]
        except KeyError:
            error = _("Input payload validation failed")
        flash(error, "error")
        logged_in_employee = session["logged_in_employee"]
        return render_template(
            "corporate_register_employee.html",
            error=error,
            logged_in_employee=logged_in_employee,
        )
    return redirect(url_for("corporate_bp.corp_dashboard"))


@corporate_bp.route("/corp/manage_employee_status/<employee_number>", methods=["post"])
def corp_manage_employee_status(employee_number):
    access_token = session["access_token"]
    new_status = request.form.get("status")
    api_base_url = current_app.config.get('API_BASE_URL')
    authorization = "Bearer {access_token}".format(access_token=access_token)
    headers = {
        "Content-Type": "application/json",
        "Authorization": authorization,
    }

    if new_status == "suspend":
        query_url = f"{api_base_url}/api/v1/employees/{employee_number}/suspend"
    else:
        query_url = f"{api_base_url}/api/v1/employees/{employee_number}/reinstate"

    response = requests.post(query_url, headers=headers)
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        error = _("Your session has expired. Please log in again.")
        return redirect(url_for("auth_corp_bp.corp_login", error=error))
    elif response.status_code in [
        HTTPStatus.CONFLICT,
        HTTPStatus.INTERNAL_SERVER_ERROR,
        HTTPStatus.BAD_REQUEST,
    ]:
        try:
            error = error_map[f"{response.json()['ErrorCode']}"]
        except KeyError:
            error = _("Input payload validation failed")
        flash(error, "error")
        return redirect(url_for("corporate_bp.corp_dashboard"))
    return redirect(url_for("corporate_bp.corp_dashboard"))


def _redirect_to_login():
    error = _("Your session has expired. Please log in again")
    p_language, portal = get_platform_language()
    return render_template(
        "corporate_login.html",
        p_language=p_language,
        portal=portal,
        error=error,
    )

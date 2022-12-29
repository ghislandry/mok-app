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
import requests
import json
from flask_babel import _

from mok.auth import error_map, logged_in_user
from mok.platform_config import get_platform_language
from mok.models import RolesTypes, Portals
from mok.utils.error_codes import (
    PASSWORD_RESET_REQUIRED,
    EMPLOYEE_NOT_FOUND,
    WRONG_USERNAME_OR_PASSWORD,
    USER_NOT_FOUND,
)


auth_corp_bp = Blueprint("auth_corp_bp", __name__)


@auth_corp_bp.route("/corp/login")
def corp_login():
    p_language, portal = get_platform_language()
    return render_template("corporate_login.html", p_language=p_language, portal=portal)


@auth_corp_bp.route("/corp/login", methods=["post"])
def corp_login_post():
    api_base_url = current_app.config.get("API_BASE_URL")
    password = request.form.get("corp_password")
    corporate_id = request.form.get("corporate_id")
    data = {
        "corporate_id": request.form.get("corporate_id"),
        "password": request.form.get("corp_password"),
    }
    authorization = "Bearer {access_token}".format(
        access_token=current_app.config.get("API_KEY")
    )
    headers = {
        "Content-Type": "application/json",
        "Authorization": authorization,
    }
    response = requests.post(
        f"{api_base_url}/api/v1/auth/corporate/login",
        headers=headers,
        data=json.dumps(data),
    )
    if response.json()["status"] == "fail":
        p_language, portal = get_platform_language()
        if (
            "ErrorCode" in response.json()
            and response.json()["ErrorCode"] == PASSWORD_RESET_REQUIRED
        ):
            session["verification_code"] = password
            session["corporate_id"] = corporate_id
            return redirect(url_for("auth_corp_bp.reset_password"))
        else:
            error = (
                _("Incorrect Corporate Id or Password")
                if response.json()["ErrorCode"]
                in [WRONG_USERNAME_OR_PASSWORD, USER_NOT_FOUND]
                else error_map[f"{response.json()['ErrorCode']}"]
            )
            flash(error, "error")
            return render_template(
                "corporate_login.html",
                p_language=p_language,
                portal=portal,
            )
    access_token = response.json()["access_token"]
    # Store the session token and employee number
    session["access_token"] = access_token
    # find out which user is connected and route accordingly
    url = f"{api_base_url}/api/v1/auth/corporate/user"
    response = logged_in_user(access_token=access_token, url=url)

    if response.status_code == HTTPStatus.UNAUTHORIZED:
        error = _("Your session has expired. Please log in again")
        flash(error, "error")
        p_language, portal = get_platform_language()
        return render_template(
            "corporate_login.html",
            p_language=p_language,
            portal=portal,
        )
    if (
        "ErrorCode" in response.json()
        and response.json()["ErrorCode"] == EMPLOYEE_NOT_FOUND
    ):
        error = (
            _("Incorrect Corporate Id or Password")
            if response.json()["ErrorCode"]
            in [WRONG_USERNAME_OR_PASSWORD, USER_NOT_FOUND]
            else error_map[f"{response.json()['ErrorCode']}"]
        )
        p_language, portal = get_platform_language()
        flash(error, "error")
        return render_template(
            "corporate_login.html",
            p_language=p_language,
            portal=portal,
        )
    logged_in_employee = {
        "employee_number": response.json()["employee_number"],
        "phone_number": response.json()["phone_number"],
        "last_name": None,
    }
    role = response.json()["role"]
    # Get employee profile details
    url = f"{api_base_url}/api/v1/employees/{response.json()['employee_number']}"
    response = logged_in_user(access_token=access_token, url=url)
    found = True
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        error = _("Your session has expired. Please log in again")
        flash(error, "error")
        p_language, portal = get_platform_language()
        return render_template(
            "corporate_login.html",
            p_language=p_language,
            portal=portal,
        )
    if (
        "ErrorCode" in response.json()
        and response.json()["ErrorCode"] == EMPLOYEE_NOT_FOUND
    ):
        found = False
    if found is True:
        logged_in_employee.update({"last_name": response.json()["last_name"]})

    session["logged_in_employee"] = logged_in_employee
    if role in [RolesTypes.senioremployee.name]:
        return redirect(url_for("corporate_bp.corp_dashboard"))
    else:
        session["employee_profile"] = response.json() if found is True else None
        return redirect(url_for("corporate_bp.corp_profile"))


@auth_corp_bp.route("/corp/forgot-password")
def forgot_password():
    p_language, portal = get_platform_language()
    return render_template("corporate_forgot_password.html", portal=portal)


@auth_corp_bp.route("/corp/forgot-password", methods=["post"])
def forgot_password_post():
    corporate_id = request.form.get("corporate_id")
    phone_number = request.form.get("phone_number")
    data = {"corporate_id": corporate_id, "phone_number": phone_number}
    session["corporate_id"] = corporate_id
    session["phone_number"] = phone_number
    authorization = "Bearer {access_token}".format(
        access_token=current_app.config.get("API_KEY")
    )
    headers = {
        "Content-Type": "application/json",
        "Authorization": authorization,
    }
    api_base_url = current_app.config.get("API_BASE_URL")
    _ = requests.post(
        f"{api_base_url}/api/v1/auth/corporate/forgot_password",
        headers=headers,
        data=json.dumps(data),
    )
    return redirect(url_for("auth_corp_bp.reset_password_code"))


@auth_corp_bp.route("/corp/reset-credentials")
def reset_password_code():
    return render_template("corporate_reset_password_code.html")


@auth_corp_bp.route("/corp/reset-credentials", methods=["post"])
def reset_password_code_post():
    session["verification_code"] = request.form.get("verification_code")
    return redirect(url_for("auth_corp_bp.reset_password"))


@auth_corp_bp.route("/corp/reset-password")
def reset_password():
    return render_template("corporate_reset_password.html")


@auth_corp_bp.route("/corp/reset-password", methods=["post"])
def reset_password_post():
    new_password = request.form.get("new_password")
    re_password = request.form.get("re_password")
    if new_password != re_password:
        error = _("Password does not match")
        return render_template("corporate_reset_password.html", error=error)
    try:
        phone_number = session.pop("phone_number")
    except KeyError:
        phone_number = ""
    data = {
        "verification_code": session.pop("verification_code"),
        "password": new_password,
        "phone_number": phone_number,
        "corporate_id": session.pop("corporate_id"),
    }
    authorization = "Bearer {access_token}".format(
        access_token=current_app.config.get("API_KEY")
    )
    headers = {
        "Content-Type": "application/json",
        "Authorization": authorization,
    }
    response = requests.post(
        f"{current_app.config.get('API_BASE_URL')}/api/v1/auth/corporate/reset_password",
        headers=headers,
        data=json.dumps(data),
    )
    if response.json()["status"] == "fail":
        flash(error_map[f"{response.json()['ErrorCode']}"], "error")
        return render_template("corporate_reset_password.html")
    flash(_("Password successfully changed"), "information")
    p_language, portal = get_platform_language()
    return (
        redirect(url_for("auth_corp_bp.corp_login"))
        if portal == Portals.corp.name
        else redirect(url_for("auth_bo_bp.bo_login"))
    )


@auth_corp_bp.route("/corp/logout")
def corp_logout():
    access_token = session["access_token"]
    authorization = "Bearer {access_token}".format(access_token=access_token)
    headers = {
        "Content-Type": "application/json",
        "Authorization": authorization,
    }
    response = requests.post(
        f"{current_app.config.get('API_BASE_URL')}/api/v1/auth/corporate/logout",
        headers=headers,
    )
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        return redirect(url_for("auth_corp_bp.corp_login"))
    _ = session.pop("access_token")
    return redirect(url_for("auth_corp_bp.corp_login"))

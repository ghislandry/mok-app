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

from mok_admin.auth import error_map, logged_in_user
from mok_admin.platform_config import get_platform_language
from mok_admin.models import RolesTypes
from mok_admin.utils.error_codes import PASSWORD_RESET_REQUIRED, EMPLOYEE_NOT_FOUND


auth_corp_bp = Blueprint("auth_corp_bp", __name__)


@auth_corp_bp.route("/corp/login")
def corp_login():
    p_language, portal = get_platform_language()
    return render_template("corporate_login.html", p_language=p_language, portal=portal)


@auth_corp_bp.route("/corp/login", methods=["post"])
def corp_login_post():
    password = request.form.get("corp_password")
    corporate_id = request.form.get("corporate_id")
    data = {
        "corporate_id": request.form.get("corporate_id"),
        "password": request.form.get("corp_password")
    }
    authorization = "Bearer {access_token}".format(
        access_token=current_app.config.get("API_KEY")
    )
    headers = {
        "Content-Type": "application/json",
        "Authorization": authorization,
    }
    response = requests.post(
        f"{current_app.config.get('API_BASE_URL')}/api/v1/auth/corporate/login",
        headers=headers,
        data=json.dumps(data),
    )
    if response.json()["status"] == "fail":
        p_language, portal = get_platform_language()
        if"ErrorCode" in response.json() and response.json()["ErrorCode"] == PASSWORD_RESET_REQUIRED:
            session["verification_code"] = password
            session["corporate_id"] = corporate_id
            return redirect(url_for("auth_corp_bp.reset_password"))
        else:
            return render_template(
                "corporate_login.html",
                p_language=p_language,
                portal=portal,
                error=error_map[f"{response.json()['ErrorCode']}"],
            )
    # Store the session token and employee number
    session["access_token"] = response.json()["access_token"]
    # find out which user is connected and route accordingly
    url = f"{current_app.config.get('API_BASE_URL')}/api/v1/auth/corporate/user"
    response = logged_in_user(access_token=response.json()["access_token"], url=url)

    if response.status_code == HTTPStatus.UNAUTHORIZED:
        error = _("Your session has expired. Please log in again")
        p_language, portal = get_platform_language()
        return render_template(
            "corporate_login.html",
            p_language=p_language,
            portal=portal,
            error=error,
        )
    if "ErrorCode" in response.json() and response.json()["ErrorCode"] == EMPLOYEE_NOT_FOUND:
        error = error_map[f"{response.json()['ErrorCode']}"]
        p_language, portal = get_platform_language()
        return render_template(
            "corporate_login.html",
            p_language=p_language,
            portal=portal,
            error=error,
        )
    logged_in_employee = {
        "employee_number": response.json()["employee_number"],
        "phone_number": response.json()["phone_number"],
    }
    session["logged_in_employee"] = logged_in_employee
    role = response.json()["role"]
    if role in [RolesTypes.senioremployee.name]:
        return redirect(url_for("corporate_bp.corp_dashboard"))
    else:
        return redirect(url_for("corporate_bp.corp_profile"))


@auth_corp_bp.route("/corp/forgot-password")
def forgot_password():
    return render_template("corporate_forgot_password.html")


@auth_corp_bp.route("/corp/forgot-password", methods=["post"])
def forgot_password_post():
    corporate_id = request.form.get("corporate_id")
    phone_number = request.form.get("phone_number")
    data = {
        "corporate_id": corporate_id,
        "phone_number": phone_number
    }
    session["corporate_id"] = corporate_id
    session["phone_number"] = phone_number
    authorization = "Bearer {access_token}".format(
        access_token=current_app.config.get("API_KEY")
    )
    headers = {
        "Content-Type": "application/json",
        "Authorization": authorization,
    }
    _ = requests.post(
        f"{current_app.config.get('API_BASE_URL')}/api/v1/auth/corporate/forgot_password",
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
        return render_template(
            "corporate_reset_password.html", error=error_map[f"{response.json()['ErrorCode']}"]
        )
    flash(_("Password successfully changed"))
    return redirect(url_for("auth_corp_bp.corp_login"))


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





#
# @auth_bp.route("/register_employee")
# def register_employee():
#     return render_template("register_corporate_user.html")
#
#
# @auth_bp.route("/register_employee", methods=["post"])
# def register_employee_post():
#     access_token = session["access_token"]
#     data = {
#         "corporate_id": request.form.get("corporate_id"),
#         "phone_number": request.form.get("phone_number"),
#         "role": request.form.get("role"),
#     }
#     authorization = "Bearer {access_token}".format(access_token=access_token)
#     headers = {
#         "Content-Type": "application/json",
#         "Authorization": authorization,
#     }
#     response = requests.post(
#         f"{current_app.config.get('API_BASE_URL')}/api/v1/auth/corporate/register",
#         headers=headers,
#         data=json.dumps(data),
#     )
#     if response.status_code == HTTPStatus.UNAUTHORIZED:
#         error = _("Your session has expired. Please log in again.")
#         return redirect(
#             url_for(
#                 "auth_bp.login", error=error
#             )
#         )
#     elif response.status_code in [
#         HTTPStatus.CONFLICT,
#         HTTPStatus.INTERNAL_SERVER_ERROR,
#         HTTPStatus.BAD_REQUEST,
#     ]:
#         flash(error_map[f"{response.json()['ErrorCode']}"], "error")
#         return render_template(
#             "register_corporate_user.html",
#             error=error_map[f"{response.json()['ErrorCode']}"],
#         )
#     return redirect(url_for("main_bp.dashboard"))

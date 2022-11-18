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
from mok.utils.error_codes import PASSWORD_RESET_REQUIRED, EMPLOYEE_NOT_FOUND


auth_bo_bp = Blueprint("auth_bo_bp", __name__)


@auth_bo_bp.route("/bo/login")
def bo_login():
    try:
        p_language = (
            _("French") if session["platform_language"] == "fr" else _("English")
        )
    except KeyError:
        p_language = _("English")
    portal = _("Back Office")
    session["portal"] = Portals.bo.name
    return render_template("bo_login.html", p_language=p_language, portal=portal)


@auth_bo_bp.route("/bo/login", methods=["post"])
def bo_login_post():
    api_base_url = current_app.config.get('API_BASE_URL')
    password = request.form.get("bo_password")
    corporate_id = request.form.get("corporate_id")
    data = {
        "corporate_id": request.form.get("corporate_id"),
        "password": request.form.get("bo_password"),
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
            flash(error_map[f"{response.json()['ErrorCode']}"], "error")
            return render_template(
                "corporate_login.html",
                p_language=p_language,
                portal=portal,
            )
    # Store the session token and employee number
    access_token = response.json()["access_token"]
    session["access_token"] = access_token
    # find out which user is connected and route accordingly
    url = f"{api_base_url}/api/v1/auth/corporate/user"
    response = logged_in_user(access_token=response.json()["access_token"], url=url)

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
        error = error_map[f"{response.json()['ErrorCode']}"]
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
    session["logged_in_employee"] = logged_in_employee
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
    if role in [RolesTypes.senioremployee.name, RolesTypes.employee.name]:
        if found is True:
            logged_in_employee.update({"last_name": response.json()["last_name"]})
        session["logged_in_employee"] = logged_in_employee
        return redirect(url_for("backoffice_bp.bo_assets"))
    else:
        flash(_("You are not authorized to access this portal! Contact your administrator"))
        return redirect(url_for("backoffice_bp.bo_login"))


@auth_bo_bp.route("/bo/logout")
def bo_logout():
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
        return redirect(url_for("auth_bo_bp.bo_login"))
    _ = session.pop("access_token")
    return redirect(url_for("auth_bo_bp.bo_login"))


# @auth_bo_bp.route("/bo/login", methods=["post"])
# def login_post():
#     data = {
#         "corporate_id": request.form.get("corporate_id"),
#         "password": request.form.get("password"),
#     }
#     authorization = "Bearer {access_token}".format(
#         access_token=current_app.config.get("API_KEY")
#     )
#     headers = {
#         "Content-Type": "application/json",
#         "Authorization": authorization,
#     }
#     response = requests.post(
#         f"{current_app.config.get('API_BASE_URL')}/api/v1/auth/corp/login",
#         headers=headers,
#         data=json.dumps(data),
#     )
#     if response.json()["status"] == "fail":
#         flash(error_map[f"{response.json()['ErrorCode']}"], "error")
#         return render_template("login.html")
#     session["access_token"] = response.json()["access_token"]
#     return redirect(url_for("main_bp.dashboard"))
#
#

# @auth_bp.route("/forgot-password")
# def forgot_password():
#     return render_template("forgot-password.html")
#
#
# @auth_bp.route("/forgot-password", methods=["post"])
# def forgot_password_post():
#     data = {
#         "email": request.form.get("email"),
#     }
#     authorization = "Bearer {access_token}".format(
#         access_token=current_app.config.get("API_KEY")
#     )
#     headers = {
#         "Content-Type": "application/json",
#         "Authorization": authorization,
#     }
#     _ = requests.post(
#         f"{current_app.config.get('API_BASE_URL')}/api/v1/auth/admin/forgot_password",
#         headers=headers,
#         data=json.dumps(data),
#     )
#     return redirect(url_for("auth_bp.forgot_password_confirmation"))
#
#
# @auth_bp.route("/forgot-password-confirmation")
# def forgot_password_confirmation():
#     return render_template("forgot-password-confirmation.html")
#
#
# @auth_bp.route("/reset-password/<token>")
# def reset_password(token):
#     session["reset_password_token"] = token
#     return render_template("reset_password.html")
#
#
# @auth_bp.route("/reset-password", methods=["post"])
# def reset_password_post():
#     reset_token = session["reset_password_token"]
#     new_password = request.form.get("new_password")
#     re_password = request.form.get("re_password")
#     if new_password != re_password:
#         return render_template("reset_password.html", error="Password does not match")
#     data = {"token": reset_token, "password": request.form.get("re_password")}
#     authorization = "Bearer {access_token}".format(
#         access_token=current_app.config.get("API_KEY")
#     )
#     headers = {
#         "Content-Type": "application/json",
#         "Authorization": authorization,
#     }
#     response = requests.post(
#         f"{current_app.config.get('API_BASE_URL')}/api/v1/auth/admin/reset_password",
#         headers=headers,
#         data=json.dumps(data),
#     )
#     if response.json()["status"] == "fail":
#         return render_template(
#             "reset_password.html", error=error_map[f"{response.json()['ErrorCode']}"]
#         )
#     flash("Password successfully changed")
#     return redirect(url_for("auth_bp.login"))
#
#
# @auth_bp.route("/bo/logout")
# def logout():
#     access_token = session["access_token"]
#     authorization = "Bearer {access_token}".format(access_token=access_token)
#     headers = {
#         "Content-Type": "application/json",
#         "Authorization": authorization,
#     }
#     response = requests.post(
#         f"{current_app.config.get('API_BASE_URL')}/api/v1/auth/admin/logout",
#         headers=headers,
#     )
#     if response.status_code == HTTPStatus.UNAUTHORIZED:
#         return redirect(url_for("auth_bp.login"))
#     return redirect(url_for("auth_bp.login"))
#
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

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

from mok_admin.auth import error_map


auth_bo_bp = Blueprint("auth_bo_bp", __name__)


@auth_bo_bp.route("/bo/login")
def bo_login():
    try:
        p_language = _("French") if session["platform_language"] == "fr" else _("English")
    except KeyError:
        p_language = _("English")
    portal = _("Back Office")
    session["portal"] = "bo"
    return render_template("bo_login.html", p_language=p_language, portal=portal)


# @auth_bp.route("/login", methods=["post"])
# def login_post():
#     data = {"email": request.form.get("email"), "password": request.form.get("password")}
#     authorization = "Bearer {access_token}".format(
#         access_token=current_app.config.get("API_KEY")
#     )
#     headers = {
#         "Content-Type": "application/json",
#         "Authorization": authorization,
#     }
#     response = requests.post(
#         f"{current_app.config.get('API_BASE_URL')}/api/v1/auth/admin/login",
#         headers=headers,
#         data=json.dumps(data),
#     )
#     if response.json()["status"] == "fail":
#         return render_template(
#             "login.html", error=error_map[f"{response.json()['ErrorCode']}"]
#         )
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
# @auth_bp.route("/logout")
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

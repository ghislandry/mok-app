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
from mok.models import RolesTypes, Portals
from mok.utils.error_codes import (
    PASSWORD_RESET_REQUIRED,
    EMPLOYEE_NOT_FOUND,
    WRONG_USERNAME_OR_PASSWORD,
    USER_NOT_FOUND,
)

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
    try:
        api_base_url = current_app.config.get("API_BASE_URL")
        password = request.form.get("bo_password")
        corporate_id = request.form.get("corporate_id")
        data = {
            "corporate_id": request.form.get("corporate_id").strip(),
            "password": request.form.get("bo_password").strip(),
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
                return redirect(url_for("auth_bo_bp.bo_login"))
        # Store the session token and employee number
        access_token = response.json()["access_token"]
        session["access_token"] = access_token
        # find out which user is connected and route accordingly
        url = f"{api_base_url}/api/v1/auth/corporate/user"
        response = logged_in_user(access_token=response.json()["access_token"], url=url)

        if response.status_code == HTTPStatus.UNAUTHORIZED:
            error = _("Your session has expired. Please log in again")
            flash(error, "error")
            return redirect(url_for("auth_bo_bp.bo_login"))
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
            flash(error, "error")
            return redirect(url_for("auth_bo_bp.bo_login"))
        logged_in_employee = {
            "employee_number": response.json()["employee_number"],
            "phone_number": response.json()["phone_number"],
            "last_name": None,
            "avatar": None,
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
            return redirect(url_for("auth_bo_bp.bo_login"))
        if (
            "ErrorCode" in response.json()
            and response.json()["ErrorCode"] == EMPLOYEE_NOT_FOUND
        ):
            found = False
        if role in [RolesTypes.senioremployee.name, RolesTypes.employee.name]:
            if found is True:
                logged_in_employee.update({"last_name": response.json()["last_name"]})
                logged_in_employee.update({"avatar": response.json()["avatar"]})
            session["logged_in_employee"] = logged_in_employee
            return redirect(url_for("backoffice_bp.bo_assets"))
        else:
            flash(
                _(
                    "You are not authorized to access this portal! Contact your administrator"
                )
            )
            return redirect(url_for("backoffice_bp.bo_login"))
    except requests.exceptions.ConnectionError:
        return render_template("connection_error.html")


@auth_bo_bp.route("/bo/logout")
def bo_logout():
    try:
        try:
            access_token = session["access_token"]
        except KeyError:
            error = _("Your session has expired. Please log in again.")
            flash(error, "error")
            return redirect(url_for("auth_bo_bp.bo_login"))

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
    except requests.exceptions.ConnectionError:
        return render_template("connection_error.html")

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

from mok.models import Portals

main_bp = Blueprint("main_bp", __name__)


@main_bp.route("/")
def index():
    try:
        p_language = (
            _("French") if session["platform_language"] == "fr" else _("English")
        )
    except KeyError:
        p_language = _("English")
    portal = _("Admin Portal")
    session["portal"] = Portals.admin.name
    return render_template("login.html", p_language=p_language, portal=portal)


@main_bp.route("/dashboard")
def dashboard():
    try:
        access_token = session["access_token"]
    except KeyError:
        error = _("Your session has expired. Please log in again.")
        flash(error, "error")
        return redirect(url_for("auth_bp.login"))

    try:
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        authorization = "Bearer {access_token}".format(access_token=access_token)
        headers = {"Authorization": authorization}
        api_base_url = current_app.config.get("API_BASE_URL")
        response = requests.get(
            f"{api_base_url}/api/v1/auth/corporate/users?page={page}&per_page={per_page}",
            headers=headers,
        )
        if response.status_code == HTTPStatus.UNAUTHORIZED:
            error = _("Your session has expired. Please log in again")
            flash(error, "error")
            return redirect(url_for("auth_bp.login"))
        logged_in_employee = session["logged_in_employee"]
        return render_template(
            "dashboard.html",
            users=response.json(),
            logged_in_employee=logged_in_employee,
        )
    except requests.exceptions.ConnectionError:
        return render_template("connection_error.html")


@main_bp.route("/dashboard", methods=["post"])
def dashboard_post():
    try:
        access_token = session["access_token"]
        corporate_id = request.form.get("corporate_id")
        phone_number = request.form.get("phone_number")
        data = {
            "corporate_id": corporate_id if len(corporate_id) > 0 else None,
            "phone_number": phone_number if len(phone_number) > 0 else None,
        }
        authorization = "Bearer {access_token}".format(access_token=access_token)
        headers = {
            "Content-Type": "application/json",
            "Authorization": authorization,
        }
        response = requests.post(
            f"{current_app.config.get('API_BASE_URL')}/api/v1/auth/corporate/search",
            headers=headers,
            data=json.dumps(data),
        )
        if response.status_code == HTTPStatus.UNAUTHORIZED:
            error = _("Your session has expired. Please log in again")
            flash(error, "error")
            return redirect(url_for("auth_bp.login"))
        logged_in_employee = session["logged_in_employee"]
        return render_template(
            "dashboard.html",
            users=response.json(),
            logged_in_employee=logged_in_employee,
        )
    except requests.exceptions.ConnectionError:
        return render_template("connection_error.html")


@main_bp.route("/change_role/<corporate_id>", methods=["post"])
def change_role_post(corporate_id):
    try:
        access_token = session["access_token"]
        role = request.form.get("new_role")
        data = {"role": role}
        authorization = "Bearer {access_token}".format(access_token=access_token)
        headers = {
            "Content-Type": "application/json",
            "Authorization": authorization,
        }
        response = requests.put(
            f"{current_app.config.get('API_BASE_URL')}/api/v1/auth/corporate/{corporate_id}",
            headers=headers,
            data=json.dumps(data),
        )
        if response.status_code == HTTPStatus.UNAUTHORIZED:
            error = _("Your session has expired. Please log in again")
            flash(error, "error")
            return redirect(url_for("auth_bp.login"))
        flash(
            _(
                "Role of user %(corporate_id)s successfully changed to %(role)s!",
                corporate_id=corporate_id,
                role=role,
            ),
            "information",
        )
        return redirect(url_for("main_bp.dashboard"))
    except requests.exceptions.ConnectionError:
        return render_template("connection_error.html")


@main_bp.route("/language_en")
def language_en():
    session["platform_language"] = "en"
    return _select_url()


@main_bp.route("/language_fr")
def language_fr():
    session["platform_language"] = "fr"
    return _select_url()


def _select_url():
    try:
        portal = session["portal"]
        url = (
            "auth_bo_bp.bo_login"
            if portal == "bo"
            else ("auth_corp_bp.corp_login" if portal == "corp" else "auth_bp.login")
        )
        return redirect(url_for(url))
    except KeyError:
        return redirect(url_for("auth_bp.login"))

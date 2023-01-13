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
import base64


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
    api_base_url = current_app.config.get("API_BASE_URL")
    try:
        user = session.pop("employee_profile")
    except KeyError:
        response = requests.get(
            f"{api_base_url}/api/v1/employees/{logged_in_employee['employee_number']}",
            headers=headers,
        )
        if response.status_code == HTTPStatus.UNAUTHORIZED:
            error = _("Your session has expired. Please log in again")
            p_language, portal = get_platform_language()
            flash(error, "error")
            return render_template(
                "corporate_login.html",
                p_language=p_language,
                portal=portal,
                # error=error,
            )
        if (
            "error_code" in response.json()
            and response.json()["error_code"] == EMPLOYEE_NOT_FOUND
        ):
            # the user does not have a profile yet!
            return redirect(url_for("corporate_bp.corp_dashboard"))
        user = response.json()
    return render_template("corporate_profile.html", user=user)


@corporate_bp.route("/update_profile/<data_dict>", methods=["post"])
def update_profile_post(data_dict):
    try:
        try:
            access_token = session["access_token"]
        except KeyError:
            error = _("Your session has expired. Please log in again.")
            flash(error, "error")
            return redirect(url_for("auth_corp_bp.corp_login"))
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
            flash(error, "error")
            return redirect(url_for("auth_corp_bp.corp_login"))
        flash("Contact information successfully updated", "information")
        return redirect(url_for("corporate_bp.corp_profile"))
    except requests.exceptions.ConnectionError:
        return render_template("connection_error.html")


@corporate_bp.route("/upload_avatar/<corporate_id>", methods=["post"])
def upload_profile_avatar(corporate_id):
    try:
        access_token = session["access_token"]
    except KeyError:
        error = _("Your session has expired. Please log in again.")
        flash(error, "error")
        return redirect(url_for("auth_corp_bp.corp_login"))
    datafile = request.files["id_image"]
    if not datafile:
        return redirect(url_for("corporate_bp.corp_profile"))

    extension = "." in datafile.filename and datafile.filename.rsplit(".", 1)[1].lower()
    # data = datafile.content
    data = base64.b64encode(datafile.read())
    data = data.decode()
    data = {"avatar_image": "data:image/{};base64,{}".format(extension, data)}
    authorization = "Bearer {access_token}".format(access_token=access_token)
    headers = {
        "Content-Type": "application/json",
        "Authorization": authorization,
    }
    try:
        response = requests.put(
            f"{current_app.config.get('API_BASE_URL')}/api/v1/employees/{corporate_id}",
            headers=headers,
            data=json.dumps(data),
        )
        print(response.json())
        if response.status_code == HTTPStatus.UNAUTHORIZED:
            # return {"result": url_for("auth_corp_bp.corp_login", _external=True)}, 302
            return redirect(url_for("auth_corp_bp.corp_login"))
        elif response.status_code in [
            HTTPStatus.CONFLICT,
            HTTPStatus.INTERNAL_SERVER_ERROR,
            HTTPStatus.BAD_REQUEST,
        ]:
            flash(error_map[f"{response.json()['error_code']}"], "error")
            # return {"result": url_for("corporate_bp.corp_profile", _external=True)}, 302
            return redirect(url_for("corporate_bp.corp_profile"))
        # return {"result": url_for("corporate_bp.corp_profile", _external=True)}, 302
        flash("Avatar successfully updated")
        return redirect(url_for("corporate_bp.corp_profile"))
    except requests.exceptions.ConnectionError:
        return render_template("connection_error.html")


@corporate_bp.route("/corp/dashboard")
def corp_dashboard():
    try:
        try:
            access_token = session["access_token"]
        except KeyError:
            error = _("Your session has expired. Please log in again.")
            flash(error, "error")
            return redirect(url_for("auth_corp_bp.corp_login"))

        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        authorization = "Bearer {access_token}".format(access_token=access_token)
        headers = {"Authorization": authorization}
        api_base_url = current_app.config.get("API_BASE_URL")
        response = requests.get(
            f"{api_base_url}/api/v1/employees?page={page}&per_page={per_page}",
            headers=headers,
        )
        logged_in_employee = session["logged_in_employee"]
        if response.status_code == HTTPStatus.UNAUTHORIZED:
            error = _("Your session has expired. Please log in again")
            # Get the configuration for the platform
            flash(error, "error")
            p_language, portal = get_platform_language()
            return render_template(
                "corporate_login.html",
                p_language=p_language,
                portal=portal,  # , error=error
            )
        return render_template(
            "corporate_dashboard.html",
            users=response.json(),
            logged_in_employee=logged_in_employee,
        )
    except requests.exceptions.ConnectionError:
        return render_template("connection_error.html")


@corporate_bp.route("/corp/dashboard", methods=["post"])
def corp_dashboard_post():
    try:
        try:
            access_token = session["access_token"]
        except KeyError:
            error = _("Your session has expired. Please log in again.")
            flash(error, "error")
            return redirect(url_for("auth_corp_bp.corp_login"))
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
            flash(_("No user found"), "information")
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
            flash(error, "error")
            return render_template(
                "corporate_login.html",
                p_language=p_language,
                portal=portal,  # error=error
            )
        elif "error_code" in response.json():
            users = None
            flash(_("No user found"), "information")
        else:
            users = response.json()
        return render_template(
            "corporate_dashboard.html",
            users=users,
            logged_in_employee=logged_in_employee,
        )
    except requests.exceptions.ConnectionError:
        return render_template("connection_error.html")


@corporate_bp.route("/corp/edit_employee_details/<employee_number>", methods=["post"])
def corp_edit_employee_details(employee_number):
    try:
        access_token = session["access_token"]
        api_base_url = current_app.config.get("API_BASE_URL")
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
                error = error_map[f"{response.json()['error_code']}"]
            except KeyError:
                error = _("Input payload validation failed")
            flash(error, "error")
            return render_template("corporate_register_employee.html")
        flash(_("User details successfully updated!"), "information")
        return redirect(url_for("corporate_bp.corp_dashboard"))
    except requests.exceptions.ConnectionError:
        return render_template("connection_error.html")


@corporate_bp.route("/corp/register_employee")
def corp_register_employee():
    logged_in_employee = session["logged_in_employee"]
    return render_template(
        "corporate_register_employee.html", logged_in_employee=logged_in_employee
    )


@corporate_bp.route("/corp/register_employee", methods=["post"])
def corp_register_employee_post():
    try:
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
            flash(error, "error")
            return redirect(url_for("auth_corp_bp.corp_login", error=error))
        elif response.status_code in [
            HTTPStatus.CONFLICT,
            HTTPStatus.INTERNAL_SERVER_ERROR,
            HTTPStatus.BAD_REQUEST,
        ]:
            try:
                error = error_map[f"{response.json()['error_code']}"]
            except KeyError:
                error = _("Input payload validation failed")
            flash(error, "error")
            logged_in_employee = session["logged_in_employee"]
            return render_template(
                "corporate_register_employee.html",
                logged_in_employee=logged_in_employee,
            )
        flash(_("Employee successfully registered"), "information")
        return redirect(url_for("corporate_bp.corp_dashboard"))
    except requests.exceptions.ConnectionError:
        return render_template("connection_error.html")


@corporate_bp.route("/corp/manage_employee_status/<employee_number>", methods=["post"])
def corp_manage_employee_status(employee_number):
    try:
        access_token = session["access_token"]
        new_status = request.form.get("status")
        api_base_url = current_app.config.get("API_BASE_URL")
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
            flash(error, "error")
            return redirect(url_for("auth_corp_bp.corp_login"))
        elif response.status_code in [
            HTTPStatus.CONFLICT,
            HTTPStatus.INTERNAL_SERVER_ERROR,
            HTTPStatus.BAD_REQUEST,
        ]:
            try:
                error = error_map[f"{response.json()['error_code']}"]
            except KeyError:
                error = _("Input payload validation failed")
            flash(error, "error")
            return redirect(url_for("corporate_bp.corp_dashboard"))
        return redirect(url_for("corporate_bp.corp_dashboard"))
    except requests.exceptions.ConnectionError:
        return render_template("connection_error.html")


def _redirect_to_login():
    error = _("Your session has expired. Please log in again")
    p_language, portal = get_platform_language()
    return render_template(
        "corporate_login.html",
        p_language=p_language,
        portal=portal,
        error=error,
    )

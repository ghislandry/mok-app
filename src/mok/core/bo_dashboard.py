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
    jsonify,
)
from flask_babel import _
import requests
import json

# import copy
import ast

from mok.platform_config import get_platform_language
from mok.auth import error_map

# from mok.utils.error_codes import EMPLOYEE_NOT_FOUND

backoffice_bp = Blueprint("backoffice_bp", __name__)


@backoffice_bp.route("/bo/assets")
def bo_assets():
    try:
        access_token = session["access_token"]
    except KeyError:
        error = _("Your session has expired. Please log in again.")
        flash(error, "error")
        return redirect(url_for("auth_bo_bp.bo_login"))

    api_base_url = current_app.config.get("API_BASE_URL")
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
        # p_language, portal = get_platform_language()
        # return render_template(
        #    "bo_login.html", p_language=p_language, portal=portal,
        # )
        return redirect(url_for("auth_bo_bp.bo_login"))
    # store the fact that we are looking
    return render_template(
        "bo_assets.html",
        assets=response.json(),
        logged_in_employee=logged_in_employee,
    )


@backoffice_bp.route("/bo/customers")
def bo_customers():
    """
    handle redirect to
    :return:
    """
    try:
        access_token = session["access_token"]
    except KeyError:
        error = _("Your session has expired. Please log in again.")
        flash(error, "error")
        return redirect(url_for("auth_bo_bp.bo_login"))

    api_base_url = current_app.config.get("API_BASE_URL")
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
        return redirect(url_for("auth_bo_bp.bo_login"))
    # store the fact that we are looking
    return render_template(
        "bo_customers.html",
        users=response.json(),
        logged_in_employee=logged_in_employee,
    )


@backoffice_bp.route("/bo/customers_details/<contract_number>")
def bo_customers_details(contract_number):
    try:
        access_token = session["access_token"]
    except KeyError:
        error = _("Your session has expired. Please log in again.")
        flash(error, "error")
        return redirect(url_for("auth_bo_bp.bo_login"))

    api_base_url = current_app.config.get("API_BASE_URL")

    authorization = "Bearer {access_token}".format(access_token=access_token)
    headers = {"Authorization": authorization}
    response = requests.get(
        f"{api_base_url}/api/v1/customers/{contract_number}",
        headers=headers,
    )
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        error = _("Your session has expired. Please log in again")
        # Get the configuration for the platform
        flash(error, "error")
        return redirect(url_for("auth_bo_bp.bo_login"))
    session["result"] = response.json()
    return response.json()


@backoffice_bp.route("/bo/customers_fetch_images/<contract_number>/<params>")
def bo_customers_fetch_images(contract_number, params):
    try:
        access_token = session["access_token"]
    except KeyError:
        error = _("Your session has expired. Please log in again.")
        flash(error, "error")
        return redirect(url_for("auth_bo_bp.bo_login"))

    authorization = "Bearer {access_token}".format(access_token=access_token)
    headers = {"Authorization": authorization}
    api_base_url = current_app.config.get("API_BASE_URL")
    if params != "none":
        if params == "passport":
            # Get the temporary token
            response = requests.get(
                f"{api_base_url}/customers/{contract_number}/passport",
                headers=headers,
            )
            temporary_token = response.json()["temporary_token_id"]
            # Get the link to the image
            response = requests.get(
                f"{api_base_url}/customers/{contract_number}/kyc_document/{temporary_token}",
                headers=headers,
            )
            response_headers = response.headers["filename"]
            return jsonify({"result": response})
        elif params == "cni":
            images = []
            for item in ["id_card_pg1", "id_card_pg2"]:
                response = requests.get(
                    f"{api_base_url}/customers/{contract_number}/{item}",
                    headers=headers,
                )
                temporary_token = response.json()["temporary_token_id"]
                # Get the link to the image
                response = requests.get(
                    f"{api_base_url}/customers/{contract_number}/kyc_document/{temporary_token}",
                    headers=headers,
                )
                images.append(response.json())
            return jsonify({"result": images})


@backoffice_bp.route("/bo/register_customer")
def bo_register_customer():
    try:
        logged_in_employee = session["logged_in_employee"]
    except KeyError:
        error = _("Your session has expired. Please log in again.")
        flash(error, "error")
        return redirect(url_for("auth_bo_bp.bo_login"))
    return render_template(
        "bo_customer_register.html", logged_in_employee=logged_in_employee
    )


@backoffice_bp.route("/bo/register_customer", methods=["post"])
def bo_register_customer_post():
    try:
        access_token = session["access_token"]
    except KeyError:
        error = _("Your session has expired. Please log in again.")
        flash(error, "error")
        return redirect(url_for("auth_bo_bp.bo_login"))

    data = {
        "contract_number": request.form.get("contract_number"),
        "first_name": request.form.get("first_name"),
        "last_name": request.form.get("last_name"),
        "gender": request.form.get("gender"),
        "date_of_birth": request.form.get("date_of_birth"),
        "city": request.form.get("city"),
        "phone_number": request.form.get("phone_number"),
    }
    authorization = "Bearer {access_token}".format(access_token=access_token)
    headers = {
        "Content-Type": "application/json",
        "Authorization": authorization,
    }
    response = requests.post(
        f"{current_app.config.get('API_BASE_URL')}/api/v1/customers",
        headers=headers,
        data=json.dumps(data),
    )
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        error = _("Your session has expired. Please log in again.")
        flash(error, "error")
        return redirect(url_for("auth_bo_bp.bo_login"))
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
            "bo_customer_register.html",
            logged_in_employee=logged_in_employee,
        )
    flash(_("Customer successfully registered"), "information")
    return redirect(url_for("backoffice_bp.bo_customers"))


@backoffice_bp.route("/bo/edit_customer/<contract_number>", methods=["post"])
def bo_edit_customer_details(contract_number):
    try:
        access_token = session["access_token"]
    except KeyError:
        error = _("Your session has expired. Please log in again.")
        flash(error, "error")
        return redirect(url_for("auth_bo_bp.bo_login"))

    api_base_url = current_app.config.get("API_BASE_URL")
    data = {
        "last_name": request.form.get("last_name"),
        "phone_number": request.form.get("phone_number"),
        "first_name": request.form.get("first_name"),
        "date_of_birth": request.form.get("date_of_birth"),
        "gender": request.form.get("gender"),
        "city": request.form.get("city"),
    }
    authorization = "Bearer {access_token}".format(access_token=access_token)
    headers = {
        "Content-Type": "application/json",
        "Authorization": authorization,
    }
    response = requests.put(
        f"{api_base_url}/api/v1/customers/{contract_number}",
        headers=headers,
        data=json.dumps(data),
    )
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        error = _("Your session has expired. Please log in again.")
        flash(error, "error")
        return redirect(url_for("auth_bo_bp.bo_login"))
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
        return redirect(url_for("backoffice_bp.bo_customers"))
    flash(_("User details successfully updated!"), "information")
    return redirect(url_for("backoffice_bp.bo_customers"))


@backoffice_bp.route("/bo/readings")
def bo_readings():
    access_token = _get_access_token("auth_bo_bp.bo_login")
    api_base_url = current_app.config.get("API_BASE_URL")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    authorization = "Bearer {access_token}".format(access_token=access_token)
    headers = {"Authorization": authorization}
    response = requests.get(
        f"{api_base_url}/api/v1/readings?page={page}&per_page={per_page}",
        headers=headers,
    )
    logged_in_employee = session["logged_in_employee"]
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        error = _("Your session has expired. Please log in again")
        # Get the configuration for the platform
        flash(error, "error")
        p_language, portal = get_platform_language()
        return render_template(
            "bo_login.html",
            p_language=p_language,
            portal=portal,
        )
    print(response.json())
    # store the fact that we are looking
    return render_template(
        "bo_readings.html",
        readings=response.json(),
        logged_in_employee=logged_in_employee,
    )


def _get_access_token(login_url):
    """
    Returns the access token or redirect to the login page

    Args:
        login_url: str login url to redirect to.
        this url must be of the form auth_bo_bp.bo_login,
        where auth_bo_bp is the namespace blueprint, and bo_login
        the function that handles the login

    Returns:
         str: access token if successful
    """
    try:
        access_token = session["access_token"]
        return access_token
    except KeyError:
        error = _("Your session has expired. Please log in again.")
        flash(error, "error")
        return redirect(url_for(login_url))

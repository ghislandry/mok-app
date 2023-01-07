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
import base64

from mok.auth import error_map


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
        return redirect(url_for("auth_bo_bp.bo_login"))
    # store the fact that we are looking
    return render_template(
        "bo_assets.html",
        assets=response.json(),
        logged_in_employee=logged_in_employee,
    )


@backoffice_bp.route("/bo/assets", methods=["post"])
def bo_assets_post():
    try:
        access_token = session["access_token"]
    except KeyError:
        error = _("Your session has expired. Please log in again.")
        flash(error, "error")
        return redirect(url_for("auth_bo_bp.bo_login"))
    try:
        meter_number = request.form.get("meter_number")
        serial_number = request.form.get("serial_number")
        data = {
            "meter_number": meter_number if len(meter_number) > 0 else None,
            "serial_number": serial_number if len(serial_number) > 0 else None,
        }
        authorization = "Bearer {access_token}".format(access_token=access_token)
        headers = {
            "Content-Type": "application/json",
            "Authorization": authorization,
        }
        response = requests.post(
            f"{current_app.config.get('API_BASE_URL')}/api/v1/assets/search",
            headers=headers,
            data=json.dumps(data),
        )
        logged_in_employee = session["logged_in_employee"]
        if response.status_code == HTTPStatus.UNAUTHORIZED:
            error = _("Your session has expired. Please log in again")
            flash(error, "error")
            return redirect(url_for("auth_bo_bp.bo_login"))
        return render_template(
            "bo_assets.html",
            assets=response.json(),
            logged_in_employee=logged_in_employee,
        )
    except requests.exceptions.ConnectionError:
        return render_template("connection_error.html")


@backoffice_bp.route("/bo/register_asset")
def bo_register_asset():
    try:
        logged_in_employee = session["logged_in_employee"]
    except KeyError:
        error = _("Your session has expired. Please log in again.")
        flash(error, "error")
        return redirect(url_for("auth_bo_bp.bo_login"))
    return render_template(
        "bo_asset_register.html", logged_in_employee=logged_in_employee
    )


@backoffice_bp.route("/bo/register_asset", methods=["post"])
def bo_register_asset_post():
    try:
        access_token = session["access_token"]
    except KeyError:
        error = _("Your session has expired. Please log in again.")
        flash(error, "error")
        return redirect(url_for("auth_bo_bp.bo_login"))
    try:
        data = {
            "contract_number": request.form.get("contract_number"),
            "meter_number": request.form.get("meter_number"),
            "serial_number": request.form.get("serial_number"),
        }
        authorization = "Bearer {access_token}".format(access_token=access_token)
        headers = {"Authorization": authorization}

        if request.files["file"]:
            datafile = request.files["file"]
            response = requests.post(
                f"{current_app.config.get('API_BASE_URL')}/api/v1/assets",
                headers=headers,
                data=data,
                files={
                    "document": (f"{datafile.filename}", datafile, datafile.content_type)
                },
            )
        else:
            response = requests.post(
                f"{current_app.config.get('API_BASE_URL')}/api/v1/assets",
                headers=headers,
                data=data,
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
                "bo_asset_register.html",
                logged_in_employee=logged_in_employee,
            )
        flash(_("Meter successfully added"), "information")
        return redirect(url_for("backoffice_bp.bo_assets"))
    except requests.exceptions.ConnectionError:
        return render_template("connection_error.html")


@backoffice_bp.route("/bo/asset/<meter_number>", methods=["post"])
def bo_edit_asset(meter_number):
    try:
        access_token = session["access_token"]
    except KeyError:
        error = _("Your session has expired. Please log in again.")
        flash(error, "error")
        return redirect(url_for("auth_bo_bp.bo_login"))

    data = {
        "meter_number": meter_number,
        "serial_number": request.form.get("serial_number"),
        "contract_number": request.form.get("contract_number"),
    }
    try:
        authorization = "Bearer {access_token}".format(access_token=access_token)
        headers = {"Authorization": authorization}
        if request.files["file"]:
            datafile = request.files["file"]
            response = requests.put(
                f"{current_app.config.get('API_BASE_URL')}/api/v1/assets/{meter_number}",
                headers=headers,
                data=data,
                files={
                    "document": (f"{datafile.filename}", datafile, datafile.content_type)
                },
            )
        else:
            response = requests.put(
                f"{current_app.config.get('API_BASE_URL')}/api/v1/assets/{meter_number}",
                headers=headers,
                data=data,
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
                "bo_asset_register.html",
                logged_in_employee=logged_in_employee,
            )
        flash(_("Meter successfully Updated"), "information")
        return redirect(url_for("backoffice_bp.bo_assets"))
    except requests.exceptions.ConnectionError:
        return render_template("connection_error.html")


@backoffice_bp.route("/bo/customers")
def bo_customers():
    """
    handle redirect to
    :return:
    """
    try:
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
    except requests.exceptions.ConnectionError:
        return render_template("connection_error.html")


@backoffice_bp.route("/bo/customers", methods=["post"])
def bo_customers_post():
    try:
        access_token = session["access_token"]
    except KeyError:
        error = _("Your session has expired. Please log in again.")
        flash(error, "error")
        return redirect(url_for("auth_bo_bp.bo_login"))
    try:
        contract_number = request.form.get("contract_number")
        phone_number = request.form.get("phone_number")
        last_name = request.form.get("last_name")
        data = {
            "contract_number": contract_number if len(contract_number) > 0 else None,
            "phone_number": phone_number if len(phone_number) > 0 else None,
            "last_name": last_name if len(last_name) > 0 else None,
        }
        authorization = "Bearer {access_token}".format(access_token=access_token)
        headers = {
            "Content-Type": "application/json",
            "Authorization": authorization,
        }
        response = requests.post(
            f"{current_app.config.get('API_BASE_URL')}/api/v1/customers/search",
            headers=headers,
            data=json.dumps(data),
        )
        logged_in_employee = session["logged_in_employee"]
        if response.status_code == HTTPStatus.UNAUTHORIZED:
            error = _("Your session has expired. Please log in again")
            flash(error, "error")
            return redirect(url_for("auth_bo_bp.bo_login"))
        return render_template(
            "bo_customers.html",
            users=response.json(),
            logged_in_employee=logged_in_employee,
        )
    except requests.exceptions.ConnectionError:
        return render_template("connection_error.html")


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
    try:
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
    except requests.exceptions.ConnectionError:
        return render_template("connection_error.html")


@backoffice_bp.route("/bo/customers_fetch_images/<contract_number>/<params>")
def bo_customers_fetch_images(contract_number, params):
    try:
        access_token = session["access_token"]
    except KeyError:
        error = _("Your session has expired. Please log in again.")
        flash(error, "error")
        return redirect(url_for("auth_bo_bp.bo_login"))
    try:
        authorization = "Bearer {access_token}".format(access_token=access_token)
        headers = {"Authorization": authorization}
        api_base_url = current_app.config.get("API_BASE_URL")
        if params != "none":
            if params == "passport":
                # Get the temporary token
                response = requests.get(
                    f"{api_base_url}/api/v1/customers/{contract_number}/passport",
                    headers=headers,
                )
                if response.status_code == HTTPStatus.UNAUTHORIZED:
                    error = _("Your session has expired. Please log in again")
                    # Get the configuration for the platform
                    flash(error, "error")
                    return redirect(url_for("auth_bo_bp.bo_login"))
                temporary_token = response.json()["temporary_token_id"]
                # Get the link to the image
                response = requests.get(
                    f"{api_base_url}/api/v1/customers/"
                    f"{contract_number}/kyc_document/{temporary_token}",
                    headers=headers,
                )
                if response.status_code == HTTPStatus.UNAUTHORIZED:
                    error = _("Your session has expired. Please log in again")
                    # Get the configuration for the platform
                    flash(error, "error")
                    return redirect(url_for("auth_bo_bp.bo_login"))

                filename = response.headers["Content-Disposition"].split("filename=")[1]
                extension = "." in filename and filename.rsplit(".", 1)[1].lower()
                data = response.content
                data = base64.b64encode(data)
                data = data.decode()
                return {
                    "result": '<img src="data:image/{};base64,{}" width="100%" '
                    'height="auto" oncontextmenu="return false;"/>'.format(
                        extension, data
                    )
                }
            elif params == "cni":
                images = []
                for item in ["id_card_pg1", "id_card_pg2"]:
                    response = requests.get(
                        f"{api_base_url}/api/v1/customers/{contract_number}/{item}",
                        headers=headers,
                    )
                    temporary_token = response.json()["temporary_token_id"]
                    # Get the link to the image
                    response = requests.get(
                        f"{api_base_url}/api/v1/customers/{contract_number}"
                        f"/kyc_document/{temporary_token}",
                        headers=headers,
                    )
                    filename = response.headers["Content-Disposition"].split(
                        "filename="
                    )[1]
                    extension = "." in filename and filename.rsplit(".", 1)[1].lower()
                    data = response.content
                    data = base64.b64encode(data)
                    data = data.decode()
                    img_str = (
                        '<img src="data:image/{};base64,{}" width="100%" '
                        'height="auto" oncontextmenu="return false;"/>'.format(
                            extension, data
                        )
                    )
                    images.append(img_str)
                st = (
                    "<span style='color:darkolivegreen;font-weight:bold'> Page 1 </span>"
                    + images[0]
                    + "<br><span style='color:darkolivegreen;font-weight:bold'> "
                    "Page 2 </span>" + images[1]
                )
                return {"result": st}
    except requests.exceptions.ConnectionError:
        return render_template("connection_error.html")


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
    try:
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
    except requests.exceptions.ConnectionError:
        return render_template("connection_error.html")


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
    try:
        data.update({"kyc_status": request.form.get("kyc_status")})
    except KeyError:
        pass
    authorization = "Bearer {access_token}".format(access_token=access_token)
    headers = {
        "Content-Type": "application/json",
        "Authorization": authorization,
    }
    try:
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
    except requests.exceptions.ConnectionError:
        return render_template("connection_error.html")


@backoffice_bp.route("/bo/readings")
def bo_readings():
    try:
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
            f"{api_base_url}/api/v1/readings?page={page}&per_page={per_page}",
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
            "bo_readings.html",
            readings=response.json(),
            logged_in_employee=logged_in_employee,
        )
    except requests.exceptions.ConnectionError:
        return render_template("connection_error.html")


@backoffice_bp.route("/bo/readings", methods=["post"])
def bo_readings_post():
    try:
        access_token = session["access_token"]
    except KeyError:
        error = _("Your session has expired. Please log in again.")
        flash(error, "error")
        return redirect(url_for("auth_bo_bp.bo_login"))
    try:
        meter_number = request.form.get("meter_number")
        reading_ref = request.form.get("reading_reference")
        reading_verified = request.form.get("verification_status")
        data = {
            "meter_number": meter_number if len(meter_number) > 0 else None,
            "reading_ref": reading_ref if len(reading_ref) > 0 else None,
            "reading_verified": reading_verified
            if reading_verified != "CLEAR"
            else None,
        }
        authorization = "Bearer {access_token}".format(access_token=access_token)
        headers = {
            "Content-Type": "application/json",
            "Authorization": authorization,
        }
        response = requests.post(
            f"{current_app.config.get('API_BASE_URL')}/api/v1/readings/search",
            headers=headers,
            data=json.dumps(data),
        )
        logged_in_employee = session["logged_in_employee"]
        if response.status_code == HTTPStatus.UNAUTHORIZED:
            error = _("Your session has expired. Please log in again")
            flash(error, "error")
            return redirect(url_for("auth_bo_bp.bo_login"))
        return render_template(
            "bo_readings.html",
            readings=response.json(),
            logged_in_employee=logged_in_employee,
        )
    except requests.exceptions.ConnectionError:
        return render_template("connection_error.html")


@backoffice_bp.route("/bo/submit_reading")
def bo_submit_reading():
    try:
        try:
            logged_in_employee = session["logged_in_employee"]
        except KeyError:
            error = _("Your session has expired. Please log in again.")
            flash(error, "error")
            return redirect(url_for("auth_bo_bp.bo_login"))
        return render_template(
            "bo_reading_submit.html", logged_in_employee=logged_in_employee
        )
    except requests.exceptions.ConnectionError:
        return render_template("connection_error.html")


@backoffice_bp.route("/bo/submit_reading", methods=["post"])
def bo_submit_reading_post():
    try:
        access_token = session["access_token"]
    except KeyError:
        error = _("Your session has expired. Please log in again.")
        flash(error, "error")
        return redirect(url_for("auth_bo_bp.bo_login"))
    data = {
        "contract_number": request.form.get("contract_number"),
        "meter_number": request.form.get("meter_number"),
        "energy": request.form.get("energy"),
        "unit": request.form.get("unit"),
        "reading_date": request.form.get("reading_date"),
    }
    try:
        datafile = request.files["reading_photo"]

        authorization = "Bearer {access_token}".format(access_token=access_token)
        headers = {"Authorization": authorization}
        response = requests.post(
            f"{current_app.config.get('API_BASE_URL')}/api/v1/readings",
            headers=headers,
            data=data,
            files={
                "document": (f"{datafile.filename}", datafile, datafile.content_type)
            },
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
                "bo_reading_submit.html",
                logged_in_employee=logged_in_employee,
            )
        flash(_("Meter reading successfully submitted"), "information")
        return redirect(url_for("backoffice_bp.bo_readings"))
    except requests.exceptions.ConnectionError:
        return render_template("connection_error.html")


@backoffice_bp.route("/bo/reading_fetch_images/<reading_reference>/<meter_number>")
def bo_reading_fetch_image(reading_reference, meter_number):
    try:
        try:
            access_token = session["access_token"]
        except KeyError:
            error = _("Your session has expired. Please log in again.")
            flash(error, "error")
            return redirect(url_for("auth_bo_bp.bo_login"))

        authorization = "Bearer {access_token}".format(access_token=access_token)
        headers = {"Authorization": authorization}
        api_base_url = current_app.config.get("API_BASE_URL")

        # Get the temporary token
        response = requests.get(
            f"{api_base_url}/api/v1/readings/{meter_number}/{reading_reference}",
            headers=headers,
        )
        if response.status_code != HTTPStatus.OK:
            return {"result": "session expires"}, response.status_code

        filename = response.headers["Content-Disposition"].split("filename=")[1]
        extension = "." in filename and filename.rsplit(".", 1)[1].lower()
        data = response.content
        data = base64.b64encode(data)
        data = data.decode()
        return {
            "result": '<img src="data:image/{};base64,{}" width="100%" '
            'height="auto" oncontextmenu="return false;"/>'.format(extension, data)
        }
    except requests.exceptions.ConnectionError:
        return render_template("connection_error.html")


@backoffice_bp.route(
    "/bo/reading/update/<contract_number>/<reading_reference>", methods=["post"]
)
def bo_reading_update_reading(contract_number, reading_reference):
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
        api_base_url = current_app.config.get("API_BASE_URL")
        data = {
            "reading_verified": request.form.get("reading_verified"),
            "contract_number": contract_number,
        }
        # Get the corresponding meter details
        response = requests.put(
            f"{api_base_url}/api/v1/readings/{reading_reference}",
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
            redirect(url_for("backoffice_bp.bo_readings"))
        flash(_("Meter reading successfully updated"), "information")
        return redirect(url_for("backoffice_bp.bo_readings"))
    except requests.exceptions.ConnectionError:
        return render_template("connection_error.html")


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

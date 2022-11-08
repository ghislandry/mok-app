import requests
from flask_babel import _

error_map = {
    "2002": _("Too many login attempts"),
    "2009": _("Email not verified!"),
    "2003": _("Incorrect password or email!"),
    "2004": _("Account has been suspended!"),
    "2001": _("Password reset required!"),
    "2023": _("Password too weak!"),
    "2000": _("The server encountered an error while processing your request."),
    "2006": _("Incorrect password or email."),
    "2007": _("Check that the phone number is valid."),
    "2008": _("An employee with the provided employee number already exist!"),
    "2016": _("An employee with this number already exist"),
    "2019": _("Employee profile has not been created"),
}


def logged_in_user(access_token, url):
    authorization = "Bearer {access_token}".format(access_token=access_token)
    headers = {
        "Authorization": authorization,
        "Content-Type": "application/json"
    }
    return requests.get(url, headers=headers)

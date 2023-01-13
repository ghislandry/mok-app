from flask import session
from flask_babel import _
from mok.models import Portals


def get_platform_language(portal=Portals.corp.name):
    try:
        p_language = (
            _("French") if session["platform_language"] == "fr" else _("English")
        )
    except KeyError:
        p_language = _("English")
    session["portal"] = portal
    platform = (
        _("Employee Portal")
        if portal == Portals.corp.name
        else (_("Back Office") if portal == Portals.bo.name else _("Admin Portal"))
    )
    return p_language, platform

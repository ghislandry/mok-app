from flask import session
from flask_babel import _


def get_platform_language(portal="corp"):
    try:
        p_language = _("French") if session["platform_language"] == "fr" else _("English")
    except KeyError:
        p_language = _("English")
    session["portal"] = portal
    platform = (
        _("Employee Portal")
        if portal == "corp"
        else (
            _("Back Office")
            if portal == "bo"
            else _("Admin Portal")
        )
    )
    return p_language, platform

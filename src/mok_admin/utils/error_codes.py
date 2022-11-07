SQLAlCHEMYERROR = 2000  # HTTPStatus.INTERNAL_SERVER_ERROR
PASSWORD_RESET_REQUIRED = 2001  # HTTPStatus.UNAUTHORIZED
TOO_MANY_LOGIN_ATTEMPTS = 2002  # HTTPStatus.UNAUTHORIZED
WRONG_USERNAME_OR_PASSWORD = 2003  # HTTPStatus.UNAUTHORIZED
ACCOUNT_SUSPENDED = 2004  # HTTPStatus.UNAUTHORIZED
INVALID_VERIFICATION_CODE = 2005  # HTTPStatus.UNAUTHORIZED
USER_NOT_FOUND = 2006  # HTTPStatus.NO_FOUND
INVALID_INPUT_DATA = 2007  # HTTPStatus.BAD_REQUEST
USER_ALREADY_EXIST = 2008  # HTTPStatus.CONFLICT
EMAIL_NOT_VERIFIED = 2009  # HTTPStatus.FORBIDDEN
EMAIL_CONFIRMATION_LINK_EXPIRED = 2010  # HTTPStatus.GONE
ACCOUNT_ALREADY_VERIFIED = 1011  # HTTPStatus.CONFLICT
TOO_MANY_METER_READING_SUBMISSION = 2011  # HTTPStatus.TOO_MANY_REQUESTS
NOT_ENOUGH_PRIVILEGE = 2012  # HTTPStatus.FORBIDDEN
PROFILE_ALREADY_EXIST = 2013  # HTTPStatus.FORBIDDEN
FILE_TYPE_NOT_ALLOWED = 2014  # HTTPStatus.BAD_REQUEST
TEMPORARY_TOKEN_EXPIRED = 2015  # HTTPStatus.UNAUTHORIZED
EMPLOYEE_ALREADY_EXIST = 2016  # HTTPStatus.CONFLICT
EMPLOYEE_SELF_PROFILE_CREATION = 2017  # HTTPStatus.FORBIDDEN
EMPLOYEE_NOT_REGISTERED = 2018  # HTTPStatus.FORBIDDEN
EMPLOYEE_NOT_FOUND = 2019  # HTTPStatus.NOT_FOUND
EMPLOYEE_NOT_UPDATING_OWN_PROFILE = 2020  # HTTPStatus.FORBIDDEN
ASSET_NOT_FOUND = 2021  # HTTPStatus.NO_FOUND
ASSET_NOT_ALLOCATED = 2022  # HTTPStatus.NO_FOUND
PASSWORD_NOT_STRONG_ENOUGH = 2023

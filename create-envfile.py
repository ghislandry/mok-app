#!/usr/local/bin/python
import os

env_keys = list(dict(os.environ).keys())

out_file = ""

# Copied from: https://github.com/SpicyPizza/create-envfile/blob/main/src/create-envfile.py
# Make sure the env keys are sorted to have reproducible output
ENV_VARIABLES = [
    "FLASK_APP",
    "FLASK_ENV",
    "FLASK_RUN_PORT",
    "FLASK",
    "SECRET_KEY",
    "DOMAIN_NAME",
    "DOMAIN_NAME_1",
    "DOMAIN_NAME_2",
    "API_BASE_URL",
    "API_KEY",
]


for key in [x for x in sorted(env_keys) if x in ENV_VARIABLES]:
    value = os.getenv(key, "")
    # If the key is empty, throw an error.
    if value == "" and os.getenv("INPUT_FAIL_ON_EMPTY", "false") == "true":
        raise Exception(f"Empty env key found: {key}")

    out_file += "{}={}\n".format(key, value)

# get directory name in which we want to create .env file
directory = str(os.getenv("INPUT_DIRECTORY", ""))

# get file name in which we want to add variables
# .env is set by default
file_name = str(os.getenv("INPUT_FILE_NAME", ".env"))

path = str(os.getenv("GITHUB_WORKSPACE", "/github/workspace"))

# This should resolve https://github.com/SpicyPizza/create-envfile/issues/27
if path in ["", "None"]:
    path = "."

if directory == "":
    full_path = os.path.join(path, file_name)
elif directory.startswith("/"):
    # Throw an error saying that absolute paths are not allowed. This is because
    # we're in a Docker container, and an absolute path would lead us out of the
    # mounted directory.
    raise Exception("Absolute paths are not allowed. Please use a relative path.")
elif directory.startswith("./"):
    full_path = os.path.join(path, directory[2:], file_name)
# Any other case should just be a relative path
else:
    full_path = os.path.join(path, directory, file_name)

print("Creating file: {}".format(full_path))

with open(full_path, "w") as text_file:
    text_file.write(out_file)
FROM python:3.7-slim-buster

WORKDIR /app

# Copying the source folder and requirements file
COPY ./src /app/src
COPY ./migrations /app/migrations
COPY ./setup.py /app
COPY ./README.md /app
COPY ./wsgi.py /app
COPY ./templates /app/templates

# install the env
ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV --prompt elect

ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN pip install --upgrade pip setuptools wheel

RUN cd /app && pip install .

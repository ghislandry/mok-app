# Nginx Dockerfile
FROM nginx:1.19-alpine

# Install certbot for letsencrypt certificates
RUN apk --update --no-cache add \
      python3 \
      py3-pip && \
      pip3 install j2cli
RUN apk add --no-cache certbot

# Replace existing files by our own configs
RUN rm /etc/nginx/nginx.conf && rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/
COPY ./conf.d/flask_app.conf /etc/nginx/conf.d/

# We use a small hack with envsubst to pass variables to our Nginx config file.
# The variables in Nginx needs to be in this specific format: ${FOO}. That's why
# we create also a DOLLAR variable to add the "real" $ in our config flask_app.conf
# ex: $host needs to be set as ${DOLLAR}host
ARG DOMAIN_NAME
ARG DOMAIN_NAME_1
ARG DOMAIN_NAME_2
ARG FLASK
ARG EMAIL_ADDRESS
ARG FLASK_RUN_PORT

ENV DOMAIN_NAME=$DOMAIN_NAME
ENV DOMAIN_NAME_1=$DOMAIN_NAME_1
ENV DOMAIN_NAME_2=$DOMAIN_NAME_2
ENV FLASK=$FLASK
ENV FLASK_RUN_PORT=$FLASK_RUN_PORT
ENV EMAIL_ADDRESS=$EMAIL_ADDRESS
ENV DOLLAR='$'

# Substitute contents and write a new application.conf file, which is imported
# by nginx.conf
RUN envsubst \
      </etc/nginx/conf.d/flask_app.conf \
      >/etc/nginx/conf.d/application.conf \
  && rm /etc/nginx/conf.d/flask_app.conf

# Directory needed for LetEncrypt certificates renewal
RUN mkdir /var/lib/certbot

# App entrypoint and auto-renewal scripts
COPY ./bin/entrypoint.sh /entrypoint.sh
COPY ./bin/renew /etc/periodic/weekly/renew
RUN chmod +x /entrypoint.sh \
  && chmod +x /etc/periodic/weekly/renew


# Install certificates and launch
ENTRYPOINT ../entrypoint.sh $DOMAIN_NAME $DOMAIN_NAME_1 $DOMAIN_NAME_2 $EMAIL_ADDRESS
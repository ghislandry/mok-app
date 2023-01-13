#!/bin/sh

certbot certonly --standalone -d $1,$2,$3 --email $4 -n --agree-tos --expand
/usr/sbin/nginx -g "daemon off;"
/usr/sbin/crond -f -d 8 &
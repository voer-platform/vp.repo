#!/usr/bin/sh
set -e
source ../bin/activate
exec ./vpr/gunicorn.sh

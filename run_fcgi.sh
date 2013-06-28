#!/usr/bin/sh
cd ./vpr
python ./vpr/manage.py runfcgi host=127.0.0.1 port=8001

#!/bin/bash
 
NAME="VPR"
DJANGODIR=<EDIT_THIS>/vp.repo/vpr
SOCKFILE=<EDIT_THIS>/vp.repo/vpr/gunicorn.sock
USER=voer
GROUP=voer
NUM_WORKERS=4
DJANGO_SETTINGS_MODULE=vpr.settings.prod
DJANGO_WSGI_MODULE=vpr.wsgi
ADDRESS=127.0.0.1:8001
TIMEOUT=120

echo "Starting $NAME..."
  
# Activate the virtual environment
cd $DJANGODIR
source ../../bin/activate
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH
  
# Create the run directory if it doesn't exist
RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR
   
# Start your Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)
exec gunicorn ${DJANGO_WSGI_MODULE}:application \
    --name $NAME \
    --workers $NUM_WORKERS \
    --user=$USER --group=$GROUP \
    --log-level=warning \
    --timeout=$TIMEOUT \
    --bind=$ADDRESS
    #--bind=unix:$SOCKFILE


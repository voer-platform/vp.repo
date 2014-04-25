#! /usr/bin/sh

echo '
VOER REPOSITORY INSTALLATION'

command -v pip >/dev/null 2>&1 || { echo >&2 "ERROR: Installation requires 'pip' installed before proceeding."; exit 1; }

echo '
01: Install Python packages ...
'

pip install -r requirements.txt

echo '
02: Create MySQL database ...
'
python -c 'import MySQLdb' >/dev/null 2>&1 || { echo >&2 "ERROR: There is no MySQL-Python installed."; exit 1; }
./vpr/manage.py syncdb --noinput

echo '
VOER Repository installation completed.
'

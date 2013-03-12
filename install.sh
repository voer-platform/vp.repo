#! /usr/bin/sh

command -v pip >/dev/null 2>&1 || { echo >&2 "Installation requires 'pip' installed before proceeding."; exit 1; }

pip install -r requirements.txt

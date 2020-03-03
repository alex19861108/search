#!/usr/bin/env sh
HOST="0.0.0.0"
PORT="8000"
nohup venv/bin/uliweb runserver -h ${HOST} -p ${PORT} 1>log.stdout 2>&1 &

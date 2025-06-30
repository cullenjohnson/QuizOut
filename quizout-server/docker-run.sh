#!/usr/bin/env bash
flask --app app db upgrade
gunicorn -k gevent -w 1 -b 0.0.0.0:8000 'app:create_app()'
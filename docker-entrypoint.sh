#!/bin/sh

alembic upgrade head
python3 -m app
#python -m app

#gunicorn -w $(nproc) --bind 0.0.0.0:8000 apps.wsgi
FROM python:3.8-alpine3.12

WORKDIR /srv

# Update package index
RUN apk update

# Add base build dependencies
RUN apk add build-base python3-dev

# Add development tools
RUN apk add git curl openssh

# Add extra build dependencies
#
# Dependency graph:
# - psycopg2
#   - postgresql-dev
# - Pillow:
#   - jpeg-dev
#   - zlib-dev
RUN apk add jpeg-dev zlib-dev postgresql-dev

# Install application requirements
COPY requirements requirements
RUN pip install -U pip
RUN pip install -Ur requirements/production.txt

# Copy main application source files
COPY docker-entrypoint.sh docker-entrypoint.sh
COPY test.sh test.sh
COPY pytest.ini .
COPY scripts scripts
COPY manage.py .
COPY settings.py settings.py
COPY tests tests
COPY lib lib
COPY apps apps

# Setup main command
CMD ["./docker-entrypoint.sh"]

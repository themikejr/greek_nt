# Base image for building the application
FROM python:3.13-slim-bullseye AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /opt/greek-nt/src/

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --disable-pip-version-check --no-cache-dir --upgrade pip setuptools wheel poetry

# Copy Poetry files and install dependencies
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.in-project true && \
    poetry install --no-root --only main && \
    rm -rf /root/.cache

# Copy application source code
COPY greek_nt greek_nt
COPY theme theme
COPY manage.py .
COPY data data

# Production image
FROM python:3.13-slim-bullseye

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    DJANGO_SETTINGS_MODULE=greek_nt.settings \
    DJANGO_ALLOWED_HOSTS="localhost,127.0.0.1,0.0.0.0,[::1]"

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq-dev \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create a non-root user and group
RUN addgroup --system app && adduser --system --group app

# Set work directory
WORKDIR /opt/greek-nt/src/

# Copy virtual environment and application from builder stage
COPY --from=builder /opt/greek-nt/src /opt/greek-nt/src

# Set ownership of the application files to the non-root user
RUN chown -R app:app /opt/greek-nt

# Switch to the non-root user
USER app

# Create static files directory and collect static files
RUN mkdir -p /opt/greek-nt/src/staticfiles && \
    /opt/greek-nt/src/.venv/bin/python manage.py collectstatic --noinput

# Create a script to run migrations, load data, and start the server
RUN echo '#!/bin/bash\n\
/opt/greek-nt/src/.venv/bin/python manage.py migrate --noinput\n\
/opt/greek-nt/src/.venv/bin/python manage.py load_token_data --all\n\
/opt/greek-nt/src/.venv/bin/gunicorn --bind 0.0.0.0:8000 greek_nt.wsgi:application' > /opt/greek-nt/src/start.sh && \
chmod +x /opt/greek-nt/src/start.sh && \
chown app:app /opt/greek-nt/src/start.sh

# Expose the application port
EXPOSE 8000

# Run migrations and start the server
CMD ["/opt/greek-nt/src/start.sh"]

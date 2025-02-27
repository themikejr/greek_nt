# Running Locally

## Setup
- Install dependencies: `poetry install`
- Apply migrations: `poetry run python manage.py migrate`
- Load data: `poetry run python manage.py load_token_data --all`

## Development
- Start Django: `poetry run python manage.py runserver`
- Tailwind Listener: `poetry run python manage.py tailwind start`

# Deployment

- Build Tailwind: `python manage.py tailwind build`
- Fly.io: `fly deploy`

# Data Management

This project uses a data loading management command rather than data migrations to keep schema changes separate from data loading.

The data loading is idempotent (only loads data if needed) and is automatically run during deployment, so no manual steps are required after deployment.

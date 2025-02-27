# Running Locally

## Setup
- Install dependencies: `poetry install`
- Apply migrations: `poetry run python manage.py migrate`
- Load data: `poetry run python manage.py load_token_data --all`

## Development
- Start Django: `poetry run python manage.py runserver`
- Tailwind Listener: `poetry run python manage.py tailwind start`

# Deployment

## Automated Deployment
Run the deployment script which handles building, deploying, and database setup:
```
./deploy.sh
```

If you need to reset the database (e.g., after schema changes):
```
./deploy.sh --reset
```
This will delete the existing database and recreate it from scratch, applying all migrations and reloading all data.

## Manual Deployment Steps
1. Build Tailwind: `poetry run python manage.py tailwind build`
2. Deploy to Fly.io: `fly deploy`
3. Set up the database:
   ```
   fly ssh console
   cd /opt/greek-nt/src
   ./.venv/bin/python manage.py deploy_db
   exit
   ```

# Troubleshooting Deployment

If you encounter database issues after deployment:

1. Check the logs: `fly logs`
2. Try the reset option: `./deploy.sh --reset`
3. For manual troubleshooting, SSH into the container: `fly ssh console`
4. Run the database deployment command:
   ```
   cd /opt/greek-nt/src
   ./.venv/bin/python manage.py deploy_db
   ```
5. Check if migrations applied: 
   ```
   ./.venv/bin/python manage.py showmigrations
   ```
6. If all else fails, you can manually reset the database:
   ```
   rm /data/db.sqlite3
   cd /opt/greek-nt/src
   ./.venv/bin/python manage.py deploy_db
   ```

# Data Management

This project uses a data loading management command rather than data migrations to keep schema changes separate from data loading.

The data loading is idempotent (only loads data if needed) and should be run manually after deployment for the first time or when schema changes occur.

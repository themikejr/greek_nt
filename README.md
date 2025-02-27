# Running Locally

## Setup
- Install dependencies: `poetry install`
- Configure database (see Database Configuration below)
- Apply migrations: `poetry run python manage.py migrate`
- Load data: `poetry run python manage.py load_token_data --all`

## Database Configuration

The application supports both SQLite (development) and PostgreSQL via Supabase (production) databases.

### Database Configurations

The application supports three database configurations:

- **sqlite**: Local SQLite database (default for development)
- **remote**: Remote Supabase PostgreSQL (for testing with production database)
- **production**: Supabase PostgreSQL (automatically used in production)

### Setting Up Database Configuration

1. Copy the environment template if you haven't already:
   ```
   cp .env.example .env
   ```

2. To switch between database configurations, simply change the `DATABASE_CONFIG` value in your `.env` file:

   ```
   # For local SQLite database
   DATABASE_CONFIG=sqlite
   
   # For remote Supabase database
   DATABASE_CONFIG=remote
   
   # For production database (same as remote currently)
   DATABASE_CONFIG=production
   ```

3. Make sure your Supabase credentials are set in your `.env` file when using `remote` or `production` configurations:
   ```
   SUPABASE_DB_NAME=postgres
   SUPABASE_DB_USER=postgres
   SUPABASE_DB_PASSWORD=your-password
   SUPABASE_DB_HOST=your-project-ref.supabase.co
   SUPABASE_DB_PORT=5432
   ```

4. Apply migrations after changing database configuration:
   ```
   poetry run python manage.py migrate
   ```

## Development
- Start Django: `poetry run python manage.py runserver`
- Tailwind Listener: `poetry run python manage.py tailwind start`

# Deployment

## Setting Up Supabase in Production

1. Make sure your Supabase credentials are correctly set in your local `.env` file:
   ```
   SUPABASE_DB_NAME=postgres
   SUPABASE_DB_USER=postgres
   SUPABASE_DB_PASSWORD=your-password
   SUPABASE_DB_HOST=your-project-ref.supabase.co
   SUPABASE_DB_PORT=5432
   ```

2. Set your Supabase credentials as Fly.io secrets using the provided script:
   ```
   ./set_fly_secrets.sh
   ```
   This will read database credentials from your `.env` file and set them as secrets in Fly.io.

3. The `fly.toml` file is already configured to use the production database configuration:
   ```
   [env]
   ENVIRONMENT = "production"
   DATABASE_CONFIG = "production"
   ```

## Automated Deployment
Run the deployment script which handles building, deploying, and database setup:
```
./deploy.sh
```

If you need to reset the database (e.g., after schema changes):
```
./deploy.sh --reset
```
This will reset the PostgreSQL schema, applying all migrations and reloading all data.

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
2. Verify that your database secrets are set correctly: `fly secrets list`
3. Confirm that production is using the correct database configuration:
   ```
   fly ssh console
   cd /opt/greek-nt/src
   ./.venv/bin/python -c "import os; print(f'DATABASE_CONFIG: {os.getenv(\"DATABASE_CONFIG\")}')"
   ```
4. Try the reset option: `./deploy.sh --reset`
5. For manual troubleshooting, SSH into the container: `fly ssh console`
6. Run the database deployment command:
   ```
   cd /opt/greek-nt/src
   ./.venv/bin/python manage.py deploy_db
   ```
7. Check if migrations applied: 
   ```
   ./.venv/bin/python manage.py showmigrations
   ```
8. For PostgreSQL-specific issues, make sure the database exists and your user has proper permissions
9. If you want to manually reset the PostgreSQL schema:
   ```
   cd /opt/greek-nt/src
   RESET_DB=true ./.venv/bin/python manage.py deploy_db
   ```

# Data Management

This project uses a data loading management command rather than data migrations to keep schema changes separate from data loading.

The data loading is idempotent (only loads data if needed) and should be run manually after deployment for the first time or when schema changes occur.

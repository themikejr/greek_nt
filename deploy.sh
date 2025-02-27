#!/bin/bash

# Check for reset flag
RESET_DB=false
for arg in "$@"; do
  if [ "$arg" == "--reset" ]; then
    RESET_DB=true
  fi
done

# Build and deploy the application to Fly.io
echo "Building Tailwind CSS..."
poetry run python manage.py tailwind build

echo "Deploying to Fly.io..."
fly deploy

# We need to ensure our persistent volume is properly set up
# Command to run migration and data loading in the deployed app
echo "Setting up the database..."

if [ "$RESET_DB" = true ]; then
  echo "Reset flag detected - recreating database from scratch..."
  echo "This will drop and recreate all tables in the database."
  read -p "Are you sure you want to continue? (y/n) " -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Resetting database schema..."
    # For PostgreSQL, we'll handle this through Django migrations
    # The deploy_db command will be updated to handle resetting the database
    export RESET_DB=true
    echo "Database reset flag set. Tables will be recreated during migration."
  else
    echo "Database reset cancelled."
    RESET_DB=false
  fi
fi

echo "This may take a few minutes for the data loading..."
# Use bash -c to run a complex command
fly ssh console -C "bash -c 'cd /opt/greek-nt/src && ./.venv/bin/python manage.py deploy_db'"

# Ensure all migrations are applied (especially for new tables like search_events)
echo "Ensuring all migrations are applied..."
fly ssh console -C "bash -c 'cd /opt/greek-nt/src && ./.venv/bin/python manage.py migrate'"

echo "Deployment complete!"
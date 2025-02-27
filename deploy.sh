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
  echo "This will delete the existing database and recreate it."
  read -p "Are you sure you want to continue? (y/n) " -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Removing existing database..."
    # Remove the database file
    fly ssh console -C "bash -c 'rm -f /data/db.sqlite3'"
    echo "Database reset complete. Now setting up fresh database..."
  else
    echo "Database reset cancelled."
    RESET_DB=false
  fi
fi

echo "This may take a few minutes for the data loading..."
# Use bash -c to run a complex command
fly ssh console -C "bash -c 'cd /opt/greek-nt/src && ./.venv/bin/python manage.py deploy_db'"

echo "Deployment complete!"
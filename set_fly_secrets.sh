#!/bin/bash

# Script to set Fly.io secrets from .env file
# Usage: ./set_fly_secrets.sh [path_to_env_file]

# Default to .env if no file specified
ENV_FILE=${1:-.env}

# Check if the env file exists
if [ ! -f "$ENV_FILE" ]; then
  echo "Error: Environment file $ENV_FILE not found."
  exit 1
fi

# Check if fly CLI is installed
if ! command -v fly &> /dev/null; then
  echo "Error: fly CLI is not installed. Please install it first."
  exit 1
fi

echo "Setting secrets from $ENV_FILE..."

# Create a temporary file for formatting secrets
TEMP_SECRETS=$(mktemp)

# Extract database variables and prepare them for fly secrets command
grep -E '^(SUPABASE_DB_)' "$ENV_FILE" | sed 's/^/export /' > "$TEMP_SECRETS"

# Add SECRET_KEY if it exists
grep -E '^SECRET_KEY=' "$ENV_FILE" | sed 's/^/export /' >> "$TEMP_SECRETS"

# Show what will be set (without values)
echo "The following secrets will be set:"
grep -E '^export ' "$TEMP_SECRETS" | cut -d '=' -f 1 | sed 's/export //'

# Confirm with user
read -p "Do you want to continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "Operation cancelled."
  rm "$TEMP_SECRETS"
  exit 0
fi

# Set secrets
fly secrets import < "$TEMP_SECRETS"

# Clean up
rm "$TEMP_SECRETS"

echo "Secrets have been set successfully!"
echo "You can verify them with: fly secrets list"
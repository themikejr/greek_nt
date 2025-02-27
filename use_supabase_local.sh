#!/bin/bash

# Script to set up local development to use Supabase PostgreSQL
# Usage: ./use_supabase_local.sh [on|off]

MODE=${1:-on}

ENV_FILE=".env"

# Check if the env file exists
if [ ! -f "$ENV_FILE" ]; then
  echo "Error: Environment file $ENV_FILE not found."
  exit 1
fi

if [ "$MODE" = "on" ]; then
  echo "Setting local development to use Supabase PostgreSQL..."
  
  # Check if DATABASE_TYPE already exists in .env and update it
  if grep -q "^DATABASE_TYPE=" "$ENV_FILE"; then
    sed -i '' "s/^DATABASE_TYPE=.*/DATABASE_TYPE=postgres/" "$ENV_FILE"
  else
    echo "DATABASE_TYPE=postgres" >> "$ENV_FILE"
  fi
  
  echo "Local environment set to use Supabase PostgreSQL."
  echo "Make sure your .env file has the correct Supabase credentials:"
  echo "- SUPABASE_DB_USER"
  echo "- SUPABASE_DB_PASSWORD"
  echo "- SUPABASE_DB_HOST"
  echo "- SUPABASE_DB_PORT"
  echo "- SUPABASE_DB_NAME"
  echo "Or a DATABASE_URL with the connection string."
elif [ "$MODE" = "off" ]; then
  echo "Setting local development to use SQLite..."
  
  # Check if DATABASE_TYPE already exists in .env and update it
  if grep -q "^DATABASE_TYPE=" "$ENV_FILE"; then
    sed -i '' "s/^DATABASE_TYPE=.*/DATABASE_TYPE=sqlite/" "$ENV_FILE"
  else
    echo "DATABASE_TYPE=sqlite" >> "$ENV_FILE"
  fi
  
  echo "Local environment set to use SQLite."
else
  echo "Usage: ./use_supabase_local.sh [on|off]"
  echo "  on  - Use Supabase PostgreSQL for local development"
  echo "  off - Use SQLite for local development"
  exit 1
fi
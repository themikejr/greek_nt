#!/bin/bash

echo "Switching to SQLite for local development..."

# Update DATABASE_CONFIG in .env file
if grep -q "^DATABASE_CONFIG=" .env; then
  # If the line exists, replace it
  sed -i '' 's/^DATABASE_CONFIG=.*/DATABASE_CONFIG=sqlite/' .env
else
  # If the line doesn't exist, add it
  echo "DATABASE_CONFIG=sqlite" >> .env
fi

echo "Done! Your environment is now configured to use SQLite."
echo "Run 'poetry run python manage.py migrate' to apply migrations."
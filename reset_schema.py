#!/usr/bin/env python
import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

# Get connection details from environment
db_url = os.getenv("DATABASE_URL")

if not db_url:
    user = os.getenv("SUPABASE_DB_USER")
    password = os.getenv("SUPABASE_DB_PASSWORD")
    host = os.getenv("SUPABASE_DB_HOST")
    port = os.getenv("SUPABASE_DB_PORT")
    dbname = os.getenv("SUPABASE_DB_NAME")
    
    if not all([user, password, host, port, dbname]):
        print("Error: DATABASE_URL or individual credentials must be set")
        exit(1)
        
    db_url = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"

try:
    # Connect to the database with gssencmode=disable to avoid GSSAPI issues
    print("Connecting to database...")
    conn = psycopg2.connect(db_url, sslmode='require', gssencmode='disable')
    conn.autocommit = True  # We need autocommit for schema operations
    
    # Create a cursor
    cur = conn.cursor()
    
    print("About to reset the entire public schema. This will delete all tables and data.")
    confirmation = input("Are you sure you want to proceed? (yes/no): ")
    
    if confirmation.lower() != "yes":
        print("Operation cancelled.")
        exit(0)
    
    # Drop and recreate the public schema
    print("Dropping public schema...")
    cur.execute("DROP SCHEMA public CASCADE;")
    
    print("Creating fresh public schema...")
    cur.execute("CREATE SCHEMA public;")
    
    # Grant privileges
    print("Setting privileges...")
    cur.execute("GRANT ALL ON SCHEMA public TO postgres;")
    cur.execute("GRANT ALL ON SCHEMA public TO public;")
    
    # Close cursor and connection
    cur.close()
    conn.close()
    
    print("Schema reset complete. The public schema is now empty.")
    print("You can now run 'python manage.py migrate' to recreate all tables.")
    print("Then run 'python manage.py load_token_data --all' to load your data.")
    
except Exception as e:
    print(f"Error: {e}")
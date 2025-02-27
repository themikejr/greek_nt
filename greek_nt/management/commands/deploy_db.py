import os
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
from django.db import connection
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Special command for deployment to ensure proper DB setup in both SQLite and PostgreSQL environments'

    def handle(self, *args, **options):
        # Check what database engine we're using
        db_engine = settings.DATABASES['default']['ENGINE']
        is_sqlite = 'sqlite3' in db_engine
        is_postgres = 'postgresql' in db_engine
        
        self.stdout.write(f"Database engine: {db_engine}")
        
        # Check if we're in production
        is_production = settings.ENVIRONMENT == "production"
        self.stdout.write(f"Running in production: {is_production}")
        
        # Check if we need to reset the database
        reset_db = os.environ.get('RESET_DB', 'false').lower() == 'true'
        self.stdout.write(f"Reset database: {reset_db}")
        
        if is_sqlite and is_production:
            database_path = settings.DATABASES['default']['NAME']
            self.stdout.write(f"SQLite database path: {database_path}")
            
            db_dir = os.path.dirname(database_path)
            # Make sure the data directory exists
            if not os.path.exists(db_dir):
                self.stdout.write(f"Creating data directory: {db_dir}")
                try:
                    os.makedirs(db_dir, exist_ok=True)
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Failed to create directory: {e}"))
                    return
            
            # Check if DB file exists and has appropriate permissions
            db_exists = os.path.exists(database_path)
            self.stdout.write(f"Database file exists: {db_exists}")
            
            if db_exists:
                try:
                    # Check if we can write to it
                    with open(database_path, 'a') as f:
                        pass
                    self.stdout.write("Database file is writable")
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Database file is not writable: {e}"))
                    # Try to fix permissions
                    try:
                        os.chmod(database_path, 0o666)
                        self.stdout.write("Fixed database file permissions")
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Failed to fix permissions: {e}"))
                        return
        
        if is_postgres and reset_db:
            self.stdout.write("Resetting PostgreSQL database schema...")
            # Drop all tables in the public schema
            with connection.cursor() as cursor:
                try:
                    cursor.execute("DROP SCHEMA public CASCADE;")
                    cursor.execute("CREATE SCHEMA public;")
                    cursor.execute("GRANT ALL ON SCHEMA public TO postgres;")
                    cursor.execute("GRANT ALL ON SCHEMA public TO public;")
                    self.stdout.write(self.style.SUCCESS("Successfully reset PostgreSQL schema"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error resetting PostgreSQL schema: {e}"))
        
        # Run migrations with verbosity to see exactly what's happening
        self.stdout.write("Running migrations...")
        call_command('migrate', verbosity=2, interactive=False)
        
        # Check if we need to load token data (always load after reset, or if the table is empty)
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM token")
            count = cursor.fetchone()[0]
        
        if reset_db or count == 0:
            self.stdout.write("Loading token data...")
            call_command('load_token_data', all=True)
        else:
            self.stdout.write(f"Skipping token data load (found {count} existing records)")
        
        self.stdout.write(self.style.SUCCESS('Database deployment completed successfully'))
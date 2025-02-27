import os
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Special command for Fly.io deployment to ensure proper DB setup'

    def handle(self, *args, **options):
        database_path = settings.DATABASES['default']['NAME']
        
        self.stdout.write(f"Database path: {database_path}")
        
        # Check if we're in production
        is_production = settings.ENVIRONMENT == "production"
        self.stdout.write(f"Running in production: {is_production}")
        
        if is_production:
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
        
        # Run migrations with verbosity to see exactly what's happening
        self.stdout.write("Running migrations...")
        call_command('migrate', verbosity=2, interactive=False)
        
        # Load all token data
        self.stdout.write("Loading token data...")
        call_command('load_token_data', all=True)
        
        self.stdout.write(self.style.SUCCESS('Database deployment completed successfully'))
import re
import sqlite3
import os
import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "greek_nt.settings")

# Import Django settings
import django
django.setup()
from django.conf import settings

def clean_definition(text):
    """
    Clean SDBG definition text by making references more readable.
    
    Examples of patterns to clean:
    - {L:μαθητεύω<SDBG:μαθητεύω:000000>}[a] -> μαθητεύω
    - {D:36.31} -> (domain 36.31)
    - {N:001} -> (removed)
    """
    if not text:
        return text
    
    # Replace lexicon references with just the term
    # Handle both with and without [a] suffix
    text = re.sub(r'\{L:([^<]+)<SDBG:[^:]+:[^>]+>\}(?:\s*\[[a-z]\])?', r'\1', text)
    
    # Replace domain references with a cleaner format
    text = re.sub(r'\{D:([^}]+)\}', r'(domain \1)', text)
    
    # Remove note references as they don't have corresponding content
    text = re.sub(r'\{N:[^}]+\}', '', text)
    
    # Clean up extra whitespace
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    # Fix any cases where we might have ended up with double commas or periods
    text = re.sub(r',\s*,', ',', text)
    text = re.sub(r'\.\s*\.', '.', text)
    
    # Fix cases where we removed a reference at the start of the text
    if text.startswith(', '):
        text = text[2:]
    
    # Fix cases where we have empty parentheses
    text = re.sub(r'\(\s*\)', '', text)
    text = re.sub(r'\(\s*,\s*\)', '', text)
    
    return text

def update_database_definitions():
    """
    Updates the definitions in the database with cleaned versions.
    Uses the database configuration from environment variables.
    """
    # Get database type from Django settings
    db_config = settings.DATABASES['default']
    
    # Check if we're using PostgreSQL
    if 'postgresql' in db_config.get('ENGINE', ''):
        # For PostgreSQL, use the DATABASE_URL and connection parameters from Django settings
        import psycopg2
        
        # Get connection info
        name = db_config.get('NAME', '')
        user = db_config.get('USER', '')
        password = db_config.get('PASSWORD', '')
        host = db_config.get('HOST', '')
        port = db_config.get('PORT', '')
        
        # Get postgres options from settings
        postgres_options = {
            "sslmode": "require",
            "gssencmode": "disable",
            "options": "-c search_path=public -c pool_mode=transaction"
        }
        
        # Build the connection string
        dsn = f"dbname='{name}' user='{user}' password='{password}' host='{host}'"
        if port:
            dsn += f" port='{port}'"
        
        # Add the postgres options
        for key, value in postgres_options.items():
            dsn += f" {key}='{value}'"
            
        print(f"Connecting to PostgreSQL database: {name} on {host}")
        conn = psycopg2.connect(dsn)
    else:
        # For SQLite (default fallback)
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'db.sqlite3')
        print(f"Connecting to SQLite database at: {db_path}")
        conn = sqlite3.connect(db_path)
    
    cursor = conn.cursor()
    
    # Determine placeholder style based on database type
    is_postgres = 'postgresql' in db_config.get('ENGINE', '')
    placeholder = "%s" if is_postgres else "?"
    
    # Get count of tokens with definitions
    cursor.execute("SELECT COUNT(*) FROM token WHERE definition != ''")
    total_count = cursor.fetchone()[0]
    print(f"Found {total_count} tokens with definitions to process")
    
    # Process in batches to improve performance and memory usage
    batch_size = 1000
    processed_count = 0
    updated_count = 0
    
    # Process in batches
    while processed_count < total_count:
        # Fetch a batch of tokens
        print(f"Processing batch {processed_count//batch_size + 1} of {(total_count + batch_size - 1)//batch_size}...")
        
        if is_postgres:
            cursor.execute(
                "SELECT id, definition FROM token WHERE definition != '' ORDER BY id LIMIT %s OFFSET %s",
                (batch_size, processed_count)
            )
        else:
            cursor.execute(
                "SELECT id, definition FROM token WHERE definition != '' ORDER BY id LIMIT ? OFFSET ?",
                (batch_size, processed_count)
            )
            
        batch_tokens = cursor.fetchall()
        if not batch_tokens:
            break  # No more tokens to process
            
        # Process each definition in the batch
        batch_updates = []
        for token_id, definition in batch_tokens:
            cleaned_definition = clean_definition(definition)
            
            # Only update if the definition actually changed
            if cleaned_definition != definition:
                batch_updates.append((cleaned_definition, token_id))
        
        # Perform batch update if we have changes
        if batch_updates:
            # Create a new cursor for updates to avoid any potential issues
            update_cursor = conn.cursor()
            
            # Execute updates in a single batch
            for cleaned_definition, token_id in batch_updates:
                update_cursor.execute(
                    f"UPDATE token SET definition = {placeholder} WHERE id = {placeholder}",
                    (cleaned_definition, token_id)
                )
                
            updated_count += len(batch_updates)
            print(f"  Updated {len(batch_updates)} definitions in this batch")
            
            # Commit each batch
            conn.commit()
            
        # Update counters
        processed_count += len(batch_tokens)
        print(f"  Progress: {processed_count}/{total_count} tokens processed ({(processed_count/total_count)*100:.1f}%)")
        
        # Commit after each batch to avoid large transactions
        conn.commit()
    
    # Commit the changes
    conn.commit()
    conn.close()
    
    print(f"Completed cleaning. Updated {updated_count} definitions.")

if __name__ == "__main__":
    import sys
    
    # Check if any arguments are passed
    if len(sys.argv) > 1 and sys.argv[1] == "--update-db":
        print("Running database update...")
        update_database_definitions()
    else:
        # Example usage for testing the function
        print("Testing definition cleanup with examples:")
        
        # Test multiple examples to see how different definitions are handled
        examples = [
            "(derivative of {L:μαθητεύω<SDBG:μαθητεύω:000000>}[a] 'to follow, to be a disciple of,' {D:36.31}) a person who is a disciple or follower of someone",
            "the act of being a disciple or follower of someone {D:36.31}",
            "{L:λόγος<SDBG:λόγος:000000>}[a] 'speech, word' {D:33.98} a communication consisting of words",
            "a symbol consisting of letters of the alphabet which together represent a concept in a language {D:33.26}",
            "(derivative of {L:ὑποκρίνομαι<SDBG:ὑποκρίνομαι:000000>} 'to pretend,' {D:88.227}) one who pretends to be other than he really is"
        ]
        
        # Show examples of reference resolution
        for i, example in enumerate(examples, 1):
            cleaned = clean_definition(example)
            print(f"\nExample {i} Definition Cleanup:")
            print("Original:", example)
            print("Cleaned:", cleaned)
        
        print("\nTo update the database with cleaned definitions, run:")
        print("python data/sdbg_cleaner.py --update-db")
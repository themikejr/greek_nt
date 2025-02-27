import os
import csv
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from greek_nt.models import Token


class Command(BaseCommand):
    help = 'Loads token data from TSV files into the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--sblgnt', 
            action='store_true', 
            help='Load SBLGNT token data'
        )
        parser.add_argument(
            '--sdbg', 
            action='store_true', 
            help='Load SDBG definition data'
        )
        parser.add_argument(
            '--all', 
            action='store_true', 
            help='Load all data'
        )
        parser.add_argument(
            '--clear', 
            action='store_true', 
            help='Clear all existing data before loading'
        )
        parser.add_argument(
            '--limit', 
            type=int,
            help='Limit the number of records to process (for testing)'
        )
        
    def handle(self, *args, **options):
        data_dir = Path(__file__).resolve().parents[3] / 'data'
        
        # Clear data if requested
        if options['clear']:
            self.stdout.write('Clearing all token data...')
            Token.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('All token data has been cleared'))
        
        # Process loading requests
        if options['all'] or options['sblgnt']:
            self.load_sblgnt_data(data_dir / 'macula-greek-sblgnt.tsv', limit=options.get('limit'))
            
        if options['all'] or options['sdbg']:
            self.load_sdbg_data(data_dir / 'sdbg.tsv', limit=options.get('limit'))
            
        if not (options['all'] or options['sblgnt'] or options['sdbg']):
            self.stdout.write('No data specified to load. Use --sblgnt, --sdbg, or --all')
    
    def load_sblgnt_data(self, file_path, limit=None):
        """Load SBLGNT token data"""
        if not os.path.exists(file_path):
            raise CommandError(f'File not found: {file_path}')
            
        self.stdout.write(f'Loading SBLGNT token data from {file_path}')
        if limit:
            self.stdout.write(f'Limiting to {limit} records for testing')
        
        # Check if data is already loaded
        if Token.objects.exists():
            count = Token.objects.count()
            self.stdout.write(f'Found {count} tokens already in database')
            if count > 130000:  # Approximate expected token count
                self.stdout.write('SBLGNT data appears to be completely loaded. Skipping.')
                return
                
        # Load the data
        tokens_to_create = []
        fields_to_update = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            row_count = 0
            for row in reader:
                row_count += 1
                if limit and row_count > limit:
                    break
                # Create token object
                token = Token(
                    id=row['xml:id'],
                    ref=row['ref'],
                    role=row.get('role', ''),
                    class_field=row.get('class', ''),
                    type=row.get('type', ''),
                    english=row.get('english', ''),
                    mandarin=row.get('mandarin', ''),
                    gloss=row.get('gloss', ''),
                    text=row['text'],
                    after=row.get('after', ''),
                    lemma=row['lemma'],
                    normalized=row.get('normalized', ''),
                    strong=row.get('strong', ''),
                    morph=row.get('morph', ''),
                    person=row.get('person', ''),
                    number=row.get('number', ''),
                    gender=row.get('gender', ''),
                    case=row.get('case', ''),
                    tense=row.get('tense', ''),
                    voice=row.get('voice', ''),
                    mood=row.get('mood', ''),
                    degree=row.get('degree', ''),
                    domain=row.get('domain', ''),
                    ln=row.get('ln', ''),
                    frame=row.get('frame', ''),
                    subjref=row.get('subjref', ''),
                    referent=row.get('referent', ''),
                )
                
                tokens_to_create.append(token)
                
                if len(tokens_to_create) >= 1000:
                    with transaction.atomic():
                        Token.objects.bulk_create(tokens_to_create)
                    self.stdout.write(f'Created {len(tokens_to_create)} tokens')
                    tokens_to_create = []
                    
        # Create any remaining tokens
        if tokens_to_create:
            with transaction.atomic():
                Token.objects.bulk_create(tokens_to_create)
            self.stdout.write(f'Created {len(tokens_to_create)} tokens')
            
        self.stdout.write(self.style.SUCCESS('Successfully loaded SBLGNT token data'))
    
    def load_sdbg_data(self, file_path, limit=None):
        """Load SDBG definition data"""
        if not os.path.exists(file_path):
            raise CommandError(f'File not found: {file_path}')
            
        self.stdout.write(f'Loading SDBG definition data from {file_path}')
        if limit:
            self.stdout.write(f'Limiting to {limit} records for testing')
        
        # Check if definition data is already loaded
        if Token.objects.filter(definition__isnull=False, definition__gt='').exists():
            count = Token.objects.filter(definition__isnull=False, definition__gt='').count()
            self.stdout.write(f'Found {count} tokens with definitions already in database')
            if count > 100000:  # Approximate expected count
                self.stdout.write('SDBG definition data appears to be loaded. Skipping.')
                return
        
        # Dictionary to collect data by token_id for bulk update
        token_updates = {}
        
        # Read the TSV file
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter='\t')
            row_count = 0
            for row in reader:
                row_count += 1
                if limit and row_count > limit:
                    break
                token_id = row['token_id']
                sense_id = row['sense_id']
                
                # Extract semantic domain from sense_id (format: SDBG:lemma:number:DomainName)
                semantic_domain = sense_id.split(':')[-1] if ':' in sense_id else ''
                
                token_updates[token_id] = {
                    'sense_id': sense_id,
                    'semantic_domain': semantic_domain,
                    'contextual_glosses': row['glosses'],
                    'definition': row['definition']
                }
                
                if row_count % 10000 == 0:
                    self.stdout.write(f'Processed {row_count} rows')
        
        # Batch update tokens in database
        with transaction.atomic():
            # Process in batches to avoid overwhelming memory
            batch_size = 1000
            token_ids = list(token_updates.keys())
            total_batches = (len(token_ids) + batch_size - 1) // batch_size
            
            for i in range(0, len(token_ids), batch_size):
                batch_ids = token_ids[i:i+batch_size]
                tokens = list(Token.objects.filter(id__in=batch_ids))
                
                for token in tokens:
                    updates = token_updates.get(token.id, {})
                    token.sense_id = updates.get('sense_id', '')
                    token.semantic_domain = updates.get('semantic_domain', '')
                    token.contextual_glosses = updates.get('contextual_glosses', '')
                    token.definition = updates.get('definition', '')
                
                Token.objects.bulk_update(
                    tokens, 
                    ['sense_id', 'semantic_domain', 'contextual_glosses', 'definition']
                )
                
                self.stdout.write(f'Updated {len(tokens)} tokens with SDBG data (batch {i//batch_size + 1} of {total_batches})')
        
        self.stdout.write(self.style.SUCCESS('Successfully loaded SDBG definition data'))
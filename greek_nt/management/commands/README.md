# Greek NT Data Management Commands

This directory contains Django management commands for managing the Greek NT data.

## Data Loading

Data loading has been decoupled from migrations to make the system more maintainable. After running migrations to set up the database schema, use the `load_token_data` command to load data.

### Loading Data

```bash
# Load all data (both SBLGNT and SDBG)
python manage.py load_token_data --all

# OR load specific datasets
python manage.py load_token_data --sblgnt  # Load SBLGNT token data
python manage.py load_token_data --sdbg    # Load SDBG definition data
```

### Features

The data loading command is:

1. **Idempotent**: It checks if data is already loaded and avoids reloading if it's complete.
2. **Batch-oriented**: It processes data in batches to manage memory usage.
3. **Transactional**: It uses database transactions to ensure data consistency.
4. **Informative**: It provides progress updates during loading.

### Required Data Files

- `data/macula-greek-sblgnt.tsv`: Contains the core token data.
- `data/sdbg.tsv`: Contains definition data for tokens.

## Development Notes

If you need to make schema changes:

1. Modify the models.py file
2. Run `python manage.py makemigrations` to generate migration files
3. Run `python manage.py migrate` to apply migrations
4. Run `python manage.py load_token_data --all` to load/update data

This approach separates schema changes from data loading, making it more robust when the schema evolves.
# Greek NT Project Guidelines

## Commands

- Run server: `poetry run python manage.py runserver`
- Tailwind dev: `poetry run python manage.py tailwind start`
- Tailwind build: `poetry run python manage.py tailwind build`
- Django shell: `poetry run python manage.py shell`
- Run specific test: `poetry run python manage.py test greek_nt.tests.<test_file>`
- Format code: `poetry run black .`
- Deploy: `fly deploy`

## Code Style

- Use Black for formatting
- Imports order: stdlib, django, third-party, local
- Do not use typing tools for python
- Use class-based views when possible
- Document models with detailed field descriptions
- Cache expensive queries with Django's cache decorators
- Create DB indexes for frequently queried fields
- Use environment variables for configuration
- Handle errors with try/except and provide helpful messages
- Add docstrings to all functions and classes
- Prefer explicit over implicit

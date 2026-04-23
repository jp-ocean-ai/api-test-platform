# Backend

Django backend for the API Test Platform.

## Current Status

This backend is now initialized and runnable.

Included in the first backend version:

- Django project: `config`
- Core apps:
  - users
  - projects
  - environments
  - apis
  - testcases
  - executions
  - reports
  - core
- DRF CRUD APIs for:
  - projects
  - environments
  - apis
  - testcases
  - executions
  - reports
- Swagger / Redoc docs
- pytest + pytest-django scaffold

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

## API Entry

- `/api/projects/`
- `/api/environments/`
- `/api/apis/`
- `/api/testcases/`
- `/api/executions/`
- `/api/reports/`

## API Docs

- `/swagger/`
- `/redoc/`

## Test

```bash
pytest
```

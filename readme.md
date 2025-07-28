# Pingi Task

## SetUp venv:
- `source venv/bin/activate`

## Install modules:
- `pip install -r requirements.txt`

## SetUp Dev:
 Run Postgresql and Redis with docker compose
### RUN:
- `docker compose -f ./docker-compose.dev.yml up`
### Stop:
- `docker compose -f ./docker-compose.dev.yml down`

## pre-run:

#### Create env:
- `cp .env.example .env`

#### Create tables:
- `python manage.py migrate`

#### Run tests:
- `pytest .`

#### Test and run:
- `python manage.py runserver`

# Support Intelligence API

API for classifying and processing support tickets.

This project evolves a support ticket classifier from a simple
rule-based API into a backend application with persistence, testing, and
future AI integration.

Current implementation uses FastAPI and keyword-based classification
rules. The API returns `category`, `priority`, `summary`, and
`entities`.

## Project status

Current version: v0.2 (database persistence)

Implemented:

-   FastAPI API endpoints.
-   Pydantic request and response schemas.
-   Rule-based ticket classification.
-   PostgreSQL persistence using SQLAlchemy.
-   Ticket and prediction storage.
-   Classification history endpoint.
-   Automated tests with pytest.
-   GitHub Actions CI for the test suite.

## Architecture

Current flow:

    Client
      |
      v
    FastAPI
      |
      +--> Classifier service
      |
      +--> Persistence service
                |
                v
           SQLAlchemy
                |
                v
           PostgreSQL

## Technologies

-   FastAPI: API framework.
-   Pydantic: request and response schemas.
-   Uvicorn: ASGI server.
-   SQLAlchemy: database access layer.
-   PostgreSQL: persistence database.
-   pytest: automated testing.
-   FastAPI TestClient: API endpoint testing.
-   GitHub Actions: continuous integration.

## Project structure

    app/
    ├── database.py
    ├── main.py
    ├── schemas/
    │   └── ticket.py
    └── services/
        ├── classifier.py
        └── persistence.py

    tests/
    ├── test_api.py
    ├── test_classifier.py
    └── test_persistence.py

## How to run the project

### Create virtual environment

``` bash
python -m venv .venv
```

Activate it:

``` bash
source .venv/Scripts/activate
```

Install dependencies:

``` bash
python -m pip install -r requirements.txt
```

## Database configuration

The project uses PostgreSQL for persistence.

Configure:

-   `DB_USER`
-   `DB_PASSWORD`
-   `DB_HOST`
-   `DB_PORT`
-   `DB_NAME`

The initial database schema is currently managed through SQLAlchemy
metadata.

Database migrations with Alembic are planned as a future improvement.

## Run the API

``` bash
uvicorn app.main:app --reload
```

Interactive documentation:

    /docs

## API endpoints

### POST /classify

Classifies a support ticket.

Example request:

``` json
{
  "text": "The user got an error during login"
}
```

Example response:

``` json
{
  "category": "technical",
  "priority": 1,
  "summary": "The user got an error during login",
  "entities": [
    "error",
    "login"
  ]
}
```

### GET /history/{ticket_id}

Returns stored classification history for a ticket.

## Testing

Run:

``` bash
python -m pytest
```

Current coverage:

-   Category classification:
    -   technical
    -   billing
    -   general
-   Entity extraction.
-   Complete classifier behavior.
-   API responses.
-   Invalid requests.
-   Persistence flow:
    -   save classification;
    -   retrieve stored data from PostgreSQL.

The test suite runs automatically through GitHub Actions on push and
pull request.

Persistence integration tests currently require a PostgreSQL
environment. Adding a PostgreSQL service to GitHub Actions is planned as
a future improvement.

## Current limitations

-   Classification still relies on keyword-based rules.
-   Summary currently returns the original input text.
-   Entity extraction uses a fixed keyword list.
-   Advanced validation is not implemented yet.

## Future improvements

-   Replace rule-based classification with AI-based classification.
-   Add Alembic database migrations.
-   Add PostgreSQL service to CI for persistence integration tests.
-   Add Docker support.
-   Add LLM integration and evaluation.

# Support Intelligence API

API for classifying and processing support tickets using FastAPI,
PostgreSQL, and LLM-based classification.

The project demonstrates the evolution of a support ticket classifier
from a simple rule-based baseline into a backend application with
persistence, automated testing, prompt versioning, LLM integration,
and reproducible evaluation.

The API analyzes each support ticket in a single LLM request and returns
`category`, `priority`, `summary`, and `entities`.

## Project status

Current version: v0.3 (LLM classification and evaluation)

Implemented:

- FastAPI API endpoints.
- Pydantic request and response schemas.
- Rule-based classifier preserved as a baseline.
- OpenAI-based ticket classification.
- Structured ticket analysis in a single LLM request.
- Prompt versioning.
- PostgreSQL persistence using SQLAlchemy.
- Database migrations with Alembic.
- Ticket and prediction storage.
- Classification history endpoint.
- Automated tests with pytest.
- GitHub Actions CI for the test suite.
- Versioned evaluation dataset with 24 support tickets.
- Reproducible LLM evaluation script.

## Architecture

Current flow:

    Client
      |
      v
    FastAPI
      |
      v
    LLM Classifier
      |
      v
    OpenAI API
      |
      v
    Structured result
      |
      v
    Persistence service
      |
      v
    SQLAlchemy
      |
      v
    PostgreSQL

The original rule-based classifier is preserved as a baseline for
comparison and testing purposes.

## Technologies

- FastAPI: API framework.
- Pydantic: request and response schemas.
- Uvicorn: ASGI server.
- OpenAI API: LLM-based ticket analysis.
- SQLAlchemy: database access layer.
- PostgreSQL: persistence database.
- Alembic: database schema migrations.
- pytest: automated testing.
- FastAPI TestClient: API endpoint testing.
- GitHub Actions: continuous integration.

## Project structure

    app/
    ├── database.py
    ├── main.py
    ├── schemas/
    │   └── ticket.py
    └── services/
        ├── classifier.py
        ├── llm_classifier.py
        ├── openai_client.py
        └── persistence.py

    alembic/
    └── versions/

    data/
    └── eval_tickets.json

    scripts/
    └── evaluate_llm.py

    tests/
    ├── test_api.py
    ├── test_classifier.py
    └── test_persistence.py

## How to run the project

### Create virtual environment

```bash
python -m venv .venv
```

Activate it on Git Bash:

```bash
source .venv/Scripts/activate
```

Activate it on PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Environment configuration

Configure the OpenAI API key:

```text
OPENAI_API_KEY=your_api_key
```

## Database configuration

The project uses PostgreSQL for persistence.

Configure:

- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`
- `DB_NAME`

The database schema is defined with SQLAlchemy metadata and managed
through Alembic migrations.

Apply pending migrations with:

```bash
python -m alembic upgrade head
```

## Run the API

```bash
uvicorn app.main:app --reload
```

Interactive documentation:

    /docs

## API endpoints

### POST /classify

Classifies and analyzes a support ticket using the LLM.

Example request:

```json
{
  "text": "I was charged twice for my subscription and now I cannot access my account"
}
```

Example response:

```json
{
  "category": "billing",
  "priority": 3,
  "summary": "The user was charged twice for their subscription and is unable to access their account.",
  "entities": [
    "charged twice",
    "subscription",
    "access account"
  ]
}
```

### GET /history/{ticket_id}

Returns stored classification history for a ticket.

Stored predictions include the prompt version used for classification.

## Testing

Run the automated test suite with:

```bash
python -m pytest -q
```

Current test suite:

- Rule-based baseline classifier behavior.
- Category classification.
- Entity extraction.
- API responses.
- Invalid requests.
- Persistence flow.
- Prompt version persistence.

The API tests mock the LLM classifier, so the normal test suite does not
call OpenAI and does not require a real API key.

The test suite runs automatically through GitHub Actions on push and
pull request.

Persistence integration tests currently require a PostgreSQL
environment.

## LLM evaluation

The project includes a versioned evaluation dataset:

    data/eval_tickets.json

Run the LLM evaluation with:

```bash
python -m scripts.evaluate_llm
```

Unlike the automated test suite, this script performs real OpenAI API
calls.

Current evaluation for prompt version 2:

```text
Dataset: 24 tickets
Category: 24 / 24 (100.0%)
Priority: 22 / 24 (91.7%)
```

The remaining priority mismatches are boundary cases where severity can
reasonably be interpreted differently. The prompt is not adjusted only
to force a perfect score on the current dataset.

## Prompt versioning

Predictions store the prompt version used during classification.

Current prompt version:

```text
2
```

This makes it possible to compare future prompt changes against the
evaluation dataset and understand which prompt generated a stored
prediction.

## Current limitations

- LLM output parsing currently expects valid JSON.
- Invalid or malformed LLM JSON does not yet have a dedicated fallback.
- Evaluation currently uses a small initial dataset of 24 tickets.
- LLM evaluation requires a real OpenAI API call and may have usage cost.
- Persistence integration tests require PostgreSQL.
- Docker support is not implemented yet.

## Future improvements

- Add stronger validation and fallback handling for malformed LLM output.
- Expand the evaluation dataset.
- Add more detailed evaluation metrics.
- Add Docker support.
- Continue comparing new prompt versions against the evaluation baseline.

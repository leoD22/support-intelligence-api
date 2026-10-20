# Support Intelligence API

A FastAPI service that classifies support tickets and stores their results in PostgreSQL. It also includes an assistant that can retrieve a ticket's classification history using OpenAI function calling.

The project started with a rule-based classifier. The current implementation adds LLM classification, structured responses, persistence, evaluation, usage metrics, and a controlled fallback to the original rules.

## What it does

- **Classify tickets:** produce `category`, `priority`, `summary`, and `entities` from a ticket description.
- **Keep a rule-based fallback:** use deterministic classification when selected OpenAI requests fail or return invalid structured results.
- **Store predictions:** persist classifications and their prompt version, model, token usage, latency, and estimated cost when available.
- **Read classification history:** retrieve stored predictions by ticket ID.
- **Answer questions about tickets:** let the model request `get_ticket_history(ticket_id)`, execute that lookup in Python, and return the result for a final answer.

### Request flow

```text
POST /classify
    -> OpenAI structured classification
       -> on selected errors: rule-based fallback
    -> PostgreSQL (ticket + prediction)
    -> classification response

POST /assistant/ask
    -> OpenAI Responses API
    -> optional get_ticket_history tool call
    -> PostgreSQL lookup
    -> tool result returned to OpenAI
    -> assistant response
```

The assistant currently supports one round of tool execution, not a general-purpose agent loop.

## Tech stack

Python 3.10, FastAPI, Pydantic, OpenAI Responses API, PostgreSQL, SQLAlchemy Core, Alembic, pytest, and Flake8. A GitHub Actions workflow runs the automated test suite.

## Project structure

```text
app/
  main.py
  database.py
  schemas/
    ticket.py
    assistant.py
  services/
    classifier.py
    llm_classifier.py
    openai_client.py
    persistence.py
    pricing.py
    ticket_tools.py
    ticket_assistant.py
alembic/versions/       # Database migrations
scripts/evaluate_llm.py
data/eval_tickets.json
tests/
```

## Running locally

The application needs Python 3.10, a running PostgreSQL instance, and an OpenAI API key for LLM-powered requests.

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it. On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Then install dependencies:

```bash
python -m pip install -r requirements.txt
```

Provide the required environment settings to the application process:

```text
OPENAI_API_KEY=<your API key>
DB_USER=<database user>
DB_PASSWORD=<database password>
DB_HOST=localhost
DB_PORT=5432
DB_NAME=<database name>
```

Create the database if necessary, then apply the migrations:

```bash
python -m alembic upgrade head
```

Start the development server:

```bash
uvicorn app.main:app --reload
```

Open [Swagger UI](http://127.0.0.1:8000/docs) to try the endpoints. Keep the server bound to localhost: the current API has no user authentication or ticket-level authorization.

## API

### `POST /classify`

Request:

```json
{
  "text": "I was charged twice for my subscription."
}
```

The response contains `category`, `priority`, `summary`, and `entities`. The exact values can differ depending on the model's output or whether the rule-based fallback was used. Successful requests are persisted.

### `GET /history/{ticket_id}`

Returns the stored classification history for a numeric ticket ID.

### `POST /assistant/ask`

Request:

```json
{
  "question": "Summarize the classification history for ticket 17."
}
```

Response structure:

```json
{
  "answer": "<answer based on the available history>"
}
```

The ticket ID above is only an example; its history is not part of the repository. If the model requests a history lookup, the server runs `get_ticket_history` and sends the resulting data back to OpenAI.

An empty or missing `question` returns HTTP 422. Selected OpenAI availability failures return HTTP 503.

## Tests and evaluation

Run the tests without making real LLM API calls:

```bash
python -m pytest -q
```

The last locally confirmed run passed **36 tests**. Tests cover classification, API validation and errors, database persistence, pricing, and tool-calling behavior. Some persistence tests need a local PostgreSQL instance.

Check style with:

```bash
python -m flake8 app tests
```

The command above only checks `app/` and `tests/`, not Alembic-generated migration scripts. Migration scripts should remain version-controlled.

To run the separate evaluation script:

```bash
python -m scripts.evaluate_llm
```

**This command makes real OpenAI API calls and may incur costs.** The initial evaluation dataset contains 24 labeled tickets. For prompt version 2, the recorded results were 24/24 category matches and 22/24 priority matches. These results describe that small dataset, not expected performance on unseen tickets.

## Limitations

- **Not ready for public deployment:** no authentication, ticket-level authorization, or request rate limiting.
- **One tool-calling round:** subsequent tool requests after the continuation are not handled.
- **Limited fallback:** only selected LLM failures fall back to the rule-based classifier; database and other application errors are separate.
- **Error handling:** invalid assistant tool arguments are not yet mapped to a dedicated HTTP error response.
- **Evaluation:** the labeled dataset is small and needs to grow before drawing broader conclusions.
- **Deployment:** Docker packaging, production monitoring, and deployment are not implemented yet.

Development work is tested locally and reviewed before being merged into the main branch.

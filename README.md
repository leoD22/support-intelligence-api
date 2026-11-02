# Support Intelligence API

A FastAPI service that classifies support tickets and stores their results in PostgreSQL. It also includes an assistant that can retrieve a ticket's classification history using OpenAI function calling.

The project started with a rule-based classifier. The current implementation adds LLM classification, structured responses, input validation, persistence, evaluation, usage metrics, a controlled fallback to the original rules, and API key authentication.

## What it does

- **Classify tickets:** produce `category`, `priority`, `summary`, and `entities` from a ticket description.
- **Validate requests:** reject missing, empty, or whitespace-only ticket descriptions and assistant questions with HTTP 422.
- **Keep a rule-based fallback:** use deterministic classification when selected OpenAI requests fail or return invalid structured results.
- **Store predictions:** persist classifications and their prompt version, model, token usage, latency, and estimated cost when available.
- **Read classification history:** retrieve stored predictions by ticket ID.
- **Answer questions about tickets:** let the model request `get_ticket_history(ticket_id)`, execute that lookup in Python, and return the result for a final answer.
- **Require an API key:** protect the three application endpoints with a shared `X-API-Key` header.
- **Check service availability:** expose public liveness (`/health`) and PostgreSQL readiness (`/ready`) endpoints.

### Request flow

```text
Application endpoint request
    -> X-API-Key verification
    -> request validation
    -> endpoint handler

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

Python 3.10, FastAPI, Pydantic, OpenAI Responses API, PostgreSQL, SQLAlchemy Core, Alembic, Docker, pytest, and Flake8. A GitHub Actions workflow runs the automated test suite.

## Project structure

```text
app/
  main.py
  security.py            # X-API-Key authentication dependency
  database.py
  schemas/
    ticket.py
    assistant.py
    llm.py
  services/
    classifier.py
    llm_classifier.py
    openai_client.py
    persistence.py
    pricing.py
    ticket_tools.py
    ticket_assistant.py
alembic/versions/        # Database migrations
scripts/evaluate_llm.py
data/eval_tickets.json
tests/
  test_api.py
  test_security.py
Dockerfile               # Docker image for the FastAPI application
.dockerignore            # Files excluded from the Docker build context
.env.example             # Example environment configuration (no real secrets)
```

## Running locally

The application needs Python 3.10, a running PostgreSQL instance, and an OpenAI API key for LLM-powered requests. Its application endpoints also require an API access key.

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

Create a local `.env` file from `.env.example` (in Git Bash or another Bash shell):

```bash
cp .env.example .env
```

On Windows PowerShell, use `Copy-Item .env.example .env` instead. Configure the values for your local environment:

```dotenv
OPENAI_API_KEY=<your OpenAI API key>
DB_USER=<database user>
DB_PASSWORD=<database password>
DB_HOST=localhost
DB_PORT=5432
DB_NAME=<database name>
API_ACCESS_KEY=<a long, random, private API access key>
```

The values in angle brackets are placeholders, not literal credentials. Keep `.env` out of Git; never commit real API keys or database passwords. Choose a unique, hard-to-guess `API_ACCESS_KEY`. The authentication setting is loaded when the Python module starts, so **restart the API after changing it**.

Create the database if necessary, then apply the migrations:

```bash
python -m alembic upgrade head
```

Start the development server:

```bash
uvicorn app.main:app --reload
```

Open [Swagger UI](http://127.0.0.1:8000/docs) to try the endpoints. Use **Authorize** to supply your API key; FastAPI documents it as an `X-API-Key` header.

Keep the development server bound to localhost. API key authentication does not provide user accounts, per-ticket access control, rate limiting, or transport encryption.

## Running with Docker

The Docker image packages the FastAPI application and its Python dependencies. **PostgreSQL runs separately** and must be available before starting the container. Docker Compose is not part of this setup.

### Prerequisites

- Docker Desktop (or a compatible Docker Engine).
- An accessible PostgreSQL instance with the required database and migrations applied.
- An `.env` file containing the variables listed in [Running locally](#running-locally), including `API_ACCESS_KEY` and `OPENAI_API_KEY`. Use `.env.example` as a reference.

Keep `.env` out of Git. The Docker build excludes it from the image; environment variables are supplied when starting the container.

The current image does not contain `alembic.ini` or `alembic/`. Create the database and run `python -m alembic upgrade head` from the local Python environment before using Docker with a new database.

### Build the image

From the repository root:

```bash
docker build -t support-intelligence-api:docker-test .
```

### Run the container

The following setup was previously verified on Windows with Docker Desktop and PostgreSQL running on the host. The updated API-key-protected image should be tested again after rebuilding. Run from the repository root in Bash or Git Bash:

```bash
docker run --rm \
  --name support-api-test \
  -p 127.0.0.1:8000:8000 \
  --env-file .env \
  -e DB_HOST=host.docker.internal \
  support-intelligence-api:docker-test
```

`--env-file .env` supplies the application settings, including `API_ACCESS_KEY`, at runtime. `DB_HOST=host.docker.internal` overrides the database hostname for this container so it can reach PostgreSQL on the Windows host. If PostgreSQL runs elsewhere, use its reachable hostname instead. The port mapping binds the API to the host's loopback interface rather than exposing it on all network interfaces.

Stop the container with Ctrl+C. The `--rm` option removes it after it stops. Do not publish this setup directly on the public Internet: ticket-level authorization, request rate limiting, and production deployment protections are not implemented.

### Verify the API

Open [Swagger UI](http://127.0.0.1:8000/docs), click **Authorize**, and enter the value configured in `API_ACCESS_KEY`. Try `GET /history/{ticket_id}` with an existing test ticket to check the PostgreSQL connection. Previous manual Docker verification of the history endpoint predates API key authentication; repeat it with the current version.

The automated suite is currently run from the local Python environment (see [Tests and evaluation](#tests-and-evaluation)); the Docker runtime image does not include the test suite.

## API

### Authentication

All three application endpoints require the following request header:

```http
X-API-Key: <your API_ACCESS_KEY value>
```

The server compares the supplied value with `API_ACCESS_KEY` from its environment.

| Condition | HTTP status |
| --- | --- |
| Valid API key | Request proceeds to endpoint processing |
| Missing or incorrect API key | `403 Forbidden` |
| Server-side `API_ACCESS_KEY` not configured | `503 Service Unavailable` |

The key is **shared by trusted API consumers**. This first version does not have user identities or tenant-specific permissions. In particular, possession of the key permits access to the available ticket history; it does **not** establish ownership of any individual ticket.

The `/health` and `/ready` operational endpoints do not require an API key.

An example classification request using Bash/Git Bash (replace the placeholder with your local key):

```bash
curl -X POST http://127.0.0.1:8000/classify \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_ACCESS_KEY" \
  -d '{"text":"I was charged twice for my subscription."}'
```

Never put real credentials in committed examples. Use HTTPS and appropriate additional protections before considering a network-accessible deployment.

### `POST /classify`

Request:

```json
{
  "text": "I was charged twice for my subscription."
}
```

The response contains `category`, `priority`, `summary`, and `entities`. The exact values can differ depending on the model's output or whether the rule-based fallback was used. Successful requests are persisted.

The `text` field is required. Leading and trailing whitespace is stripped; missing, empty, or whitespace-only values return HTTP 422 for authenticated requests.

### `GET /history/{ticket_id}`

Returns the stored classification history for a numeric ticket ID. Requires a valid API key. The ID identifies a ticket; there is currently no per-ticket ownership check.

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

The `question` field is required and trimmed of surrounding whitespace. Missing, empty, or whitespace-only questions return HTTP 422 for authenticated requests. Selected OpenAI availability failures return HTTP 503.

### `GET /health`

Liveness check. Returns HTTP 200 with `{"status": "ok"}` while the API can respond to requests. It does not check PostgreSQL or OpenAI availability. No API key is required.

### `GET /ready`

Readiness check. Runs a minimal `SELECT 1` query against PostgreSQL to verify that the database is reachable. No API key is required.

- **200 OK:** `{"status": "ready"}` when the database check succeeds.
- **503 Service Unavailable:** `{"status": "not ready"}` when SQLAlchemy reports a database error.

## Tests and evaluation

Run the tests without making real LLM API calls:

```bash
python -m pytest -q
```

The last locally confirmed run on `feature/health-readiness` passed **55 tests**. Tests cover classification, input validation, API key authentication, API error handling, health and readiness checks, database persistence, pricing, and tool-calling behavior. Some persistence tests need a local PostgreSQL instance.

The authentication tests include direct checks of `verify_api_key()` and HTTP checks for protected routes. A pytest fixture provides a valid API key for regular endpoint tests, while negative authentication tests intentionally send a missing or incorrect key.

Check style with:

```bash
python -m flake8 app tests
```

The command above only checks `app/` and `tests/`, not Alembic-generated migration scripts. Migration scripts should remain version-controlled.

A GitHub Actions workflow runs tests with a PostgreSQL service on pushes and pull requests.

To run the separate evaluation script:

```bash
python -m scripts.evaluate_llm
```

**This command makes real OpenAI API calls and may incur costs.** The initial evaluation dataset contains 24 labeled tickets. For prompt version 2, the recorded results were 24/24 category matches and 22/24 priority matches. These results describe that small dataset, not expected performance on unseen tickets.

## Limitations

- **Not ready for public deployment:** a single shared API key is implemented, but user identities, ticket-level authorization, rate limiting, and other production security controls are not.
- **One tool-calling round:** subsequent tool requests after the continuation are not handled.
- **Limited fallback:** only selected LLM failures fall back to the rule-based classifier; database and other application errors are separate.
- **Error handling:** invalid assistant tool arguments are not yet mapped to a dedicated HTTP error response.
- **Evaluation:** the labeled dataset is small and needs to grow before drawing broader conclusions.
- **Deployment:** Docker packaging is available for local use. Docker Compose, cloud deployment, and production monitoring are not implemented yet.

Development work is tested locally and reviewed before being merged into the main branch.

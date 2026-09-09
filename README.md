# Support Intelligence API

API for classifying and processing support tickets.

This API uses FastAPI and simple keyword-based rules to classify tickets. The response returns the fields `category`, `priority`, `summary`, and `entities`.

## Technologies

- FastAPI: building the API endpoints.
- Pydantic: definition and basic validation of input and output schemas.
- Uvicorn: ASGI server used to run the application.
- pytest: automated testing of classifier logic and API behavior.
- FastAPI TestClient: testing the `/classify` endpoint without running the server manually.

## How to run the project

### First-time setup

Create a virtual environment in the project folder:

```bash
python -m venv .venv
```

Activate the virtual environment:

```bash
source .venv/Scripts/activate
```

Install the required dependencies:

```bash
python -m pip install -r requirements.txt
```

### Run the API

With the virtual environment activated:

```bash
uvicorn app.main:app --reload
```

## Using the API

### Interactive documentation

With the server running, you can access `/docs`, where FastAPI displays the endpoint documentation and the input/output schemas.

### POST /classify

Receives a JSON body with the `text` field and returns a JSON response with the ticket classification.

#### Request body

```json
{
  "text": "The user got an error during login"
}
```

#### Response body

```json
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

## Testing

With the virtual environment activated, run the test suite with:

```bash
python -m pytest
```

The current test suite covers:

- `technical`, `billing`, and `general` category classification.
- Multiple and empty entity extraction results.
- Full `classify_ticket()` output.
- Successful `POST /classify` responses.
- Missing required `text` input.

## Limitations

- Classification currently relies on simple keyword-based rules. In future versions, the rule-based classifier will gradually be replaced by AI-based classification.
- `summary` currently returns the input text, not an actual summary.
- `entities` only detects a fixed list of words.
- Advanced input validation is left for a future version.

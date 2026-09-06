# Support Intelligence API

API for classifying and processing support tickets.

This API uses FastAPI and simple rules to classify tickets. The response returns the fields `category`, `priority`, `summary`, and `entities`.

## Technologies

- FastAPI: building the API endpoints.
- Pydantic: definition and basic validation of input and output schemas.
- Uvicorn: ASGI server used to run the application.

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

### POST/classify 

Receives a JSON body with the `text` field and returns a JSON response with the ticket classification.


#### Request body
```json
{
  "text": "Factura de compra de equipo para la oficina"
}
```
	
#### Response body
```json
{
  "category": "billing",
  "priority": 1,
  "summary": "Factura de compra de equipo para la oficina",
  "entities": [
    "factura"
  ]
}
```

## Limitations

- Classification currently relies on simple keyword-based rules. In future versions, the rule-based classifier will gradually be replaced by AI-based classification.

- `summary` currently returns the input text, not an actual summary.

- `entities` only detects a fixed list of words.

- Advanced input validation is left for a future version.

- The current keyword rules are primarily based on Spanish terms.
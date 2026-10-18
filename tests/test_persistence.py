from decimal import Decimal

from app.services.persistence import save_classification, get_classifications
from sqlalchemy import select
from app.database import engine, tickets, predictions

example_prompt_version = 1


def test_save_and_get():
    example_text = 'The user got an error during login'
    example_category = "technical"
    example_priority = 1
    example_summary = "The user got an error during login"
    example_entities = ["error", "login"]
    model_name = "test-model"
    input_tokens = 100
    output_tokens = 20
    total_tokens = 120
    latency_ms = 500
    cost_usd = Decimal("0.00012345")

    ticket_id = save_classification(
        text=example_text,
        category=example_category,
        priority=example_priority,
        summary=example_summary,
        entities=example_entities,
        prompt_version=example_prompt_version,
        model_name=model_name,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=total_tokens,
        latency_ms=latency_ms,
        cost_usd=cost_usd
        )

    assert ticket_id > 0

    classification_history = get_classifications(ticket_id)

    assert classification_history != []

    prediction = classification_history[0]

    assert prediction["text"] == example_text
    assert prediction["category"] == example_category
    assert prediction["priority"] == example_priority
    assert prediction["summary"] == example_summary
    assert prediction["entities"][0] == example_entities[0]
    assert prediction["entities"][1] == example_entities[1]
    assert prediction["prompt_version"] == example_prompt_version

    stmt = (
        select(
            predictions.c.model_name,
            predictions.c.input_tokens,
            predictions.c.output_tokens,
            predictions.c.total_tokens,
            predictions.c.latency_ms,
            predictions.c.cost_usd,
            predictions.c.created_at,
            tickets.c.created_at.label('tickets_created_at')
        )
        .join(predictions)
        .where(tickets.c.id == ticket_id)
    )

    with engine.connect() as connection:
        result = connection.execute(stmt).mappings().one()

    assert result['model_name'] == model_name
    assert result['input_tokens'] == input_tokens
    assert result['output_tokens'] == output_tokens
    assert result['total_tokens'] == total_tokens
    assert result['latency_ms'] == latency_ms
    assert result['cost_usd'] == cost_usd
    assert result['created_at'] is not None
    assert result['tickets_created_at'] is not None

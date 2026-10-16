from sqlalchemy import insert, select

from app.database import engine, tickets, predictions


def save_classification(
        text,
        category: str,
        priority: int,
        summary: str,
        entities: list[str],
        prompt_version: int,
        model_name: str | None = None,
        input_tokens: int | None = None,
        output_tokens: int | None = None,
        total_tokens: int | None = None,
        latency_ms: int | None = None
) -> int:
    with engine.begin() as connection:
        ticket_id = save_ticket(connection, text)
        save_prediction(
            connection=connection,
            ticket_id=ticket_id,
            category=category,
            priority=priority,
            summary=summary,
            entities=entities,
            prompt_version=prompt_version,
            model_name=model_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            latency_ms=latency_ms
        )

    return ticket_id


def save_ticket(connection, text: str) -> int:
    stmt = insert(tickets).values(text=text)
    result = connection.execute(stmt)
    ticket_id = result.inserted_primary_key[0]

    return ticket_id


def save_prediction(
        connection,
        ticket_id: int,
        category: str,
        priority: int,
        summary: str,
        entities: list[str],
        prompt_version: int,
        model_name: str | None = None,
        input_tokens: int | None = None,
        output_tokens: int | None = None,
        total_tokens: int | None = None,
        latency_ms: int | None = None
) -> None:
    stmt = (
        insert(predictions)
        .values(
            ticket_id=ticket_id,
            category=category,
            priority=priority,
            summary=summary,
            entities=entities,
            prompt_version=prompt_version,
            model_name=model_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            latency_ms=latency_ms
        )
    )

    connection.execute(stmt)


def get_classifications(ticket_id: int):
    stmt = (
        select(
            tickets.c.text,
            predictions.c.category,
            predictions.c.priority,
            predictions.c.summary,
            predictions.c.entities,
            predictions.c.prompt_version
        )
        .join(predictions)
        .where(tickets.c.id == ticket_id)
    )

    with engine.connect() as connection:
        result = connection.execute(stmt).mappings().all()

    return result

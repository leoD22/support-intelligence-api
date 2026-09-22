from sqlalchemy import insert

from app.database import engine, tickets, predictions


def save_classification(
        text,
        category,
        priority: int,
        summary: str,
        entities: list[str]
) -> int:
    with engine.begin() as connection:
        ticket_id = save_ticket(connection, text)
        save_prediction(
            connection,
            ticket_id,
            category,
            summary,
            priority,
            entities
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
        summary: str,
        priority: int,
        entities: list[str]) -> None:
    stmt = (
        insert(predictions)
        .values(
                ticket_id=ticket_id,
                category=category,
                priority=priority,
                summary=summary,
                entities=entities
            )
        )

    connection.execute(stmt)

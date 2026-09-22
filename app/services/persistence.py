from sqlalchemy import insert, select

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
            priority,
            summary,
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
        priority: int,
        summary: str,
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


def get_classifications(ticket_id: int):
    stmt = ( 
        select(
            tickets.c.text,
            predictions.c.category,
            predictions.c.priority,
            predictions.c.summary,
            predictions.c.entities
        )
        .join(predictions)
        .where(tickets.c.id == ticket_id)
    )

    with engine.connect() as connection:
        result = connection.execute(stmt).mappings().all()

    return result

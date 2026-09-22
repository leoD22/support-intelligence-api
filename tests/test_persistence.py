from app.services.persistence import save_classification, get_classifications


def test_save_and_get():
    example_text = 'The user got an error during login'
    example_category = "technical"
    example_priority = 1
    example_summary = "The user got an error during login"
    example_entities = ["error", "login"]

    ticket_id = save_classification(
        example_text,
        example_category,
        example_priority,
        example_summary,
        example_entities
        )

    assert ticket_id > 0

    predictions = get_classifications(ticket_id)

    assert predictions != []

    prediction = predictions[0]

    assert prediction["text"] == example_text
    assert prediction["category"] == example_category
    assert prediction["priority"] == example_priority
    assert prediction["summary"] == example_summary
    assert prediction["entities"][0] == example_entities[0]
    assert prediction["entities"][1] == example_entities[1]

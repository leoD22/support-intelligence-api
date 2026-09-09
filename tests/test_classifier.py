from app.services.classifier import (
    classify_category,
    extract_entities,
    classify_ticket
)


def test_classify_category_technical():
    example_text = 'The user got an error during login'
    assert classify_category(example_text) == 'technical'


def test_classify_category_billing():
    example_text = 'The client detect a extra charge'
    assert classify_category(example_text) == 'billing'


def test_classify_category_general():
    example_text = 'The website is confusing'
    assert classify_category(example_text) == 'general'


def test_extract_entities_multiple():
    example_text = 'The user got an error during login'
    assert extract_entities(example_text) == ['error', 'login']


def test_extract_entities_empty():
    example_text = 'The website is confusing'
    assert extract_entities(example_text) == []


def test_classify_ticket():
    example_text = 'The user got an error during login'
    expected_output = {
        "category": "technical",
        "priority": 1,
        "summary": "The user got an error during login",
        "entities": [
            "error",
            "login"
        ]
    }

    assert classify_ticket(example_text) == expected_output

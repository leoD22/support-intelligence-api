def classify_ticket(text: str):
    normalized_text = text.lower()

    category = classify_category(normalized_text)
    entities = extract_entities(normalized_text)

    return {
        "category": category,
        "priority": 1,
        "summary": text,
        "entities": entities
    }


def classify_category(normalized_text: str):
    if "charge" in normalized_text or "bill" in normalized_text:
        category = "billing"
    elif "error" in normalized_text or "login" in normalized_text:
        category = "technical"
    else:
        category = "general"

    return category


def extract_entities(normalized_text: str):
    possible_entities = ["charge", "bill", "error", "login"]
    entities = []
    for entity in possible_entities:
        if entity in normalized_text:
            entities.append(entity)

    return entities

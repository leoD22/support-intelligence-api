def classify_ticket(text: str):
    text_lower = text.lower()
    possible_entities = ["cobro", "factura","error","login"]
    entities = []

    for entity in possible_entities:
        if entity in text_lower:
            entities.append(entity)

    if "cobro" in text_lower or "factura" in text_lower:
        category = "billing"
        
    elif "error" in text_lower or "login" in text_lower:
        category = "technical"
    else:
        category = "general"
        


    return {"category": category, "priority": 1, "summary": text, "entities":entities}
    
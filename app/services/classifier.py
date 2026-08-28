def classify_ticket(text: str):
    text = text.lower()


    if "cobro" in text or "factura" in text:
        category = "billing"
    elif "error" in text or "login" in text:
        category = "technical"
    else:
        category = "general"

        
    return {"category": category, "priority": 1}
    
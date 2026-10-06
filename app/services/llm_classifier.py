import json
from app.services.openai_client import get_openai_client

PROMPT_VERSION = 2


def classify_ticket_with_llm(text: str):
    client = get_openai_client()
    system_str = """
    You are a support ticket analyzer.

    Analyze each support ticket and provide:

    - category
    - priority
    - summary
    - entities

    Category rules:

    - billing:
    issues related to payments, charges, invoices, refunds, pricing,
    subscriptions, or other financial matters.
    Questions about prices, plans, or subscription costs are also billing.

    - technical:
    issues related to errors, bugs, login problems, system failures,
    incorrect software behavior, or features that are not working as expected.

    - general:
    questions, feedback, requests, or issues that do not clearly belong
    to billing or technical.

    If a ticket mentions both a technical issue and a financial matter,
    prefer billing.

    Priority rules:

    - 1:
    low-impact questions, feedback, or non-urgent issues.
    - 2:
    problems affecting normal use without completely blocking the user.
    A delayed or pending refund is priority 2 unless it also causes blocked access
    or another critical issue.
    - 3:
    blocked access, an essential action being impossible, repeated or incorrect
    charges, or a serious system failure.

    Summary rules:

    - Write a short one-sentence summary of the ticket.

    Entities rules:

    - Return relevant terms or concepts explicitly mentioned in the ticket.
    - If there are no relevant entities, return an empty list.

    Return exactly the following JSON structure:

    {
        "category": "<general, billing, or technical>",
        "priority": <1, 2, or 3>,
        "summary": "<one sentence>",
        "entities": ["<entity>", "..."]
    }

    Do not include explanations, markdown, or any text outside the JSON.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_str},
            {"role": "user", "content": text}
        ],
        max_completion_tokens=150,
        temperature=0
    )

    result = json.loads(response.choices[0].message.content)

    return result

import time
from app.services.openai_client import get_openai_client
from app.schemas.ticket import TicketResponse
from app.schemas.llm import LLMClassificationResult

PROMPT_VERSION = 2


def classify_ticket_with_llm(text: str) -> LLMClassificationResult:
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
    A delayed or pending refund is priority 2 unless it also causes blocked
    access or another critical issue.
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
    start_time = time.perf_counter()

    response = client.responses.parse(
        model="gpt-4o-mini",
        instructions=system_str,
        input=text,
        max_output_tokens=150,
        temperature=0,
        text_format=TicketResponse
    )

    end_time = time.perf_counter()

    latency_ms = int((end_time - start_time) * 1000)

    result = LLMClassificationResult(
        classification=response.output_parsed,
        model_name=response.model,
        input_tokens=response.usage.input_tokens,
        output_tokens=response.usage.output_tokens,
        total_tokens=response.usage.total_tokens,
        latency_ms=latency_ms
    )

    return result

import json

from app.services.llm_classifier import classify_ticket_with_llm, PROMPT_VERSION


with open("data/eval_tickets.json", "r", encoding="utf-8") as file:
    tickets = json.load(file)

print(f'Prompt version: {PROMPT_VERSION}')

correct_category = 0
correct_priority = 0

for ticket in tickets:
    result = classify_ticket_with_llm(ticket["text"])

    if result["category"] == ticket["expected_category"]:
        correct_category += 1
    else:
        print(f'Text: {ticket["text"]}')
        print(f'Expected category: {ticket["expected_category"]}')
        print(f'Actual category: {result["category"]}')

    if result["priority"] == ticket["expected_priority"]:
        correct_priority += 1
    else:
        print(f'Text: {ticket["text"]}')
        print(f'Expected priority: {ticket["expected_priority"]}')
        print(f'Actual priority: {result["priority"]}')

category_accuracy = correct_category / len(tickets) * 100
priority_accuracy = correct_priority / len(tickets) * 100

print(
    f'Category: {correct_category} / {len(tickets)} '
    f'({category_accuracy:.1f}%)'
)

print(
    f'Priority: {correct_priority} / {len(tickets)} '
    f'({priority_accuracy:.1f}%)'
)

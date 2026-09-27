from app.services.openai_client import get_openai_client


def classify_category_with_llm(text: str) -> str:
    client = get_openai_client()
    system_str = '''
    - Choose exactly one category from: general, billing, technical
    - Answer only with the category name
    '''

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_str},
            {"role": "user", "content": "noticed a difference on the payment"},
            {"role": "assistant", "content": "billing"},
            {"role": "user", "content": text}
        ],
        max_completion_tokens=50,
        temperature=0
    )

    category = response.choices[0].message.content

    return category

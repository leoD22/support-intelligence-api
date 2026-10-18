from decimal import Decimal


MODEL_PRICING = {
    "gpt-4o-mini-2024-07-18": {
        "input": Decimal("0.15"),
        "output": Decimal("0.60")
    }
}


def calculate_cost(
        model_name: str,
        input_tokens: int,
        output_tokens: int
        ) -> Decimal | None:
    model = MODEL_PRICING.get(model_name)
    if model is not None:

        input_price = model["input"]
        output_price = model["output"]

        input_cost = Decimal(input_tokens) / Decimal(1_000_000) * input_price
        output_cost = Decimal(output_tokens) / Decimal(1_000_000) * output_price

        return input_cost + output_cost

    return None

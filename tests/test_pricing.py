from decimal import Decimal
from app.services.pricing import calculate_cost


def test_calculate_cost_with_input_tokens_only():
    assert calculate_cost(
        "gpt-4o-mini-2024-07-18",
        1_000_000,
        0
    ) == Decimal("0.15")


def test_calculate_cost_with_output_tokens_only():
    assert calculate_cost(
        "gpt-4o-mini-2024-07-18",
        0,
        1_000_000
    ) == Decimal("0.60")


def test_calculate_cost_with_input_and_output_tokens():
    assert calculate_cost(
        "gpt-4o-mini-2024-07-18",
        1_000_000,
        1_000_000
    ) == Decimal("0.75")


def test_calculate_cost_returns_none_for_unknown_model():
    assert calculate_cost("GPT-Test", 1_000_000, 1_000_000) is None

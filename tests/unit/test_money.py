from decimal import Decimal

from app.money import as_text, from_cents, round_cents


def test_cents_become_decimal_money() -> None:
    assert from_cents(12999) == Decimal("129.99")


def test_rounding_is_half_up_to_the_cent() -> None:
    assert round_cents(Decimal("0.005")) == Decimal("0.01")
    assert round_cents(Decimal("2.675")) == Decimal("2.68")


def test_wire_format_has_two_decimals() -> None:
    assert as_text(Decimal("5")) == "5.00"

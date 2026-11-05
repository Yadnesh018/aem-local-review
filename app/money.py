"""Money as Decimal, rounded half up to the cent (guardrail: never float)."""

from decimal import ROUND_HALF_UP, Decimal

CENT = Decimal("0.01")


def from_cents(cents: int) -> Decimal:
    return Decimal(cents) / 100


def round_cents(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def as_text(value: Decimal) -> str:
    """The legacy wire format: a string with exactly two decimals."""
    return str(round_cents(value))

"""Invoice pricing: line totals, discount tiers and VAT, as the legacy service computes them."""

from __future__ import annotations

from decimal import Decimal

from app.money import as_text, from_cents, round_cents

VAT_RATES = {"ES": 21, "PT": 23, "FR": 20}


class Refusal(Exception):
    """A request the legacy service refuses, with its status and body."""

    def __init__(self, status: int, body: dict) -> None:
        super().__init__(body.get("error"))
        self.status = status
        self.body = body


def discount_percent(subtotal: Decimal) -> int:
    """Tiers on the subtotal before VAT; the threshold itself qualifies."""
    if subtotal >= Decimal("5000"):
        return 10
    if subtotal >= Decimal("1000"):
        return 5
    return 0


def price(order: dict, lookup) -> dict:
    """Price an order. ``lookup(sku)`` returns the product row or None.

    Refusals are checked in the legacy order: empty order, country, then each
    line in turn (quantity, then product).
    """
    lines = order.get("lines") or []
    if not lines:
        raise Refusal(400, {"error": "empty_order"})
    country = str(order.get("country") or "").upper()
    if country not in VAT_RATES:
        raise Refusal(422, {"error": "unsupported_country", "country": country})

    priced = []
    for index, line in enumerate(lines, start=1):
        quantity = line.get("quantity")
        if not isinstance(quantity, int) or quantity <= 0:
            raise Refusal(400, {"error": "invalid_quantity", "line": index})
        product = lookup(line.get("sku"))
        if product is None:
            raise Refusal(404, {"error": "unknown_product", "sku": line.get("sku")})
        unit = from_cents(product["price_cents"])
        priced.append({"sku": product["sku"], "quantity": quantity, "unit": unit, "total": round_cents(unit * quantity)})

    rate = VAT_RATES[country]
    subtotal = sum((line["total"] for line in priced), Decimal("0"))
    percent = discount_percent(subtotal)
    discount = round_cents(subtotal * percent / 100)
    taxable = subtotal - discount
    # VAT once, on the discounted subtotal; never per line.
    vat = round_cents(taxable * rate / 100)
    return {
        "country": country,
        "lines": [{"sku": l["sku"], "quantity": l["quantity"], "unit_price": as_text(l["unit"]),
                   "line_total": as_text(l["total"])} for l in priced],
        "subtotal": as_text(subtotal),
        "discount_percent": percent,
        "discount": as_text(discount),
        "vat_rate": rate,
        "vat": as_text(vat),
        "total": as_text(taxable + vat),
    }

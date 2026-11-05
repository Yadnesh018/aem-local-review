import pytest

from app.pricing import Refusal, price

CATALOGUE = {"CHAIR-01": 12999, "LAMP-03": 2495, "MAT-04": 3333}


def lookup(sku):
    return {"sku": sku, "price_cents": CATALOGUE[sku]} if sku in CATALOGUE else None


def test_a_small_order_is_priced_with_vat() -> None:
    invoice = price({"country": "ES", "lines": [{"sku": "LAMP-03", "quantity": 2}]}, lookup)
    assert (invoice["subtotal"], invoice["discount"], invoice["vat"], invoice["total"]) == ("49.90", "0.00", "10.48", "60.38")


def test_line_totals_are_rounded_to_the_cent() -> None:
    invoice = price({"country": "PT", "lines": [{"sku": "MAT-04", "quantity": 3}]}, lookup)
    assert invoice["lines"][0]["line_total"] == "99.99"


@pytest.mark.parametrize(("order", "status", "error"), [
    ({"country": "ES", "lines": []}, 400, "empty_order"),
    ({"country": "ES", "lines": [{"sku": "LAMP-03", "quantity": 0}]}, 400, "invalid_quantity"),
    ({"country": "ES", "lines": [{"sku": "NOPE", "quantity": 1}]}, 404, "unknown_product"),
    ({"country": "DE", "lines": [{"sku": "LAMP-03", "quantity": 1}]}, 422, "unsupported_country"),
])
def test_refusals_carry_the_legacy_status(order, status, error) -> None:
    with pytest.raises(Refusal) as caught:
        price(order, lookup)
    assert (caught.value.status, caught.value.body["error"]) == (status, error)

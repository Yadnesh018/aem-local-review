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


def priced_at(cents: int, country: str = "ES") -> dict:
    return price({"country": country, "lines": [{"sku": "X", "quantity": 1}]},
                 lambda sku: {"sku": sku, "price_cents": cents})


@pytest.mark.parametrize(("cents", "percent"), [
    (99999, 0), (100000, 5), (100001, 5), (499999, 5), (500000, 10), (500001, 10),
])
def test_discount_tiers_include_the_threshold(cents, percent) -> None:
    assert priced_at(cents)["discount_percent"] == percent


def test_vat_is_charged_once_on_the_discounted_subtotal() -> None:
    # 1299.90 - 5% (65.00) = 1234.90; VAT 21% = 259.329 -> 259.33
    invoice = price({"country": "ES", "lines": [{"sku": "CHAIR-01", "quantity": 10}]}, lookup)
    assert (invoice["subtotal"], invoice["discount"], invoice["vat"], invoice["total"]) == \
        ("1299.90", "65.00", "259.33", "1494.23")


def test_vat_is_not_summed_per_line() -> None:
    # Per line: 20.00 + 5.00 = 25.00 (99.99*0.2=19.998, 24.95*0.2=4.99); once: 124.94*0.2 = 24.988 -> 24.99
    invoice = price({"country": "FR", "lines": [{"sku": "MAT-04", "quantity": 3}, {"sku": "LAMP-03", "quantity": 1}]}, lookup)
    assert invoice["vat"] == "24.99"


def test_the_discount_is_rounded_half_up() -> None:
    # 1032.33 * 5% = 51.6165 -> 51.62
    assert priced_at(103233)["discount"] == "51.62"


@pytest.mark.parametrize(("order", "status", "error"), [
    ({"country": "DE", "lines": []}, 400, "empty_order"),
    ({"country": "DE", "lines": [{"sku": "LAMP-03", "quantity": 0}]}, 422, "unsupported_country"),
    ({"country": "DE", "lines": [{"sku": "NOPE", "quantity": 1}]}, 422, "unsupported_country"),
    ({"country": "ES", "lines": [{"sku": "NOPE", "quantity": 1}, {"sku": "LAMP-03", "quantity": 0}]}, 404, "unknown_product"),
    ({"country": "ES", "lines": [{"sku": "NOPE", "quantity": 0}]}, 400, "invalid_quantity"),
])
def test_refusals_are_checked_in_the_legacy_order(order, status, error) -> None:
    with pytest.raises(Refusal) as caught:
        price(order, lookup)
    assert (caught.value.status, caught.value.body["error"]) == (status, error)

import pytest

from tests.parity.conftest import same

pytestmark = pytest.mark.parity


@pytest.mark.parametrize("order", [
    {"country": "ES", "lines": [{"sku": "LAMP-03", "quantity": 2}]},
    {"country": "PT", "lines": [{"sku": "MAT-04", "quantity": 3}, {"sku": "CHAIR-01", "quantity": 1}]},
    {"country": "fr", "lines": [{"sku": "CHAIR-01", "quantity": 2}]},
    # VAT once on the discounted subtotal, not per line
    {"country": "FR", "lines": [{"sku": "MAT-04", "quantity": 3}, {"sku": "LAMP-03", "quantity": 1}]},
    # just under the 1000.00 tier: 999.00
    {"country": "ES", "lines": [{"sku": "DESK-02", "quantity": 2}]},
    # 5% tier, discount rounded half up (1032.33 -> 51.62)
    {"country": "ES", "lines": [{"sku": "DESK-02", "quantity": 2}, {"sku": "MAT-04", "quantity": 1}]},
    {"country": "ES", "lines": [{"sku": "CHAIR-01", "quantity": 10}]},
    # exactly 5000.00: the threshold qualifies for 10%
    {"country": "PT", "lines": [{"sku": "CHAIR-01", "quantity": 1}, {"sku": "DESK-02", "quantity": 8},
                                {"sku": "LAMP-03", "quantity": 19}, {"sku": "MAT-04", "quantity": 12}]},
])
def test_invoice_totals_match_the_legacy(both, order) -> None:
    legacy, target = both
    left, right = legacy.post("/invoices", json=order), target.post("/invoices", json=order)
    assert right.status_code == left.status_code == 201
    a, b = left.json(), right.json()
    a.pop("number"), b.pop("number")
    assert b == a


@pytest.mark.parametrize("order", [
    {"country": "ES", "lines": []},
    {"country": "ES", "lines": [{"sku": "LAMP-03", "quantity": -1}]},
    {"country": "ES", "lines": [{"sku": "NOPE", "quantity": 1}]},
    {"country": "DE", "lines": [{"sku": "LAMP-03", "quantity": 1}]},
    # order of checks
    {"country": "DE", "lines": []},
    {"country": "DE", "lines": [{"sku": "NOPE", "quantity": 1}]},
    {"country": "DE", "lines": [{"sku": "LAMP-03", "quantity": 0}]},
    {"country": "ES", "lines": [{"sku": "NOPE", "quantity": 0}]},
    {"country": "ES", "lines": [{"sku": "NOPE", "quantity": 1}, {"sku": "LAMP-03", "quantity": 0}]},
])
def test_refusals_match_the_legacy(both, order) -> None:
    legacy, target = both
    same(legacy.post("/invoices", json=order), target.post("/invoices", json=order))


@pytest.mark.parametrize("content", [b"", b"not json"])
def test_raw_bodies_are_refused_like_the_legacy(both, content) -> None:
    legacy, target = both
    headers = {"Content-Type": "application/json"}
    same(legacy.post("/invoices", content=content, headers=headers),
         target.post("/invoices", content=content, headers=headers))


def test_a_created_invoice_reads_back_as_created(both) -> None:
    _, target = both
    created = target.post("/invoices", json={"country": "ES", "lines": [{"sku": "LAMP-03", "quantity": 1}]})
    assert created.status_code == 201
    fetched = target.get(f"/invoices/{created.json()['number']}")
    assert (fetched.status_code, fetched.json()) == (200, created.json())


def test_invoice_numbers_follow_creation_order(both) -> None:
    _, target = both
    order = {"country": "ES", "lines": [{"sku": "LAMP-03", "quantity": 1}]}
    first, second = (int(target.post("/invoices", json=order).json()["number"][4:]) for _ in range(2))
    assert second == first + 1


@pytest.mark.parametrize("number", ["INV-999999", "x' OR '1'='1"])
def test_an_unknown_invoice_is_404_like_the_legacy(both, number) -> None:
    legacy, target = both
    same(legacy.get(f"/invoices/{number}"), target.get(f"/invoices/{number}"))

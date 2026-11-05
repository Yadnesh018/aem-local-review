import pytest

from tests.parity.conftest import same

pytestmark = pytest.mark.parity


@pytest.mark.parametrize("order", [
    {"country": "ES", "lines": [{"sku": "LAMP-03", "quantity": 2}]},
    {"country": "PT", "lines": [{"sku": "MAT-04", "quantity": 3}, {"sku": "CHAIR-01", "quantity": 1}]},
    {"country": "fr", "lines": [{"sku": "CHAIR-01", "quantity": 2}]},
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
])
def test_refusals_match_the_legacy(both, order) -> None:
    legacy, target = both
    same(legacy.post("/invoices", json=order), target.post("/invoices", json=order))


def test_an_unknown_invoice_is_404_like_the_legacy(both) -> None:
    legacy, target = both
    same(legacy.get("/invoices/INV-999999"), target.get("/invoices/INV-999999"))

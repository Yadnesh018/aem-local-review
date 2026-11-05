import pytest

from tests.parity.conftest import same

pytestmark = pytest.mark.parity


def test_products_match_the_legacy_list(both) -> None:
    legacy, target = both
    same(legacy.get("/products"), target.get("/products"))

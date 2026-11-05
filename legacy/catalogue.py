"""The legacy product catalogue: prices in cents, as the old database held them."""

PRODUCTS = {
    "CHAIR-01": {"sku": "CHAIR-01", "name": "Office chair", "price_cents": 12999},
    "DESK-02": {"sku": "DESK-02", "name": "Standing desk", "price_cents": 49950},
    "LAMP-03": {"sku": "LAMP-03", "name": "Desk lamp", "price_cents": 2495},
    "MAT-04": {"sku": "MAT-04", "name": "Floor mat", "price_cents": 3333},
}

VAT_RATES = {"ES": 21, "PT": 23, "FR": 20}

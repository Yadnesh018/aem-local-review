# What the legacy invoicing service does

The port must reproduce this exactly. Where the legacy behaviour looks odd, it
is still the behaviour: clients depend on it.

## `POST /invoices`

Request: `{"country": "ES", "lines": [{"sku": "CHAIR-01", "quantity": 2}]}`

1. **Line totals.** Unit price is the catalogue price in cents / 100. Each line
   total is `unit × quantity`, rounded half up to the cent.
2. **Subtotal** is the sum of the line totals.
3. **Discount tier** on the subtotal: 5% at **1000.00 or more**, 10% at
   **5000.00 or more** (the threshold itself qualifies). The discount is
   rounded half up to the cent.
4. **VAT** is computed **once, on the discounted subtotal**, at the country's
   rate (ES 21, PT 23, FR 20), rounded half up to the cent. Never per line.
5. **Total** = discounted subtotal + VAT.
6. All money is returned as strings with exactly two decimals.
7. Success is **201**, with the invoice number `INV-000001`, `INV-000002`, …
   numbered in order of creation.

Refusals, checked in this order:

| Case | Status | Body |
|---|---|---|
| no lines | 400 | `{"error": "empty_order"}` |
| country not ES/PT/FR (case-insensitive) | 422 | `{"error": "unsupported_country", "country": "<upper-cased>"}` |
| quantity missing, not an integer, or ≤ 0 | 400 | `{"error": "invalid_quantity", "line": <1-based>}` |
| unknown SKU | 404 | `{"error": "unknown_product", "sku": "<sku>"}` |
| body is not JSON | 400 | `{"error": "malformed_body"}` |

Lines are checked in order; the first bad line is the one reported.

## `GET /invoices/{number}`

200 with the stored invoice, exactly as it was returned on creation, or 404
`{"error": "not_found"}`.

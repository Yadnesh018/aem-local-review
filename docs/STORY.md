# Story: Port invoice creation and retrieval

Paste this into AEM when you create the story.

**Title:** Port invoice creation and retrieval

**Description:** Port `POST /invoices` and `GET /invoices/{number}` from the
legacy invoicing service to the FastAPI service, matching the legacy
behaviour exactly (docs/legacy-behaviour.md). Invoices are stored in SQLite.

**Acceptance criteria**

1. `POST /invoices` returns 201 with line totals, subtotal, discount, VAT and
   total identical to the legacy service, to the cent, as two-decimal strings.
2. The discount tier applies at 1000.00 and 5000.00 inclusive, as in the legacy service.
3. VAT is computed once on the discounted subtotal, at the country's rate.
4. Every refusal returns the legacy status and body, in the legacy order of checks.
5. Invoice numbers are `INV-000001`, `INV-000002`, … in order of creation.
6. `GET /invoices/{number}` returns the stored invoice, or 404 `{"error": "not_found"}`.

**Subtasks**

- *Invoice pricing* — line totals, subtotal, discount tiers and VAT (criteria 1–3).
- *Refusals* — validation with the legacy status codes and bodies (criterion 4).
- *Invoice storage and retrieval* — SQLite table, numbering, `GET /invoices/{number}` (criteria 5–6).

**Guardrails to add to the project** (Project → Guardrails)

- *Money is Decimal* — money is never `float`; use `decimal.Decimal`, rounded half up to the cent.
- *Legacy refusals* — a refusal returns exactly the legacy status and body.
- *Parameterised SQL* — SQL is never built by string formatting or concatenation.

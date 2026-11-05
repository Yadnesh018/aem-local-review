# LRT-1: Port invoice creation and retrieval

Port POST /invoices and GET /invoices/{number} from the legacy invoicing service to the FastAPI service, matching the legacy behaviour exactly (docs/legacy-behaviour.md). Invoices are stored in SQLite.

> The approved brief for this story, committed when the branch was created. The pull request is reviewed against the acceptance criteria below, so change them in the tool rather than here — edits to this file are not read back.

## Acceptance criteria

- POST /invoices returns 201 with line totals, subtotal, discount, VAT and total identical to the legacy service, to the cent, as two-decimal strings.
- The discount tier applies at 1000.00 and 5000.00 inclusive, as in the legacy service.
- VAT is computed once on the discounted subtotal, at the country's rate.
- Every refusal returns the legacy status and body, in the legacy order of checks.
- Invoice numbers are INV-000001, INV-000002, ... in order of creation.
- GET /invoices/{number} returns the stored invoice, or 404 {"error": "not_found"}.

## Planned subtasks

- [other] Invoice pricing (LRT-2)
- [other] Refusals (LRT-3)
- [other] Invoice storage and retrieval (LRT-4)

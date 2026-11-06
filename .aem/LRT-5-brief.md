# LRT-5: Apply a discount to an invoice

As a billing clerk, I want to apply a discount when I create an invoice, so that agreed customer discounts appear on the invoice and its total.

- The clerk can give a discount when creating an invoice.
- The discount is shown on the invoice as its own line, and the total goes down by that amount.
- An invoice cannot end up with a negative total.
- The new service must match what the legacy service does for invoices without a discount.

Not decided yet: whether the discount is a percentage or a fixed amount, whether there is a maximum, how amounts are rounded, and whether tax is calculated before or after the discount.

> The approved brief for this story, committed when the branch was created. The pull request is reviewed against the acceptance criteria below, so change them in the tool rather than here — edits to this file are not read back.

## Functional requirements

- The billing clerk can apply a discount when creating an invoice.
- The discount is displayed on the invoice as a separate line item.
- The total amount on the invoice is reduced by the discount amount.
- The invoice total cannot be negative.

## Non-functional requirements

- The new discount application service must match the functionality of the legacy service for invoices without a discount.

## Acceptance criteria

- The discount is correctly applied and displayed on the invoice.
- The invoice total is accurately reduced by the discount amount.
- The invoice total does not go below zero.
- The discount application process is consistent with the legacy system for invoices without a discount.
- The discount is a percentage and does not exceed 20%.

## Business rules

- Discounts cannot result in a negative invoice total.

## Answers from the product owner

- Should the discount be a percentage or a fixed amount? → Percentage, maximum 20%

## Test-driven workflow

The acceptance criteria above were used to generate the tests below, committed alongside this brief. Build to make them pass — run them with the project's own test tools as you work, not only once at the end. Do not consider this story implemented until every one passes, or you have said here why one cannot be.

- `tests/api/LRT-5/test-1.txt`
- `tests/api/LRT-5/test-2.txt`
- `tests/api/LRT-5/test-3.txt`
- `tests/api/LRT-5/test-4.txt`
- `tests/api/LRT-5/test-5.txt`

## Planned subtasks

- [other] Design and implement DiscountDTO (LRT-6)
  Create the DiscountDTO class to represent discount data. Ensure it includes fields for percentage and validation rules.
- [other] Design and implement DiscountService (LRT-7)
  Create the DiscountService class to handle discount calculations. Ensure it adheres to the legacy system's behavior for invoices without a discount.
- [other] Update InvoiceDTO to include discount (LRT-8)
  Modify the InvoiceDTO class to include a field for the discount. Ensure it can handle the discount as a separate line item.
- [other] Update InvoiceService to apply discount (LRT-9)
  Modify the InvoiceService class to apply the discount to the invoice total. Ensure the total does not go below zero.
- [other] Update InvoiceRepository to save discount (LRT-10)
  Modify the InvoiceRepository class to save the discount information to the database. Ensure it updates the invoices table correctly.
- [other] Update InvoiceController to handle discount input (LRT-11)
  Modify the InvoiceController class to accept discount input when creating an invoice. Ensure it validates the discount and applies it correctly.
- [other] Write tests for DiscountService (LRT-12)
  Create unit tests for the DiscountService class. Ensure tests cover discount calculations, validation, and legacy system behavior.
- [other] Write tests for InvoiceService with discount (LRT-13)
  Create unit tests for the InvoiceService class with discount functionality. Ensure tests cover discount application, total calculation, and negative total prevention.
- [other] Write tests for InvoiceRepository with discount (LRT-14)
  Create unit tests for the InvoiceRepository class with discount functionality. Ensure tests cover database updates and integrity.
- [other] Write tests for InvoiceController with discount (LRT-15)
  Create integration tests for the InvoiceController class with discount functionality. Ensure tests cover input validation, service interaction, and response correctness.
- [other] Document discount application process (LRT-16)
  Create documentation for the discount application process, including user instructions, system architecture, and API endpoints. Ensure it aligns with the acceptance criteria.

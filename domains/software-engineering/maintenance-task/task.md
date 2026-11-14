# Task Brief

## Objective

Fix the calculation defect in the supplied Java 17 Maven project.

The current implementation applies the discount percentage to both the item subtotal and shipping. The intended business rule is that only the item subtotal is discounted; shipping remains payable in full.

## Expected output

- A minimal production-code fix.
- All acceptance tests passing.
- A short root-cause and verification note.

## Inputs

Copy `fixtures/java-discount-calculator/` to a writable directory.

## Acceptance conditions

For an item subtotal of 10,000 cents, shipping of 1,000 cents and a 10% discount:

- Discounted subtotal: 9,000 cents.
- Shipping: 1,000 cents.
- Expected total: 10,000 cents.

With no discount, the same inputs must total 11,000 cents.

## Constraints

- Keep the public method signature unchanged.
- Do not change or delete acceptance tests.
- Do not add unrelated features or refactor unrelated code.
- Use Java 17 and Maven.

## Non-goals

No new discount types, tax calculations, shipping promotions or validation-policy changes.

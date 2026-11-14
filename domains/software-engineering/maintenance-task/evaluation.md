# Evaluation Instructions

## 1. Prepare

1. Copy `fixtures/java-discount-calculator/` into a fresh writable working directory.
2. Record the model/version, host/version, workflow, Skills/tools, runtime, start time and budget.
3. Confirm JDK 17 and Maven are available.

## 2. Establish baseline

Run:

```bash
mvn test
```

The baseline is intentionally expected to fail because the implementation discounts shipping. Preserve the baseline output as evidence; do not alter the acceptance tests.

## 3. Assign the task

Give the executor `task.md` and the fixture. Do not reveal an implementation patch. Ask it to diagnose and fix the defect with the smallest appropriate change.

## 4. Verify

Run:

```bash
mvn clean test
```

Inspect the source diff and verify:

- Discount is applied only to subtotal.
- Shipping remains unchanged.
- No-discount behavior remains correct.
- The public API and acceptance tests remain unchanged.

## 5. Record

Create an Experiment Record and capture:

- Model, version, host and agent configuration.
- Skills/tools and versions.
- Baseline failure and final test output.
- Source diff and final artifact revision.
- Time to first correct diagnosis and end-to-end time.
- Retries, human corrections and available token/cost data.
- Evaluator identity/type and any deviations.

## 6. Acceptance

Both automated acceptance tests and the rubric's hard gates must pass. A green test suite alone is insufficient if tests were modified or the source change violates the task constraints.

This pack is suitable as a bounded software-maintenance task. It is not a broad measure of general software engineering ability.

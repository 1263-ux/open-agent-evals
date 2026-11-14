# Existing-project maintenance task

<badge>Active evaluation pack</badge>

A self-contained, reproducible Java 17 / Maven task. The fixture contains an intentional calculation bug: a discount is incorrectly applied to shipping as well as the item subtotal.

## Run it

1. Copy `fixtures/java-discount-calculator/` to a writable directory.
2. Run `mvn test` to capture the expected failing baseline.
3. Give the executor `../../task.md` (or the pack's task brief) and ask for the smallest production-code fix.
4. Run `mvn clean test` and inspect the source diff. Do not weaken or delete the tests.

See [pack.yaml](pack.yaml), [task.md](task.md), [rubric.yaml](rubric.yaml) and [evaluation.md](evaluation.md).

This is a bounded software-maintenance case, not a comprehensive measure of software engineering ability. No formal model/workflow comparison has yet been recorded.

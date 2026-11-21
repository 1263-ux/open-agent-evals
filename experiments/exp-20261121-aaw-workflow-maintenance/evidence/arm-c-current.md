# Current work
Status: done

Goal: Fix the Java discount bug so the test suite passes
Result: Discount now applies to subtotal only, shipping undiscounted. `mvn -q -o test` exit 0; Tests run: 2, Failures: 0, Errors: 0, Skipped: 0.
Changed: src/main/java/org/openagentevals/PriceCalculator.java
Next: none
Dead-Ends: none

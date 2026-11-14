package org.openagentevals;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertEquals;

class PriceCalculatorTest {
    private final PriceCalculator calculator = new PriceCalculator();

    @Test
    void discountAppliesToSubtotalButNotShipping() {
        assertEquals(10_000, calculator.calculateTotalCents(10_000, 1_000, 10));
    }

    @Test
    void noDiscountKeepsSubtotalAndShippingUnchanged() {
        assertEquals(11_000, calculator.calculateTotalCents(10_000, 1_000, 0));
    }
}

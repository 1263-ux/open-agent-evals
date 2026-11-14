package org.openagentevals;

/**
 * Calculates an order total in cents.
 * This fixture contains an intentional bug: the discount is applied to shipping.
 */
public class PriceCalculator {
    public int calculateTotalCents(int subtotalCents, int shippingCents, int discountPercent) {
        return (subtotalCents + shippingCents) * (100 - discountPercent) / 100;
    }
}

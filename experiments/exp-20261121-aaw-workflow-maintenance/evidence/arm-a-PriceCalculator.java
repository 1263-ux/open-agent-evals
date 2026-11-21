package org.openagentevals;

/**
 * Calculates an order total in cents.
 * The discount applies to the subtotal only, never to shipping.
 */
public class PriceCalculator {
    public int calculateTotalCents(int subtotalCents, int shippingCents, int discountPercent) {
        return subtotalCents * (100 - discountPercent) / 100 + shippingCents;
    }
}

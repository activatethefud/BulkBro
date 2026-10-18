"""Wolt Market delivery cost and discount model.

This module models the economics of placing an order on Wolt Market so the meal
planner can *optimize* for the true cost of a plan, not just the grocery
subtotal. It reproduces the key rules observed on the live Wolt Market (Serbia)
venue and used by the historical BulkBro "wolt" version:

- **Order minimum** - baskets below a threshold incur a surcharge.
- **Delivery fee** - a flat fee applies unless the basket is large enough to
  qualify for free delivery.
- **Basket discount** - a fixed amount off once the basket reaches a minimum
  spend (a common Wolt Market promotion).

A "basket" here is the group of groceries bought in a single delivery. In the
planner this is the spend accumulated between stock refills (see
:func:`simulation.simulate_plan`), so buying larger, less frequent orders lowers
delivery cost while smaller frequent orders raise it.

The default values are taken from the live ``wolt-market-dorol`` venue scraper
output and can be overridden through :mod:`config`.
"""

from dataclasses import dataclass

import config


@dataclass
class DeliveryResult:
    """Breakdown of delivery-related costs for a plan.

    Attributes
    ----------
    delivery_fees : float
        Total delivery fees plus order-minimum surcharges (RSD).
    delivery_cost : float
        Portion of ``delivery_fees`` that is pure delivery fees.
    surcharge : float
        Portion of ``delivery_fees`` from order-minimum shortfalls.
    discount : float
        Total promotional discount applied to baskets (RSD, positive).
    num_orders : int
        Number of delivery orders (baskets) simulated.
    """

    delivery_fees: float = 0.0
    delivery_cost: float = 0.0
    surcharge: float = 0.0
    discount: float = 0.0
    num_orders: int = 0


def compute_delivery(order_subtotals):
    """Compute delivery fees and discounts for a list of order baskets.

    Each element of ``order_subtotals`` is the grocery subtotal (RSD) of one
    delivery. The function applies, per basket:

    1. **Basket discount** - subtract ``config.BASKET_DISCOUNT_AMOUNT`` when the
       subtotal is at least ``config.BASKET_DISCOUNT_MIN``.
    2. **Order-minimum surcharge** - add the shortfall when the subtotal is
       below ``config.ORDER_MINIMUM``.
    3. **Delivery fee** - add ``config.DELIVERY_FEE`` unless the (post-discount)
       subtotal reaches ``config.FREE_DELIVERY_THRESHOLD``.

    Parameters
    ----------
    order_subtotals : iterable of float
        Grocery subtotal of each order in RSD.

    Returns
    -------
    DeliveryResult
        Aggregated delivery breakdown.
    """
    if not config.DELIVERY_ENABLED:
        return DeliveryResult(num_orders=0)

    orders = [s for s in order_subtotals if s > 0]
    total_fees = 0.0
    total_delivery = 0.0
    total_surcharge = 0.0
    total_discount = 0.0
    discounts_used = 0

    for subtotal in orders:
        # 1. Basket discount on reaching the minimum spend. Capped at
        # ``BASKET_DISCOUNT_MAX_USES`` orders so the optimizer is not rewarded
        # for splitting a plan into many small orders to farm the discount.
        discount = 0.0
        if (config.BASKET_DISCOUNT_AMOUNT > 0
                and subtotal >= config.BASKET_DISCOUNT_MIN
                and discounts_used < config.BASKET_DISCOUNT_MAX_USES):
            discount = config.BASKET_DISCOUNT_AMOUNT
            discounts_used += 1
        total_discount += discount
        net = subtotal - discount

        # 2. Order-minimum surcharge.
        if subtotal < config.ORDER_MINIMUM:
            surcharge = config.ORDER_MINIMUM - subtotal
            total_surcharge += surcharge
            total_fees += surcharge

        # 3. Delivery fee unless the net basket qualifies for free delivery.
        if net < config.FREE_DELIVERY_THRESHOLD:
            total_delivery += config.DELIVERY_FEE
            total_fees += config.DELIVERY_FEE

    return DeliveryResult(
        delivery_fees=round(total_fees, 2),
        delivery_cost=round(total_delivery, 2),
        surcharge=round(total_surcharge, 2),
        discount=round(total_discount, 2),
        num_orders=len(orders),
    )


def total_plan_cost(grocery_subtotal, delivery):
    """Return total plan cost = groceries + delivery - discounts.

    Parameters
    ----------
    grocery_subtotal : float
        Sum of grocery prices in RSD.
    delivery : DeliveryResult
        Delivery breakdown from :func:`compute_delivery`.

    Returns
    -------
    float
        Total cost in RSD (never negative).
    """
    return max(0.0, grocery_subtotal + delivery.delivery_fees - delivery.discount)

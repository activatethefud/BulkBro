"""Simulation and helper functions for BulkBro meal planning."""

import random as rd
import datetime as dt
from pprint import pformat

import numpy as np
from nutrition import Nutrition
from day import Day
from ingredient import ingredients
from meals import meals


# ============================================================================
# Ingredient lookup tables (for performance)
# ============================================================================
_ingr_price = {name: i.price for name, i in ingredients.items()}
_ingr_min_qty = {name: i.min_qty for name, i in ingredients.items()}
_ingr_rots_in = {name: i.rots_in for name, i in ingredients.items()}

# Caches
_sim_cache = {}
_day_rots_cache = {}
_day_nutri_cache = {}

MAX_MEALS_PER_DAY = 7


# ============================================================================
# Helper functions
# ============================================================================
def sublists(arr):
    """Group elements by identity."""
    arr_set = set(arr)
    mapping = {key: val for val, key in enumerate(arr_set)}
    res = [[] for _ in range(len(arr_set))]
    for elem in arr:
        res[mapping[elem]].append(elem)
    return res


def _get_day_rots(day):
    did = id(day)
    if did in _day_rots_cache:
        return _day_rots_cache[did]
    rots = float('inf')
    for meal in day:
        for ingr in meal.ingredients:
            rots = min(rots, _ingr_rots_in.get(ingr.name, 999))
    _day_rots_cache[did] = rots
    return rots


def _get_day_nutrition_cached(day):
    did = id(day)
    if did in _day_nutri_cache:
        return _day_nutri_cache[did]
    nutr = day.day_nutri()
    _day_nutri_cache[did] = nutr
    return nutr


# ============================================================================
# Core simulation functions
# ============================================================================
def simulate_plan(plan):
    """Simulate a meal plan and return costs, nutrition, waste."""
    plan_hash = hash(tuple(tuple(m.name for m in day) for day in plan))
    if plan_hash in _sim_cache:
        cached = _sim_cache[plan_hash].copy()
        cached['plan'] = plan
        return cached

    price = 0
    waste = 0
    ingredients_info = {}
    rot_info = {}

    delivery_fee = 1500
    delivery_fees = 0

    fastest_rot_arr = [_get_day_rots(day) for day in plan]
    old_price = 0

    refill_on_days = [0]
    while (_i := refill_on_days[-1]) < len(fastest_rot_arr):
        refill_on_days.append(fastest_rot_arr[_i] + _i)
    refill_on_days = set(refill_on_days)

    for idx, day in enumerate(plan):
        for meal in day:
            for ingr in meal.ingredients:
                name = ingr.name
                price_val = _ingr_price.get(name, 0)
                min_qty = _ingr_min_qty.get(name, 1)
                rots_in = _ingr_rots_in.get(name, 999)

                if name not in ingredients_info:
                    qty = ingr.qty
                    to_buy = (qty + min_qty - 1) // min_qty
                    price += to_buy * price_val
                    ingredients_info[name] = to_buy * min_qty
                    rot_info[name] = rots_in

                if rot_info[name] <= 0:
                    qty = ingr.qty
                    to_buy = (qty + min_qty - 1) // min_qty
                    price += to_buy * price_val
                    waste += (ingredients_info[name] / min_qty) * price_val
                    ingredients_info[name] = to_buy * min_qty
                    rot_info[name] = rots_in

                ingredients_info[name] -= ingr.qty

                if (remaining := ingredients_info[name]) < 0:
                    to_buy = (-remaining + min_qty - 1) // min_qty
                    price += to_buy * price_val
                    ingredients_info[name] = to_buy * min_qty
                    rot_info[name] = rots_in

        for name in ingredients_info:
            rot_info[name] -= 1

        if idx in refill_on_days and (price_diff := price - old_price) < delivery_fee:
            delivery_fees += delivery_fee - price_diff
            old_price = price

    for name in ingredients_info:
        min_qty = _ingr_min_qty.get(name, 1)
        waste += (ingredients_info[name] / min_qty) * _ingr_price.get(name, 0)

    day_nutris = [_get_day_nutrition_cached(day) for day in plan]
    n = len(plan) or 1
    avg_nutri = Nutrition(
        sum(dn.kcal for dn in day_nutris) / n,
        sum(dn.carb for dn in day_nutris) / n,
        sum(dn.prot for dn in day_nutris) / n,
        sum(dn.fat for dn in day_nutris) / n
    )

    result = {
        'plan': plan,
        'price': price,
        'nutri': avg_nutri,
        'waste': waste,
        'delivery_fees': 0
    }

    if len(_sim_cache) < 500:
        cache_entry = result.copy()
        del cache_entry['plan']
        _sim_cache[plan_hash] = cache_entry

    return result


def generate_day(target_nutri, target_mealcount, meals=meals):
    """Generate a random day meeting nutrition targets.
    
    Args:
        target_nutri: [kcal, carb, prot, fat] target values
        target_mealcount: desired meals per day (-1 to ignore, uses random 1-5)
        meals: meal database to choose from
    
    Returns:
        Day with reasonable meal count (1-7)
    """
    day = []
    N = len(meals)

    if N == 0:
        return Day(day)

    if target_mealcount > 0:
        target_meals = target_mealcount
    else:
        target_meals = rd.randint(1, 3)
    
    meal_count = 0
    while meal_count < target_meals and meal_count < MAX_MEALS_PER_DAY:
        chosen_meal = rd.choice(meals)
        day.append(chosen_meal)
        meal_count += 1
    
    if len(day) == 0 and N > 0:
        day = [rd.choice(meals)]

    return Day(day)


def shopping_list(plan, reach=-1):
    """Generate shopping list for a plan."""
    fastest_rot_arr = [min([ingr.rots_in for meal in day for ingr in meal.ingredients]) for day in plan]

    if reach == -1:
        reach = 1
        while reach - 1 < len(plan) and fastest_rot_arr[reach - 1] >= reach:
            reach += 1
        reach -= 1

    ingr_needed = [
        sum(x) for x in sublists([
            ingredient for day in plan[:reach]
            for meal in day
            for ingredient in meal.ingredients
        ])
    ]

    ingr_shopping_list = {
        "spisak": [{
            "Sastojak": ingr.name,
            "k": ingr.to_buy(),
            "mk": ingr.min_qty,
            "required": ingr.qty
        } for ingr in ingr_needed]
    }
    ingr_shopping_list["cena"] = sum([ingr.price * ingr.to_buy() for ingr in ingr_needed])
    ingr_shopping_list["za broj dana"] = reach

    return ingr_shopping_list


def generate_shopping_list(plan, filename, reach=-1, today=None):
    """Generate and save shopping list to file."""
    if today is None:
        today = dt.date.today()

    import os
    os.makedirs("plans", exist_ok=True)

    with open(f"plans/{filename}_shopping.txt", 'w') as f:
        for idx, date in enumerate((today + dt.timedelta(n) for n in range(len(plan)))):
            f.write("\n")
            f.write("Shopping list - ".upper() + date.isoformat() + "\n")
            f.write("----------------------------" + "\n")
            f.write(pformat([date, plan[idx], shopping_list(plan[idx:], reach)]) + "\n")

            for meal in plan[idx]:
                f.write("\n")
                f.write(meal.name.upper() + "\n")
                f.write(str(meal.nutri()) + "\n")
                f.write("-------------------------" + "\n")

                for ingr in meal.ingredients:
                    f.write(f"\t\t{ingr.name}, {ingr.qty} {ingr.nutri_info}\n")

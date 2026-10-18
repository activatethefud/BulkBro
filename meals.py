"""Meal database and source management for BulkBro."""

from copy import deepcopy
import numpy as np

from ingredient import ingredients
from meal import Meal
from vegan_meals import meals as vegan_meals
from djina_meals import meals as djina_meals
from nikola_meals import meals as nikola_meals
from insulin_index import predict_insulin_index


MEAL_SOURCES = {
    'nikola': nikola_meals,
    'vegan': vegan_meals,
    'djina': djina_meals,
}

DEFAULT_SOURCE = 'nikola'
current_source = DEFAULT_SOURCE
meals = MEAL_SOURCES[DEFAULT_SOURCE]


def _init_meal_data():
    """Initialize derived meal data (runs at module load and after source change)."""
    global meals, meals_cpy, ingredients_in_meals, ingredients_in_meals_list
    global meals_complement, breakfasts, snacks, lunches, dinners, healthy, eye, nutris

    # Work on a fresh copy so the raw source list in MEAL_SOURCES is never
    # mutated (portion expansion below appends to ``meals``).
    meals = [deepcopy(m) for m in MEAL_SOURCES[current_source]]
    meals_cpy = deepcopy(meals)
    ingredients_in_meals = {ingr.name for meal in meals_cpy for ingr in meal.ingredients}
    ingredients_in_meals_list = sorted(ingredients_in_meals, key=lambda x: -ingredients[x].price)
    
    for meal in meals:
        _nutri = meal.nutri()
        meal.insulin_index = sum(
            predict_insulin_index(
                ingr.nutri_info.carb,
                ingr.nutri_info.prot,
                ingr.nutri_info.fat
            ) * ingr.nutri_info.kcal / _nutri.kcal
            for ingr in meal.ingredients if _nutri.kcal > 0
        )
    
    unique_check = set()
    for meal in meals:
        if meal.name in unique_check:
            raise AssertionError(f"Duplicate meal name: {meal.name}")
        unique_check.add(meal.name)
    
    original_meals = list(meals)
    for meal in original_meals:
        for portion_factor in np.arange(0.60, 1.0, 0.01):
            meals.append(deepcopy(meal).portion(portion_factor))
    
    meals.sort(key=lambda x: x.nutri().kcal)
    
    meals_complement = {
        ingredients[ingr].name: {m for m in meals if ingredients[ingr] not in m.ingredients}
        for ingr in ingredients_in_meals
    }
    
    breakfasts = [m for m in meals if "breakfast" in m.categories]
    snacks = [m for m in meals if "snack" in m.categories]
    lunches = [m for m in meals if "lunch" in m.categories]
    dinners = [m for m in meals if "dinner" in m.categories]
    healthy = [m for m in meals if "healthy" in m.categories]
    eye = [m for m in meals if "eye" in m.categories]
    
    nutris = [meal.nutri() for meal in meals]


def set_meal_source(source: str):
    """Switch meal source.
    
    Args:
        source: One of 'nikola', 'vegan', 'djina'
    """
    global current_source, meals
    
    if source not in MEAL_SOURCES:
        raise ValueError(f"Unknown source: {source}. Available: {list(MEAL_SOURCES.keys())}")
    
    current_source = source
    meals = MEAL_SOURCES[source]
    _init_meal_data()


_init_meal_data()

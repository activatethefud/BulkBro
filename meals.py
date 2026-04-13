from ingredient import ingredients, Ingredient
import numpy as np
from copy import deepcopy, copy
from meal import Meal
from vegan_meals import meals as vegan_meals
from djina_meals import meals as djina_meals
from nikola_meals import meals as nikola_meals

from insulin_index import predict_insulin_index, meal_insulin_index

MEAL_SOURCES = {
    'nikola': nikola_meals,
    'vegan': vegan_meals,
    'djina': djina_meals,
}

DEFAULT_SOURCE = 'nikola'
current_source = DEFAULT_SOURCE
meals = MEAL_SOURCES[DEFAULT_SOURCE]


def set_meal_source(source: str):
    """Switch meal source. Call before importing meal data.
    
    Args:
        source: One of 'nikola', 'vegan', 'djina'
    """
    global current_source, meals, meals_cpy, ingredients_in_meals
    global ingredients_in_meals_list, meals_complement, breakfasts, snacks
    global lunches, dinners, healthy, eye, nutris
    
    if source not in MEAL_SOURCES:
        raise ValueError(f"Unknown source: {source}. Available: {list(MEAL_SOURCES.keys())}")
    
    current_source = source
    meals = MEAL_SOURCES[source]
    meals_cpy = deepcopy(meals)
    ingredients_in_meals = set([ingr.name for meal in meals_cpy for ingr in meal.ingredients])
    ingredients_in_meals_list = sorted(list(ingredients_in_meals), key = lambda x : -ingredients[x].price)
    
    for meal in meals:
            _nutri = meal.nutri()
            meal.fii = sum(
                    predict_insulin_index(
                            ingr.nutri_info.carb,
                            ingr.nutri_info.prot,
                            ingr.nutri_info.fat
                    ) * ingr.nutri_info.kcal/_nutri.kcal for ingr in meal.ingredients
            )
    
    check = set()
    for meal in meals:
            assert meal.name not in check
            check.add(meal.name)
    
    for meal in copy(meals):
            for portion_factor in np.arange(0.60,1,0.01):
                    meals.append(deepcopy(meal).portion(portion_factor))
    
    meals.sort(key = lambda x : x.nutri().kcal)
    
    meals_complement = { ingredients[ingr].name : set([m for m in meals if ingredients[ingr] not in m.ingredients]) for ingr in ingredients_in_meals}
    
    breakfasts = [x for x in meals if "breakfast" in x.categories]
    snacks = [x for x in meals if "snack" in x.categories]
    lunches = [x for x in meals if "lunch" in x.categories]
    dinners = [x for x in meals if "dinner" in x.categories]
    healthy = [x for x in meals if "healthy" in x.categories]
    eye = [x for x in meals if "eye" in x.categories]
    
    nutris = [meal.nutri() for meal in meals]

meals_cpy = deepcopy(meals)
ingredients_in_meals = set([ingr.name for meal in meals_cpy for ingr in meal.ingredients])
ingredients_in_meals_list = sorted(list(ingredients_in_meals), key = lambda x : -ingredients[x].price)

# embed fii info in meals
for meal in meals:
        _nutri = meal.nutri()

        meal.fii = sum(
                predict_insulin_index(
                        ingr.nutri_info.carb,
                        ingr.nutri_info.prot,
                        ingr.nutri_info.fat
                ) * ingr.nutri_info.kcal/_nutri.kcal for ingr in meal.ingredients
        )

# Assert unique meal names
check = set()
for meal in meals:
        assert meal.name not in check
        check.add(meal.name)

# Preprocess for portion fitting
for meal in copy(meals):
        if True:
                for portion_factor in np.arange(0.60,1,0.01):
                        meals.append(deepcopy(meal).portion(portion_factor))

meals.sort(key = lambda x : x.nutri().kcal)

meals_complement = { ingredients[ingr].name : set([m for m in meals if ingredients[ingr] not in m.ingredients]) for ingr in ingredients_in_meals}

breakfasts = [x for x in meals if "breakfast" in x.categories]
snacks = [x for x in meals if "snack" in x.categories]
lunches = [x for x in meals if "lunch" in x.categories]
dinners = [x for x in meals if "dinner" in x.categories]
healthy = [x for x in meals if "healthy" in x.categories]
eye = [x for x in meals if "eye" in x.categories]

nutris = [meal.nutri() for meal in meals]

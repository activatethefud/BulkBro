# BulkBro API Reference


## Module: day

### Class: Day

Represents a day containing multiple meals.

**Parameters**
----------
meals : list
    List of Meal objects


## Module: djina_meals


## Module: harmony

### Class: HarmonyOptimizer

Harmony search optimizer for meal planning with improved mathematics.

### Function: optimize()

Convenience function to run optimization.


## Module: ingredient

### Class: Ingredient

### Function: export_to_csv()


## Module: insulin_index

### Function: predict_insulin_index()

Predict Food Insulin Index from macronutrients. Based on simplified formula from data analysis: FII ≈ 0.9*Carbs + 0.3*Protein + 0.2*Fat Args: carb: Available carbohydrates in grams protein: Protein in grams fat: Fat in grams

**Returns**
-------
Predicted Insulin Index (higher = more insulin demand)

### Function: meal_insulin_index()

Calculate weighted average Insulin Index for a meal. Args: meals: List of Meal objects

**Returns**
-------
Weighted average Insulin Index

### Function: day_insulin_index()

Calculate average Insulin Index across a day or plan. Args: days: List of Day objects

**Returns**
-------
Average Insulin Index

### Function: ii_category()

Get category name for Insulin Index value. Args: ii: Insulin Index value

**Returns**
-------
Category string: 'low', 'moderate', or 'high'


## Module: main

### Function: print_plan_summary()

Print a formatted summary of the optimized plan.

**Parameters**
----------
solution : list
    List of Day objects List of Day objects targets : dict
targets : dict
    Dict with keys: days, meals, kcal, prot, ratio

### Function: main()

### Function: do_run()

### Function: do_shop()

### Function: do_load()

### Function: do_run_interactive()


## Module: meal

### Class: Meal

Represents a meal with ingredients and nutritional information.

**Parameters**
----------
name : str
    Meal name Meal name
ingredients : list
    List of Ingredient objects List of Ingredient objects
categories : list
    List of category strings


## Module: meals

### Function: _init_meal_data()

Initialize derived meal data (runs at module load and after source change).

### Function: set_meal_source()

Switch meal source. Args: source: One of 'nikola', 'vegan', 'djina'


## Module: nikola_meals


## Module: nutrition

### Class: Nutrition

Represents nutritional values for a meal or day.

**Parameters**
----------
kcal : float
    Kilocalories Kilocalories
carb : float
    Carbohydrates in grams Carbohydrates in grams
prot : float
    Protein in grams Protein in grams
fat : float
    Fat in grams


## Module: simulation

### Function: sublists()

Group elements by identity. Args: arr: List of elements

**Returns**
-------
List of lists, each containing elements with same identity

### Function: _get_day_rots()

Get minimum shelf life (rots_in) for any ingredient in day.

### Function: _get_day_nutrition_cached()

Get cached daily nutrition.

### Function: simulate_plan()

Simulate a meal plan and return costs, nutrition, waste. Args: plan: List of Day objects

**Returns**
-------
Dict with 'plan', 'price', 'nutri', 'waste', 'delivery_fees'

### Function: generate_day()

Generate a random day meeting nutrition targets. Args: target_nutri: [kcal, carb, prot, fat] target values target_mealcount: desired meals per day (-1 to ignore, uses random 1-5) meals: meal database to choose from

**Returns**
-------
Day with reasonable meal count (1-7)

### Function: shopping_list()

Generate shopping list for a plan.

### Function: generate_shopping_list()

Generate and save shopping list to file.


## Module: util

### Function: load_sol()

Load a solution from pickle file.


## Module: vegan_meals


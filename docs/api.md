# BulkBro API Reference


## Module: day

### Class: Day


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

Predict Food Insulin Index from macronutrients. Based on simplified formula from data analysis: FII ≈ 0.9*Carbs + 0.3*Protein + 0.2*Fat

**Args:**
- `carb`: Available carbohydrates in grams
- `protein`: Protein in grams
- `fat`: Fat in grams  Predicted Insulin Index (higher = more insulin demand)

### Function: meal_insulin_index()

Calculate weighted average Insulin Index for a meal.

**Args:**
- `meals`: List of Meal objects  Weighted average Insulin Index

### Function: day_insulin_index()

Calculate average Insulin Index across a day or plan.

**Args:**
- `days`: List of Day objects  Average Insulin Index

### Function: ii_category()

Get category name for Insulin Index value.

**Args:**
- `ii`: Insulin Index value  Category string: 'low', 'moderate', or 'high'


## Module: main

### Function: main()

### Function: do_run()

### Function: do_shop()

### Function: do_load()

### Function: do_run_interactive()


## Module: meal

### Class: Meal


## Module: meals

### Function: _init_meal_data()

Initialize derived meal data (runs at module load and after source change).

### Function: set_meal_source()

Switch meal source.

**Args:**
- `source`: One of 'nikola', 'vegan', 'djina'


## Module: nikola_meals


## Module: nutrition

### Class: Nutrition

Represents nutritional values for a meal or day.


## Module: simulation

### Function: sublists()

Group elements by identity.

### Function: _get_day_rots()

### Function: _get_day_nutrition_cached()

### Function: simulate_plan()

Simulate a meal plan and return costs, nutrition, waste.

### Function: generate_day()

Generate a random day meeting nutrition targets.

**Args:**
- `target_nutri`: [kcal, carb, prot, fat] target values
- `target_mealcount`: desired meals per day (-1 to ignore, uses random 1-5)
- `meals`: meal database to choose from  Day with reasonable meal count (1-7)

### Function: shopping_list()

Generate shopping list for a plan.

### Function: generate_shopping_list()

Generate and save shopping list to file.


## Module: util

### Function: load_sol()

Load a solution from pickle file.


## Module: vegan_meals


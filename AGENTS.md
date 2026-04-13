# BulkBro

Personal meal planning and nutrition optimization project.

## Entry Point

```bash
python3 main.py run              # Interactive mode
python3 main.py run -d 7 -t 60  # With arguments
python3 main.py --help         # Show help
```

## Usage

### Run Optimization

```bash
python3 main.py run [options]

Options:
  -d, --days NUM        Number of days to plan (default: 3)
  -m, --meals NUM       Meals per day (default: 3)
  -k, --kcal NUM       Target daily calories (default: 2000)
  -p, --protein NUM   Target daily protein in grams (default: 100)
  -r, --ratio NUM    Target carb/fat ratio (default: 2.0)
  -t, --time-limit  Optimization time limit in seconds (default: 60)
  -o, --output      Output filename (default: meal_plan)
  --pop-size     Population size (default: 150)
```

## Usage

### Run Optimization

```bash
python3 main.py run [options]

Options:
  -d, --days NUM        Number of days to plan (default: 3)
  -m, --meals NUM       Meals per day (default: 3)
  -k, --kcal NUM       Target daily calories (default: 2000)
  -p, --protein NUM   Target daily protein in grams (default: 100)
  -r, --ratio NUM    Target carb/fat ratio (default: 2.0)
  -t, --time-limit  Optimization time limit in seconds (default: 60)
  -o, --output      Output filename (default: meal_plan)
  --pop-size     Population size (default: 200)
```

### Generate Shopping List

```bash
python3 main.py shop <solution_file> [-r NUM]
```

### Load and Display Solution

```bash
python3 main.py load <solution_file>
```

## Interactive Mode

```bash
python3 main.py run
Generate for numof. days: 7
Goal daily meal count: 3
Goal kcal: 2000
Goal prot: 100
Goal carb/fat ratio: 2.0
Improvement time limit (sec)?: 60
```

## Output

After optimization:
- `plans/<output>.pickle` - Solution pickle
- `plans/<output>` - Text plan

Generate shopping list:
- `plans/<output>_shopping.txt`

## Structure

- `main.py` - CLI entry point + core simulation (+ generate_day, simulate_plan)
- `harmony.py` - HarmonyOptimizer class
- `nutrition.py`, `meal.py`, `day.py` - Domain models
- `meals.py`, `nikola_meals.py`, `vegan_meals.py`, `djina_meals.py` - Meal sources
- `ingredient.py` - Ingredient catalog (~1000 ingredients)
- `util.py` - Utilities (statlist, load_sol)

## Meal Source Selection

Edit `meals.py` to change source:
```python
meals = MEAL_SOURCES['nikola']  # 'nikola', 'vegan', 'djina'
```

Or use `set_meal_source('vegan')` function.

## Testing

```bash
python3 test_runner.py
```

Run 21 tests covering core functionality.

## Dependencies

numpy, scikit-learn (fii_predictor requires PyTorch only)
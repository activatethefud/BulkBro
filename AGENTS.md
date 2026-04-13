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
- `insulin_index.py` - Insulin Index predictor
- `simulation.py` - Core simulation functions
- `util.py` - Utilities (load_sol)
- `test_runner.py` - Test suite (48 tests)
- `docs.py` - Documentation generator

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

Run 48 tests covering core functionality.

## Documentation

Generate documentation:
```bash
python3 docs.py           # Generate HTML + Markdown
python3 docs.py --api   # Generate API Markdown only
python3 docs.py --html  # Generate HTML only
```

Output:
- `docs/index.html` - Main HTML documentation
- `docs/api.md` - API reference in Markdown

## Dependencies

numpy, scikit-learn

## Git Practices

After making changes, create sensible commits for traceability and potential rollback:

### Before Committing
1. Run tests to verify changes work: `python3 test_runner.py`
2. Check what changed: `git status` and `git diff`

### Commit Guidelines
- Make **one commit per logical change** (feature, fix, or cleanup)
- Write **clear commit messages** describing what and why
- **Test before committing** to ensure no regressions

### Example Workflow
```bash
# After making changes
git status
git diff

# If tests pass and changes look good
git add <files>
git commit -m "Add insulin index predictor based on Bell formula

- Created insulin_index.py with predict_insulin_index()
- Updated meals.py to use new predictor
- Added 4 new tests for insulin index"
```

### Rollback if Needed
```bash
# View history
git log --oneline

# Restore to previous commit
git checkout <commit-hash> -- <file>

# Or reset to previous commit (discards changes)
git reset --hard <commit-hash>
```
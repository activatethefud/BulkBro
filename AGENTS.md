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
  --no-fridge    All ingredients spoil in 1 day (no refrigerator)
  --no-delivery  Ignore delivery fees and basket discounts
```

### Ingredient sourcing: Maxi (this branch)

On the `maxi` branch every ingredient is sourced from **Maxi** (Belgrade
`maxi-kralja-milana` venue, scraped via the Wolt consumer assortment API). This
branch replaces the earlier Wolt Market sourcing: prices in `ingredient.py` and
the product correspondence come from the Maxi catalog.

```bash
python3 maxi_scraper.py            # scrape Maxi catalog -> maxi_catalog.json (gitignored)
python3 maxi_refresh.py report     # price/availability report (no writes)
python3 maxi_refresh.py apply      # write refreshed prices, drop missing items
python3 maxi_refresh.py export     # regenerate maxi_products.py
python3 main.py maxi              # full ingredient -> Maxi product table
python3 main.py maxi -f jogurt    # filter by ingredient or product name
```

The curated `MAXI_MAP` in `maxi_refresh.py` maps each ingredient concept to the
cheapest suitable single-ingredient Maxi product. Loose produce is priced
per-kg (`wolt_grams=1000`); counted/per-piece produce uses a `grams_block`
override. A few ingredients Maxi does not stock are mapped to the closest
single-ingredient substitute (lentils->white beans, chia->flaxseed, rice
cakes->crispbread, dried pineapple->raisins). The generated `maxi_products.py`
(`MAXI_PRODUCTS`) is attached at import as `ingr.wolt` with `ingr.wolt_name` /
`ingr.wolt_id`. Shopping lists emit a `MAXI ORDER` block with exact product names.

Maxi via Wolt: min order **1,500 RSD**, delivery fee ~49-249 RSD (flat 249 for
large baskets), basket discount 400 RSD off >=1,000 RSD. Maxi's own site has a
3,500 RSD minimum and 199 RSD fee; not used here.

### Delivery optimization

The optimizer minimizes the **grand total** (groceries + delivery - discounts), not
just the grocery subtotal. Groceries bought between stock refills form a delivery
basket; the model rewards fewer/larger baskets that clear the free-delivery
threshold and unlocks the basket discount. Tunables live in `config.py`:

```python
DELIVERY_ENABLED = True        # include delivery economics in the objective
ORDER_MINIMUM = 1500           # RSD; shortfalls incur a surcharge
DELIVERY_FEE = 119             # RSD flat fee (waived above free threshold)
FREE_DELIVERY_THRESHOLD = 2500 # RSD basket value for free delivery
BASKET_DISCOUNT_AMOUNT = 400   # RSD off once the basket reaches the minimum
BASKET_DISCOUNT_MIN = 1000     # RSD minimum basket for the discount
```

### Legacy (wolt branch): refresh prices from Wolt Market

`ingredient.py` prices can be refreshed from the live Wolt Market catalog. The
scraper and refresher live in `wolt_scraper.py` and `wolt_refresh.py`:

```bash
python3 wolt_scraper.py                    # fetch live catalog -> wolt_catalog.json
python3 wolt_refresh.py report             # price/availability report (no writes)
python3 wolt_refresh.py candidates         # suggest new products to add
python3 wolt_refresh.py apply              # write refreshed prices, drop missing items
python3 wolt_refresh.py apply --keep-missing   # refresh prices only, keep all entries
python3 wolt_refresh.py export             # regenerate wolt_products.py (name correspondence)
```

Prices are normalized to the ingredient's `min_qty` using `nutri_std_size`
(grams per block) so counted items (eggs, bananas) compare fairly. Wolt does not
expose nutrition data, so nutrition is preserved from the existing records. The
`WOLT_MAP` in `wolt_refresh.py` curates which Wolt product each ingredient maps
to.

### Legacy (wolt branch): ingredient -> Wolt product correspondence

**Every ingredient must be sourced from Wolt Market.** The catalog only contains
ingredients that map to a real Wolt Market product; an ingredient with no
suitable product is removed together with every meal that uses it (e.g.
`orah`/walnut — no plain walnut kernels exist on the venue, only cookies/oil/
spreads — was dropped along with the `orah`, `sejk (banana & orah)` and
`ovsene (banana & orah)` meals). Two tests enforce this:
`test_every_ingredient_has_wolt_product` and
`test_all_meal_ingredients_are_wolt_sourced`.

The exact Wolt product each ingredient represents is stored in the committed,
human-readable `wolt_products.py` (generated by `wolt_refresh.py export`) and
attached to each `Ingredient` at import as `ingr.wolt` (keys `id`, `name`,
`pack`) with `ingr.wolt_name` / `ingr.wolt_id` helpers.

```bash
python3 main.py wolt                # full ingredient -> Wolt product table
python3 main.py wolt -f jogurt      # filter by ingredient or product name
```

The generated shopping list (`plans/<output>_shopping.txt`) includes a
**WOLT MARKET ORDER** block per day listing each product by its exact Wolt
name and pack count, so it can be used directly in the Wolt app.

Each shopping block also states **how many days it lasts** (`LASTS N DAY(S)`),
derived from the rotting logic: a buy covers consecutive days until the
fastest-spoiling ingredient in it would expire. The same value is available
programmatically as `shopping_list(plan)["za broj dana"]` and is shown by
`main.py run` / `main.py load` ("First shopping list lasts: N day(s)").

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

- `main.py` - CLI entry point (+ generate_day, simulate_plan wiring)
- `harmony.py` - HarmonyOptimizer class
- `nutrition.py`, `meal.py`, `day.py` - Domain models
- `meals.py`, `nikola_meals.py`, `vegan_meals.py`, `djina_meals.py` - Meal sources
- `ingredient.py` - Ingredient catalog (~97 ingredients, Maxi priced)
- `maxi_products.py` - Generated Ingredient -> Maxi product name/id/pack map
- `maxi_scraper.py` - Scrape live Maxi catalog (via Wolt venue API)
- `maxi_refresh.py` - Refresh/normalize ingredient prices from the Maxi catalog
- `wolt_products.py` - Legacy Wolt correspondence (from the `wolt` branch)
- `insulin_index.py` - Insulin Index predictor
- `simulation.py` - Core simulation functions (incl. basket/order tracking)
- `delivery.py` - Delivery-fee + basket-discount cost model
- `wolt_scraper.py` - Scrape live Wolt Market food catalog
- `wolt_refresh.py` - Refresh/normalize ingredient prices from the catalog
- `config.py` - Central tunables (targets, optimizer, delivery economics)
- `util.py` - Utilities (load_sol)
- `test_runner.py` - Test suite (157 tests)
- `docs.py` - Documentation generator
- `SPEC.md` - Full project specification (architecture, models, algorithms, config)

## Delivery & Discount Model

`delivery.py` models Wolt Market order economics per delivery basket:

- **Order minimum** - baskets below `ORDER_MINIMUM` incur a surcharge.
- **Delivery fee** - `DELIVERY_FEE` applies unless the basket reaches
  `FREE_DELIVERY_THRESHOLD`.
- **Basket discount** - `BASKET_DISCOUNT_AMOUNT` off once the basket reaches
  `BASKET_DISCOUNT_MIN`, capped at `BASKET_DISCOUNT_MAX_USES` orders so the
  optimizer cannot farm the discount by splitting into many tiny orders.

`simulate_plan` returns `price`, `delivery_fees`, `discount`, `num_orders` and
`total_price`. The optimizer's `delivery` objective minimizes net delivery
overhead as a fraction of groceries, naturally preferring fewer, larger baskets.

## Fine-grained rotting (sealed vs opened)

Each ingredient has two shelf lives:

- `rots_in` - days a pack lasts **once opened / in use** (the everyday value).
- `rots_sealed` - days an **unopened** pack lasts (usually longer; defaults to
  `rots_in` where opening makes no difference, e.g. fresh produce/meat).

`simulate_plan` keeps a two-pool inventory per ingredient (sealed vs opened).
Packages bought go into the sealed pool and are opened as they're consumed.
Shelf-stable goods (dry goods, oils, nuts, canned, frozen) have a long sealed
life; perishables rot soon after opening. This gives **truer waste**: leftover
shelf-stable stock at plan end is *carried over* (not thrown away), so `waste`
reflects only food that actually spoils. `rots_sealed` values are assigned by a
category heuristic at the bottom of `ingredient.py` (`SEALED_OVERRIDES` for
special cases). `config.WASTE_ENABLED` adds an always-on `waste_frac` objective
so the optimizer also avoids plans that discard food. `main.py run` prints a
`Food Waste:` line. `NO_FRIDGE` forces both shelf lives to 1 day.

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

Run 157 tests covering core functionality, including the delivery/discount model.

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

For the human-readable architecture/algorithm reference see **`SPEC.md`**
(published at https://github.com/activatethefud/BulkBro).

## Dependencies

numpy, scikit-learn

## Git Practices

After making changes, create sensible commits for traceability and potential rollback:

### Before Committing
1. Run tests to verify changes work: `python3 test_runner.py`
2. Check what changed: `git status` and `git diff`
3. Regenerate documentation: `python3 docs.py`

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

### Publishing SPEC.md and tests to GitHub

The canonical public mirror (including `SPEC.md` and the full test suite) is:

- **Repo:** https://github.com/activatethefud/BulkBro (public, default branch `main`)
- **Account:** `activatethefud` (`gh auth status` should show it active)

`SPEC.md` and `test_runner.py` are ordinary tracked files, so publishing them is
just a normal push. The current local branch (`maxi`) is published as `main`, and
**only that branch is pushed** (experimental branches stay local):

```bash
# One-time: create the repo + wire the remote (if not already done)
gh repo create BulkBro --public \
  --description "BulkBro: multi-day meal-planning & nutrition optimizer with \
    delivery-cost, discount and food-waste optimisation (Maxi sourcing). \
    Includes SPEC.md and a 157-test suite."
git remote add origin https://github.com/activatethefud/BulkBro.git

# Push the current branch as the remote main
git push -u origin maxi:main

# Subsequent updates (after committing SPEC.md / tests / code)
git push origin maxi:main
```

Verify what is live:

```bash
gh repo view activatethefud/BulkBro --json name,visibility,defaultBranchRef,url
gh api repos/activatethefud/BulkBro/contents/ --jq '.[].name' | sort   # root files
gh api repos/activatethefud/BulkBro/contents/SPEC.md --jq '.name,.size'
```

Publishing checklist / caveats:
1. Run `python3 test_runner.py` first — a published mirror should be green (157 tests).
2. The generated catalogs (`maxi_catalog.json`, `wolt_catalog.json`), `plans/*`,
   `*.pickle` and `*.txt` are **git-ignored** and are therefore not published.
3. Leave the uncommitted `meals.py` `DEFAULT_SOURCE` edit out of commits unless it
   is intentional (it is a local/source preference).
4. Do not push experimental branches (`wolt`, `finer-rotting`, `univerexport`)
   unless explicitly asked; publish only the intended branch (`maxi` -> `main`).
5. To make the mirror private/public later: `gh repo edit activatethefud/BulkBro --visibility private|public`.
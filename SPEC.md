# BulkBro — Specification

> **Status:** this document describes the `maxi` branch, where every ingredient is
> sourced from **Maxi** (Belgrade `maxi-kralja-milana` venue). Legacy Wolt-era
> behaviour is noted where relevant.

---

## 1. Purpose

BulkBro generates multi‑day meal plans that hit nutrition targets at the lowest
**all‑things‑considered** cost. It is a combinatorial optimiser over a catalogue
of ingredients and a database of meals, with three cost/quality dimensions beyond
raw groceries:

1. **Grocery cost** — the sum of packs actually bought (pack rounding included).
2. **Delivery economics** — order minimums, delivery fees, basket discounts.
3. **Food waste** — perishable leftovers that spoil before being eaten.

Given targets (days, meals/day, kcal, protein, carb/fat ratio) it searches for a
plan that is nutritionally close, cheap, low‑waste, diverse, and internally
consistent, and emits a shopping list that names the exact supermarket product to
order.

---

## 2. High‑level architecture

```
                    ┌──────────────────────────┐
   catalogue ─────► │ ingredient.py (97 items) │ ◄── maxi_products.py
   (scraper)        └────────────┬─────────────┘      (exact SKU map)
                                 │
   meal sources ──► meals.py ────┤
   (nikola/vegan/  (portion       │
    djina)          expansion)    ▼
                          simulation.py  ◄── delivery.py
                          (cost / waste /     (fees, discounts)
                           nutrition)
                                 ▲
                                 │ fitness
                    harmony.py (HarmonyOptimizer)
                                 │
                                 ▼
              main.py (CLI) ──► plans/*.pickle, plans/*.txt
```

Data flow at runtime: `meals.py` loads a meal source, expands portions, and builds
lookup tables → `simulation.simulate_plan()` evaluates a plan → the optimiser
(`harmony.py`) uses `simulate_plan` + derived objectives as its fitness → `main.py`
prints a summary, saves a pickle, and writes the shopping list.

---

## 3. Domain model

### 3.1 `Nutrition` (`nutrition.py`)

Immutable‑style value object holding `kcal, carb, prot, fat` (grams). Supports
scalar `__mul__`, `Nutrition.__add__` / `sum()` via `__radd__`, equality, and a
weighted distance used by the optimiser:

```
dist(other) = sqrt( kcal_term + (prot_self - prot_other)^2 )
kcal_term   = Δkcal                    if Δkcal <= DIST_KCAL_THRESHOLD (65)
            = Δkcal^2                  otherwise   (quadratic for large gaps)
```

### 3.2 `Ingredient` (`ingredient.py`)

The central catalogue record. One instance = one purchasable ingredient concept.

| Field | Meaning |
|---|---|
| `name` | Unique key / display name |
| `price` | RSD per **one `min_qty` block** |
| `min_qty` | Block size: **grams**, or a **piece count** for counted items |
| `qty` | Current portion quantity (starts at `min_qty`) |
| `rots_in` | **Opened/in‑use** shelf life in days (everyday spoilage value) |
| `rots_sealed` | **Unopened** shelf life in days (`>= rots_in` for shelf‑stable goods) |
| `nutri_info` | `Nutrition` for one `min_qty` block |
| `nutri_std_size` | Grams represented by one block, for counted items (else `min_qty`) |
| `wolt` | Dict `{id, name, pack}` → exact supermarket SKU (populated from `maxi_products.py`) |

**Operators / helpers**

- `to_buy(qty=None)` → `ceil(qty / min_qty)` packs.
- `ingr * x` → copy with absolute `qty = x`; `nutri_info` scaled by `x/min_qty`.
  (Used in meal recipes as `ingredients['kikiriki']*100` = 100 g.)
- `ingr ** x` → copy with `qty = min_qty * x`; `nutri_info` scaled by `x`.
  (Used as `ingredients['tofu']**0.5` = half a standard block.)
- `portion(f)` → scales `qty` **only when `qty > 10`** (i.e. gram‑based items;
  small counted items are left alone to avoid fragmentation), scaling nutrition by `f`.
- `+`, `-`, `copy()`, `__eq__`/`__hash__` by name.
- `is_shelf_stable` → `rots_sealed > rots_in`.
- `wolt_name` / `wolt_id` → convenience accessors into `wolt`.

### 3.3 `Meal` (`meal.py`)

`Meal(name, ingredients, categories)` where `categories` is a list of tags
(`breakfast`, `snack`, `lunch`, `dinner`, `healthy`, `eye`, `banana`, …).
`nutri()` sums ingredient nutrition; `portion(f)` scales all ingredients.

### 3.4 `Day` (`day.py`)

`Day(meals)` caches per‑meal and total nutrition; `set_meal(i, m)` recomputes.
`__str__` prints shortened meal tokens (e.g. `[tof*zi  kik*ki  banana]`).

### 3.5 Meal sources (`meals.py`, `*_meals.py`)

Three sources: `nikola` (41 meals), `vegan` (17), `djina` (25). Selection:

```python
DEFAULT_SOURCE = 'vegan'         # current branch/user setting
current_source = DEFAULT_SOURCE
meals = MEAL_SOURCES[DEFAULT_SOURCE]
```

`_init_meal_data()` (re)builds derived state on load and after `set_meal_source()`:

1. Deep‑copy the raw source list (never mutate the source).
2. Compute each meal's **insulin index** (kcal‑weighted, `insulin_index.py`).
3. Guard against duplicate meal names.
4. **Portion expansion:** for every meal append copies at `0.60, 0.61, …, 0.99`
   (`np.arange(0.60, 1.0, 0.01)`) so the search has fine‑grained portion variants.
5. Sort by kcal; build `meals_complement` (per ingredient, the meals that do *not*
   contain it), and category subsets (`breakfasts`, `snacks`, `lunches`,
   `dinners`, `healthy`, `eye`).

---

## 4. Catalogue & sourcing pipeline

### 4.1 Ingredient catalogue

`ingredient.py` defines `ingredients = {name: Ingredient(...)}` — **97 items**.
Entries are authored in `Ingredient(name, price, min_qty, rots_in, Nutrition(...)[, nutri_std_size])`.
At import time two post‑processing passes run:

1. **Attach SKU map** from `maxi_products.MAXI_PRODUCTS` → `ingr.wolt = {id,name,pack}`.
2. **Assign `rots_sealed`** via category heuristic (§6.3), unless `SEALED_OVERRIDES`
   provides an explicit value.

A duplicate‑key assertion runs at the end.

### 4.2 Scrapers

**`wolt_scraper.py`** — generic Wolt consumer‑assortment client (reused by Maxi):

- `ASSORTMENT_BASE = consumer-api.wolt.com/consumer-api/consumer-assortment/v1`
- `fetch_assortment(venue)` → category tree; `walk_food_categories()`
- `fetch_category_items(venue, slug, language)` → paginated items
- `fetch_item_details(venue, item_ids)` → POST `assortment/items` in batches of 60
- `normalize_item()` → compact record; **prices are in para → divided by 100**.

Normalised catalog entry:

```json
{ "id", "name", "price", "original_price", "discount_pct", "unit_info",
  "grams", "sell_by_weight", "price_per_kg", "top_category", "category",
  "barcode", "description", "image" }
```

`grams` is parsed from `unit_info` (`"300 g"`, `"1,32 l"`, `"1 kg"`, `"150 ml"`;
liquids treated 1 ml ≈ 1 g).

**`maxi_scraper.py`** — scrapes Maxi specifically:

- `DEFAULT_VENUE = "maxi-kralja-milana"`, `CATALOG_FILE = "maxi_catalog.json"`,
  `LANGUAGE = "sr"`.
- `FOOD_LEAVES`: 108 curated food leaf categories (non‑food excluded).
- Output: `{venue, language, scraped_at, categories, items}` (`maxi_catalog.json`,
  git‑ignored, ~3,500 items).

### 4.3 Refresh tools

**`wolt_refresh.py`** — shared machinery:

- `_grams_per_block(ing)` → grams per `min_qty` block; treats `min_qty <= 12`
  with `nutri_std_size > min_qty` as a counted item and returns the std.
- `_pack_units(prod)` → parses `"10/1"`, `"12 kom"` from a product name.
- `_norm_price(product, ing, spec)` — normalises a product price to one block:
  - `unit="grams"` (default): `price * grams_block / grams`
  - `unit="pack"`: `price * min_qty / pack_units`
  - overrides via `spec["grams_block"]`, `spec["wolt_grams"]`, `spec["pack_units"]`.
- `build_report(catalog)` → per‑ingredient old/new price, delta, status
  (`refreshable` / `unmapped` / `remove`), plus a **suspicious‑price guard**
  (unit‑mismatch detection) and duplicate detection.
- `apply_refresh(rows)` → rewrites prices in `ingredient.py`, optionally drops
  missing entries (`--keep-missing` to keep). `dedupe_blocks`,
  `_remove_ingredient_block`, `_replace_ingredient_price`.
- `export_products(catalog, path, dict_name, market, command)` → generates the
  product‑correspondence module.
- `print_candidates()` → suggests new products to add.

**`maxi_refresh.py`** — the Maxi driver, reusing `wolt_refresh` by rebinding its
module globals (`_bind()`), with a hand‑curated `MAXI_MAP`:

```bash
python3 maxi_scraper.py            # -> maxi_catalog.json
python3 maxi_refresh.py report     # report, no writes
python3 maxi_refresh.py apply      # rewrite prices, drop missing
python3 maxi_refresh.py export     # -> maxi_products.py
```

`MAXI_MAP` values: a product **id** (grams basis), a **spec dict**
(`{"id", "grams_block", "wolt_grams", "unit", "pack_units"}`), `None`
(leave unchanged), or `MARK_REMOVE`. Curation rules:

- Cheapest suitable **single‑ingredient** product (no snack mixes / combos).
- Canned legumes preferred where available.
- **Loose produce is priced per‑kg** (`wolt_grams=1000`) with `grams_block` set to
  the grams the ingredient’s block represents (e.g. 3 onions ≈ 675 g).
- **Per‑piece** items (e.g. `Avokado komad`) use `wolt_grams` = piece weight.
- Where Maxi lacks a product, map to the closest single‑ingredient substitute:
  lentils → white beans, chia → flaxseed, rice cakes → crispbread, dried
  pineapple → raisins.

**`maxi_products.py`** — generated, human‑readable `MAXI_PRODUCTS` dict
`name -> (product_id, exact name, pack)`; imported by `ingredient.py`.

> **Empirical note:** for products present in both catalogues, maxi‑via‑Wolt
> prices match `maxi.rs` exactly (52/55 sampled identical, median 0.0 %). Wolt
> does not mark up Maxi shelf prices; differences are assortment (Wolt carries a
> subset) and fees/minimums, not unit price.

### 4.4 SKU / sourcing rule

Every catalogue ingredient maps to a real supermarket product; the test suite
enforces 97/97 coverage (`test_every_ingredient_has_wolt_product`) and that every
meal ingredient is sourced (`test_all_meal_ingredients_are_wolt_sourced`).
Ingredients with no suitable product are removed together with every meal using
them (enforced historically; the current `maxi` branch maps all items).

---

## 5. Simulation engine (`simulation.py`)

### 5.1 `simulate_plan(plan)`

Evaluates a `list[Day]` and returns:

```python
{
  'plan', 'price',                 # grocery subtotal (RSD)
  'total_price',                   # groceries + delivery fees - discounts
  'nutri',                         # average daily Nutrition
  'waste',                         # RSD value of spoiled food
  'delivery_fees', 'delivery_cost', 'delivery_surcharge',
  'discount', 'num_orders'
}
```

**Two‑pool inventory (sealed vs opened).** Per ingredient it keeps:

- `sealed_qty` / `sealed_rot` — unopened packs and their shelf‑life clock
  (`rots_sealed`).
- `opened_qty` / `opened_rot` — currently open portion and its clock (`rots_in`).

For each ingredient needed:

1. Consume from the **opened** pool first.
2. While still short: take a **sealed** pack if one exists, otherwise **buy** a
   fresh pack (`price += ingr.price`); then move one `min_qty` into the opened
   pool.
3. Each simulated day, decrement both clocks; when a clock hits 0 the remaining
   stock is **wasted** (`waste += qty/min_qty * price`).

**Refill days / baskets.** `fastest_rot_arr[i]` = minimum `rots_in` over day `i`’s
ingredients. Refill days are `{0, r0+0, r_{r0}+r0, …}` (cumulative). Spend between
refill days forms one delivery **basket** (`order_subtotals`); the final leftover
spend is a closing basket.

**End‑of‑plan leftovers.** Only **perishable** leftovers count as waste
(`_is_perishable` = opened shelf life `<= PERISHABLE_MAX_OPENED_DAYS`, default 14).
Shelf‑stable stock is carried over, not thrown away.

**Caching.** Results keyed by `hash(tuple(meal names per day))` in `_sim_cache`
(bounded by `PRICE_CACHE_SIZE`); day shelf lives in `_day_rots_cache`. `clear_caches()`
resets both (called when `NO_FRIDGE`/`DELIVERY_ENABLED` change).

`NO_FRIDGE=True` forces both shelf lives to 1 day.

### 5.2 `generate_day(target_nutri, target_mealcount, meals)`

Target‑biased random day construction. For each candidate meal it computes
relative errors in kcal, protein and carb/fat ratio versus per‑meal targets and
samples meals with weight `1 / (kcal_err + prot_err + ratio_err + 0.01)`, until
`target_mealcount` meals (capped at `MAX_MEALS_PER_DAY=7`); random 1–3 if
`target_mealcount <= 0`.

### 5.3 Shopping list

`shopping_list(plan, reach=-1)`:

- Computes `reach` = how many days the first buy covers, from the fastest‑spoiling
  ingredient (`reach` grows while `fastest_rot >= reach`).
- Aggregates needed ingredients over `plan[:reach]`, groups by identity, and emits:

```python
{
  "spisak": [ {"Sastojak", "k", "mk", "required", "maxi"} ... ],  # k=packs to buy
  "cena": <grocery subtotal RSD>,
  "za broj dana": <reach>
}
```

`generate_shopping_list(plan, filename, reach, today)` writes
`plans/<filename>_shopping.txt` with, per shopping trip:

- `LASTS N DAY(S) (start -> end)`
- a **`MAXI ORDER`** block listing `packs x exact product name`
- `Estimated groceries: … RSD`
- the full structured `pformat` dump for tooling
- per‑meal ingredient breakdown with `[Maxi: product]` annotations

---

## 6. Delivery economics (`delivery.py`, `config.py`)

A **basket** is the grocery spend accumulated between stock refills (from
`simulate_plan`). `compute_delivery(order_subtotals)` applies, per non‑empty basket:

1. **Basket discount** — subtract `BASKET_DISCOUNT_AMOUNT` if
   `subtotal >= BASKET_DISCOUNT_MIN`, capped at `BASKET_DISCOUNT_MAX_USES` orders
   (prevents farming the discount by splitting orders).
2. **Order‑minimum surcharge** — add `ORDER_MINIMUM - subtotal` if below the minimum.
3. **Delivery fee** — add `DELIVERY_FEE` unless post‑discount `net >= FREE_DELIVERY_THRESHOLD`.

Returns `DeliveryResult(delivery_fees, delivery_cost, surcharge, discount, num_orders)`.
`total_plan_cost = max(0, groceries + delivery_fees - discount)`.

### 6.1 Defaults (`config.py`)

| Constant | Default | Meaning |
|---|---|---|
| `DELIVERY_ENABLED` | `True` | Include delivery in the objective |
| `ORDER_MINIMUM` | `1500` | RSD minimum order |
| `DELIVERY_FEE` | `119` | RSD flat fee |
| `FREE_DELIVERY_THRESHOLD` | `2500` | RSD for free delivery |
| `BASKET_DISCOUNT_AMOUNT` | `400` | RSD off |
| `BASKET_DISCOUNT_MIN` | `1000` | RSD to unlock discount |
| `BASKET_DISCOUNT_MAX_USES` | `1` | Discount uses per plan |

### 6.2 Route economics (reference)

| Route | Min order | Delivery fee | Notes |
|---|---|---|---|
| Maxi via Wolt (modelled) | 1,500 RSD | ~49–249 RSD | 400 off ≥1,000; subset assortment |
| maxi.rs own site | 3,500 RSD | 199 RSD | promo `QVMZ1000` (1,000 off first order); Delivery+ ~€10/mo; full assortment |

### 6.3 Sealed vs opened shelf‑life heuristics (`ingredient.py`)

`rots_in` is authored per item (opened life). `rots_sealed` is assigned by
category keyword rules (first match wins), floored at `rots_in`:

| Category keywords | `rots_sealed` (days) |
|---|---|
| canned fish / ready meals (`rio mare`, `skusa`, `sardina`, `carnex`, `konzerva`, `tuna`) | 540 |
| dry pantry (grains, pasta, flour, seeds, nuts, oils, legumes, jam, dates, garlic, potato) | 300 |
| frozen (`zamrznut`, `zaledjen`, `smrznut`, `kinezi`, `sladoled`) | 200 |
| dairy / spreads / bread (`jogurt`, `mleko`, `sir`, `puter`, `tofu`, `humus`, `dvopek`, …) | 45 |
| produce / meat / fish / eggs | none (sealed == opened) |

`SEALED_OVERRIDES` can pin an explicit value per ingredient.

---

## 7. Optimiser (`harmony.py` → `HarmonyOptimizer`)

A **Harmony Search** metaheuristic with adaptive parameters, multi‑threading,
elitism, and statlist‑normalised multi‑objective fitness.

### 7.1 State

- `gene_size = plan_len`; each **gene is a `Day`**, each day is a list of meals.
- `goal_nutri`, `target_nutri = [kcal, carb, prot, fat]` derived from
  `kcal, prot, ratio` (`carbfat_kcals = kcal − 4·prot`, split by `ratio`).
- Skip flags: any target `< 0` disables that criterion (`_skip_kcal`, `_skip_prot`,
  `_skip_ratio`, `_skip_mealcount`, `_skip_diversity`).
- `statlists`: running `{kcal, prot, ratio, price, waste, waste_frac, diversity,
  mealcount, consistency, meal_rep, delivery}` used to normalise raw scores to
  `[0,1]` (`raw / max_abs`).
- `fitness_cache`, `generate_day_cache`.

### 7.2 Initialisation

`init_pop(pop_size, gene_size)` — **stratified**: 40 % from ingredient‑masked meal
subsets (for diversity, via `_mask_ingredients()` / `meals_complement`), 60 % from
the full meal list, generated by `generate_chromosome` → `simulate.generate_day`.

### 7.3 Fitness (maximised; less negative = better)

`fitness(sol)` caches by meal‑name hash, runs `simulate_plan`, computes objectives,
and combines **equal‑weighted, statlist‑normalised** penalty terms:

| Term | Raw score | When active |
|---|---|---|
| kcal | `|actual − goal| / goal` | unless skipped |
| prot | `|actual − goal| / goal` | unless skipped |
| ratio | `|actual − goal| / goal` on carb/fat | unless skipped |
| mealcount | `|mean meals − goal| / goal` | unless skipped |
| price | `|price − goal_price| / goal_price` | if `goal_price > 0` |
| waste | `|waste_frac − goal_waste| / goal_waste` | if `goal_waste > 0` |
| diversity | target distance | only if `goal_diversity > 0` **and** below target |
| meal_rep | `1 − unique_meals/total_slots` | always |
| consistency | mean of per‑day `std/mean` over kcal/prot/carb/fat | always |
| delivery | `(fees − discount) / groceries` (clipped ≥ −1) | if `DELIVERY_ENABLED` |
| waste_frac | `waste / groceries` (clipped ≤ 1) | if `WASTE_ENABLED` |

`num_active` counts active terms; `weight = 1/num_active`; total fitness is
`Σ −weight · normalised_score`. The optimiser therefore rewards *low* penalties.

`_soft_constraint_penalty(actual, target, mult=5)` returns 0 inside
`±TOLERANCE` (15 %) else a negative distance penalty.

### 7.4 Search loop (`optimize(time_limit)`)

1. Build harmony memory: `heapq` of `(fitness, solution)` keeping the best N.
2. Spawn `n_threads = os.cpu_count()` worker threads. Each iteration:
   - With prob `HMCR`: **recombine** — for each gene take a day from one random
     memory solution, for each meal slot take the meal from another (**gene‑wise
     crossover**). Else: generate a random chromosome.
   - **Mutation** with prob `mutation_rate`: replace a day with a fresh
     `generate_day` around a perturbed target (`µ=1, σ=0.1`).
   - Evaluate, update global best (thread‑locked), `heappushpop` into memory
     (memory‑locked).
3. Main thread ticks once/second, logs every 10 iterations, and adapts:
   - **Plateau** (no improvement): `HMCR` decays toward `HMCR_MIN`,
     `mutation_rate` grows toward `MUTATION_MAX`.
   - **Improvement**: reset mutation, nudge `HMCR` toward `HMCR_MAX`.
   Resetting `time_limit` on improvement is used as a convergence heuristic.
4. On timeout/`KeyboardInterrupt`, stop threads and return `self.solution`.

`_elitism_selection` keeps `pop_size * ELITE_RATIO` best; `_compute_crowding`
provides an objective‑space distance (used for diversity preservation).

### 7.5 Algorithm parameters (`config.py`)

| Constant | Default |
|---|---|
| `HMCR` / `HMCR_MIN` / `HMCR_MAX` | 0.90 / 0.70 / 0.95 |
| `MUTATION_RATE` / `MUTATION_MAX` | 0.15 / 0.30 |
| `ELITE_RATIO` | 0.10 |
| `TOLERANCE` | 0.15 |
| `DEFAULT_POP_SIZE` | 150 |
| `MAX_MEALS_PER_DAY` | 7 |
| `PRICE_CACHE_SIZE` | 500 |
| `DIST_KCAL_THRESHOLD` | 65 |

### 7.6 Plan generation / persistence

`generate_plan(sol, date_from)` → `[(date, Day), …, price, nutri]`.
`save_plan(filename, sol)` → `plans/<filename>.pickle`.

---

## 8. CLI (`main.py`)

```
bulkbro [--no-fridge] [--no-delivery] <command> [options]

Commands
  run     Run optimisation
  load    Load and display a saved solution
  maxi    Print ingredient -> Maxi product correspondence
  (none)  Interactive mode
```

### 8.1 `run`

```
-d/--days N        days to plan           (default 3)
-m/--meals N       meals/day (-1 = ignore)(default 3)
-k/--kcal N        target kcal/day        (default 2000)
-p/--protein N     target protein (g)     (default 100)
-r/--ratio F       target carb/fat ratio  (default 2.0)
-i/--diversity N   target unique ingredients (default 10)
-t/--time-limit N  seconds                (default 60)
-o/--output NAME   output basename        (default meal_plan)
--pop-size N       population size        (default 150)
--no-fridge        all ingredients spoil in 1 day
--no-delivery      ignore delivery/discounts
```

Output: prints a summary (targets vs achieved, total price, food waste, delivery
breakdown, grand total, variance, shopping duration, first days), saves
`plans/<output>.pickle`, and writes `plans/<output>_shopping.txt`.

### 8.2 `load <solution>`

Loads a pickle, prints price, nutrition, first shopping‑list duration, and the
meals per day.

### 8.3 `maxi [-f TEXT]`

Prints the `ingredient → Maxi product` table (id/name/pack), optionally filtered.

### 8.4 Interactive

Prompts for days, meals, kcal, protein, ratio, fridge/delivery flags, time limit;
then optionally saves.

---

## 9. Outputs & file formats

| Path | Contents |
|---|---|
| `plans/<name>.pickle` | Pickled solution: `list[Day]` |
| `plans/<name>` | Text plan (written by some flows) |
| `plans/<name>_shopping.txt` | Per‑trip shopping list with `LASTS`, `MAXI ORDER`, ingredients |
| `docs/api.md`, `docs/index.html` | Generated API/HTML docs (`docs.py`) |

**`simulate_plan` return schema** and **`shopping_list` schema** are given in §5.1
and §5.3 respectively.

Generated/derived files (git‑ignored): `maxi_catalog.json`, `wolt_catalog.json`,
`plans/*`, `*.pickle`, `*.txt`.

---

## 10. Configuration reference

All tunables live in `config.py` (see §6.1 and §7.5). Notable groups:

- **Defaults:** `DEFAULT_DAYS=3`, `DEFAULT_MEALS_PER_DAY=3`, `DEFAULT_KCAL=2000`,
  `DEFAULT_PROTEIN=100`, `DEFAULT_RATIO=2.0`, `DEFAULT_TIME_LIMIT=60`,
  `DEFAULT_DIVERSITY=10`, `DEFAULT_POP_SIZE=150`.
- **Simulation:** `MAX_MEALS_PER_DAY=7`, `DEFAULT_ROTS_IN=999`,
  `DEFAULT_MIN_QTY=1`, `PRICE_CACHE_SIZE=500`.
- **Delivery:** §6.1.
- **Waste:** `WASTE_ENABLED=True`, `PERISHABLE_MAX_OPENED_DAYS=14`, `NO_FRIDGE=False`.
- **Variance/display:** `VARIANCE_GOOD=10`, `VARIANCE_MODERATE=20`,
  `DAYS_PREVIEW=3`, `PRINT_WIDTH=80`.

---

## 11. Testing

Custom runner: `python3 test_runner.py` (no pytest). **157 tests, 0 known
failures** on `maxi`. Coverage groups:

- Domain model: `Nutrition` arithmetic/distance, `Ingredient` operators,
  `Meal`/`Day` nutrition.
- Simulation: price bounds/accuracy, waste, delivery fields, caching, multi‑day
  averages, pickle round‑trip.
- Optimiser: init, target scoring, skip flags, normalisation range, equal‑weight
  criteria, `statlist`, constraint penalty, no‑meal‑spam regression (stochastic,
  historically flaky ~1–2/15).
- Delivery model: free‑above‑threshold, fee‑below, surcharge, discount & cap,
  fewer‑orders‑cheaper, disabled path.
- Sourcing: every ingredient has a product; every meal ingredient is sourced;
  product id/name/pack present; correspondence survives copies; no zero prices;
  unit‑mismatch guard; shopping list includes product names and the `MAXI ORDER`
  block.

---

## 12. Repository layout

```
main.py            CLI entry point
config.py          All tunables
nutrition.py       Nutrition value object
ingredient.py      Ingredient class + 97-item catalogue + sealed-life heuristics
meal.py / day.py   Meal and Day models
meals.py           Source selection + portion expansion + derived indexes
nikola_meals.py    Meal source: nikola (41)
vegan_meals.py     Meal source: vegan (17)
djina_meals.py     Meal source: djina (25)
insulin_index.py   Food Insulin Index predictor (Bell et al.)
simulation.py      simulate_plan, generate_day, shopping_list
delivery.py        Delivery fees / surcharge / basket discount model
harmony.py         HarmonyOptimizer
util.py            statlist, load_sol
docs.py            Docs generator (HTML + API markdown)
test_runner.py     Test suite (157 tests)

maxi_scraper.py    Scrape Maxi -> maxi_catalog.json
maxi_refresh.py    MAXI_MAP + report/apply/export
maxi_products.py   Generated MAXI_PRODUCTS (name -> id/name/pack)
wolt_scraper.py    Wolt assortment client (shared HTTP helpers)
wolt_refresh.py    Shared refresh machinery (_norm_price, build_report, export)
wolt_products.py   Legacy Wolt correspondence
```

**Branches:** `master`, `wolt`, `maxi` (current), `finer-rotting`, `univerexport`.

---

## 13. Design decisions & known limitations

- **Buying is a greedy, fixed policy:** one `min_qty` pack is bought whenever stock
  runs out. The optimiser does not choose *when* to buy ahead, so stockpiling
  savings do not emerge endogenously; grocery price is largely invariant to plan
  shape apart from pack rounding. Delivery discounts/fees are the main basket‑level
  lever.
- **Basket discounts are capped** (`BASKET_DISCOUNT_MAX_USES=1`) so the search
  cannot farm them by splitting into many tiny orders.
- **Produce unit ambiguity:** unlabeled loose produce is treated as **per‑kg**
  (`wolt_grams=1000`) with explicit `grams_block` overrides; a few per‑piece items
  use `wolt_grams` = piece weight. This is a curated heuristic, not metadata from
  the source.
- **Assortment subset:** the Wolt‑catalog Maxi is a subset of `maxi.rs`; shared
  products are price‑identical, but `maxi.rs` exposes cheaper variants (e.g. a
  93.99 RSD canned chickpea vs the 296.99 one in the Wolt subset).
- **Substitute mappings** are used for four concepts Maxi does not stock
  (lentils→beans, chia→flax, rice cakes→crispbread, dried pineapple→raisins).
- **Stochastic search:** results vary run to run; time‑limited, CPU‑threaded, with
  plateau‑driven parameter adaptation. One regression test is mildly flaky.
- **Nutrition data** is authored per block and preserved across price refreshes
  (scrapers supply prices only).

---

## 14. Extending

- **New ingredient:** add an `Ingredient(...)` entry to `ingredients` in
  `ingredient.py`, then map it in `MAXI_MAP` and run `maxi_refresh.py apply`/`export`.
- **New meal:** add `Meal(name, [ingredients[...] *qty ...], [categories])` to the
  relevant `*_meals.py`; portion variants are generated automatically.
- **New meal source:** create `foo_meals.py` exporting `meals`, register it in
  `MEALS` in `meals.py`, then `set_meal_source('foo')`.
- **New objective:** add a `statlist` entry, compute a raw score in `fitness`,
  normalise it, include it in `num_active` and the weighted sum.
- **New market:** subclass/reuse `wolt_scraper` for the venue, add a
  `<market>_refresh.py` mirroring `maxi_refresh.py` with a curated map, and point
  `ingredient.py` at the generated products module.
- **Different fee schedule:** edit constants in `config.py` (a second delivery
  profile — e.g. maxi.rs’s 3,500 minimum / 199 fee / promo — can be modelled by
  swapping `ORDER_MINIMUM`, `DELIVERY_FEE`, `FREE_DELIVERY_THRESHOLD`, and
  discount constants).

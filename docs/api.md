# BulkBro API Reference


## Module: config


## Module: day

### Class: Day

Represents a day containing multiple meals.

**Parameters**
----------
meals : list
    List of Meal objects


## Module: delivery

### Class: DeliveryResult

Breakdown of delivery-related costs for a plan.

**Parameters**
----------
delivery_fees : float
    Total delivery fees plus order-minimum surcharges (RSD). Total delivery fees plus order-minimum surcharges (RSD).
delivery_cost : float
    Portion of ``delivery_fees`` that is pure delivery fees. Portion of ``delivery_fees`` that is pure delivery fees.
surcharge : float
    Portion of ``delivery_fees`` from order-minimum shortfalls. Portion of ``delivery_fees`` from order-minimum shortfalls.
discount : float
    Total promotional discount applied to baskets (RSD, positive). Total promotional discount applied to baskets (RSD, positive).
num_orders : int
    Number of delivery orders (baskets) simulated.

### Function: compute_delivery()

Compute delivery fees and discounts for a list of order baskets. Each element of ``order_subtotals`` is the grocery subtotal (RSD) of one delivery. The function applies, per basket: 1. **Basket discount** - subtract ``config.BASKET_DISCOUNT_AMOUNT`` when the subtotal is at least ``config.BASKET_DISCOUNT_MIN``. 2. **Order-minimum surcharge** - add the shortfall when the subtotal is below ``config.ORDER_MINIMUM``. 3. **Delivery fee** - add ``config.DELIVERY_FEE`` unless the (post-discount) subtotal reaches ``config.FREE_DELIVERY_THRESHOLD``.

**Parameters**
----------
order_subtotals : iterable of float
    Grocery subtotal of each order in RSD. Grocery subtotal of each order in RSD. DeliveryResult DeliveryResult Aggregated delivery breakdown. Aggregated delivery breakdown.

### Function: total_plan_cost()

Return total plan cost = groceries + delivery - discounts.

**Parameters**
----------
grocery_subtotal : float
    Sum of grocery prices in RSD. Sum of grocery prices in RSD. delivery : DeliveryResult
delivery : DeliveryResult
    Delivery breakdown from :func:`compute_delivery`.
Delivery breakdown from : func:`compute_delivery`.
    float float Total cost in RSD (never negative). Total cost in RSD (never negative).


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

Get daily nutrition from Day's internal cache.

### Function: simulate_plan()

Simulate a meal plan and return costs, nutrition, waste. Args: plan: List of Day objects

**Returns**
-------
Dict with 'plan', 'price', 'nutri', 'waste', 'delivery_fees'

### Function: generate_day()

Generate a day with target-biased meal selection. Meals closer to per-meal nutrition targets get higher selection weight.

**Parameters**
----------
target_nutri : list
    [kcal, carb, prot, fat] target values [kcal, carb, prot, fat] target values target_mealcount : int
target_mealcount : int
    Desired meals per day (-1 to ignore, uses random 1-5) Desired meals per day (-1 to ignore, uses random 1-5) meals : list
meals : list
    Meal database to choose from Meal database to choose from Day Day Day with reasonable meal count (1-7) Day with reasonable meal count (1-7)

### Function: shopping_list()

Generate shopping list for a plan.

### Function: clear_caches()

Clear simulation caches (call when config flags change that affect simulation).

### Function: generate_shopping_list()

Generate and save shopping list to file.


## Module: util

### Class: statlist

### Function: load_sol()

Load a solution from pickle file.


## Module: vegan_meals


## Module: wolt_refresh

### Function: _grams_per_block()

Grams represented by one ``min_qty`` block of an ingredient. BulkBro is ambiguous: for most ingredients ``min_qty`` is already grams, but for counted items (bananas, eggs, cans) ``min_qty`` is a piece count and ``nutri_std_size`` holds the gram weight of that block. The heuristic below treats small counts (``min_qty <= 12``) whose ``std`` is heavier than ``min_qty`` as counted items; everything else is grams.

### Function: _pack_units()

Best-effort piece count for a pack item with no gram size. Parses patterns like ``"10/1"`` or ``"12 kom"`` from the product name.

### Function: _norm_price()

Price of one ``min_qty`` block of ``ing`` at the Wolt product price. Two normalization modes are supported via the mapping ``spec``: - ``unit == "grams"`` (default): both sides are converted to grams. The Wolt pack has ``grams`` at ``price`` RSD, so the price of one ``min_qty`` block is ``price * grams_block / grams``. ``grams_block`` defaults to the ingredient's ``nutri_std_size`` (grams per ``min_qty`` block) and can be overridden with ``spec["grams_block"]``. - ``unit == "pack"``: the Wolt item is a multi-pack of ``pack_units`` identical pieces (default parsed from the name). The price scales by ``min_qty / pack_units``.

**Parameters**
----------
product : dict
    Normalized Wolt catalog entry. Normalized Wolt catalog entry. ing : Ingredient
ing : Ingredient
    Existing BulkBro ingredient. Existing BulkBro ingredient. spec : dict
spec : dict
    Mapping spec, may carry ``unit`` / ``grams_block`` / ``pack_units`` / Mapping spec, may carry ``unit`` / ``grams_block`` / ``pack_units`` / ``wolt_grams`` overrides. ``wolt_grams`` overrides. float or None float or None Normalized price in RSD, or ``None`` if it cannot be computed. Normalized price in RSD, or ``None`` if it cannot be computed.

### Function: build_report()

Compute a per-ingredient refresh report.

**Parameters**
----------
catalog : dict
    Parsed ``wolt_catalog.json``. Parsed ``wolt_catalog.json``. list of dict list of dict One entry per current ingredient with old/new price and status. One entry per current ingredient with old/new price and status.

### Function: print_report()

Print the refresh report in a readable table.

### Function: _remove_ingredient_block()

Remove an ingredient entry (dict literal) from the source text. Matches ``"name": Ingredient(...),`` including trailing comma and the surrounding whitespace, deleting the whole entry.

**Returns**
-------
tuple of (str, int) ``(new_source, count_removed)``.

### Function: dedupe_blocks()

Remove duplicate ingredient entries, keeping the first occurrence. BulkBro's ingredient dict silently overwrites duplicate keys, so duplicate ``Ingredient`` entries are dead code. This deletes every duplicate block after the first.

**Returns**
-------
tuple of (str, int) ``(new_source, duplicates_removed)``.

### Function: apply_refresh()

Write refreshed prices (and remove missing items) into ingredient.py. Only ``ok`` rows with a computed ``new_price`` are applied. When ``remove_missing`` is true, ``remove`` rows are deleted from the file. The file is rewritten in place.

**Parameters**
----------
rows : list of dict
    Output of :func:`build_report`.
Output of : func:`build_report`.
    source_path : str, optional
source_path : str, optional
    Path to ``ingredient.py``. Path to ``ingredient.py``. remove_missing : bool, optional
remove_missing : bool, optional
    Whether to delete entries marked for removal. Whether to delete entries marked for removal. tuple of (int, int) tuple of (int, int) ``(prices_changed, entries_removed)``. ``(prices_changed, entries_removed)``.

### Function: print_candidates()

Print notable Wolt products not yet in the BulkBro catalog. Lists available food products sorted by protein-per-100g where known, to suggest new ingredient candidates for the catalog.

### Function: _replace_ingredient_price()

Replace the numeric price for ``name`` in the ingredient.py source text. Matches the pattern:: "name": Ingredient( "name", <price>, ...

### Function: main()

Command-line entry point.


## Module: wolt_scraper

### Function: _get()

Perform a GET request and return parsed JSON.

**Parameters**
----------
url : str
    Full URL to request. Full URL to request. retries : int, optional
retries : int, optional
    Number of retries on transient failure. Number of retries on transient failure. timeout : int, optional
timeout : int, optional
    Timeout in seconds. Timeout in seconds. dict dict Parsed JSON response. Parsed JSON response.

### Function: _post()

Perform a POST request with a JSON body and return parsed JSON.

### Function: fetch_assortment()

Fetch the top-level assortment (category tree) for a venue.

**Parameters**
----------
venue : str, optional
    Venue slug. Venue slug. language : str, optional
language : str, optional
    Menu language code. Menu language code. dict dict Raw assortment with a ``categories`` tree. Raw assortment with a ``categories`` tree.

### Function: walk_food_categories()

Return leaf food categories as ``(top_name, slug, name)`` tuples. Walks the category tree, keeping only categories under :data:`FOOD_CATEGORY_SLUGS`. Non-leaf categories are expanded.

**Parameters**
----------
assortment : dict
    Result of :func:`fetch_assortment`.
Result of : func:`fetch_assortment`.
    list of tuple list of tuple ``(top_name, leaf_slug, leaf_name)`` entries. ``(top_name, leaf_slug, leaf_name)`` entries.

### Function: fetch_category_items()

Fetch all items (with pagination) for a leaf category.

**Parameters**
----------
venue : str
    Venue slug. Venue slug. category_slug : str
category_slug : str
    Leaf category slug. Leaf category slug. language : str, optional
language : str, optional
    Menu language code. Menu language code. list of dict list of dict Item records as returned inline by the category endpoint. Item records as returned inline by the category endpoint.

### Function: fetch_item_details()

Bulk-fetch full item records by ID.

**Parameters**
----------
venue : str
    Venue slug. Venue slug. item_ids : iterable of str
item_ids : iterable of str
    Item IDs to fetch. Item IDs to fetch. language : str, optional
language : str, optional
    Menu language code. Menu language code. batch : int, optional
batch : int, optional
    Number of IDs per POST. Number of IDs per POST. dict dict Mapping ``item_id -> item record``. Mapping ``item_id -> item record``.

### Function: _unit_grams()

Best-effort conversion of ``unit_info`` text to grams. Wolt unit strings look like ``"300 g"``, ``"1,32 l"``, ``"1 kg"``, ``"150 ml"``. Returns grams for solids and millilitres for liquids (treated as 1:1 for catalog purposes), or ``None`` if unknown.

### Function: normalize_item()

Convert a raw Wolt item record to a compact catalog entry. Prices from the API are in *para* (1 RSD = 100 para); this converts to RSD.

**Parameters**
----------
item : dict
    Raw item record. Raw item record. top_name : str
top_name : str
    Top-level category name. Top-level category name. leaf_name : str
leaf_name : str
    Leaf category name. Leaf category name. dict dict Normalized catalog entry. Normalized catalog entry.

### Function: scrape()

Scrape the full food catalog of a Wolt Market venue.

**Parameters**
----------
venue : str, optional
    Venue slug. Venue slug. language : str, optional
language : str, optional
    Menu language code. Menu language code. verbose : bool, optional
verbose : bool, optional
    Print progress. Print progress. dict dict ``{"venue": ..., "scraped_at": ..., "categories": [...], ``{"venue": ..., "scraped_at": ..., "categories": [...], "items": [...]}`` with normalized item entries. "items": [...]}`` with normalized item entries.

### Function: main()

Command-line entry point.


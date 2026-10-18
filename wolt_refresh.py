"""Refresh BulkBro ingredients against a live Wolt Market catalog.

This tool bridges :mod:`wolt_scraper` (which produces ``wolt_catalog.json``)
and :mod:`ingredient`. For each ingredient in the current catalog it looks up a
curated Wolt product, computes the price normalized to the ingredient's
``min_qty``, and reports the delta. Ingredients that are no longer sold are
flagged for removal, and a list of candidate new products is produced.

Workflow
--------
1. ``python3 wolt_scraper.py``            # produce wolt_catalog.json
2. ``python3 wolt_refresh.py report``     # human-readable price/availability report
3. ``python3 wolt_refresh.py apply``      # rewrite ingredient.py prices in place

The mapping (:data:`WOLT_MAP`) is curated by hand because Wolt product names do
not match BulkBro's internal names and nutrition data is not available from
Wolt (nutrition is preserved from the existing ingredient records).

Note on units: Wolt returns prices in *para* (the scraper converts to RSD) and a
pack size (``grams`` in grams / ml). BulkBro ingredients store a ``price`` for
``min_qty`` grams. To compare fairly we convert the Wolt pack to a price per
``min_qty`` grams:

    new_price(min_qty) = wolt_pack_price * min_qty / wolt_pack_grams

For counted items (eggs, tortillas) ``min_qty`` is a piece count and we use a
``pieces`` basis in the map.
"""

import argparse
import json
import re
import sys

from ingredient import ingredients

CATALOG_FILE = "wolt_catalog.json"
INGREDIENT_FILE = "ingredient.py"
PRODUCTS_FILE = "wolt_products.py"

# =============================================================================
# Curated mapping: BulkBro ingredient name -> Wolt product id (+ basis)
# =============================================================================
# ``basis`` is one of:
#   "grams"  - Wolt item has a gram/ml size; normalize price to min_qty grams
#   "pieces" - Wolt item is a pack of counted pieces; min_qty is a piece count
#
# When a value is a string it is treated as a product id with basis "grams".
# When it is ``None`` the ingredient is intentionally left unchanged.
# ``MARK_REMOVE`` items are no longer sold on Wolt Market.
MARK_REMOVE = object()

WOLT_MAP = {
    # ---- nuts / seeds -----------------------------------------------------
    "kikiriki": "637b786c880553d6340e1ce4",            # Kikiriki pečeni slani 180g
    "kikiriki svetofor": "62f3bc0b3b1a7a65f0a13489",   # Kikiriki prženi vakum Fun&Fit 250g
    "badem": "62f3bc0b3b1a7a65f0a134b0",               # Badem sirovi Jumbo Fun&Fit 75g (raw, cheapest/kg)
    "badem svetofor": "62f3bc0b3b1a7a65f0a134b0",
    "suncokret": "d9fd028fa9c66488c8e176b0",           # Colonial Suncokret oljušteni 100g
    "orah": None,                                     # no plain walnut kernels on this venue (only cookie/oil/spread)
    "indijski orah": "62f3bc0b3b1a7a65f0a13458",       # Indijski orah prženi Jumbo 75g
    "kikiriki puter dm": "fa50bf247e93a942b72deb1f",   # Well Kikiriki puter crunchy 500g (cheapest/kg)
    "kinoa": "98c4cdb0557a5c6d63dc6f8e",               # Kinoa bela BIO 200g
    "chia semenke maxi": "68751e4bedff0b60df2bcff8",   # Čia Colonial 200g
    "lanene semenke": "66471ddac67bc77287dbca2a",      # Laneno seme BIO 200gr
    "leblebije maxi": "62f3bc0b3b1a7a65f0a132cf",      # Leblebija kuvana Benlian Food 480g (canned)

    # ---- carbs / grains / pasta ------------------------------------------
    "ovsene pahuljice": "055c2b65629346bb3e308cd2",    # Pahuljice ovsene 500g
    "ovsene svetofor 500g": "055c2b65629346bb3e308cd2",
    "pirinac 1kg": "62f3bc0c3b1a7a65f0a1377f",         # Pirinač basmati Riso Scotti 500g
    "pirinac svetofor": "62f3bc0c3b1a7a65f0a1377f",   # Pirinač basmati Riso Scotti 500g
    "braon pirinac 500g": "c827c784c26f49666c0e1755",  # Pirinac jasmin integralni BIO 200g
    "palenta svetofor": "62f3bc0d3b1a7a65f0a139da",    # Palenta instant Oetker 500g
    "pasta 500g": "62f3bc0c3b1a7a65f0a13749",          # Testenina fusilli Barilla 500g
    "integralna pasta": "62f3bc0c3b1a7a65f0a13749",    # Testenina fusilli Barilla 500g
    "posne makarone svetofor": "62f3bc0c3b1a7a65f0a13749",
    "socivo pasta": "5b80050e32aec69ba3da06f3",        # Colonial Socivo zeleno 500g
    "tortilja 8": {"id": "3a9c19e243121812cabb639a", "unit": "pack", "pack_units": 12},  # Tortilje 12 kom

    # ---- veg / legumes ----------------------------------------------------
    "pasulj beli svetofor 1kg": "e52b26187337d3c3d22919f7",  # Beli pasulj Podravka 400g (canned)
    "pasulj": "e52b26187337d3c3d22919f7",
    "pasulj konzerva": "e52b26187337d3c3d22919f7",     # Beli pasulj Podravka 400g
    "zamrznuti grasak svetofor 1kg": "635fb87089302d314cc99498",  # Grašak Frikom 700g
    "zaledjeni grasak": "642ffb1e8cd31a36cef315a7",     # Grašak Polar Food 400g
    "carnex posni pasulj": {"id": "62f3bc0c3b1a7a65f0a1393b", "grams_block": 400},  # Prego Pasulj posno 400g (1 can)
    "carnex posni grasak": {"id": "635fb87089302d314cc99498", "grams_block": 700},  # Grašak Frikom 700g (1 pack)
    "zamrznuti spanac": "642ffb1e8cd31a36cef315b0",     # Spanać list u briketu Polar Food 400g
    "zaledjeni spanac": "642ffb1e8cd31a36cef315b0",
    "spanać svez": "67063a58899bf17360277b71",         # Baby spanać 90g
    "najlepse zelje": {"id": "7c33562a35bcade7781a6267", "grams_block": 42},  # Čokolada Lion white 42g (closest snack bar)
    "krompir": "634d6dca4de9349f1a00650f",             # Krompir beli opran 1kg (cheapest/kg)
    "krompir svetofor": "634d6dca4de9349f1a00650f",    # Krompir beli opran 1kg (cheapest/kg)
    "batat kom": {"id": "62f3bc0c3b1a7a65f0a13858", "grams_block": 600},  # Batat 1kg (block ~3 batats)
    "crni luk kom": "62f3bc0c3b1a7a65f0a1383b",        # Luk crni ~500 g
    "crni luk svetofor": "62f3bc0c3b1a7a65f0a1383b",
    "crveni luk kom": {"id": "2deed0ea4819021edf75df30", "grams_block": 675},  # Luk crveni ~500 g (block 3 pcs)
    "beli luk": {"id": "75c17367e77da4fb93afb4e1", "wolt_grams": 250},  # Beli Luk Pak 250g
    "kupus": {"id": "641d8d38ce2c818415144f89", "wolt_grams": 1000},  # Kupus beli glavica ~1000 g
    "crveni kupus kom": "634403bd035b6871583871f0",    # Kupus ljubičasti 1kg
    "sargarepa kom": {"id": "62f3bc0c3b1a7a65f0a13837", "grams_block": 392},  # Šargarepa 500g (block 4 pcs)
    "cvekla kom": {"id": "63297d265d8854fef2de93d2", "grams_block": 440},  # Cvekla ~500 g (block 4 pcs)
    "patlidzan": {"id": "62f3bc0c3b1a7a65f0a1384d", "wolt_grams": 1000},  # Patlidžan 1kg
    "brokoli": "642ffb1e8cd31a36cef315aa",             # Brokoli Polar Food 400g
    "pecurke": "63297d265d8854fef2de93ee",             # Šampinjoni tacna 400g (fresh)
    "kinezi miks": "652fcf8865146680ba5e734a",       # Mešavina povrća 4 godišnja doba Frikom 400g
    "smrznuti miks": "652fcf8865146680ba5e734a",      # Mešavina povrća 4 godišnja doba Frikom 400g
    "borovnice": "64746bc8d826cfbe29e21035",           # Borovnica Polar Food 300g
    "pomorandza": {"id": "62f3bc0c3b1a7a65f0a137e4", "grams_block": 200},  # Pomorandža ~1000 g (1 orange ~200 g)
    "ananas": {"id": "347cf55b70d2d5bfe4adba89", "wolt_grams": 1000},  # Ananas baby 1kom (fresh whole pineapple)
    "avokado": {"id": "62f3bc0c3b1a7a65f0a13811", "wolt_grams": 215},  # Avokado 1kom (single, cheapest)
    "rukola": "68c9111b3b54e1ed3a431508",              # Rukola 90g
    "banana": "62f3bc0c3b1a7a65f0a1384c",              # Banana, ~1000 g (regular, cheapest)
    "jabuka": {"id": "62f3bc0c3b1a7a65f0a137fd", "grams_block": 150},  # Jabuka Zlatni delišes ~500 g (cheapest/kg)

    # ---- dairy / eggs -----------------------------------------------------
    "jaja 10kom": {"id": "62f3bc0b3b1a7a65f0a132c0", "unit": "pack", "pack_units": 10},  # Jaja M 10/1
    "jaje": {"id": "62f3bc0b3b1a7a65f0a132c0", "unit": "pack", "pack_units": 10},
    "mleko": "65f2fcb88998c58ded7966ea",               # Sveže mleko 2.8% Moja Kravica D3 PET 1.75l (cheapest/kg)
    "jogurt": "65f2fcb88998c58ded7966ec",              # Jogurt Kravica 2.8% 1.75kg PET (cheapest/kg)
    "kiselo mleko": "62f3bc0b3b1a7a65f0a13298",        # Mleko kiselo 2.8%mm Moja Kravica 400g (cheapest/kg)
    "kefir casa": {"id": "6581a5e22330911ef4c02261", "grams_block": 180},  # Kefir 2.8% 1kg (1 cup ~180 g)
    "grcki jogurt olimpus": "62f3bc0d3b1a7a65f0a13ac0",  # Jogurt Grekos 9% 400g
    "zott jogurt": {"id": "62f3bc0b3b1a7a65f0a13502", "grams_block": 115},  # Jogurt voćni Zottis 115g
    "dukatos": "6413243c0e20de17e4904e26",             # Jogurt natur Dukatos 400g
    "zbregov": "67594de8764fcdaf647be705",             # Zbregov protein 500ml
    "puter": "62f3bc0b3b1a7a65f0a13273",               # Maslac Moja Kravica 125g
    "stari sir": "ede9acb14d0c2cc51b0bd189",           # Hans Gauda komad 250g

    # ---- meat / fish ------------------------------------------------------
    "pilece belo 100g": "67b85803950497fd04d3a0b2",    # Pilece grudi u omotu 350g
    "pileca prsa 8": {"id": "67b85803950497fd04d3a0b2", "unit": "pack", "pack_units": 8},
    "pastrmka": {"id": "6489cdc16c6d8c7d4ddda344", "grams_block": 200},  # Filet lososa 200g (closest fresh fish)
    "sardina": "b416d830eb7861fcc86a0471",             # Eva sardina u biljnom ulju 100g
    "skusa eva 170g": "24e58b429855275244b4ec22",      # Skuša fileti 125g
    "skusa la perla": "24e58b429855275244b4ec22",
    "rio mare tuna": {"id": "62f3bc0b3b1a7a65f0a1338b", "grams_block": 160},  # Tunjevina Rio Mare 160g
    "rio mare kuskus": {"id": "62f3bc0b3b1a7a65f0a13341", "grams_block": 160},  # Tunjevina salata kus kus 160g

    # ---- pantry / sauces --------------------------------------------------
    "maslinovo ulje": "6618ff4a56a12eb63a6f1762",      # Fontoliva Extra Devičansko Maslinovo Ulje 1L (cheapest EVOO/kg)
    "pasirani paradajz": "e5646b5bc8719ea0a31817a8",   # Pasirani paradajz 500g
    "pasirani paradajz svetofor": "e5646b5bc8719ea0a31817a8",
    "dzem dm": "67efb20568fdca5c47058568",             # Džem jagoda Bakina tajna 375g
    "dvopek": "62f3bc0c3b1a7a65f0a1367d",              # Dvopek Mulino fette 315g
    "fitnes hleb": "62f3bc0c3b1a7a65f0a13740",         # Hleb Tonus 300g
    "humus": "62f3bc0b3b1a7a65f0a13399",               # Hummus natural Ribella 200g (straight hummus, not Grab&go combo)
    "sojino mleko": {"id": "62f3bc0b3b1a7a65f0a133b3", "wolt_grams": 1000},  # Napitak od soje bez šećera i soli Alpro 1l (plain unsweetened soy milk)
    "urme": "63aeb20d48e3846acfe56a9f",                  # Suva urma organska 200g
    "urme svetofor": "63aeb20d48e3846acfe56a9f",         # Suva urma organska 200g
    "tofu 250g pak": "64e36559c094baaeb1df27e6",       # Tofu natural Joya 250g
    "kokice": "62f3bc0c3b1a7a65f0a139ae",              # Kukuruz kokičar Fun&Fit 200g (popcorn kernels, not ready-salted popcorn)
    "heidi": "d7763a5f8bcb1b92a183489a",                # Čokolada mlečna Galeb 80g (closest to Heidi)
    "sladoledi 10kom": {"id": "84d8e9ac216e9acdbf1af813", "unit": "pack", "pack_units": 10},  # Sladoled F&C Vanila 120g (single)
    "rajs kejk": {"id": "62f3bc0b3b1a7a65f0a13289", "grams_block": 100},  # Galete pirinač natural Rice Cakes 100g

    # ---- ingredients restored for the Wolt-period meal set ----------------
    "golica": "83bbbd3ca8e6d1d8484d7095",              # Golica sirova 500g
    "socivo": "5b80050e32aec69ba3da06f3",             # Colonial Socivo zeleno 500g
    "seme bundeve": "67e1a1846bf9b03d44047ec0",       # Semenke bundeve Jumbo 150g (cheapest/kg)
    "jumbo mix": "62f3bc0c3b1a7a65f0a135fe",          # Protein Mix Jumbo 75g
    "nutrino labs sok": {"id": "6684080a9065eb9c27df67c1", "grams_block": 500},  # Sok Rock multivitamin 500ml (1 bottle)
    "paradajz": {"id": "62f3bc0c3b1a7a65f0a137ff", "grams_block": 140},  # Paradajz čeri 500g (fresh cherry tomato)
}


def _grams_per_block(ing):
    """Grams represented by one ``min_qty`` block of an ingredient.

    BulkBro is ambiguous: for most ingredients ``min_qty`` is already grams,
    but for counted items (bananas, eggs, cans) ``min_qty`` is a piece count and
    ``nutri_std_size`` holds the gram weight of that block. The heuristic below
    treats small counts (``min_qty <= 12``) whose ``std`` is heavier than
    ``min_qty`` as counted items; everything else is grams.
    """
    std = getattr(ing, "nutri_std_size", None)
    if ing.min_qty <= 12 and std and std > ing.min_qty:
        return std
    return ing.min_qty


def _pack_units(prod):
    """Best-effort piece count for a pack item with no gram size.

    Parses patterns like ``"10/1"`` or ``"12 kom"`` from the product name.
    Returns 1 when unknown (treat as a single block).
    """
    name = prod["name"]
    m = re.search(r"(\d+)\s*/\s*1\b", name)
    if m:
        return int(m.group(1))
    m = re.search(r"(\d+)\s*kom", name, re.IGNORECASE)
    if m:
        return int(m.group(1))
    return 1


def _norm_price(product, ing, spec):
    """Price of one ``min_qty`` block of ``ing`` at the Wolt product price.

    Two normalization modes are supported via the mapping ``spec``:

    - ``unit == "grams"`` (default): both sides are converted to grams. The
      Wolt pack has ``grams`` at ``price`` RSD, so the price of one ``min_qty``
      block is ``price * grams_block / grams``. ``grams_block`` defaults to the
      ingredient's ``nutri_std_size`` (grams per ``min_qty`` block) and can be
      overridden with ``spec["grams_block"]``.
    - ``unit == "pack"``: the Wolt item is a multi-pack of ``pack_units``
      identical pieces (default parsed from the name). The price scales by
      ``min_qty / pack_units``.

    Parameters
    ----------
    product : dict
        Normalized Wolt catalog entry.
    ing : Ingredient
        Existing BulkBro ingredient.
    spec : dict
        Mapping spec, may carry ``unit`` / ``grams_block`` / ``pack_units`` /
        ``wolt_grams`` overrides.

    Returns
    -------
    float or None
        Normalized price in RSD, or ``None`` if it cannot be computed.
    """
    unit = spec.get("unit", "grams")

    if unit == "pack":
        pack_units = spec.get("pack_units") or _pack_units(product)
        if pack_units <= 0:
            return None
        return round(product["price"] * ing.min_qty / pack_units, 2)

    grams_block = spec.get("grams_block") or _grams_per_block(ing)
    wolt_grams = spec.get("wolt_grams") or product.get("grams")
    if not wolt_grams:
        # Fall back to pack handling when the Wolt item has no gram size.
        pack_units = spec.get("pack_units") or _pack_units(product)
        if pack_units <= 0:
            return None
        return round(product["price"] * ing.min_qty / pack_units, 2)
    return round(product["price"] * grams_block / wolt_grams, 2)


def build_report(catalog):
    """Compute a per-ingredient refresh report.

    Parameters
    ----------
    catalog : dict
        Parsed ``wolt_catalog.json``.

    Returns
    -------
    list of dict
        One entry per current ingredient with old/new price and status.
    """
    items = catalog["items"]
    by_id = {it["id"]: it for it in items}
    rows = []
    for name, ing in ingredients.items():
        spec = WOLT_MAP.get(name, None)
        row = {
            "name": name,
            "old_price": ing.price,
            "min_qty": ing.min_qty,
            "status": "unmapped",
            "wolt_name": None,
            "wolt_price": None,
            "new_price": None,
            "delta_pct": None,
        }
        if spec is MARK_REMOVE:
            row["status"] = "remove"
            rows.append(row)
            continue
        if spec is None:
            rows.append(row)
            continue
        if isinstance(spec, dict):
            pid = spec["id"]
        else:
            pid = spec
            spec = {}
        prod = by_id.get(pid)
        if not prod:
            row["status"] = "missing_id"
            rows.append(row)
            continue
        new_price = _norm_price(prod, ing, spec)
        row["wolt_name"] = prod["name"]
        row["wolt_price"] = prod["price"]
        row["new_price"] = new_price
        if new_price is not None and ing.price:
            row["delta_pct"] = round((new_price - ing.price) / ing.price * 100, 1)
            # Guard against unit mis-normalization: a mapped item whose price
            # collapses to a tiny fraction of the old one almost always means a
            # grams-vs-pack unit mismatch (e.g. min_qty=1 mapped to a gram item).
            # Flag it for manual review instead of silently writing a bogus price.
            if new_price <= 0 or new_price < ing.price * 0.05:
                row["status"] = "suspicious"
                rows.append(row)
                continue
        row["status"] = "ok" if new_price is not None else "no_size"
        rows.append(row)
    return rows


def print_report(rows):
    """Print the refresh report in a readable table."""
    ok = [r for r in rows if r["status"] == "ok"]
    remove = [r for r in rows if r["status"] == "remove"]
    unmapped = [r for r in rows if r["status"] in ("unmapped", "missing_id", "no_size")]
    suspicious = [r for r in rows if r["status"] == "suspicious"]

    print("=" * 100)
    print("WOLT MARKET CATALOG REFRESH REPORT")
    print("=" * 100)
    print(f"{'ingredient':32} {'old':>9} {'new':>9} {'Δ%':>8}  wolt product")
    print("-" * 100)
    for r in sorted(ok, key=lambda x: (x["delta_pct"] is None, -abs(x["delta_pct"] or 0))):
        np_ = "?" if r["new_price"] is None else f"{r['new_price']:.0f}"
        dp = "" if r["delta_pct"] is None else f"{r['delta_pct']:+.0f}%"
        print(f"{r['name'][:32]:32} {r['old_price']:>9.0f} {np_:>9} {dp:>8}  {r['wolt_name'][:44]}")

    print("\n" + "-" * 100)
    print(f"UNMAPPED / NEEDS DECISION ({len(unmapped)}):")
    for r in unmapped:
        print(f"  [{r['status']}] {r['name']}")

    print(f"\nNO LONGER ON WOLT - REMOVE ({len(remove)}):")
    for r in remove:
        print(f"  {r['name']}")

    print(f"\nSUSPICIOUS PRICE (unit mismatch, not applied) ({len(suspicious)}):")
    for r in suspicious:
        print(f"  {r['name']}: {r['old_price']:.0f} -> {r['new_price']} ({r['wolt_name']})")

    print("\n" + "=" * 100)
    print(f"Summary: {len(ok)} refreshable, {len(remove)} remove, "
          f"{len(unmapped)} unmapped, {len(suspicious)} suspicious")
    print("=" * 100)


def _remove_ingredient_block(source, name):
    """Remove an ingredient entry (dict literal) from the source text.

    Matches ``"name": Ingredient(...),`` including trailing comma and the
    surrounding whitespace, deleting the whole entry.

    Returns
    -------
    tuple of (str, int)
        ``(new_source, count_removed)``.
    """
    pattern = re.compile(
        r'\n[ \t]*"' + re.escape(name) + r'"\s*:\s*Ingredient\(.*?\n[ \t]*\),',
        re.DOTALL,
    )
    new_src, n = pattern.subn("", source)
    return new_src, n


def dedupe_blocks(source):
    """Remove duplicate ingredient entries, keeping the first occurrence.

    BulkBro's ingredient dict silently overwrites duplicate keys, so duplicate
    ``Ingredient`` entries are dead code. This deletes every duplicate block
    after the first.

    Returns
    -------
    tuple of (str, int)
        ``(new_source, duplicates_removed)``.
    """
    block_re = re.compile(
        r'\n[ \t]*"([^"]+)"\s*:\s*Ingredient\(.*?\n[ \t]*\),',
        re.DOTALL,
    )
    seen = set()
    removed = 0
    out = []
    last = 0
    for m in block_re.finditer(source):
        name = m.group(1)
        out.append(source[last:m.start()])
        if name in seen:
            removed += 1
            # Drop the duplicate block entirely.
        else:
            seen.add(name)
            out.append(m.group(0))
        last = m.end()
    out.append(source[last:])
    return "".join(out), removed


def apply_refresh(rows, source_path=INGREDIENT_FILE, remove_missing=True):
    """Write refreshed prices (and remove missing items) into ingredient.py.

    Only ``ok`` rows with a computed ``new_price`` are applied. When
    ``remove_missing`` is true, ``remove`` rows are deleted from the file.
    The file is rewritten in place.

    Parameters
    ----------
    rows : list of dict
        Output of :func:`build_report`.
    source_path : str, optional
        Path to ``ingredient.py``.
    remove_missing : bool, optional
        Whether to delete entries marked for removal.

    Returns
    -------
    tuple of (int, int)
        ``(prices_changed, entries_removed)``.
    """
    with open(source_path, encoding="utf-8") as f:
        source = f.read()

    changed = 0
    for r in rows:
        if r["status"] != "ok" or r["new_price"] is None:
            continue
        source, n = _replace_ingredient_price(source, r["name"], r["new_price"])
        if n:
            changed += 1

    removed = 0
    if remove_missing:
        for r in rows:
            if r["status"] != "remove":
                continue
            source, n = _remove_ingredient_block(source, r["name"])
            removed += n

    source, dups = dedupe_blocks(source)

    with open(source_path, "w", encoding="utf-8") as f:
        f.write(source)
    return changed, removed, dups


def print_candidates(catalog, limit=40):
    """Print notable Wolt products not yet in the BulkBro catalog.

    Lists available food products sorted by protein-per-100g where known, to
    suggest new ingredient candidates for the catalog.
    """
    existing_grams = {}  # name -> grams, so we can value-match
    try:
        for name, ing in ingredients.items():
            existing_grams[name] = _grams_per_block(ing)
    except Exception:
        pass

    # Food categories most relevant for meal planning.
    wanted = {
        "Meso i riba", "Jaja, sir i namazi", "Mlečno i biljno",
        "Voće i povrće", "Smrznuti proizvodi", "Testenine i pirinač",
        "Ceralije", "Proteinski proizvodi", "Zdrav(iji) zalogaj(i)",
        "Konzervirano", "Namirnice za kuvanje",
    }
    seen = set()
    picks = []
    for it in catalog["items"]:
        if it["top_category"] not in wanted:
            continue
        if not it.get("grams"):
            continue
        if it["discount_pct"]:
            continue
        key = it["name"].lower()
        if key in seen:
            continue
        seen.add(key)
        picks.append(it)

    print("=" * 96)
    print("WOLT PRODUCTS NOT YET IN CATALOG (candidate additions)")
    print("=" * 96)
    print(f"{'name':52} {'price':>8} {'unit':>9} {'category':>18}")
    print("-" * 96)
    for it in picks[:limit]:
        print(f"{it['name'][:52]:52} {it['price']:>8.0f} {it['unit_info'] or '':>9} {it['category'][:18]:>18}")
    print(f"\n({len(picks)} candidate products total; showing {min(limit, len(picks))})")


def _replace_ingredient_price(source, name, new_price):
    """Replace the numeric price for ``name`` in the ingredient.py source text.

    Matches the pattern::

        "name": Ingredient(
                "name",
                <price>,
                ...
    """
    pattern = re.compile(
        r'("' + re.escape(name) + r'"\s*:\s*Ingredient\(\s*\n\s*"' + re.escape(name) +
        r'",\s*\n\s*)([0-9]+(?:\.[0-9]+)?)',
        re.MULTILINE,
    )
    def repl(m):
        return m.group(1) + str(int(round(new_price)))
    new_src, n = pattern.subn(repl, source)
    return new_src, n


def export_products(catalog, path=PRODUCTS_FILE):
    """Write the Wolt product correspondence module (``wolt_products.py``).

    Emits a human-readable ``WOLT_PRODUCTS`` dict mapping every BulkBro
    ingredient to the exact Wolt product (id, name, pack). ``ingredient.py``
    imports this at load time to attach the correspondence to each ingredient.

    Parameters
    ----------
    catalog : dict
        Parsed ``wolt_catalog.json``.
    path : str, optional
        Output module path.

    Returns
    -------
    int
        Number of mappings written.
    """
    by_id = {it["id"]: it for it in catalog["items"]}
    rows = []
    for name in ingredients:
        spec = WOLT_MAP.get(name)
        if spec is None or spec is MARK_REMOVE:
            continue
        pid = spec["id"] if isinstance(spec, dict) else spec
        prod = by_id.get(pid)
        if not prod:
            continue
        rows.append((name, pid, prod["name"], prod.get("unit_info") or ""))
    rows.sort()

    lines = [
        '"""Wolt Market product correspondence for BulkBro ingredients.',
        '',
        'Auto-generated by ``python3 wolt_refresh.py export`` from a live',
        '``wolt_catalog.json`` scrape. Maps each BulkBro ingredient name to the',
        'exact Wolt Market product it represents so shopping lists can name the',
        'product to order. Edit via WOLT_MAP in wolt_refresh.py, then re-export.',
        '"""',
        '',
        '# name -> (wolt product id, exact Wolt product name, pack label)',
        'WOLT_PRODUCTS = {',
    ]
    for name, pid, pname, unit in rows:
        lines.append('    %r: (%r, %r, %r),' % (name, pid, pname, unit))
    lines.append('}')
    lines.append('')

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return len(rows)


def main(argv=None):
    """Command-line entry point."""
    parser = argparse.ArgumentParser(description="Refresh ingredients from Wolt catalog")
    parser.add_argument("command", choices=["report", "apply", "candidates", "export"],
                        help="What to do")
    parser.add_argument("--catalog", default=CATALOG_FILE, help="Wolt catalog JSON")
    parser.add_argument("--keep-missing", action="store_true",
                        help="Do not remove ingredients missing from Wolt")
    args = parser.parse_args(argv)

    try:
        with open(args.catalog, encoding="utf-8") as f:
            catalog = json.load(f)
    except FileNotFoundError:
        print(f"Catalog not found: {args.catalog}. Run wolt_scraper.py first.")
        return 1

    rows = build_report(catalog)
    if args.command == "report":
        print_report(rows)
    elif args.command == "candidates":
        print_candidates(catalog)
    elif args.command == "export":
        n = export_products(catalog)
        print(f"Wrote {n} product mappings to {PRODUCTS_FILE}")
    else:
        changed, removed, dups = apply_refresh(rows, remove_missing=not args.keep_missing)
        print(f"Updated {changed} prices, removed {removed} missing entries "
              f"and {dups} duplicates in {INGREDIENT_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

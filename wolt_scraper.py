"""Wolt Market scraper for BulkBro ingredient catalog refresh.

Scrapes the live Wolt Market (Serbia) assortment so ingredient prices,
minimum quantities, and the product list can be refreshed from the source.

Data flow
---------
1. ``fetch_assortment`` pulls the category tree for a venue.
2. ``walk_food_categories`` selects the leaf categories under food-related
   top-level categories.
3. ``fetch_category_items`` pages through each leaf category to collect item
   IDs (and cheap inline data).
4. ``fetch_item_details`` bulk-fetches full item records (prices, units,
   sell-by-weight config) in a single POST per batch.
5. ``scrape`` orchestrates the whole thing and returns a normalized catalog.

Usage
-----
    python3 wolt_scraper.py                      # default Dorcol venue
    python3 wolt_scraper.py --venue wolt-market-dorol
    python3 wolt_scraper.py --out wolt_catalog.json

The Wolt API is undocumented and may change. This module uses the same
endpoints the public website (wolt.com) uses.
"""

import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

# =============================================================================
# API configuration
# =============================================================================
CONSUMER_API = "https://consumer-api.wolt.com"
ASSORTMENT_BASE = CONSUMER_API + "/consumer-api/consumer-assortment/v1"

#: Default venue and language
DEFAULT_VENUE = "wolt-market-dorol"
DEFAULT_LANGUAGE = "sr"

#: Top-level category slugs that contain food / pantry ingredients.
#: Non-food segments (home, beauty, pharmacy, electronics, pets) are excluded.
FOOD_CATEGORY_SLUGS = {
    "voce-i-povrce-20",
    "meso-i-riba-27",
    "pekara-32",
    "sladoled-38",
    "frikom-43",
    "smrznuti-proizvodi-48",
    "mlecno-i-biljno-54",
    "jaja-sir-i-namazi-63",
    "delikates-71",
    "kolaci-i-torte-75",
    "international-cuisine-80",
    "polugotova-i-gotova-jela-85",
    "voda-sokovi-energija-88",
    "slane-grickalice-122",
    "cokolade-i-bombonjere-128",
    "keks-vafl-i-biskviti-133",
    "bombone-i-zvake-137",
    "specijalna-ishrana-141",
    "zdraviji-zalogaji-145",
    "proteinski-proizvodi-150",
    "ceralije-155",
    "kafa-caj-napici-158",
    "med-dzem-krem-164",
    "namirnice-za-kuvanje-169",
    "testenine-i-pirinac-173",
    "prelivi-i-sosevi-177",
    "konzervirano-183",
    "dorucak-kod-ljiljane-36",
}

#: HTTP headers mimicking a normal browser request.
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120 Safari/537.36"
    ),
    "Accept": "application/json",
}

#: Pause between HTTP calls (seconds) to be polite to the API.
REQUEST_DELAY = 0.25


def _get(url, retries=3, timeout=25):
    """Perform a GET request and return parsed JSON.

    Parameters
    ----------
    url : str
        Full URL to request.
    retries : int, optional
        Number of retries on transient failure.
    timeout : int, optional
        Timeout in seconds.

    Returns
    -------
    dict
        Parsed JSON response.
    """
    req = urllib.request.Request(url, headers=HEADERS)
    last_err = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
            last_err = exc
            time.sleep(REQUEST_DELAY * (attempt + 2))
    raise RuntimeError(f"GET failed: {url} ({last_err})")


def _post(url, payload, retries=3, timeout=25):
    """Perform a POST request with a JSON body and return parsed JSON."""
    body = json.dumps(payload).encode("utf-8")
    headers = dict(HEADERS, **{"Content-Type": "application/json"})
    last_err = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, data=body, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
            last_err = exc
            time.sleep(REQUEST_DELAY * (attempt + 2))
    raise RuntimeError(f"POST failed: {url} ({last_err})")


def fetch_assortment(venue=DEFAULT_VENUE, language=DEFAULT_LANGUAGE):
    """Fetch the top-level assortment (category tree) for a venue.

    Parameters
    ----------
    venue : str, optional
        Venue slug.
    language : str, optional
        Menu language code.

    Returns
    -------
    dict
        Raw assortment with a ``categories`` tree.
    """
    url = (
        f"{ASSORTMENT_BASE}/venues/slug/{venue}/assortment"
        f"?menu_language={language}&user_language={language}"
    )
    return _get(url)


def walk_food_categories(assortment):
    """Return leaf food categories as ``(top_name, slug, name)`` tuples.

    Walks the category tree, keeping only categories under
    :data:`FOOD_CATEGORY_SLUGS`. Non-leaf categories are expanded.

    Parameters
    ----------
    assortment : dict
        Result of :func:`fetch_assortment`.

    Returns
    -------
    list of tuple
        ``(top_name, leaf_slug, leaf_name)`` entries.
    """
    def leaves(node):
        subs = node.get("subcategories") or node.get("categories") or []
        if subs:
            out = []
            for sub in subs:
                out.extend(leaves(sub))
            return out
        return [(node["slug"], node["name"])]

    result = []
    for cat in assortment.get("categories", []):
        if cat.get("slug") not in FOOD_CATEGORY_SLUGS:
            continue
        subs = cat.get("subcategories") or cat.get("categories") or []
        if subs:
            for slug, name in leaves(cat):
                result.append((cat["name"], slug, name))
        else:
            result.append((cat["name"], cat["slug"], cat["name"]))
    return result


def fetch_category_items(venue, category_slug, language=DEFAULT_LANGUAGE):
    """Fetch all items (with pagination) for a leaf category.

    Parameters
    ----------
    venue : str
        Venue slug.
    category_slug : str
        Leaf category slug.
    language : str, optional
        Menu language code.

    Returns
    -------
    list of dict
        Item records as returned inline by the category endpoint.
    """
    items = []
    seen_ids = set()
    page_token = None
    while True:
        params = {"language": language}
        if page_token:
            params["page_token"] = page_token
        query = urllib.parse.urlencode(params)
        url = (
            f"{ASSORTMENT_BASE}/venues/slug/{venue}"
            f"/assortment/categories/slug/{category_slug}?{query}"
        )
        data = _get(url)
        new = [it for it in data.get("items", []) if it["id"] not in seen_ids]
        for it in new:
            seen_ids.add(it["id"])
        items.extend(new)
        page_token = (data.get("metadata") or {}).get("next_page_token")
        if not page_token or not new:
            break
        time.sleep(REQUEST_DELAY)
    return items


def fetch_item_details(venue, item_ids, language=DEFAULT_LANGUAGE, batch=60):
    """Bulk-fetch full item records by ID.

    Parameters
    ----------
    venue : str
        Venue slug.
    item_ids : iterable of str
        Item IDs to fetch.
    language : str, optional
        Menu language code.
    batch : int, optional
        Number of IDs per POST.

    Returns
    -------
    dict
        Mapping ``item_id -> item record``.
    """
    ids = list(item_ids)
    result = {}
    for i in range(0, len(ids), batch):
        chunk = ids[i:i + batch]
        url = (
            f"{ASSORTMENT_BASE}/venues/slug/{venue}/assortment/items"
            f"?language={language}"
        )
        data = _post(url, {"item_ids": chunk})
        for it in data.get("items", []):
            result[it["id"]] = it
        time.sleep(REQUEST_DELAY)
    return result


def _unit_grams(unit_info, sell_by_weight):
    """Best-effort conversion of ``unit_info`` text to grams.

    Wolt unit strings look like ``"300 g"``, ``"1,32 l"``, ``"1 kg"``,
    ``"150 ml"``. Returns grams for solids and millilitres for liquids
    (treated as 1:1 for catalog purposes), or ``None`` if unknown.
    """
    if sell_by_weight and sell_by_weight.get("grams_per_step"):
        return float(sell_by_weight["grams_per_step"])
    if not unit_info:
        return None
    text = unit_info.lower().replace(",", ".").strip()
    num = None
    for tok in text.split():
        try:
            num = float(tok)
            break
        except ValueError:
            continue
    if num is None:
        return None
    if "kg" in text:
        return num * 1000
    if " g" in text or text.endswith("g"):
        return num
    if "l" in text and "ml" not in text:
        return num * 1000
    if "ml" in text:
        return num
    return None


def normalize_item(item, top_name, leaf_name):
    """Convert a raw Wolt item record to a compact catalog entry.

    Prices from the API are in *para* (1 RSD = 100 para); this converts to RSD.

    Parameters
    ----------
    item : dict
        Raw item record.
    top_name : str
        Top-level category name.
    leaf_name : str
        Leaf category name.

    Returns
    -------
    dict
        Normalized catalog entry.
    """
    price = item.get("price")
    original = item.get("original_price")
    unit_info = item.get("unit_info")
    sbw = item.get("sell_by_weight")

    def rsd(v):
        return round(v / 100.0, 2) if v is not None else None

    return {
        "id": item["id"],
        "name": item.get("name", "").strip(),
        "price": rsd(price),
        "original_price": rsd(original),
        "discount_pct": (
            round((1 - price / original) * 100, 1)
            if price and original and original > price else None
        ),
        "unit_info": unit_info,
        "grams": _unit_grams(unit_info, sbw),
        "sell_by_weight": bool(sbw),
        "price_per_kg": rsd((sbw or {}).get("price_per_kg")),
        "top_category": top_name,
        "category": leaf_name,
        "barcode": item.get("barcode_gtin"),
        "description": (item.get("description") or "").strip(),
    }


def scrape(venue=DEFAULT_VENUE, language=DEFAULT_LANGUAGE, verbose=True):
    """Scrape the full food catalog of a Wolt Market venue.

    Parameters
    ----------
    venue : str, optional
        Venue slug.
    language : str, optional
        Menu language code.
    verbose : bool, optional
        Print progress.

    Returns
    -------
    dict
        ``{"venue": ..., "scraped_at": ..., "categories": [...],
        "items": [...]}`` with normalized item entries.
    """
    if verbose:
        print(f"Fetching assortment for venue '{venue}' ...")
    assortment = fetch_assortment(venue, language)
    leaves = walk_food_categories(assortment)
    if verbose:
        print(f"Found {len(leaves)} food leaf categories")

    item_ids = {}          # id -> (top_name, leaf_name)
    for idx, (top, slug, name) in enumerate(leaves, 1):
        try:
            items = fetch_category_items(venue, slug, language)
        except RuntimeError as exc:
            if verbose:
                print(f"  [skip] {slug}: {exc}")
            continue
        for it in items:
            item_ids.setdefault(it["id"], (top, name))
        if verbose:
            print(f"  [{idx}/{len(leaves)}] {name}: {len(items)} items")

    if verbose:
        print(f"Total unique items: {len(item_ids)}; fetching details ...")

    details = fetch_item_details(venue, item_ids.keys(), language)

    catalog_items = []
    for iid, (top, leaf) in item_ids.items():
        raw = details.get(iid)
        if not raw:
            continue
        catalog_items.append(normalize_item(raw, top, leaf))

    catalog_items.sort(key=lambda x: (x["top_category"], x["category"], x["name"]))

    return {
        "venue": venue,
        "language": language,
        "scraped_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "categories": [
            {"top": t, "slug": s, "name": n} for t, s, n in leaves
        ],
        "items": catalog_items,
    }


def main(argv=None):
    """Command-line entry point."""
    parser = argparse.ArgumentParser(description="Scrape Wolt Market food catalog")
    parser.add_argument("--venue", default=DEFAULT_VENUE, help="Venue slug")
    parser.add_argument("--language", default=DEFAULT_LANGUAGE, help="Menu language")
    parser.add_argument("--out", default="wolt_catalog.json", help="Output JSON file")
    args = parser.parse_args(argv)

    catalog = scrape(args.venue, args.language)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=False, indent=1)
    print(f"Saved {len(catalog['items'])} items -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

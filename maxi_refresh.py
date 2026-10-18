"""Refresh BulkBro ingredients against a live Maxi (Delhaize) catalog.

Maxi is a full supermarket with substantially cheaper prices than the Wolt
Market convenience listing, so this branch sources every ingredient from Maxi.
The mapping (:data:`MAXI_MAP`) is curated by hand: for each original ingredient
concept it picks the cheapest suitable *single-ingredient* Maxi product,
preferring canned goods for legumes where available (no snack mixes / prepared
combos).

Workflow
--------
    python3 maxi_scraper.py             # produce maxi_catalog.json
    python3 maxi_refresh.py report      # price/availability report (no writes)
    python3 maxi_refresh.py apply       # rewrite ingredient.py prices, drop missing
    python3 maxi_refresh.py export      # regenerate maxi_products.py

Reuses the normalization/reporting machinery from :mod:`wolt_refresh`
(``_norm_price``, ``build_report`` etc.) by binding the module-level constants
to Maxi's catalog/map.
"""

import argparse
import json
import sys

import wolt_refresh as _wr
from ingredient import ingredients

CATALOG_FILE = "maxi_catalog.json"
INGREDIENT_FILE = "ingredient.py"
PRODUCTS_FILE = "maxi_products.py"

MARK_REMOVE = _wr.MARK_REMOVE

# =============================================================================
# Curated mapping: BulkBro ingredient name -> Maxi product id (or spec dict)
# =============================================================================
# A plain string is a Maxi product id with grams basis (price normalized to the
# ingredient's min_qty). A dict allows overrides:
#   {"id": <pid>, "grams_block": N}   price for N grams (piece items)
#   {"id": <pid>, "unit": "pack", "pack_units": K}
# None = leave price unchanged. MARK_REMOVE = drop ingredient + its meals.
MAXI_MAP = {
    # ---- nuts / seeds ----
    "kikiriki": "cedb2ec7050362433c4563c9",            # Kikiriki prženi/slani Emma 60g
    "kikiriki svetofor": "cedb2ec7050362433c4563c9",
    "badem": "a4b9da278b3b581c3d2091d6",               # Badem sirovi Emma 70g
    "badem svetofor": "a4b9da278b3b581c3d2091d6",
    "suncokret": "1e5f546afb21f4a705adaf04",           # Semenke suncokreta oljuštene Emma 250g
    "golica": "566bf341e197285a8ec97cd5",              # Sirova golica Nature's Promise 100g
    "seme bundeve": "6c46b396f2e5409853fe4942",        # Semenke bundeve pečene/slane Emma 60g
    "indijski orah": "f51fb1c01c5b58dee6188a65",       # Indijski orah natural Emma 200g
    "chia semenke maxi": "43d6c47c8ceddcd6bdbb82de",   # Seme lana Nature's Promise 100g (flax substitute)
    "lanene semenke": "43d6c47c8ceddcd6bdbb82de",      # Seme lana Nature's Promise 100g
    "pasulj": "0f13a099fabac626bab29258",              # Beli krupni pasulj Maxi 500g (dry)
    "pasulj beli svetofor 1kg": "0f13a099fabac626bab29258",
    "urme": "697e67a84ffd65652088ba00",                # Suve urme bez koštice Emma 200g
    "urme svetofor": "697e67a84ffd65652088ba00",
    "borovnice": {"id": "dff5b8340282f5454a195968", "grams_block": 250, "wolt_grams": 250},  # Blueberry packed 250g
    "leblebije maxi": {"id": "a2a6ab7db9bcf976906b32d3", "wolt_grams": 160},  # Leblebije Bonduelle 2x80g (canned, 160g)

    # ---- grains / pasta ----
    "ovsene pahuljice": "1dec9af759bc30021ad1d68a",    # Pahuljice ovsene instant Emma 500g
    "ovsene svetofor 500g": "1dec9af759bc30021ad1d68a",
    "pirinac 1kg": "2ad2c1d25fafe0a6854caa51",         # Pirinač beli AB 1kg
    "pirinac svetofor": "2ad2c1d25fafe0a6854caa51",
    "braon pirinac 500g": "a1ce60f8007bcc4c4d77c3a4",  # Pirinač integralni BF 500g
    "pasta 500g": "eff2525c304b5415cede89ec",          # Testenina Durum Fusilli Danubius 400g
    "integralna pasta": "b886dcc00a1034272c9b6591",    # Testenina integralna fusilli 400g
    "posne makarone svetofor": "eff2525c304b5415cede89ec",
    "palenta svetofor": "c1bdf132becb7ca429485ca5",    # Palenta Maxi 500g
    "kinoa": "07deff6f465ef5596115f94a",               # Kinoa Nature's Promise BIO 250g
    "socivo": "0f13a099fabac626bab29258",              # Beli krupni pasulj (beans ~ lentils)
    "socivo pasta": "eff2525c304b5415cede89ec",        # Durum fusilli (legume-pasta substitute)
    "tortilja 8": {"id": "5d3ca048a2ae9cff011c3ff9", "grams_block": 45},  # Tortilja pšen. 370g (~8 pcs, ~45g ea)

    # ---- vegetables ----
    "krompir": "34934555018230a7798a2caa",    # Krompir za kuvanje 1.5kg (has grams)
    "krompir svetofor": "34934555018230a7798a2caa",
    "crni luk kom": {"id": "5932483a4d821a9683ec615b", "grams_block": 150, "wolt_grams": 1000},  # Luk crni domaći (per kg)
    "crni luk svetofor": {"id": "5932483a4d821a9683ec615b", "grams_block": 100, "wolt_grams": 1000},  # Luk crni domaći (per kg)
    "crveni luk kom": {"id": "66b721ee7e9d4d2bdc570fcf", "grams_block": 675, "wolt_grams": 1000},  # Luk crveni domaći (per kg, 3 pcs)
    "beli luk": {"id": "9606ca945c51e04aa40e9080", "wolt_grams": 58},  # Beli luk granule 58g (no fresh loose)
    "kupus": {"id": "71a5e8f49138d3c425863b5d", "grams_block": 750, "wolt_grams": 1000},  # Mladi kupus (per kg)
    "crveni kupus kom": {"id": "ae88eb1710bbb761134bb8fc", "grams_block": 540, "wolt_grams": 1000},  # Kupus crveni domaći (per kg)
    "sargarepa kom": {"id": "bb4b49ba5362e51b27c8e599", "grams_block": 392, "wolt_grams": 1000},  # Šargarepa domaća (per kg, 4 pcs)
    "cvekla kom": {"id": "b0d31cc658e1b32590a3d283", "grams_block": 440, "wolt_grams": 1000},  # Cvekla (per kg, 4 pcs)
    "patlidzan": {"id": "422ce0d7fae284748c144c3b", "grams_block": 550, "wolt_grams": 1000},  # Plavi patlidžan (per kg)
    "brokoli": {"id": "720fa84c2a965bc7fcd731ed", "wolt_grams": 450},  # Smrznuti brokoli Gustona 450g
    "pecurke": "61c52864f6a4b2d5050214f0",             # Šampinjoni 400g Maxi Pijaca
    "spanać svez": "eb9c02314aaaf07073654b04",         # Spanać Maxi Pijaca 300g
    "rukola": "a2823778223348f45e7c8071",              # Salata rukola 70g Maxi Pijaca
    "batat kom": {"id": "f19e646998e270cd96a103b1", "grams_block": 390, "wolt_grams": 1000},  # Krompir slatki batat (per kg, 3 pcs)

    # ---- fruit ----
    "banana": "564c1a09eb4a31288c958f32",              # Banana 730g
    "jabuka": {"id": "1df99f3e359356ae215bbf96", "grams_block": 150, "wolt_grams": 1000},  # Jabuka Gala domaća (per kg)
    "pomorandza": {"id": "666d482e31d17b9ad273dd06", "grams_block": 200, "wolt_grams": 1000},  # Pomorandža (per kg)
    "avokado": {"id": "74383e50e6b38996f80930a9", "grams_block": 215, "wolt_grams": 215},  # Avokado komad (~215g)
    "ananas": "f8e53bf82671630443d41b21",               # Suvo grožđe Emma 200g (dried-fruit substitute)

    # ---- dairy / eggs ----
    "jogurt": "f48f9883d44ae2f4b4dee4e3",              # Jogurt 2,8%mm Maxi 1.5kg
    "mleko": "88dd709994de56c1c8954ed4",                # Mleko sterilizovano Maxi 2,8% 1l
    "kiselo mleko": "9e7bd5be9ce166fadb2a1d41",         # Kiselo mleko 2.8% Maxi 400g
    "kefir casa": {"id": "2967d5e8eb410ad149084dde", "wolt_grams": 950},  # Balans+ kefir 950g
    "grcki jogurt olimpus": "73f82066eb1432eb48a8ba27", # High Protein Grekos 400g
    "zott jogurt": {"id": "542ad62434cf15b98eca4b5a", "wolt_grams": 115},  # Zottis Fruit 115g
    "dukatos": "f9ee53a364ae329af50ea217",              # Jogurt 2.8%mm Maxi 1kg (plain)
    "zbregov": {"id": "87f669eaa2eeff7b99af0f93", "wolt_grams": 500},  # Sir domaći mladi President 500g
    "puter": "7498f7812fed338730cbbbd9",                # Maslac Moja Kravica 125g
    "stari sir": "54a66d48987b0bc96b22f8ba",            # Sir Gauda Maxi 250g
    "jaja 10kom": {"id": "71e6fd636de7143694dba2c4", "unit": "pack", "pack_units": 10},  # Kokošija jaja M Maxi 10/1
    "jaje": {"id": "71e6fd636de7143694dba2c4", "unit": "pack", "pack_units": 10},

    # ---- meat / fish ----
    "pilece belo 100g": "9a3d20a3183fb06c50c034c5",     # Pileći file premium sveže meso 500g
    "pileca prsa 8": {"id": "9a3d20a3183fb06c50c034c5", "unit": "pack", "pack_units": 8},
    "sardina": "a5c45ab7797d4a6793895046",              # Sardina u biljnom ulju Maxi 105g
    "skusa eva 170g": "7fd88b7dfe6f9ac2fc849620",       # Skuša fileti u ulju Maxi 170g
    "skusa la perla": "7fd88b7dfe6f9ac2fc849620",
    "rio mare tuna": {"id": "55eca3b5c52e32a206de0b23", "grams_block": 160, "wolt_grams": 160},  # Tunjevina komadići Maxi 160g
    "rio mare kuskus": {"id": "e0e646d779c8831a5a32caec", "grams_block": 160, "wolt_grams": 160},  # Rio Mare Kus Kus salata 160g
    "pastrmka": {"id": "c0454b939d2e4a43ba3f7ec1", "grams_block": 200},  # Zamrz. filet pastrmke 400g

    # ---- pantry / sauces ----
    "maslinovo ulje": "b72ec5cac3f7443042a7811f",       # Ulje maslinovo extra vergine WM 1l
    "pasirani paradajz": "2da0be6e6e324b82f202ccce",    # Gurman paradajz pasirani 500g
    "pasirani paradajz svetofor": "c1e120c25258520b448563dd",  # Gurman pasirani 1000ml
    "paradajz": {"id": "c43ce9a5f1bc31b91951a27d", "grams_block": 140, "wolt_grams": 1000},  # Paradajz Grapola (per kg)
    "dzem dm": "a8a0a82d6d3151375ee111c0",              # Ekstra džem kajsija Gustona 450g
    "dvopek": "c78491453b323b61014d98de",               # Dvopek integralni Maxi 300g
    "fitnes hleb": "79301ba91e2f62f5f13ad0eb",          # Tonus tost hleb sa raži 300g
    "humus": "56308cf963c0997fda68116e",                # Humus Carnex 95g
    "sojino mleko": "278b23ae760828964b61f8d1",         # Alpro Napitak Soja Vanila 1000ml
    "tofu 250g pak": "389663008ad7a3e396895c4f",        # Tofu Nature's Promise 300g
    "kokice": "24a964abf02e7497c243599e",               # Kokice slane Premia 100g
    "kikiriki puter dm": "c57269624774a91d6dccf558",    # Kikiriki puter smooth WM 350g
    "rajs kejk": "c78491453b323b61014d98de",            # Dvopek integralni Maxi 300g (crispbread substitute)
    "heidi": "b0f828e7fd690741958bf8e3",                # Čokolada crna Intense 75% Heidi 80g
    "najlepse zelje": {"id": "e4a5c3d1d58fa1d7f323452b", "grams_block": 145, "wolt_grams": 145},  # Najlepše želje Cookies 145g
    "sladoledi 10kom": {"id": "f78c2d2f2182fc7547a6874d", "unit": "pack", "pack_units": 10},  # Sladoled Velvet 900ml (~10 servings)

    # ---- frozen ----
    "zamrznuti spanac": "ea96f39abfc8a42e1a50021e",     # Smrz. Spanać listovi Gustona 450g
    "zaledjeni spanac": "ea96f39abfc8a42e1a50021e",
    "zamrznuti grasak svetofor 1kg": "39f47fedf42db4e825a85308",  # Smrznuti grašak Gustona 1kg
    "zaledjeni grasak": "2c9cb404869e6625ffa7a9d8",     # Smrz.grašak Maxi/Gustona 450g
    "kinezi miks": "29208a51b94b49d2a2f3a63c",          # Smrz.mix povrća karf/šar/brok Gustona 450g
    "smrznuti miks": "29208a51b94b49d2a2f3a63c",
    "jumbo mix": {"id": "85ba91dd25c8128993a14d1e", "grams_block": 75, "wolt_grams": 210},  # Trio Mix 210g
    "nutrino labs sok": {"id": "c1efbd63c0f7f0112808bbd3", "grams_block": 180, "wolt_grams": 180},  # Nutrino Lab Fitness ready mix 180g
    "carnex posni pasulj": {"id": "16716000e87ecb180d7446e6", "grams_block": 400},  # Posni pasulj Maxi 400g (ready)
    "carnex posni grasak": {"id": "69cec0e0cfc0b33c6bfb5e73", "grams_block": 400},  # Grašak posni Maxi 400g (ready)
    "pasulj konzerva": "0f13a099fabac626bab29258",  # Beli krupni pasulj Maxi 500g (dry)
}


def _bind():
    """Point wolt_refresh's module globals at Maxi's map/catalog/outputs."""
    _wr.WOLT_MAP = MAXI_MAP
    _wr.CATALOG_FILE = CATALOG_FILE
    _wr.INGREDIENT_FILE = INGREDIENT_FILE
    _wr.PRODUCTS_FILE = PRODUCTS_FILE


def build_report(catalog):
    """Build the refresh report using Maxi's map."""
    _bind()
    return _wr.build_report(catalog)


def apply_refresh(rows, remove_missing=True):
    """Apply refreshed prices / removals to ingredient.py."""
    _bind()
    return _wr.apply_refresh(rows, remove_missing=remove_missing)


def export_products(catalog):
    """Regenerate maxi_products.py from the current map."""
    _bind()
    return _wr.export_products(catalog, path=PRODUCTS_FILE,
                               dict_name="MAXI_PRODUCTS", market="Maxi",
                               command="maxi_refresh.py")


def print_report(rows):
    """Print the (Maxi) refresh report."""
    _bind()
    _wr.print_report(rows)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Refresh ingredients from Maxi catalog")
    parser.add_argument("command", choices=["report", "apply", "export"],
                        help="What to do")
    parser.add_argument("--catalog", default=CATALOG_FILE, help="Maxi catalog JSON")
    parser.add_argument("--keep-missing", action="store_true",
                        help="Do not remove ingredients missing from Maxi")
    args = parser.parse_args(argv)

    try:
        with open(args.catalog, encoding="utf-8") as f:
            catalog = json.load(f)
    except FileNotFoundError:
        print(f"Catalog not found: {args.catalog}. Run maxi_scraper.py first.")
        return 1

    _bind()
    rows = build_report(catalog)
    if args.command == "report":
        print_report(rows)
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

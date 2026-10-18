"""Scrape the Maxi (Delhaize) supermarket venue into a BulkBro catalog.

Maxi on Wolt has a large, full-supermarket assortment (unlike the limited
Wolt Market / Univerexport convenience listings). This reuses the HTTP helpers
from :mod:`wolt_scraper` and walks Maxi's own food leaf categories.

Usage
-----
    python3 maxi_scraper.py                 # -> maxi_catalog.json
    python3 maxi_scraper.py --venue maxi-kralja-milana
    python3 maxi_scraper.py --out foo.json
"""

import argparse
import json
import sys
import time

import wolt_scraper as ws

DEFAULT_VENUE = "maxi-kralja-milana"
CATALOG_FILE = "maxi_catalog.json"
LANGUAGE = "sr"

# Food leaf categories for Maxi (non-food segments excluded).
FOOD_LEAVES = [
    ('SVEŽE VOĆE I POVRĆE', 'sveze-voce-2', 'Sveže voće'),
    ('SVEŽE VOĆE I POVRĆE', 'sveze-povrce-3', 'Sveže povrće'),
    ('PEKARA', 'hleb-i-tost-5', 'Hleb i tost'),
    ('PEKARA', 'pecivo-6', 'Pecivo'),
    ('PEKARA', 'dvopek-7', 'Dvopek'),
    ('PEKARA', 'tortilje-8', 'Tortilje'),
    ('MESO I RIBA', 'piletina-10', 'Piletina'),
    ('MESO I RIBA', 'curetina-11', 'Ćuretina'),
    ('MESO I RIBA', 'svinjetina-12', 'Svinjetina'),
    ('MESO I RIBA', 'junetina-13', 'Junetina'),
    ('MESO I RIBA', 'specijalno-pripremljeno-meso-14', 'Specijalno pripremljeno meso'),
    ('MESO I RIBA', 'riba-15', 'Riba'),
    ('DELIKATES', 'delikates-16', 'DELIKATES'),
    ('UHT MLEKO, JAJA I CEREALIJE', 'uht-mleko-18', 'UHT mleko'),
    ('UHT MLEKO, JAJA I CEREALIJE', 'jaja-19', 'Jaja'),
    ('UHT MLEKO, JAJA I CEREALIJE', 'biljna-mleka-20', 'Biljna mleka'),
    ('UHT MLEKO, JAJA I CEREALIJE', 'cokoladno-mleko-i-milkshake-21', 'Čokoladno mleko i milkshake'),
    ('UHT MLEKO, JAJA I CEREALIJE', 'slatkaza-kuvanje-pavlaka-i-slag-22', 'Slatka/za kuvanje pavlaka i šlag'),
    ('UHT MLEKO, JAJA I CEREALIJE', 'ceralije-23', 'Ceralije'),
    ('SVEŽE MLEKO I MLEČNI PROIZVODI', 'sirni-namazi-25', 'Sirni namazi'),
    ('SVEŽE MLEKO I MLEČNI PROIZVODI', 'sveze-mleko-26', 'Sveže mleko'),
    ('SVEŽE MLEKO I MLEČNI PROIZVODI', 'jogurt-27', 'Jogurt'),
    ('SVEŽE MLEKO I MLEČNI PROIZVODI', 'kefir-28', 'Kefir'),
    ('SVEŽE MLEKO I MLEČNI PROIZVODI', 'grcki-jogurt-29', 'Grčki jogurt'),
    ('SVEŽE MLEKO I MLEČNI PROIZVODI', 'kiselo-mleko-30', 'Kiselo mleko'),
    ('SVEŽE MLEKO I MLEČNI PROIZVODI', 'pavlaka-31', 'Pavlaka'),
    ('SVEŽE MLEKO I MLEČNI PROIZVODI', 'slatka-pavlaka-33', 'Slatka pavlaka'),
    ('SVEŽE MLEKO I MLEČNI PROIZVODI', 'margarin-34', 'Margarin'),
    ('SVEŽE MLEKO I MLEČNI PROIZVODI', 'mileram-35', 'Mileram'),
    ('SVEŽE MLEKO I MLEČNI PROIZVODI', 'surutka-36', 'Surutka'),
    ('SVEŽE MLEKO I MLEČNI PROIZVODI', 'puding-37', 'Puding'),
    ('SVEŽE MLEKO I MLEČNI PROIZVODI', 'vocni-jogurt-38', 'Voćni jogurt'),
    ('SVEŽE MLEKO I MLEČNI PROIZVODI', 'mlecni-dezerti-39', 'Mlečni dezerti'),
    ('SVEŽE MLEKO I MLEČNI PROIZVODI', 'kafa-40', 'Kafa'),
    ('SVEŽE MLEKO I MLEČNI PROIZVODI', 'protein-41', 'Protein'),
    ('SIREVI I NAMAZI', 'od-povrca-43', 'Od povrća'),
    ('SIREVI I NAMAZI', 'sirevi-44', 'Sirevi'),
    ('SIREVI I NAMAZI', 'puter-45', 'Puter'),
    ('VODA', 'negazirana-voda-47', 'Negazirana voda'),
    ('VODA', 'gazirana-voda-48', 'Gazirana voda'),
    ('VODA', 'aromatizovana-voda-49', 'Aromatizovana voda'),
    ('SOKOVI', 'negazirani-sokovi-51', 'Negazirani sokovi'),
    ('SOKOVI', 'gazirani-sokovi-52', 'Gazirani sokovi'),
    ('SMRZNUTI PROIZVODI', 'smrznuto-voce-54', 'Smrznuto voće'),
    ('SMRZNUTI PROIZVODI', 'smrznuto-povrce-55', 'Smrznuto povrće'),
    ('SMRZNUTI PROIZVODI', 'smrznuto-testo-56', 'Smrznuto testo'),
    ('SMRZNUTI PROIZVODI', 'smrznuta-polugotova-jela-57', 'Smrznuta polugotova jela'),
    ('SMRZNUTI PROIZVODI', 'smrznuto-meso-i-riba-58', 'Smrznuto meso i riba'),
    ('SMRZNUTI PROIZVODI', 'smrznuti-dezerti-59', 'Smrznuti dezerti'),
    ('SLADOLEDI', 'sladoledi-60', 'SLADOLEDI'),
    ('ZDRAVA HRANA', 'good-food-62', 'Good food'),
    ('ZDRAVA HRANA', 'diet-food-63', 'Diet food'),
    ('ZDRAVA HRANA', 'sport-64', 'Sport'),
    ('ZDRAVA HRANA', 'gluten-free-65', 'Gluten free'),
    ('ZDRAVA HRANA', 'organska-hrana-66', 'Organska hrana'),
    ('ZDRAVA HRANA', 'cerealije-i-cereal-barovi-67', 'Cerealije i cereal barovi'),
    ('KAFA I ČAJ', 'tradicionalna-kafa-69', 'Tradicionalna kafa'),
    ('KAFA I ČAJ', 'espresso-70', 'Espresso'),
    ('KAFA I ČAJ', 'instant-kafa-71', 'Instant kafa'),
    ('KAFA I ČAJ', 'caj-72', 'Čaj'),
    ('KAFA I ČAJ', 'ostalo-73', 'Ostalo'),
    ('OSNOVNE ŽIVOTNE NAMIRNICE', 'ulje-75', 'Ulje'),
    ('OSNOVNE ŽIVOTNE NAMIRNICE', 'brasno-76', 'Brašno'),
    ('OSNOVNE ŽIVOTNE NAMIRNICE', 'secer-i-dodaci-za-kolace-77', 'Šećer i dodaci za kolače'),
    ('OSNOVNE ŽIVOTNE NAMIRNICE', 'pirinac-78', 'Pirinač'),
    ('OSNOVNE ŽIVOTNE NAMIRNICE', 'sirce-79', 'Sirće'),
    ('OSNOVNE ŽIVOTNE NAMIRNICE', 'mahunarke-80', 'Mahunarke'),
    ('TESTENINA I SOSOVI', 'sos-82', 'Sos'),
    ('TESTENINA I SOSOVI', 'testenina-83', 'Testenina'),
    ('TESTENINA I SOSOVI', 'namazi-84', 'Namazi'),
    ('KONZERVIRANA HRANA', 'humus-86', 'Humus'),
    ('KONZERVIRANA HRANA', 'mesne-konzerve-87', 'Mesne konzerve'),
    ('KONZERVIRANA HRANA', 'riblje-konzerve-88', 'Riblje konzerve'),
    ('ZAČINI, SO I SUPE', 'instant-90', 'Instant'),
    ('ZAČINI, SO I SUPE', 'so-91', 'So'),
    ('ZAČINI, SO I SUPE', 'zacini-92', 'Začini'),
    ('ZAČINI, SO I SUPE', 'supe-93', 'Supe'),
    ('PIVO I CIDERI', 'pivo-i-cideri-95', 'Pivo i cideri'),
    ('VINO', 'crveno-vino-97', 'Crveno vino'),
    ('VINO', 'belo-vino-98', 'Belo vino'),
    ('VINO', 'penusava-vina-99', 'Penušava vina'),
    ('VINO', 'roze-100', 'Roze'),
    ('VINO', 'aromatizovano-vino-101', 'Aromatizovano vino'),
    ('ŽESTOKA PIĆA', 'viski-103', 'Viski'),
    ('ŽESTOKA PIĆA', 'vodka-104', 'Vodka'),
    ('ŽESTOKA PIĆA', 'dzin-105', 'Džin'),
    ('ŽESTOKA PIĆA', 'ostala-zestina-106', 'Ostala žestina'),
    ('ŽESTOKA PIĆA', 'rakija-107', 'Rakija'),
    ('ENERGETSKA PIĆA', 'energetska-pica-108', 'ENERGETSKA PIĆA'),
    ('PRERADA OD VOĆA I POVRĆA', 'prerada-od-voca-i-med-110', 'Prerada od voća i med'),
    ('PRERADA OD VOĆA I POVRĆA', 'masline-111', 'Masline'),
    ('PRERADA OD VOĆA I POVRĆA', 'prerada-od-povrca-112', 'Prerada od povrća'),
    ('PRERADA OD VOĆA I POVRĆA', 'proizvodi-od-paradajza-113', 'Proizvodi od paradajza'),
    ('ČOKOLADE I BOMBONJERE', 'cokolade-115', 'Čokolade'),
    ('ČOKOLADE I BOMBONJERE', 'bombonjere-116', 'Bombonjere'),
    ('BOMBONE I ŽVAKE', 'bombone-118', 'Bombone'),
    ('BOMBONE I ŽVAKE', 'zvake-119', 'Žvake'),
    ('BOMBONE I ŽVAKE', 'alva-i-ratluk-120', 'Alva i ratluk'),
    ('KEKS', 'keks-121', 'KEKS'),
    ('MINI KONDITORI I KREM', 'mini-konditori-123', 'Mini konditori'),
    ('MINI KONDITORI I KREM', 'krem-124', 'Krem'),
    ('GRICKALICE', 'grickalice-126', 'Grickalice'),
    ('SUŠENO I ORAŠASTO VOĆE', 'suseno-i-orasasto-voce-127', 'SUŠENO I ORAŠASTO VOĆE'),
    ('KUHINJE SVETA', 'kuhinje-sveta-128', 'KUHINJE SVETA'),
    ('POLUGOTOVA JELA', 'polugotova-jela-129', 'POLUGOTOVA JELA'),
    ('TORTE I KOLAČI', 'torte-159', 'Torte'),
    ('TORTE I KOLAČI', 'kolaci-160', 'Kolači'),
    ('VEGE', 'vege-161', 'VEGE'),
]


def scrape(venue=DEFAULT_VENUE, language=LANGUAGE, verbose=True):
    """Scrape all food leaf categories for the Maxi venue.

    Returns
    -------
    dict
        ``{"venue", "language", "scraped_at", "categories", "items"}``.
    """
    item_ids = {}   # id -> (top, leaf)
    for idx, (top, slug, name) in enumerate(FOOD_LEAVES, 1):
        try:
            items = ws.fetch_category_items(venue, slug, language)
        except RuntimeError as exc:
            if verbose:
                print(f"  [skip] {slug}: {exc}")
            continue
        for it in items:
            item_ids.setdefault(it["id"], (top, name))
        if verbose:
            print(f"  [{idx}/{len(FOOD_LEAVES)}] {name}: {len(items)} items")
        time.sleep(0.05)

    if verbose:
        print(f"Total unique items: {len(item_ids)}; fetching details ...")
    details = ws.fetch_item_details(venue, item_ids.keys(), language)

    catalog_items = []
    for iid, (top, leaf) in item_ids.items():
        raw = details.get(iid)
        if not raw:
            continue
        catalog_items.append(ws.normalize_item(raw, top, leaf))

    catalog_items.sort(key=lambda x: (x["top_category"], x["category"], x["name"]))
    return {
        "venue": venue,
        "language": language,
        "scraped_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "categories": [{"top": t, "slug": s, "name": n} for t, s, n in FOOD_LEAVES],
        "items": catalog_items,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Scrape Maxi catalog")
    parser.add_argument("--venue", default=DEFAULT_VENUE)
    parser.add_argument("--out", default=CATALOG_FILE)
    args = parser.parse_args(argv)
    catalog = scrape(args.venue)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=False, indent=1)
    print(f"Saved {len(catalog['items'])} items -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

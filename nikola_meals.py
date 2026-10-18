from ingredient import *
from meal import Meal

# === ORIGINAL MEALS (defined as Meal objects for reuse) ===

o_kikiriki = Meal("kikiriki", [ingredients["kikiriki"]*100], ["breakfast","snack"])
o_badem = Meal("badem", [ingredients['badem']*50], ['dinner','snack'])
o_suncokret = Meal("suncokret", [ingredients['suncokret']*50], ['dinner','snack'])
o_sardina = Meal("sardina", [ingredients["sardina"]], ["breakfast","dinner"])
o_dvopek_humus = Meal("dvopek i humus", [
    ingredients["humus"]**0.33333,
    ingredients["dvopek"]**0.5,
], ['breakfast','dinner','snack'])

o_dvopek_avokado = Meal("dvopek i avokado", [
    ingredients["avokado"],
    ingredients["dvopek"]**0.5,
], ['breakfast','dinner','snack'])

o_krompir_luk = Meal("krompir luk i maslinovo ulje", [
    ingredients['krompir']*450,
    ingredients['crni luk kom'],
    ingredients["maslinovo ulje"]*13
], ['dinner'])

o_dvopek_humus_rukola = Meal("dvopek, humus i rukola", [
    ingredients['dvopek']*55,
    ingredients['humus']*50,
    ingredients['rukola']*15
], ["breakfast","dinner"])

o_tofu_pasta = Meal("tofu pasta", [
    ingredients["tofu 250g pak"]**0.5,
    ingredients['integralna pasta']*100,
    ingredients["crni luk kom"],
    ingredients['pasirani paradajz']**0.5
], ['lunch','dinner','breakfast'])

o_tofu_pasta_soc = Meal("tofu pasta soc.", [
    ingredients["tofu 250g pak"]**0.5,
    ingredients['socivo pasta']*100,
    ingredients["crni luk kom"],
    ingredients['pasirani paradajz']**0.5
], ['lunch','dinner','breakfast'])

# o_pbj_fitnes = Meal("PB&J i fitnes", [
#     ingredients["kikiriki puter dm"]*50,
#     ingredients["dzem dm"]*50,
#     ingredients["fitnes hleb"]*79
# ], ["snack","breakfast"])

# === DESSERTS (appendable ingredients) ===
dessert_heidi = ingredients['heidi']
dessert_cokoladica = ingredients["najlepse zelje"]
dessert_sladoled = ingredients["sladoledi 10kom"]*1
dessert_banana = ingredients['banana']
dessert_banana_half = ingredients['banana']**0.5
dessert_jabuka = ingredients['jabuka']

# === COMBINED MEALS (original meal + dessert appended) ===

def add_dessert(orig, dessert_ingr, dessert_name, categories):
    return Meal(
        f"{orig.name} {dessert_name}",
        orig.ingredients + [dessert_ingr],
        categories
    )

meals = [

        # 1-14: pair each original meal with a dessert
        add_dessert(o_dvopek_humus, dessert_heidi, "heidi", ['breakfast','dinner','snack']),
        add_dessert(o_dvopek_avokado, dessert_cokoladica, "cokoladica", ['breakfast','dinner','snack']),
        add_dessert(o_krompir_luk, dessert_sladoled, "sladoled", ['dinner','snack']),
        add_dessert(o_dvopek_humus_rukola, dessert_jabuka, "jabuka", ['breakfast','dinner','snack']),
        add_dessert(o_sardina, dessert_banana, "banana", ['breakfast','dinner','snack']),
        add_dessert(o_tofu_pasta, dessert_jabuka, "jabuka", ['breakfast','lunch','dinner','snack']),
        add_dessert(o_tofu_pasta_soc, dessert_banana, "banana", ['breakfast','lunch','dinner','snack']),
        add_dessert(o_kikiriki, dessert_jabuka, "jabuka", ['breakfast','snack','dinner']),
        add_dessert(o_badem, dessert_banana, "banana", ['dinner','snack']),
        add_dessert(o_suncokret, dessert_jabuka, "jabuka", ['dinner','snack']),
        add_dessert(o_kikiriki, dessert_banana, "banana", ['breakfast','dinner','snack']),

        # 13: o_pbj_fitnes (already has jam as dessert)
        #Meal(o_pbj_fitnes.name, o_pbj_fitnes.ingredients, ["snack","breakfast"]),

        # 14: PB banana i fitnes (custom: fitnes hleb + banana + PB, no jam)
        Meal("PB banana i fitnes", [
                ingredients["fitnes hleb"]*79,
                dessert_banana_half,
                ingredients["kikiriki puter dm"]*50
        ], ["snack","dinner"]),

        # 15-28: more combos
        add_dessert(o_dvopek_humus, dessert_jabuka, "jabuka", ['breakfast','dinner','snack']),
        add_dessert(o_dvopek_humus, dessert_banana, "banana", ['breakfast','dinner','snack']),
        add_dessert(o_dvopek_humus, dessert_sladoled, "sladoled", ['breakfast','dinner','snack']),
        add_dessert(o_dvopek_avokado, dessert_jabuka, "jabuka", ['breakfast','dinner','snack']),
        add_dessert(o_dvopek_avokado, dessert_banana, "banana", ['breakfast','dinner','snack']),
        add_dessert(o_dvopek_avokado, dessert_sladoled, "sladoled", ['breakfast','dinner','snack']),
        add_dessert(o_krompir_luk, dessert_jabuka, "jabuka", ['dinner','snack']),
        add_dessert(o_krompir_luk, dessert_banana, "banana", ['dinner','snack']),
        add_dessert(o_dvopek_humus_rukola, dessert_banana, "banana", ['breakfast','dinner']),
        add_dessert(o_dvopek_humus_rukola, dessert_heidi, "heidi", ['breakfast','dinner']),
        add_dessert(o_tofu_pasta, dessert_banana, "banana", ['lunch','dinner','breakfast']),
        add_dessert(o_tofu_pasta_soc, dessert_jabuka, "jabuka", ['lunch','dinner','breakfast']),
        #add_dessert(o_pbj_fitnes, dessert_jabuka, "jabuka", ["snack","breakfast"]),
        #add_dessert(o_pbj_fitnes, dessert_banana, "banana", ["snack","breakfast"]),

        # === ORIGINALS (no dessert) ===
        o_dvopek_humus,
        o_dvopek_avokado,
        o_krompir_luk,
        o_dvopek_humus_rukola,
        o_sardina,
        o_tofu_pasta,
        o_tofu_pasta_soc,
        o_kikiriki,
        o_badem,
        o_suncokret,

]


meals_dict = { x.name : x for x in meals }

# Assert unique meal names
check = set()
for meal in meals:
        try:
                assert meal.name not in check
        except AssertionError as e:
                print(meal.name)
                raise e

        check.add(meal.name)

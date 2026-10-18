from ingredient import *
from meal import Meal

reduce_factor = 0.6

meals = [

        Meal("kikiriki i banana",[
                ingredients['kikiriki']*100,
                ingredients['banana']*1
        ], ['snack']),

        Meal("kikiriki",[
                ingredients['kikiriki']*100
        ], ['breakfast','snack','dinner']),

        Meal("jabuka",[
                ingredients['jabuka']
        ], ['snack']),

        Meal("banana",[
                ingredients['banana']
        ], ['snack']),

        Meal("braon pirinac i pilece belo",[
                ingredients['pilece belo 100g']*300,
                ingredients['braon pirinac 500g']*90,
                ingredients["maslinovo ulje"]*13
        ], ['lunch']),

        Meal("beli pirinac i pilece belo",[
                ingredients['pilece belo 100g']*300,
                ingredients['pirinac 1kg']*120,
                ingredients["maslinovo ulje"]*13
        ], ['lunch']),

        
        Meal("3 kuvana jaja i rajs kejk", [
                ingredients['jaja 10kom']*3,
                ingredients['rajs kejk']**0.5
        ], ['breakfast','dinner']),

        Meal("3 kuvana jaja i kefir, rajs kejk", [
                ingredients['jaja 10kom']*3,
                ingredients['kefir casa'],
                ingredients['rajs kejk']**0.5
        ], ['breakfast','dinner']),

        
        Meal("badem",[
                ingredients['badem']*50
        ], ['snack']),

        Meal("badem i kefir",[
                ingredients['badem']*50,
                ingredients['kefir casa']
        ], ['breakfast','dinner']),
        
        Meal("kuglice", [
                ingredients['urme']*4,
                ingredients['badem']*30
        ], ['snack','dinner']).portion(1/reduce_factor),

        Meal("krompir i pilece belo", [
                ingredients['pilece belo 100g']*300,
                ingredients['krompir']*350,
                ingredients["maslinovo ulje"]*13
        ], ['lunch','dinner']),

        Meal("brokoli i pilece belo", [
                ingredients['pilece belo 100g']*300,
                ingredients['brokoli']*200,
                ingredients["maslinovo ulje"]*13
        ], ['lunch','dinner']),

        Meal('skusa eva i dvopek',[
                ingredients['skusa eva 170g'],
                ingredients['dvopek']**0.5
        ], ['dinner']).portion(1/reduce_factor),

        Meal('skusa eva i krompir',[
                ingredients['skusa eva 170g'],
                ingredients['krompir']*400,
                ingredients["maslinovo ulje"]*13
        ], ['dinner']).portion(1/reduce_factor),

        #Meal('dvopek i humus', [
        #    ingredients['dvopek']**0.5,
        #    ingredients['humus']**0.25
        #], ['breakfast','dinner']).portion(1/reduce_factor),

        Meal('zott jogurt',[
                ingredients['zott jogurt']**1
        ], ['breakfast','snack']),

        Meal('avokado i pilece belo', [
                ingredients['avokado'],
                ingredients["maslinovo ulje"]*13,
                ingredients['pilece belo 100g']*300
        ], ['lunch','dinner']),

        Meal('suncokret',[
                ingredients['suncokret']*50
        ], ['snack']),

        Meal('ananas trecina', [
                ingredients['ananas']**0.3333
        ], ['snack','healthy','eye']),

        Meal('batat 2 kom i maslinovo ulje', [
                ingredients['batat kom']*2,
                ingredients["maslinovo ulje"]*13
        ], ['healthy']),

        Meal('fitnes hleb i avokado', [
                ingredients['fitnes hleb']*140,
                ingredients['avokado'],
                ingredients['grcki jogurt olimpus']**0.5
        ], ['breakfast','dinner','snack']).portion(1/reduce_factor),

        Meal('fitnes hleb i humus', [
                ingredients['fitnes hleb']*140,
                ingredients['humus']**0.5
        ],['breakfast','dinner','snack']).portion(1/reduce_factor),

        Meal('fitnes hleb, jaja i jogurt', [
                ingredients['fitnes hleb']*140,
                ingredients['jaja 10kom']*3,
                ingredients['grcki jogurt olimpus']**0.5
        ], ['breakfast','dinner','snack']).portion(1/reduce_factor),

        Meal('budabol', [
                ingredients['kinoa']*50,
                ingredients['avokado']**0.5,
                ingredients['batat kom']**0.5,
                ingredients['pasulj konzerva']**0.333,
                ingredients['paradajz'],
                ingredients['indijski orah']*50
        ],['lunch']).portion(1/reduce_factor),

        Meal('cija ovsene', [
                #ingredients['cija semenke 100gr']*15,
                ingredients['ovsene pahuljice']*50,
                ingredients['grcki jogurt olimpus']**0.5,
                ingredients['sojino mleko']*100
        ],['breakfast','snack','dinner']).portion(1/reduce_factor),

]

for idx, meal in enumerate(meals):
        meals[idx] = meal.portion(reduce_factor)

# Assert unique meal names
####################
check = set()
for meal in meals:
        assert meal.name not in check
        check.add(meal.name)

####################

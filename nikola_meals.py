from ingredient import *
from meal import Meal

meals = [

        #Meal("pastrmka i krompir salata", [
        #        ingredients["pastrmke"]**0.5,
        #        ingredients["krompir"]*350,
        #        ingredients["crveni luk kom"]
        #], ['lunch']),

        #Meal("pastrmka i brokoli", [
        #        ingredients["pastrmke"]**0.5,
        #        ingredients["brokoli"]**0.5
        #], ['lunch']),

        #Meal("spagete origigi",[
        #        ingredients["spagete"]*100,
        #        ingredients["crni luk kom"],
        #        ingredients["mleveno meso"]*300,
        #        ingredients["maslinovo ulje"]*20,
        #        #ingredients["pasirani paradajz"]
        #], ['lunch']),

        #Meal("cufte i pire", [
        #        ingredients["krompir"]*350,
        #        ingredients["mleveno meso"]*300,
        #        ingredients["jaja 10kom"]*1,
        #        ingredients["crni luk kom"]
        #], ['lunch']),

        Meal("kikiriki i banana",[
                ingredients['kikiriki']*100,
                ingredients['banana']*1
        ], ['breakfast','dinner','snack']),

        Meal("kikiriki",[
                ingredients['kikiriki']*100
        ], ['breakfast','snack','dinner']),

        Meal("ovsene i urme",[
                ingredients['ovsene pahuljice']*90,
                ingredients['jogurt']*330,
                ingredients['urme']*4
        ], ['breakfast','dinner']),

        Meal("ovsene i jogurt",[
                ingredients['ovsene pahuljice']*90,
                ingredients['jogurt']*330
        ], ['breakfast','snack','dinner']),

        Meal("ovsene i banana",[
                ingredients['ovsene pahuljice']*90,
                ingredients['jogurt']*330,
                ingredients['banana']
        ], ['breakfast','dinner','banana']),

        Meal("jabuka",[
                ingredients['jabuka']
        ], ['breakfast','snack','dinner']),

        Meal("kikiriki i jogurt",[
                ingredients['kikiriki']*100,
                ingredients['jogurt']*330
        ], ['breakfast','dinner','snack']),

        Meal("banana",[
                ingredients['banana']
        ], ['snack','breakfast','dinner','eye']),

        Meal("braon pirinac i pilece belo",[
                ingredients['pilece belo 100g']*300,
                #ingredients['pirinac 1kg']*90
                ingredients['braon pirinac 500g']*90,
                ingredients["maslinovo ulje"]*13
        ], ['lunch']),

        Meal("beli pirinac i pilece belo",[
                ingredients['pilece belo 100g']*300,
                ingredients['pirinac 1kg']*120,
                ingredients["maslinovo ulje"]*13
        ], ['lunch']),

        Meal("pilece belo",[
                ingredients['pilece belo 100g']*300,
                ingredients["maslinovo ulje"]*13
        ], ['lunch']),

        Meal("kajgana 3 jaja", [
                ingredients['jaja 10kom']*3,
                ingredients["maslinovo ulje"]*13
        ], ['breakfast','dinner']),

        Meal("3 kuvana jaja", [
                ingredients['jaja 10kom']*3,
        ], ['breakfast','dinner']),

        #Meal("3 belanca", [
        #        ingredients['belanca 10kom']*3,
        #], ['breakfast','dinner']),

        #Meal("pasulj i pilece belo", [
        #        ingredients['pasulj']*150,
        #        ingredients['pilece belo 100g']*300
        #], ['lunch']),

        Meal("badem",[
                ingredients['badem']*50
        ], ['breakfast','dinner','snack']),

        #Meal("leblebije",[
        #        ingredients['leblebije']*50
        #], ['breakfast','dinner','snack']),

        Meal("urme",[
                ingredients['urme']*5
        ], ['snack']),

        Meal("mleko solja",[
                ingredients['mleko']*250
        ], ['breakfast','snack','dinner']),

        Meal("pecurke i pilece belo",[
                ingredients['pilece belo 100g']*300,
                ingredients['pecurke']*200,
                ingredients["maslinovo ulje"]*13
        ], ['lunch']),

        Meal("krompir i pilece belo", [
                ingredients['pilece belo 100g']*300,
                ingredients['krompir']*350,
                ingredients["maslinovo ulje"]*13
        ], ['lunch']),

        Meal("brokoli i pilece belo", [
                ingredients['pilece belo 100g']*300,
                ingredients['brokoli']*200,
                ingredients["maslinovo ulje"]*13
        ], ['lunch']),

        #Meal("brokoli i pecurke",[
        #        ingredients['brokoli']*225,
        #        ingredients['pecurke']*200,
        #        ingredients["maslinovo ulje"]*13
        #], ['breakfast','dinner']),

        #Meal("grilovano povrce i pecurke",[
        #        ingredients['paradajz'],
        #        ingredients['paprika'],
        #        ingredients['crni luk kom'],
        #        ingredients['beli luk kom']*0.2,
        #        ingredients['patlidzan']**0.3333,
        #        ingredients['pecurke']*200,
        #        ingredients['avokado'],
        #        ingredients["maslinovo ulje"]*13
        #], ['breakfast','dinner']),

        Meal("orah",[
                ingredients['orah']*33
        ], ['snack','breakfast','dinner']),

        #Meal('sardina i beli pirinac',[
        #        ingredients['sardina'],
        #        ingredients['pirinac 1kg']*90
        #], ['breakfast','dinner','snack','healthy']),

        Meal('skusa eva 170g',[
                ingredients['skusa eva 170g']
        ], ['breakfast','dinner','snack','healthy','skusa']),

        Meal('sejk',[
                ingredients['ovsene pahuljice']*90,
                ingredients['mleko']*330,
                ingredients['banana']*1,
        ], ['breakfast','dinner','snack']),

        Meal("dvopek i humus", [
            ingredients["humus"]**0.33333,
            ingredients["dvopek"]**0.5,
        ],['breakfast','dinner','snack']),

        Meal("dvopek i avokado", [
            ingredients["avokado"],
            ingredients["dvopek"]**0.5,
        ],['breakfast','dinner','snack']),

        Meal("kinoa kinezi", [
            ingredients["kinoa"]*50,
            ingredients["kinezi miks"]*100,
            ingredients["kikiriki"]*20,
            ingredients["maslinovo ulje"]*13
        ], ['breakfast','lunch','dinner']),

        Meal("kinoa pecurke miks",[
                ingredients['kinoa']*50,
                ingredients['smrznuti miks']*100,
                ingredients['pecurke']*100,
                ingredients["maslinovo ulje"]*13
        ], ['breakfast','lunch','dinner']),

        Meal("pirinac, pecurke i miks",[
                ingredients['pirinac 1kg']*90,
                ingredients['smrznuti miks']*100,
                ingredients['pecurke']*100,
                ingredients["maslinovo ulje"]*13
        ], ['breakfast','lunch','dinner']),

        Meal('sejk (banana)',[
                ingredients['ovsene pahuljice']*90,
                ingredients['sojino mleko']*330,
                ingredients['banana']*1,
        ], ['breakfast','dinner','snack']),

        Meal('sejk (banana & orah)',[
                ingredients['ovsene pahuljice']*90,
                ingredients['sojino mleko']*330,
                ingredients['banana']*1,
                ingredients['orah']*33,
        ], ['breakfast','dinner','snack']),

        Meal('bulk sejk',[
                ingredients['ovsene pahuljice']*90,
                ingredients['mleko']*330,
                ingredients['banana']*1,
                ingredients["maslinovo ulje"]*30,
        ], ['breakfast','dinner','snack']),

        Meal('sejk (kravlji)',[
                ingredients['ovsene pahuljice']*90,
                ingredients['mleko']*330,
                ingredients['banana']*1
        ], ['breakfast','dinner','snack']),


        Meal('zott jogurt',[
                ingredients['zott jogurt']**1
        ], ['breakfast','dinner','snack']),

        #Meal('zbregov',[
        #        ingredients['zbregov']
        #], ['brekfast','dinner','snack']),

        Meal('avokado i pilece belo', [
                ingredients['avokado'],
                ingredients["maslinovo ulje"]*13,
                ingredients['pilece belo 100g']*300
        ], ['lunch']),

        Meal('heidi cokolada',[
                ingredients['heidi']
        ], ['breakfast','snack','dinner']),

        #Meal('rolovana piletina i brokoli',[
        #        ingredients['slanina']*70,
        #        ingredients['pilece belo 100g']*300,
        #        ingredients['brokoli']*200
        #], ['lunch']),

        #Meal('suncokret',[
        #        ingredients['suncokret']*50
        #], ['breakfast','dinner','snack']),

        #Meal("slanina i 3 jaja",[
        #        ingredients['jaja 10kom']*3,
        #        ingredients['slanina']*70
        #], ['breakfast','dinner']),

        #Meal("slanina i 5 jaja",[
        #        ingredients['jaja 10kom']*5,
        #        ingredients['slanina']*70
        #], ['breakfast','dinner']),

        Meal("kikiriki i dukatos",[
                ingredients['kikiriki']*100,
                ingredients['dukatos']*200
        ], ['breakfast','dinner','snack']),

        Meal("kajgana(5) i puter",[
                ingredients['jaja 10kom']*5,
                ingredients['puter']*30
        ], ['breakfast','dinner']),

        Meal("krompir i puter",[
                ingredients['krompir']*350,
                ingredients['puter']*50
        ], ['breakfast','dinner']),

        Meal("krompir luk i maslinovo ulje",[
                ingredients['krompir']*450,
                ingredients['crni luk kom'],
                ingredients["maslinovo ulje"]*13
        ], ['breakfast','dinner']),

        Meal("krompir brokoli i maslinovo ulje",[
                ingredients['krompir']*450,
                ingredients['brokoli']*200,
                ingredients["maslinovo ulje"]*13
        ], ['breakfast','dinner']),

        #Meal("pirinac i jaja",[
        #        ingredients['jaja 10kom']*3,
        #        ingredients['pirinac 1kg']*90
        #], ['breakfast','dinner']),

        #Meal("pirinac", [
        #        ingredients["pirinac 1kg"]*90,
        #],['breakfast','snack','dinner']),

        #Meal("rebarca uz brokoli i puter",[
        #        ingredients['rebarca']*450,
        #        ingredients['puter']*50,
        #        ingredients['brokoli']*200
        #], ['lunch']),

        #Meal("rebarca uz brokoli",[
        #        ingredients['rebarca']*450,
        #        ingredients['brokoli']*200
        #], ['lunch']),

        ##Meal("krmenadla uz brokoli i puter",[
        ##        ingredients['krmenadla 100g']*350,
        ##        ingredients['puter']*50,
        ##        ingredients['brokoli']*200
        ##], ['lunch']),

        #Meal("krmenadla uz brokoli",[
        #        ingredients['krmenadla 100g']*350,
        #        ingredients['brokoli']*200
        #],[]),

        #Meal('sladak kupus',[
        #        ingredients['kupus']*0.5,
        #        ingredients['krompir']*500,
        #        ingredients['pilece belo 100g']*500
        #], ['lunch']),

        #Meal('spanac', [
        #        ingredients['zaledjeni spanac']*100,
        #        ingredients['beli luk kom']*0.10,
        #        #ingredients['kiselo mleko'],
        #        ingredients["maslinovo ulje"]*13
        #], ['healthy','eye']),

        #Meal('2 sargarepe', [
        #        ingredients['sargarepa kom']*2
        #], ['healthy']),

        Meal('ananas trecina', [
                ingredients['ananas']**0.3333
        ], ['healthy','eye']),

        #Meal('kelj ceo', [
        #        ingredients['kelj kom']
        #], ['healthy']),

        Meal('grasak i dvopek', [
                ingredients['zaledjeni grasak']*225,
                ingredients['smrznuti miks']*100,
                #ingredients['crni luk kom'],
                #ingredients['sargarepa kom'],
                #ingredients['pilece belo 100g']*150,
                ingredients["maslinovo ulje"]*13,
                ingredients['dvopek']**0.5
        ], ['healthy']),

        #Meal('prokelj', [
        #        ingredients['zaledjeni prokelj']*70,
        #        ingredients["sargarepa kom"]*2,
        #        ingredients["maslinovo ulje"]*13
        #], ['healthy']),

        #Meal('pola crvenog kupusa', [
        #        ingredients['crveni kupus kom']*0.5
        #], ['healthy']),

        #Meal('batat 2 kom i maslinovo ulje', [
        #        ingredients['batat kom']*2,
        #        ingredients["maslinovo ulje"]*13
        #], ['healthy']),

        #Meal('cvekla kom', [
        #        ingredients['cvekla kom']
        #], ['healthy','eye']),

        #Meal('beli luk kom', [
        #        ingredients['beli luk kom']
        #], ['healthy']),

        #Meal('crveni luk kom', [
        #        ingredients['crveni luk kom']
        #], ['healthy']),

        #Meal('avokado i pecurke', [
        #        ingredients['avokado'],
        #        ingredients['pecurke']*200,
        #        ingredients["maslinovo ulje"]*13
        #], ['healthy']),

        #Meal('pola avokada', [
        #        ingredients['avokado']*0.5
        #], ['healthy']),

        #Meal('blitva i sardina', [
        #        ingredients['zamrznuta blitva'],
        #        ingredients['krompir']*350,
        #        ingredients['beli luk kom']*0.5,
        #        ingredients['sardina']
        #], ['healthy','breakfast','dinner']),

        #Meal('zelje i sardina', [
        #        ingredients['zelje veza'],
        #        ingredients['krompir']*350,
        #        ingredients['beli luk kom']*0.5,
        #        ingredients['sardina']
        #], ['healthy','breakfast','dinner']),

        #Meal('golica i jogurt',[
        #        ingredients['golica']*50,
        #        ingredients['jogurt']*330,
        #], ['healthy','snack','dinner']),

        Meal('golica',[
                ingredients['golica']*50
        ], ['healthy','snack','dinner']),

        #Meal('golica i dukatos',[
        #        ingredients['golica']*50,
        #        ingredients['dukatos']*200,
        #], ['healthy','snack','dinner']),

        #Meal('2x pomorandza',[
        #        ingredients["pomorandza u mrezi"]*2,
        #],['healthy','snack']),

        Meal('socivo',[
                ingredients["socivo"]*80,
                ingredients["maslinovo ulje"]*13,
                ingredients['smrznuti miks']*100,
                #ingredients["pasirani paradajz"]
        ],['healthy','breakfast','dinner']),

]

meals_dict = { x.name : x for x in meals }

#reduce_factor = 0.6
#for idx, meal in enumerate(meals):
#        meals[idx] = meal.portion(reduce_factor)

# Assert unique meal names
####################
check = set()
for meal in meals:
        try:
            assert meal.name not in check
        except AssertionError as e:
            print(meal.name)
            raise e
            
        check.add(meal.name)

####################

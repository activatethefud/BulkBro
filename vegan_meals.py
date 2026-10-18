#from ingredient import *
from ingredient import *
from meal import Meal

meals = [

        #Meal("pasulj i brokoli",[
        #        ingredients['pasulj konzerva'],
        #        ingredients['brokoli']*200
        #],['breakfast','lunch','dinner']),
        #
        #Meal("prebranac",[
        #        ingredients['pasulj konzerva'],
        #        ingredients['crni luk kom']
        #], ['breakfast','lunch','dinner']),
        #
        #Meal("pasulj i rukola",[
        #        ingredients['pasulj konzerva'],
        #        ingredients['rukola']**0.25
        #], ['breakfast','lunch','dinner']),

        Meal("tofu,pecurke,kinezi",[
                ingredients["tofu 250g pak"]**0.5,
                ingredients['pecurke']*100,
                ingredients["maslinovo ulje"]*13,
                ingredients["kinezi miks"]*200,
        ],['lunch','dinner']),
        
        Meal("tofu,kinezi",[
                ingredients["tofu 250g pak"],
                ingredients["maslinovo ulje"]*13,
                ingredients["kinezi miks"]*200,
        ],['lunch','dinner']),

        Meal("tofu pasta",[
                ingredients["tofu 250g pak"]**0.5,
                ingredients['integralna pasta']*100,
                ingredients["crni luk kom"]*1,
                ingredients['pasirani paradajz']**0.5
        ],['lunch','dinner','breakfast']),

        Meal("kikiriki i banana",[
                ingredients['kikiriki']*100,
                ingredients['banana']*1
        ], ['breakfast','dinner','snack']),
        
        Meal("kikiriki",[
                ingredients['kikiriki']*100
        ], ['snack','dinner']),

        #Meal("ovsene (urme)",[
        #        ingredients['ovsene pahuljice']*90,
        #        ingredients['sojino mleko']*330,
        #        ingredients['urme']*4

        #], ['breakfast','dinner']),
        
        Meal('ovsene (banana)',[
                ingredients['ovsene pahuljice']*90,
                ingredients['sojino mleko']*330,
                ingredients['banana']*1,
        ], ['breakfast','dinner','snack']),
        
        #Meal("ovsene i urme",[
        #        ingredients['ovsene pahuljice']*90,
        #        ingredients['jogurt']*330,
        #        ingredients['urme']*4
        #], ['breakfast','dinner']),

        #Meal("ovsene i jogurt",[
        #        ingredients['ovsene pahuljice']*90,
        #        ingredients['jogurt']*330
        #], ['breakfast','snack','dinner']),

        #Meal("ovsene i banana",[
        #        ingredients['ovsene pahuljice']*90,
        #        ingredients['jogurt']*330,
        #        ingredients['banana']
        #], ['breakfast','dinner','banana']),

        Meal("jabuka",[
                ingredients['jabuka']
        ], ['snack','dinner']),

        #Meal("kikiriki i jogurt",[
        #        ingredients['kikiriki']*100,
        #        ingredients['jogurt']*330
        #], ['breakfast','dinner','snack']),

        #Meal("banana",[
        #        ingredients['banana']
        #], ['snack','dinner','eye']),

        Meal("tofu pirinac", [
                ingredients['tofu 250g pak']**0.5,
                ingredients['pirinac 1kg']*70,
                ingredients["crni luk kom"]*1
        ], ['breakfast','lunch','dinner']),
 
        #Meal("kuglice", [
        #        ingredients['urme']*10,
        #        ingredients['badem']*100
        #], ['snack','dinner']),
        
        Meal("badem",[
                ingredients['badem']*50
        ], ['dinner','snack']),

        Meal("dvopek i humus", [
            ingredients["humus"]**0.33333,
            ingredients["dvopek"]**0.5,
        ],['breakfast','dinner','snack']),

        #Meal("dvopek i avokado", [
        #    ingredients["avokado"],
        #    ingredients["dvopek"]**0.5,
        #],['breakfast','dinner','snack']),

        #Meal("kinoa kinezi", [
        #    ingredients["kinoa"]*50,
        #    ingredients["kinezi miks"]*150,
        #    ingredients["kikiriki"]*20,
        #    ingredients["maslinovo ulje"]*13
        #], ['lunch','dinner']),
        #
        #Meal("kinoa pecurke miks",[
        #        ingredients['kinoa']*50,
        #        ingredients['smrznuti miks']*100,
        #        ingredients['pecurke']*50,
        #        ingredients["maslinovo ulje"]*13
        #], ['lunch','dinner']),


        #Meal('heidi cokolada',[
        #        ingredients['heidi']
        #], ['snack','dinner']),

        #Meal('suncokret',[
        #        ingredients['suncokret']*50
        #], ['dinner','snack']),


        Meal("krompir luk i maslinovo ulje",[
                ingredients['krompir']*450,
                ingredients['crni luk kom']*1,
                ingredients["maslinovo ulje"]*13
        ], ['dinner']),

        Meal("krompir brokoli i maslinovo ulje",[
                ingredients['krompir']*450,
                ingredients['brokoli']*200,
                ingredients["maslinovo ulje"]*13
        ], ['lunch','dinner']),


        Meal('spanac', [
                ingredients['zamrznuti spanac']*100,
                ingredients['beli luk']*15,
                #ingredients['kiselo mleko'],
                ingredients["maslinovo ulje"]*13
        ], ['snack','dinner','healthy','eye']),

        #Meal('ananas trecina', [
        #        ingredients['ananas']**0.3333
        #], ['healthy','eye']),

        #Meal('batat 2 kom i maslinovo ulje', [
        #        ingredients['batat kom']*2,
        #        ingredients["maslinovo ulje"]*13,
        #        ingredients['crni luk kom']**0.5
        #], ['healthy']),
        
        #Meal('avokado i pecurke', [
        #        ingredients['avokado'],
        #        ingredients['pecurke']*200,
        #        ingredients["crni luk kom"]*1,
        #        ingredients["maslinovo ulje"]*13
        #], ['healthy']),

        #Meal("protein sladoled", [
        #        ingredients['soypro']*28,
        #        ingredients['sojino mleko']*200,
        #        ingredients['banana']
        #], ['breakfast','dinner','snack'])

        #Meal("protein sejk", [
        #        ingredients["soypro"]*28,
        #        ingredients["sojino mleko"]*300
        #], ["breakfast","snack","dinner"])

        Meal("dvopek, humus i rukola", [
                ingredients['dvopek']*55,
                ingredients['humus']*50,
                ingredients['rukola']*15
        ], ["breakfast","dinner"]),

        #Meal("leblebije", [
        #        ingredients["leblebije konzerva"]
        #], ["breakfast","dinner","snack"]),
        #
        #Meal("leblebije i rukola", [
        #        ingredients["leblebije konzerva"],
        #        ingredients["rukola"]*15
        #], ["breakfast","dinner","snack"]),
        #
        #Meal("leblebije i sok", [
        #        ingredients["leblebije konzerva"],
        #        ingredients["nutrino labs sok"]
        #], ["breakfast","dinner","snack"]),

        Meal("n. labs sok", [
                ingredients["nutrino labs sok"]
        ], ['snack','healthy']),

        Meal("seme bundeve", [
                ingredients["seme bundeve"]**0.5
        ], ["healthy","eye","snack"]),

        Meal("jumbo mix", [
                ingredients["jumbo mix"]
        ], ["snack","dinner","breakfast"])



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

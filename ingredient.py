#### WOLT ####

from copy import copy
import math
import sys
from nutrition import Nutrition

USAGE = """
        ingredients - dict of class Ingredient
        export_to_csv(ingredients: [Ingredient],filename: str)
        """

class Ingredient:

        id = 0
        
        def __init__(self,name: str,price,min_qty,rots_in,nutri_info = None,nutri_std_size = None):

                Ingredient.id += 1
                self.id = Ingredient.id
                self.name = name
                self.price = price
                self.min_qty = min_qty
                self.qty = min_qty
                self.rots_in = rots_in
                self.nutri_info = nutri_info

                if nutri_std_size == None:
                        self.nutri_std_size = self.min_qty
                else:
                        self.nutri_std_size = nutri_std_size

        def __repr__(self):
                return str(self.__dict__)

        def __eq__(self,other):
                return self.name == other.name

        def __pow__(self,other):
                
                if isinstance(other,(int,float)):

                        cpy = Ingredient(
                            self.name,
                            self.price,
                            self.min_qty,
                            self.rots_in,
                            self.nutri_info
                        )

                        cpy.qty = cpy.min_qty * other

                        if cpy.nutri_info is not None:
                                cpy.nutri_info *= cpy.qty/self.min_qty

                        return cpy


        def portion(self,other):
                
                if isinstance(other,(int,float)):

                        cpy = Ingredient(
                            self.name,
                            self.price,
                            self.min_qty,
                            self.rots_in,
                            self.nutri_info
                        )

                        cpy.qty = self.qty

                        if self.qty > 10:
                                cpy.qty = int(self.qty * other)

                                if cpy.nutri_info is not None:
                                        cpy.nutri_info *= other

                        return cpy

        def __mul__(self,other):
                if isinstance(other,(int,float)):

                        cpy = Ingredient(
                            self.name,
                            self.price,
                            self.min_qty,
                            self.rots_in,
                            self.nutri_info
                        )

                        #cpy = copy(self)
                        cpy.qty = other

                        if cpy.nutri_info is not None:
                                cpy.nutri_info *= cpy.qty/self.min_qty

                        return cpy
        
        def __hash__(self):
                return hash(self.name)
        
        def to_buy(self, qty = None):

                if qty == None:
                        qty = self.qty

                return math.ceil(qty/self.min_qty)

        def is_rotten(self):
                return self.rots_in <= 0

        def copy(self):
                cpy = Ingredient(
                        self.name,
                        self.price,
                        self.min_qty,
                        self.rots_in,
                        self.nutri_info
                )

                cpy.qty = self.qty
                return cpy

        def __add__(self,other):

                if isinstance(other,int):
                        return self.copy()

                cpy = self.copy()
                cpy.qty += other.qty
                return cpy

        def __sub__(self,other):
                
                cpy = self.copy()
                cpy.qty -= other.qty
                return cpy

        def __radd__(self,other):
                return self.__add__(other)

        def __gt__(self,other):
                if isinstance(other,(int,float)):
                        return self.qty > other
                else:
                        return self.qty > other.qty
        
        def set_rots_in(self, new_rots_in: int):
                self.rots_in = new_rots_in
                return self

        def csv(self):
                return "%s,%s,%s,%s,%s,%s,%s,%s" % (self.name,self.price,self.min_qty,self.rots_in,
                                                    self.nutri_info.kcal,
                                                    self.nutri_info.carb,
                                                    self.nutri_info.prot,
                                                    self.nutri_info.fat)

ingredients = {

        "pastrmka": Ingredient(
                "pastrmka",
                500,
                1,
                2,
                Nutrition(239,0,33.8,10.5)
        ),
        "borovnice": Ingredient(
                "borovnice",
                310,
                250,
                4,
                Nutrition(143,30.4,1.7,0.8)
        ),
        
        "rio mare tuna": Ingredient(
                "rio mare tuna",
                150,
                1,
                30,
                Nutrition(328,0,13.6,30.4)
        ),

        "rio mare kuskus": Ingredient(
                "rio mare kuskus",
                350,
                1,
                30,
                Nutrition(380.8,24,16,24)
        ),

        "pasta 500g": Ingredient(
                "pasta 500g",
                200,
                500,
                30,
                Nutrition(1794.1,355.9,62.4,10)
        ),

        "stari sir": Ingredient(
                "stari sir",
                0,
                100,
                10,
                Nutrition(258,0,15,22)
        ),


        "zuzu 1kg svetofor": Ingredient(
                "zuzu 1kg svetofor",
                142,
                1000,
                30,
                Nutrition(368,35.5,4.9,22.7)*10
        ),
        "kikiriki": Ingredient(
                "kikiriki",
                45,
                100,
                7,
                #Nutrition(567,16,26,49)
                Nutrition(567,25,26,49)
        ),
        "kikiriki svetofor": Ingredient(
                "kikiriki svetofor",
                349,
                1000,
                15,
                Nutrition(567,25,26,49)*10
        ),
        "jogurt":  Ingredient(
                "jogurt",
                194,
                1000,
                3,
                Nutrition(540,42,31,28)
        ),
        "banana": Ingredient(
                "banana",
                52,
                1,
                3,
                Nutrition(89,23,1.1,0.3),
                204
        ),
        "pasulj": Ingredient(
                "pasulj",
                259,
                500,
                90,
                Nutrition(176,21,8.1,7)*0.5
        ),
        "pasulj beli svetofor 1kg": Ingredient(
                "pasulj beli svetofor 1kg",
                223,
                1000,
                90,
                Nutrition(333,60,3.8,23.6)*10
        ),
        "zamrznuti grasak svetofor 1kg": Ingredient(
                "zamrznuti grasak svetofor 1kg",
                179,
                1000,
                90,
                Nutrition(810,145,54,4)
        ),
        "boranija svetofor 1kg": Ingredient(
                "boranija svetofor 1kg",
                179,
                1000,
                90,
                Nutrition(31,7.13,0.12,1.82)*10
        ),
        "ovsene svetofor 500g": Ingredient(
                "ovsene svetofor 500g",
                76,
                500,
                30,
                Nutrition(389,66.3,16.9,6.9)*5
        ),
        "pasirani paradajz svetofor": Ingredient(
                "pasirani paradajz svetofor",
                105,
                1000,
                10,
                Nutrition(25, 5.3, 0.9, 0.1)*10
        ),
        "pirinac svetofor": Ingredient(
                "pirinac svetofor",
                97,
                900,
                25,
                Nutrition(3522,804.2,66.5,5.4)*0.9
        ),
        "pilece belo 100g": Ingredient(
                "pilece belo 100g",
                45,
                100,
                90,
                Nutrition(164,0,27,6.4)
        ),
        "pirinac 1kg": Ingredient(
                "pirinac 1kg",
                279,
                800,
                90,
                Nutrition(3522,804.2,66.5,5.4)*0.8
        ),
        "ovsene pahuljice": Ingredient(
                "ovsene pahuljice",
                35,
                100,
                10,
                Nutrition(389,66.3,16.9,6.9)
        ),
        "jaja 10kom": Ingredient(
                "jaja 10kom",
                350,
                10,
                6,
                Nutrition(720,4,63,48),
                10*67
        ),
        "belanca 10kom": Ingredient(
                "jaja 10kom",
                350,
                10,
                6,
                Nutrition(153,2,16,0),
                10*67
        ),
        "jaje": Ingredient(
                "jaje",
                35,
                1,
                6,
                Nutrition(720,4,63,48)*0.1,
                67
        ),

        "badem": Ingredient(
                "badem",
                100,
                100,
                3,
                Nutrition(598,21,21,53)
        ),
        "badem svetofor": Ingredient(
                "badem svetofor",
                409,
                500,
                15,
                Nutrition(598,21,21,53)*(1.0/0.5)
        ),
        "urme svetofor": Ingredient(
                "urme svetofor",
                177,
                550,
                15,
                Nutrition(282,75,0.4,2.5)*5.5
                
        ),
        "urme": Ingredient(
                "urme",
                200,
                50,
                10,
                Nutrition(1150,300,10,0),
                11*50
        ),
        "sojino mleko": Ingredient(
            "sojino mleko",
            130,
            1000,
            3,
            Nutrition(38,0.7,3.2,1.9)*10
        ),
        "mleko": Ingredient(
                "mleko",
                200,
                1000,
                3,
                Nutrition(660,48,32,39)
        ),
        "krompir":Ingredient(
                "krompir",
                89,
                1000,
                15,
                Nutrition(770,167.9,19.4,1)
        ),
        "krompir svetofor": Ingredient(
                "krompir svetofor",
                53,
                1000,
                15,
                Nutrition(770,167.9,19.4,1)
        ),
        "orah": Ingredient(
                "orah",
                699,
                150,
                4,
                Nutrition(654,13.71,15.23,65.21)*1.5
        ),
        "skusa la perla": Ingredient(
                "skusa la perla",
                170,
                1,
                90,
                Nutrition(227,0,25.5,13.9),
                170
        ),
        "skusa eva 170g": Ingredient(
                "skusa eva 170g",
                410,
                1,
                90,
                Nutrition(583,0,13.8,58.65),
                170
        ),
        "sardina": Ingredient(
                "sardina",
                122,
                1,
                90,
                (Nutrition(286,0,19.5,22.9)+Nutrition(132,4.3,15.4,6))*(1/2),
                125
        ),
        "pecurke": Ingredient(
                "pecurke",
                200,
                400,
                3,
                Nutrition(88,13.2,12.4,1.2)
        ),
        "jabuka": Ingredient(
                "jabuka",
                40,
                1,
                5,
                Nutrition(104,28,0.5,0.3),
        ),
        "brokoli": Ingredient(
                "brokoli",
                249,
                400,
                90,
                Nutrition(153,29.7,12.6,1.8)*(4/4.5)
        ),
        "kupus": Ingredient(
                "kupus",
                139,
                1,
                5,
                Nutrition(250,58,13,1),
                750
        ),
        "zbregov": Ingredient(
                "zbregov",
                260,
                1,
                5,
                Nutrition(315,25.5,50,1.25),
                500
        ),
        "maslinovo ulje": Ingredient(
                "maslinovo ulje",
                0,
                1000,
                45,
                Nutrition(8884,0,0,1000)
        ),
        "dukatos": Ingredient(
                "dukatos",
                179,
                400,
                3,
                Nutrition(600,22.8,14.4,38.8)
        ),
        "heidi": Ingredient(
                "heidi",
                387,
                80,
                7,
                Nutrition(485,14,6,45.6)
        ),
        "avokado": Ingredient(
                "avokado",
                200,
                1,
                3,
                Nutrition(240,13,3,22),
                215
        ),
        "zamrznuti spanac": Ingredient(
                "zamrznuti spanac",
                200,
                400,
                95,
                Nutrition(92,14.4,11.6,1.6)
        ),
        # Prakticno isto kao spanac
        "zelje veza": Ingredient(
                "zelje veza",
                60,
                1,
                3,
                Nutrition(92,14.4,11.6,1.6)*0.3,
                50
        ),
        "zamrznuta blitva": Ingredient(
                "zamrznuta blitva",
                130,
                400,
                95,
                Nutrition(92,14.4,11.6,1.6)
        ),
        "suncokret": Ingredient(
                "suncokret",
                50,
                50,
                5,
                Nutrition(608,20,17,55)*0.5
        ),
        "rebarca": Ingredient(
                "rebarca",
                42.2,
                100,
                95,
                Nutrition(223,0,18.75,16)
        ),
        "puter": Ingredient(
                "puter",
                390,
                200,
                15,
                Nutrition(1457,0,0,164)
        ),
        "sargarepa kom": Ingredient(
                "sargarepa kom",
                64,
                4,
                5,
                Nutrition(25,6,0.5,0),
                98
        ),
        "ananas": Ingredient(
                "ananas",
                269,
                1000,
                3,
                Nutrition(452,119,4.9,0)
        ),
        "zaledjeni spanac": Ingredient(
                "zaledjeni spanac",
                200,
                450,
                95,
                Nutrition(103,16.335,12.87,1.755)
        ),
        "zaledjeni grasak": Ingredient(
                "zaledjeni grasak",
                179,
                400,
                95,
                Nutrition(810,145,54,4)*0.4
        ),
        "crveni kupus kom": Ingredient(
                "crveni kupus kom",
                100,
                1,
                3,
                Nutrition(0,0,0,0),
                540
        ),
        "batat kom": Ingredient(
                "batat kom",
                309,
                3,
                15,
                Nutrition(103,23.6,2.3,0.2)*3,
                130
        ),
        "cvekla kom": Ingredient(
                "cvekla kom",
                84,
                4,
                4,
                Nutrition(2.5*43,2.5*9.6,0,0)*4,
                110
        ),
        "beli luk": Ingredient(
                "beli luk",
                149,
                250,
                10,
                Nutrition(0,0,0,0),
                20
        ),
        "crni luk svetofor": Ingredient(
                "crni luk svetofor",
                76,
                100,
                10,
                Nutrition(349,83,9,0)
        ),
        "crni luk kom": Ingredient(
                "crni luk kom",
                40,
                1,
                6,
                Nutrition(60,14,1.7,0.2),
                150
        ),
        "crveni luk kom": Ingredient(
                "crveni luk kom",
                149,
                3,
                5,
                Nutrition(0,0,0,0),
                225
        ),
        "braon pirinac 500g": Ingredient(
               "braon pirinac 500g",
               160,
               500,
               30,
               Nutrition(560,120,11.5,4)
        ),
        #"golica": Ingredient(
        #        "golica",
        #        140,
        #        100,
        #        7,
        #        Nutrition(539,18,25,46)
        #),
        #"pomorandza u mrezi": Ingredient(
        #        "pomorandza u mrezi",
        #        100,
        #        6,
        #        6,
        #        Nutrition(330,60,5,0),
        #        6200
        #),
        #"socivo": Ingredient( # U zdravoj hrani
        #        "socivo",
        #        141,
        #        100,
        #        90,
        #        Nutrition(353,60.08,25.8,1.06)
        #),
        #"krmenadla 100g": Ingredient(
        #        "krmenadla 100g",
        #        55,
        #        100,
        #        90,
        #        Nutrition(121.586,0,15.85,6.16)
        #),
        #
        #"mleveno meso 100g": Ingredient(
        #        "mleveno meso 100g",
        #        70,
        #        100,
        #        90,
        #        Nutrition(19*4+19*8,0,19,19)
        #),
        #
        "kiselo mleko": Ingredient(
               "kiselo mleko",
               32,
               180,
               5,
               Nutrition(97.2, 7.2, 5.58, 5.04)
        ),
        
        #"paradajz": Ingredient(
        #        "paradajz",
        #        42,
        #        1,
        #        3,
        #        Nutrition(19,3,0,0),
        #        140
        #),
        #
        #"spagete": Ingredient(
        #        "spagete",
        #        118,
        #        400,
        #        60,
        #        Nutrition(1470, 294, 51.8, 6)
        #),
        #
        #"pastrmke": Ingredient(
        #        "pastrmke",
        #        362,
        #        500,
        #        120,
        #        Nutrition(644.8, 0.8, 74.8, 38.4)
        #),
        #
        "zott jogurt": Ingredient(
               "zott jogurt",
               200,
               1,
               3,
               Nutrition(130,12,20,0.4),
               130
        ),
        
        "pasirani paradajz": Ingredient(
                "pasirani paradajz",
                85,
                500,
                5,
                Nutrition(25, 5.3, 0.9, 0.1)*4
        ),
        
        "integralna pasta": Ingredient(
                "integralna pasta",
                87,
                400,
                90,
                Nutrition(371.46, 79.88, 9.84, 1.4)*4
        ),
        #
        "kefir casa": Ingredient(
               "kefir casa",
               55,
               1,
               7,
               Nutrition(97.2, 6.48, 5.4, 5.04),
               180
        ),
        
        #"leblebije": Ingredient(
        #        "leblebije",
        #        48,
        #        100,
        #        30,
        #        Nutrition(364,61,19,6)
        #),
        #
        #"paprika": Ingredient(
        #        "paprika",
        #        42,
        #        1,
        #        4,
        #        Nutrition(39,9,1.5,0.4),
        #        140
        #),

        "carska mesavina": Ingredient(
            "carska mesavina",
            181,
            1000,
            90,
            Nutrition(195, 37.6, 10, 0.4)*(1/0.4)
        ),

        "kinezi miks": Ingredient(
                "kinezi miks",
                219,
                400,
                90,
                Nutrition(195, 37.6, 10, 0.4)
        ),


        "pasulj konzerva": Ingredient(
                "pasulj konzerva",
                254,
                400,
                3,
                Nutrition(380, 56, 26, 0.8)
        ),

        #"crveni pasulj konzerva": Ingredient(
        #        "crveni pasulj konzerva",
        #        140,
        #        240,
        #        3,
        #        Nutrition(94, 14.0, 6.5, 0.2)*2.4
        #),

        "patlidzan": Ingredient(
                "patlidzan",
                165,
                1,
                4,
                Nutrition(152,32,6,0),
                550
        ),

        "kinoa": Ingredient(
           "kinoa",
           50,
           100,
           30,
           Nutrition(374,68.9,13.1,5.8)
        ),

        "humus": Ingredient(
            "humus",
            230,
            200,
            3,
            Nutrition(231,6.7,5.5,19)*2
        ),

        "dvopek": Ingredient(
            "dvopek",
            235,
            210,
            3,
            Nutrition(394, 68, 12, 7)*2.1
        ),

        "rajs kejk": Ingredient(
                "rajs kejk",
                120,
                100,
                5,
                Nutrition(393,78.3,8.3,4.3)
        ),

        #"grasak protein 1kg": Ingredient(
        #        "grasak protein 1kg",
        #        2549,
        #        1000,
        #        100,
        #        Nutrition(357, 3.0, 75, 5.0)*10.0
        #),
        #
        #"grasak protein 500gr": Ingredient(
        #        "grasak protein 500gr",
        #        2000,
        #        500,
        #        100,
        #        Nutrition(394, 9.8, 64, 9.9)*5.0
        #),
        #
        #"soypro": Ingredient(
        #        "soypro",
        #        0*2800,
        #        910,
        #        100,
        #        Nutrition(379,18,71,3.9)*9.10
        #),
        #
        #
        #"soja protein 700gr": Ingredient(
        #        "soja protein 700gr",
        #        2150,
        #        700,
        #        100,
        #        Nutrition(371, 1, 99, 3)*7.0
        #),

        "tofu 250g pak": Ingredient(
                "tofu 250g pak",
                300,
                250,
                3,
                Nutrition(142,2.02,14.17,9.5)*2.5
        ),

        "chia semenke maxi": Ingredient(
                "chia semenke maxi",
                148,
                100,
                30,
                Nutrition(486, 42, 17, 31)
        ),

        "leblebije maxi": Ingredient(
                "leblebije maxi",
                160,
                500,
                30,
                Nutrition(1820, 305, 95, 30)
        ),

        "grcki jogurt olimpus": Ingredient(
               "grcki jogurt olimpus",
               115,
               150,
               3,
               Nutrition(134,4,7,10)*1.5
        ),
        
        "fitnes hleb": Ingredient(
               "fitnes hleb",
               250,
               500,
               5,
               Nutrition(188,32.6,5.9,1.8)*5
        ),
        
        "indijski orah": Ingredient(
               "indijski orah",
               120,
               100,
               5,
               Nutrition(553,30.19,18.22,43.85)
        ),

        "rukola": Ingredient(
                "rukola",
                160,
                70,
                3,
                Nutrition(0,0,0,0)
        ),

        "fitnes hleb": Ingredient(
                "fitnes hleb",
                250,
                500,
                5,
                Nutrition(188,32.6,5.9,1.8)*5
        ),

        "indijski orah": Ingredient(
                "indijski orah",
                120,
                100,
                5,
                Nutrition(553,30.19,18.22,43.85)
        ),

        "palenta svetofor": Ingredient(
                "palenta svetofor",
                38,
                450,
                15,
                Nutrition(336,68.9,8.1,2)*(450/100)
        ),

        "posne makarone svetofor": Ingredient(
                "posne makarone svetofor",
                95,
                700,
                30,
                Nutrition(344, 65.87, 12.18, 1.86)*(700/100)
        ),
        "pileca prsa 8": Ingredient(
                "pileca prsa 8",
                150,
                8,
                2,
                Nutrition(98, 2, 18, 2)
        ),
        "tortilja 8": Ingredient(
                "tortilja 8",
                250,
                8,
                3,
                Nutrition(300, 53, 9.1, 4.9)*3.2
        ),
        "kikiriki puter dm": Ingredient(
                "kikiriki puter dm",
                265,
                170,
                10,
                Nutrition(647, 15.7, 20.4, 58.9)*1.7
        ),
        "dzem dm": Ingredient(
                "dzem dm",
                350,
                250,
                10,
                Nutrition(100, 20, 1, 1)*2.5
        ),
        "kokice": Ingredient(
                "kokice",
                17,
                100,
                15,
                Nutrition(375, 73, 11, 4)
        ),
        "carnex posni pasulj": Ingredient(
                "carnex posni pasulj",
                200,
                1,
                30,
                Nutrition(100,16,4.4,2.2)*4
        ),
        "carnex posni grasak": Ingredient(
                "carnex posni grasak",
                180,
                1,
                30,
                Nutrition(75,10,4.1,2.1)*4
        ),
        "socivo pasta": Ingredient(
                "socivo pasta",
                359,
                300,
                30,
                Nutrition(334,50,26,1.7)*3
        ),
        "blitva": Ingredient(
                "blitva",
                80,
                250,
                3,
                Nutrition(47, 9, 4, 0.5)
        ),
        "pomorandza": Ingredient(
                "pomorandza",
                20,
                1,
                7,
                Nutrition(61, 16, 1.2, 0.1)
        ),
        "spanać svez": Ingredient(
                "spanać svez",
                96,
                200,
                3,
                Nutrition(46, 7.2, 5.8, 0.8)
        ),
        "lanene semenke": Ingredient(
                "lanene semenke",
                150,
                100,
                30,
                Nutrition(534, 29, 18, 42)
        ),
        "najlepse zelje": Ingredient(
                "najlepse zelje",
                68,
                1,
                10,
                Nutrition(539, 54, 9, 32)*0.3 # 30 grama
        ),
        "sladoledi 10kom": Ingredient(
                "sladoledi 10kom",
                320,
                10,
                30,
                Nutrition(278, 24, 2.7, 19)*(100/278)
        ),


}

def export_to_csv(ingredients,filename = sys.stdout):
        s = "\n".join([i.csv() for i in ingredients.values()])
        if filename == sys.stdout:
                print(s)
        else:
                with open(filename,'w') as f:
                        f.write(s)

# duplicate ingredient check
set_check = set()
for ingr in ingredients.keys():
        assert ingr not in set_check
        set_check.add(ingr)

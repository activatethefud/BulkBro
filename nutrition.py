import math


class Nutrition:

    max_kcal = 1
    min_kcal = 10000
    max_prot = 1
    min_prot = 10000
    max_carb = 1
    min_carb = 10000
    max_fat = 1
    min_fat = 10000

    def __init__(self, kcal, carb, prot, fat):
        self.kcal = kcal
        self.carb = carb
        self.prot = prot
        self.fat = fat
    
    def to_list(self):
        return [
            self.kcal,
            self.carb,
            self.prot,
            self.fat
        ]
    
    def __eq__(self, other):
        assert isinstance(other, Nutrition)
        return self.kcal == other.kcal \
            and self.carb == other.carb \
            and self.prot == other.prot \
            and self.fat == other.fat

    def __hash__(self):
        return hash(str(self.kcal) + str(self.carb) + str(self.prot) + str(self.fat))

    @staticmethod
    def update_extremes(nutri):
        if isinstance(nutri,Nutrition):
                Nutrition.max_kcal = max(Nutrition.max_kcal,nutri.kcal)
                Nutrition.min_kcal = min(Nutrition.min_kcal,nutri.kcal)
                Nutrition.max_prot = max(Nutrition.max_prot,nutri.prot)
                Nutrition.min_prot = min(Nutrition.min_prot,nutri.prot)
                Nutrition.max_carb = max(Nutrition.max_carb,nutri.carb)
                Nutrition.min_carb = min(Nutrition.min_carb,nutri.carb)
                Nutrition.max_fat = max(Nutrition.max_fat,nutri.fat)
                Nutrition.min_fat = min(Nutrition.min_fat,nutri.fat)

                return nutri
        
        return None

    def __repr__(self):
        return f"(kcal: {self.kcal:.2f}, carb: {self.carb:.2f}, prot: {self.prot:.2f}, fat: {self.fat:.2f})"

    def __mul__(self, other):

        if isinstance(other, (int, float)):

            return Nutrition(
                self.kcal*other,
                self.carb*other,
                self.prot*other,
                self.fat*other
            )

    def __add__(self, other):

        if isinstance(other, int):
            return self

        return Nutrition(
            self.kcal + other.kcal,
            self.carb + other.carb,
            self.prot + other.prot,
            self.fat + other.fat
        )

    def __radd__(self, other):
        return self.__add__(other)

    def __lt__(self, other):

        if isinstance(other, Nutrition):
            return self.kcal <= other.kcal and self.carb <= other.carb and self.prot <= other.prot and self.fat <= other.fat

        return self

    def normalize(self):
        return self

    def dist_kcal(self, other):
        assert isinstance(other, Nutrition)
        return abs(self.kcal - other.kcal)
    
    def dist_prot(self, other):
        assert isinstance(other, Nutrition)
        return abs(self.prot - other.prot) if other.prot >= 0 and self.prot > 0 else 0

    def dist(self, other):
        first = self.normalize()
        second = other.normalize()

        if isinstance(other, Nutrition):
            #return math.sqrt((first.kcal-second.kcal)**2 + (first.carb-second.carb)**2 +
            #                 (first.prot-second.prot)**2 + (first.fat-second.fat)**2)
            #return math.sqrt(2*(first.kcal-second.kcal)**2 + (first.prot-second.prot)**2)
            #return math.sqrt((abs(first.kcal-second.kcal) > 65)*(first.kcal-second.kcal)**2 + (first.prot < second.prot)*(first.prot-second.prot)**2)
            kcal_diff = abs(first.kcal - second.kcal)
            kcal_diff_signal = kcal_diff > 65
            return math.sqrt((not kcal_diff_signal)*kcal_diff + kcal_diff_signal*kcal_diff**2 + (first.prot-second.prot)**2)

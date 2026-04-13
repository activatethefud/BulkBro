class Meal:
        
        def __init__(self,name,ingredients,categories):
                self.name = name
                self.ingredients = ingredients
                self.categories = categories

        def __repr__(self):
                #return str(self.__dict__)
                return str(self.name)

        def __hash__(self):
                return hash(self.name) + hash(self.nutri())

        def __eq__(self,other):
                assert isinstance(other, Meal)
                return self.__hash__() == other.__hash__()

        def nutri(self):
                return sum(x.nutri_info for x in self.ingredients)

        def default(self,o):
                return o.__dict__

        def __lt__(self, other):
                return self.name < other.name
        
        def portion(self, other):
                if isinstance(other, (int, float)):
                        for idx, ingr in enumerate(self.ingredients):
                                self.ingredients[idx] = ingr.portion(other)

                return self

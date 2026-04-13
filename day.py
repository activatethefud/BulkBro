class Day:

        def __init__(self, meals):
                self.meals = meals
                self._meal_nutris = [meal.nutri() for meal in meals]
                self._day_nutri = sum(self._meal_nutris)

        def __iter__(self):
                return self.meals.__iter__()

        def __len__(self):
                return len(self.meals)
        
        def __lt__(self, other):
                return True
        
        def __str__(self):
                str_rep = "["

                for idx,meal in enumerate(self.meals):
                        for word in meal.name.split():

                                if len(word) > 6:
                                        str_rep = " " + str_rep + word[:3] + "*" + word[-2:] + " "
                                else:
                                        str_rep = str_rep + word+ " "

                        if idx < len(self.meals)-1:
                                str_rep = str_rep + "   "

                str_rep = str_rep + "]"
                return str_rep
                #return str(self.meals)
        
        def __repr__(self):
                return self.__str__()

        def __getitem__(self,key):
                assert isinstance(key, int)
                return self.meals[key] if key < len(self.meals) else self.meals[-1]
        
        def set_meal(self, idx, new_meal):
                self.meals[idx] = new_meal
                self._meal_nutris = [meal.nutri() for meal in self.meals]
                self._day_nutri = sum(self._meal_nutris)
        
        def day_nutri(self):
                return self._day_nutri
        
        def meal_nutri(self, idx):
                return self._meal_nutris[idx]
"""Day class for meal planning.

Provides Day class representing a day of meals.
"""

class Day:
    """Represents a day containing multiple meals.
    
    Attributes:
        meals: List of Meal objects
    """
    
    def __init__(self, meals):
        """Initialize Day.
        
        Args:
            meals: List of Meal objects
        """
        self.meals = meals
        self._meal_nutris = [meal.nutri() for meal in meals]
        self._day_nutri = sum(self._meal_nutris)

    def __iter__(self):
        """Iterate over meals."""
        return self.meals.__iter__()

    def __len__(self):
        """Return number of meals."""
        return len(self.meals)
    
    def __lt__(self, other):
        """Always return True for sorting."""
        return True
    
    def __str__(self):
        """Return shortened meal names."""
        str_rep = "["

        for idx, meal in enumerate(self.meals):
            for word in meal.name.split():

                if len(word) > 6:
                    str_rep = " " + str_rep + word[:3] + "*" + word[-2:] + " "
                else:
                    str_rep = str_rep + word + " "

            if idx < len(self.meals) - 1:
                str_rep = str_rep + "   "

        str_rep = str_rep + "]"
        return str_rep
    
    def __repr__(self):
        """Return string representation."""
        return self.__str__()

    def __getitem__(self, key):
        """Get meal by index."""
        assert isinstance(key, int)
        return self.meals[key] if key < len(self.meals) else self.meals[-1]
    
    def set_meal(self, idx, new_meal):
        """Replace meal at index."""
        self.meals[idx] = new_meal
        self._meal_nutris = [meal.nutri() for meal in self.meals]
        self._day_nutri = sum(self._meal_nutris)
    
    def day_nutri(self):
        """Return total daily nutrition."""
        return self._day_nutri
    
    def meal_nutri(self, idx):
        """Return nutrition for specific meal."""
        return self._meal_nutris[idx]
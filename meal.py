"""Meal class for meal planning.

Provides Meal class representing a meal with ingredients and categories.
"""

from nutrition import Nutrition


class Meal:
    """Represents a meal with ingredients and nutritional information.
    
    Attributes
    ----------
    name : str
        Meal name
    ingredients : list
        List of Ingredient objects
    categories : list
        List of category strings
    """
    
    def __init__(self, name, ingredients, categories):
        """Initialize Meal.
        
        Parameters
        ----------
        name : str
            Meal name
        ingredients : list
            List of Ingredient objects
        categories : list
            List of category strings
        """
        self.name = name
        self.ingredients = ingredients
        self.categories = categories

    def __repr__(self):
        """Return meal name as string representation.
        
        Returns
        -------
        str
            Meal name
        """
        return str(self.name)

    def __hash__(self):
        """Return hash based on name and nutrition.
        
        Returns
        -------
        int
            Hash value
        """
        return hash(self.name) + hash(self.nutri())

    def __eq__(self, other):
        """Check equality with another Meal.
        
        Parameters
        ----------
        other : Meal
            Another Meal object
            
        Returns
        -------
        bool
            True if hashes match
        """
        assert isinstance(other, Meal)
        return self.__hash__() == other.__hash__()

    def nutri(self):
        """Return sum of ingredient nutrition.
        
        Returns
        -------
        Nutrition
            Sum of all ingredient nutritional values
        """
        return sum(x.nutri_info for x in self.ingredients)

    def default(self, o):
        """Return object dictionary.
        
        Parameters
        ----------
        o : object
            Any object with __dict__
            
        Returns
        -------
        dict
            Object's __dict__
        """
        return o.__dict__

    def __lt__(self, other):
        """Compare meals by name.
        
        Parameters
        ----------
        other : Meal
            Another Meal object
            
        Returns
        -------
        bool
            True if self.name < other.name
        """
        return self.name < other.name
    
    def portion(self, other):
        """Scale portion by multiplier.
        
        Multiplies each ingredient quantity by the given factor.
        
        Parameters
        ----------
        other : int or float
            Scaling factor
            
        Returns
        -------
        Meal
            Self (modified in place)
        """
        if isinstance(other, (int, float)):
            for idx, ingr in enumerate(self.ingredients):
                self.ingredients[idx] = ingr.portion(other)

        return self

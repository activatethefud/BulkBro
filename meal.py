"""Meal class for meal planning.

Provides Meal class representing a meal with ingredients and categories.
"""

class Meal:
    """Represents a meal with ingredients and nutritional information.
    
    Attributes:
        name: Meal name
        ingredients: List of Ingredient objects
        categories: List of category strings
    """
    
    def __init__(self, name, ingredients, categories):
        """Initialize Meal.
        
        Args:
            name: Meal name
            ingredients: List of Ingredient objects
            categories: List of category strings
        """
        self.name = name
        self.ingredients = ingredients
        self.categories = categories

    def __repr__(self):
        """Return meal name as string representation."""
        return str(self.name)

    def __hash__(self):
        """Return hash based on name and nutrition."""
        return hash(self.name) + hash(self.nutri())

    def __eq__(self, other):
        """Check equality with another Meal."""
        assert isinstance(other, Meal)
        return self.__hash__() == other.__hash__()

    def nutri(self):
        """Return sum of ingredient nutrition."""
        return sum(x.nutri_info for x in self.ingredients)

    def default(self, o):
        """Return object dictionary."""
        return o.__dict__

    def __lt__(self, other):
        """Compare meals by name."""
        return self.name < other.name
    
    def portion(self, other):
        """Scale portion by multiplier."""
        if isinstance(other, (int, float)):
            for idx, ingr in enumerate(self.ingredients):
                self.ingredients[idx] = ingr.portion(other)

        return self

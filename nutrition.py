"""Nutrition data class for meal planning.

Provides Nutrition class to represent nutritional values (kcal, carbs, protein, fat)
with arithmetic operations and comparison methods.
"""

import math


class Nutrition:
    """Represents nutritional values for a meal or day.
    
    Attributes:
        kcal: Kilocalories
        carb: Carbohydrates in grams
        prot: Protein in grams
        fat: Fat in grams
    """
    
    def __init__(self, kcal, carb, prot, fat):
        """Initialize Nutrition with macronutrient values.
        
        Args:
            kcal: Kilocalories
            carb: Carbohydrates in grams
            prot: Protein in grams
            fat: Fat in grams
        """
        self.kcal = kcal
        self.carb = carb
        self.prot = prot
        self.fat = fat
    
    def to_list(self):
        """Return values as list [kcal, carb, prot, fat]."""
        return [self.kcal, self.carb, self.prot, self.fat]
    
    def __eq__(self, other):
        """Check equality with another Nutrition object."""
        if not isinstance(other, Nutrition):
            return False
        return (self.kcal == other.kcal and
                self.carb == other.carb and
                self.prot == other.prot and
                self.fat == other.fat)
    
    def __hash__(self):
        """Return hash based on values."""
        return hash((self.kcal, self.carb, self.prot, self.fat))
    
    def __repr__(self):
        """Return string representation."""
        return f"(kcal: {self.kcal:.2f}, carb: {self.carb:.2f}, prot: {self.prot:.2f}, fat: {self.fat:.2f})"
    
    def __mul__(self, other):
        """Multiply all values by scalar."""
        if isinstance(other, (int, float)):
            return Nutrition(
                self.kcal * other,
                self.carb * other,
                self.prot * other,
                self.fat * other
            )
        return NotImplemented
    
    def __add__(self, other):
        """Add Nutrition values together."""
        if isinstance(other, int):
            return self
        if isinstance(other, Nutrition):
            return Nutrition(
                self.kcal + other.kcal,
                self.carb + other.carb,
                self.prot + other.prot,
                self.fat + other.fat
            )
        return NotImplemented
    
    def __radd__(self, other):
        """Reverse add support."""
        return self.__add__(other)
    
    def __lt__(self, other):
        """Less than comparison."""
        if isinstance(other, Nutrition):
            return (self.kcal <= other.kcal and
                    self.carb <= other.carb and
                    self.prot <= other.prot and
                    self.fat <= other.fat)
        return NotImplemented
    
    def dist_kcal(self, other):
        """Calculate absolute difference in kilocalories."""
        if not isinstance(other, Nutrition):
            return 0
        return abs(self.kcal - other.kcal)
    
    def dist_prot(self, other):
        """Calculate absolute difference in protein."""
        if not isinstance(other, Nutrition):
            return 0
        return abs(self.prot - other.prot) if other.prot >= 0 and self.prot > 0 else 0
    
    def dist(self, other):
        """Calculate weighted distance to another Nutrition."""
        if not isinstance(other, Nutrition):
            return 0
        first = self
        second = other
        kcal_diff = abs(first.kcal - second.kcal)
        kcal_diff_signal = kcal_diff > 65
        return math.sqrt(
            (not kcal_diff_signal) * kcal_diff +
            kcal_diff_signal * kcal_diff**2 +
            (first.prot - second.prot) ** 2
        )

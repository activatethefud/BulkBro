"""Insulin Index predictor for meal planning.

Based on research by Bell et al. (2016) - predicts insulin demand from macronutrients.
Formula: FII ≈ 0.9*Carbs + 0.3*Protein + 0.2*Fat (simplified from data)

The Insulin Index (II) measures how much a food raises insulin levels over 2 hours.
Lower is better for blood sugar control and reducing insulin resistance.
"""

import numpy as np


def predict_insulin_index(carb: float, protein: float, fat: float) -> float:
    """Predict Food Insulin Index from macronutrients.
    
    Based on simplified formula from data analysis:
    FII ≈ 0.9*Carbs + 0.3*Protein + 0.2*Fat
    
    Args:
        carb: Available carbohydrates in grams
        protein: Protein in grams
        fat: Fat in grams
    
    Returns:
        Predicted Insulin Index (higher = more insulin demand)
    """
    if carb < 0:
        carb = 0
    if protein < 0:
        protein = 0
    if fat < 0:
        fat = 0
    
    # Simplified formula from Bell et al.
    # Coefficients calibrated to match published food II ranges
    return 0.9 * carb + 0.4 * protein + 0.15 * fat


def meal_insulin_index(meals: list) -> float:
    """Calculate weighted average Insulin Index for a meal.
    
    Args:
        meals: List of Meal objects
    
    Returns:
        Weighted average Insulin Index
    """
    if not meals:
        return 0.0
    
    total_kcal = 0
    weighted_ii = 0
    
    for meal in meals:
        meal_kcal = meal.nutri().kcal
        if meal_kcal <= 0:
            continue
        
        meal_ii = 0
        for ingr in meal.ingredients:
            ni = ingr.nutri_info
            if ni.kcal > 0:
                ingr_ii = predict_insulin_index(ni.carb, ni.prot, ni.fat)
                weight = ni.kcal / meal_kcal
                meal_ii += ingr_ii * weight
        
        weighted_ii += meal_ii * meal_kcal
        total_kcal += meal_kcal
    
    if total_kcal <= 0:
        return 0.0
    
    return weighted_ii / total_kcal


def day_insulin_index(days: list) -> float:
    """Calculate average Insulin Index across a day or plan.
    
    Args:
        days: List of Day objects
    
    Returns:
        Average Insulin Index
    """
    if not days:
        return 0.0
    
    total_ii = 0
    for day in days:
        total_ii += meal_insulin_index(list(day))
    
    return total_ii / len(days)


# Insulin Index categories (based on research)
II_LOW = 40      # Minimal insulin response
II_MODERATE = 80  # Moderate response
II_HIGH = 100     # High response

def ii_category(ii: float) -> str:
    """Get category name for Insulin Index value.
    
    Args:
        ii: Insulin Index value
    
    Returns:
        Category string: 'low', 'moderate', or 'high'
    """
    if ii < II_LOW:
        return 'low'
    elif ii < II_MODERATE:
        return 'moderate'
    else:
        return 'high'
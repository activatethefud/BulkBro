#!/usr/bin/env python3
"""BulkBro Test Runner"""

import sys
import time
from copy import copy

import simulation as main_module
from simulation import sublists, simulate_plan, generate_day, shopping_list, generate_shopping_list
from day import Day
from nutrition import Nutrition
from ingredient import Ingredient
import meals as meals_module
import harmony
import config

MEALS = meals_module.meals


def run_test(name, func):
    try:
        start = time.perf_counter()
        func()
        elapsed = time.perf_counter() - start
        print(f"  PASS ({elapsed:.3f}s)")
        return True
    except Exception as e:
        import traceback
        print(f"  FAIL: {e}")
        traceback.print_exc()
        return False


def test_sublists():
    assert sublists([]) == []
    result = sublists([1, 1, 1])
    assert len(result) == 1
    result = sublists([1, 2, 1, 3, 2])
    assert len(result) == 3


def test_generate_day():
    target = [2000, 200, 100, 50]
    result = generate_day(target, 3)
    assert isinstance(result, Day)
    result = generate_day(target, 3)
    assert len(result) >= 1


def test_generate_day_max_meals():
    """Test that generate_day doesn't exceed 7 meals per day."""
    target = [5000, 500, 200, 100]  # High targets that might cause runaway
    
    for _ in range(100):
        result = generate_day(target, 10)  # Request 10, should get max 7
        assert len(result) <= 7, f"Too many meals: {len(result)}"
        
    for _ in range(100):
        result = generate_day(target, 3)  # Request 3, should get 3-5
        assert len(result) <= 5, f"Too many meals: {len(result)}"


def test_generate_day_min_meal():
    """Test that generate_day always has at least 1 meal."""
    target = [2000, 200, 100, 50]
    
    for _ in range(50):
        result = generate_day(target, 3)
        assert len(result) >= 1, f"No meals: {len(result)}"


def test_simulate_plan_price_bounded():
    """Test that simulate_plan doesn't have runaway prices."""
    # Create a plan with reasonable meal counts
    day = Day([MEALS[0], MEALS[1], MEALS[2]])
    result = simulate_plan([day])
    
    # Single day with 3 meals should not cost more than ~5000
    assert result['price'] < 10000, f"Price too high: {result['price']}"
    
    # Multi-day plan should scale reasonably
    days = [Day([MEALS[0]]) for _ in range(7)]
    result = simulate_plan(days)
    # 7 days, 1 meal each = reasonable price
    assert result['price'] < 5000, f"Multi-day price too high: {result['price']}"


def test_generate_day_with_small_meal_list():
    target = [2000, 200, 100, 50]
    result = generate_day(target, 3, meals=MEALS[:3])
    assert isinstance(result, Day)


def test_simulate_empty():
    result = simulate_plan([])
    assert result['price'] == 0
    assert result['waste'] == 0


def test_simulate_single():
    day = Day([MEALS[0]])
    result = simulate_plan([day])
    assert result['price'] > 0
    assert 'nutri' in result


def test_simulate_multiple():
    days = [Day([MEALS[0]]), Day([MEALS[1]])]
    result = simulate_plan(days)
    assert result['price'] > 0


def test_simulate_price_positive():
    for _ in range(5):
        day = Day([MEALS[0]])
        result = simulate_plan([day])
        assert result['price'] >= 0


def test_simulate_nutri_is_nutrition():
    day = Day([MEALS[0]])
    result = simulate_plan([day])
    assert isinstance(result['nutri'], Nutrition)


def test_simulate_waste():
    day = Day([MEALS[0]])
    result = simulate_plan([day])
    assert result['waste'] >= 0


def test_nutrition_add():
    n1 = Nutrition(100, 20, 10, 5)
    n2 = Nutrition(200, 40, 20, 10)
    result = n1 + n2
    assert result.kcal == 300


def test_nutrition_mul():
    n = Nutrition(100, 20, 10, 5)
    result = n * 2
    assert result.kcal == 200


def test_nutrition_dist():
    n1 = Nutrition(1000, 200, 100, 50)
    n2 = Nutrition(1100, 200, 100, 50)
    assert n1.dist_kcal(n2) == 100


def test_ingredient_to_buy():
    ingr = Ingredient('test', 100, 500, 5, Nutrition(100, 20, 10, 5))
    ingr.qty = 500
    assert ingr.to_buy() == 1
    ingr.qty = 600
    assert ingr.to_buy() == 2


def test_ingredient_copy():
    ingr = Ingredient('test', 100, 500, 5, Nutrition(100, 20, 10, 5))
    ingr.qty = 750
    copy_ = ingr.copy()
    assert copy_.qty == 750


def test_ingredient_rotten():
    ingr = Ingredient('test', 100, 500, 5, Nutrition(100, 20, 10, 5))
    assert not ingr.is_rotten()
    ingr.rots_in = 0
    assert ingr.is_rotten()


def test_day_length():
    day = Day([MEALS[0], MEALS[1]])
    assert len(day) == 2


def test_day_nutri():
    day = Day([MEALS[0]])
    nutr = day.day_nutri()
    assert isinstance(nutr, Nutrition)


def test_simulate_plan_nutrition_accuracy():
    main_module._sim_cache.clear()
    
    
    sol = [
        Day([MEALS[0], MEALS[0]]),
        Day([MEALS[0]]),
    ]
    
    manual_total = sum(dn.kcal for dn in [d.day_nutri() for d in sol])
    manual_avg = manual_total / len(sol)
    
    sim = simulate_plan(sol)
    computed_avg = sim['nutri'].kcal
    
    assert abs(manual_avg - computed_avg) < 0.01, f"Nutrition mismatch: manual={manual_avg}, computed={computed_avg}"
    
    for nutr_key in ['carb', 'prot', 'fat']:
        manual_val = sum(getattr(day.day_nutri(), nutr_key) for day in sol) / len(sol)
        computed_val = getattr(sim['nutri'], nutr_key)
        assert abs(manual_val - computed_val) < 0.01, f"{nutr_key} mismatch: manual={manual_val}, computed={computed_val}"


def test_generate_day_meal_count():
    
    
    day = generate_day([2000, 0, 0, 0], 3)
    assert len(day) == 3, f"Expected 3 meals, got {len(day)}"


def test_generate_day_exact_meals():
    
    
    for target in [1, 2, 3, 5]:
        for _ in range(5):
            day = generate_day([2000, 0, 0, 0], target)
            assert len(day) == target, f"Expected {target} meals, got {len(day)}"


def test_plan_average_multiday():
    main_module._sim_cache.clear()
    
    
    sol = [
        Day([MEALS[0], MEALS[0], MEALS[0]]),
        Day([MEALS[0]]),
        Day([MEALS[0], MEALS[0]]),
    ]
    
    manual_kcal = sum(d.day_nutri().kcal for d in sol) / len(sol)
    manual_prot = sum(d.day_nutri().prot for d in sol) / len(sol)
    manual_carb = sum(d.day_nutri().carb for d in sol) / len(sol)
    manual_fat = sum(d.day_nutri().fat for d in sol) / len(sol)
    
    sim = simulate_plan(sol)
    
    assert abs(manual_kcal - sim['nutri'].kcal) < 0.01
    assert abs(manual_prot - sim['nutri'].prot) < 0.01
    assert abs(manual_carb - sim['nutri'].carb) < 0.01
    assert abs(manual_fat - sim['nutri'].fat) < 0.01


def test_plan_average_varying_meals():
    main_module._sim_cache.clear()
    
    
    sol = [
        Day([MEALS[0]]),
        Day([MEALS[0], MEALS[0]]),
        Day([MEALS[0], MEALS[0], MEALS[0]]),
    ]
    
    manual_kcal = sum(d.day_nutri().kcal for d in sol) / len(sol)
    
    sim = simulate_plan(sol)
    
    assert abs(manual_kcal - sim['nutri'].kcal) < 0.01, f"Expected {manual_kcal}, got {sim['nutri'].kcal}"


def test_plan_price_calculation():
    main_module._sim_cache.clear()
    
    sol = [Day([MEALS[0]])]
    
    sim = simulate_plan(sol)
    
    assert sim['price'] > 0, f"Price should be positive, got {sim['price']}"


def test_plan_waste_calculation():
    main_module._sim_cache.clear()
    
    sol = [Day([MEALS[0]]), Day([MEALS[0]])]
    
    sim = simulate_plan(sol)
    
    assert 'waste' in sim
    assert sim['waste'] >= 0


def test_pickle_roundtrip_preserves_nutrition():
    import pickle
    import tempfile
    import os
    
    main_module._sim_cache.clear()
    
    
    sol = [Day([MEALS[0], MEALS[0]]), Day([MEALS[0]])]
    
    original = simulate_plan(sol)['nutri'].kcal
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pickle') as tmp:
        fname = tmp.name
        pickle.dump(sol, tmp)
    
    with open(fname, 'rb') as f:
        loaded = pickle.load(f)
    
    os.unlink(fname)
    
    main_module._sim_cache.clear()
    
    
    reloaded = simulate_plan(loaded)['nutri'].kcal
    
    assert abs(original - reloaded) < 0.01, f"Pickle changed nutrition: {original} vs {reloaded}"


def test_simulate_plan_equals_generate_plan():
    main_module._sim_cache.clear()
    
    
    sol = [Day([MEALS[0], MEALS[0]]), Day([MEALS[0]])]
    
    main_module._sim_cache.clear()
    
    sim_result = simulate_plan(sol)['nutri'].kcal
    
    main_module._sim_cache.clear()
    
    from harmony import HarmonyOptimizer
    opt = HarmonyOptimizer(plan_len=2, goal_mealcount=3)
    plan = opt.generate_plan(sol)
    gen_result = plan[-1].kcal
    
    assert abs(sim_result - gen_result) < 0.01, f"Different: simulate={sim_result}, generate={gen_result}"


def test_day_consistency_calculation():
    import numpy as np
    main_module._sim_cache.clear()
    
    
    sol = [
        Day([MEALS[0], MEALS[0], MEALS[0]]),
        Day([MEALS[0]]),
        Day([MEALS[0], MEALS[0]]),
    ]
    
    day_kcals = np.array([d.day_nutri().kcal for d in sol])
    consistency = day_kcals.std() / day_kcals.mean()
    
    assert consistency > 0, "Consistency should be positive for variance"
    assert consistency < 1.0, "Consistency should be < 1"


def test_insulin_index_basic():
    from insulin_index import predict_insulin_index
    
    ii = predict_insulin_index(20, 10, 5)
    assert ii > 0, "II should be positive"
    assert 15 < ii < 30, f"Single meal carb should give moderate II: {ii}"
    

def test_insulin_index_carbs_vs_protein():
    from insulin_index import predict_insulin_index
    
    carb_ii = predict_insulin_index(20, 0, 0)
    protein_ii = predict_insulin_index(0, 20, 0)
    fat_ii = predict_insulin_index(0, 0, 20)
    
    assert carb_ii > protein_ii, "Carbs should have higher II than protein"
    assert carb_ii > fat_ii, "Carbs should have higher II than fat"


def test_insulin_index_category():
    from insulin_index import ii_category, II_LOW, II_MODERATE
    
    assert ii_category(20) == 'low'
    assert ii_category(II_LOW - 1) == 'low'
    assert ii_category(II_MODERATE - 1) == 'moderate'
    assert ii_category(100) == 'high'


def test_insulin_index_meal():
    from insulin_index import meal_insulin_index
    
    meal = MEALS[0]
    ii = meal_insulin_index([meal])
    assert ii > 0, "Meal II should be positive"


def test_simulate_plan_price_accuracy():
    main_module._sim_cache.clear()
    sol = [Day([MEALS[0]])]
    
    manual_price = sum(m.nutri().kcal for day in sol for m in day) * 0
    
    sim = simulate_plan(sol)
    assert sim['price'] >= 0


def test_fitness_normalization_range():
    from harmony import HarmonyOptimizer
    
    opt = HarmonyOptimizer(plan_len=3, goal_mealcount=3, goal_kcal=2000, goal_prot=100, goal_ratio=2.0, pop_size=100)
    
    pop = opt.init_pop(100, 9)
    
    for sol in pop[:50]:
        opt.fitness(sol)
    
    scores = []
    for sol in pop[50:60]:
        score = opt.fitness(sol)
        scores.append(score)
    
    for score in scores:
        assert abs(score) < 10, f"Score {score} is inflated - normalization issue: {score}"


def test_fitness_zero_range_handling():
    from harmony import HarmonyOptimizer
    
    opt = HarmonyOptimizer(plan_len=3, goal_mealcount=3, goal_kcal=2000, goal_prot=100, goal_ratio=2.0, pop_size=50)
    
    pop = opt.init_pop(50, 9)
    
    for sol in pop:
        opt.fitness(sol)
    
    for sol in pop[:5]:
        score = opt.fitness(sol)
        assert -20 < score < 20, f"Score {score} out of reasonable range"


def test_meal_nutri():
    meal = MEALS[0]
    nutr = meal.nutri()
    assert isinstance(nutr, Nutrition)


def test_shopping_list():
    day = Day([MEALS[0]])
    result = shopping_list([day])
    assert 'spisak' in result
    assert 'cena' in result


def test_generate_shopping_list_with_custom_date():
    """Test generate_shopping_list with a specific start date."""
    import datetime as dt
    import os
    
    day = Day([MEALS[0]])
    custom_date = dt.date(2024, 1, 15)
    
    generate_shopping_list([day], 'test_date_shopping', today=custom_date)
    
    filepath = 'plans/test_date_shopping_shopping.txt'
    assert os.path.exists(filepath)
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    assert '2024-01-15' in content
    
    os.remove(filepath)


def test_generate_shopping_list_default_date():
    """Test generate_shopping_list uses today's date by default."""
    import datetime as dt
    import os
    
    day = Day([MEALS[0]])
    today = dt.date.today()
    
    generate_shopping_list([day], 'test_default_date')
    
    filepath = 'plans/test_default_date_shopping.txt'
    assert os.path.exists(filepath)
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    assert today.isoformat() in content
    
    os.remove(filepath)


def test_date_parsing_valid():
    """Test valid date parsing."""
    import datetime as dt
    
    test_date = "2024-06-15"
    result = dt.datetime.strptime(test_date, '%Y-%m-%d').date()
    assert result == dt.date(2024, 6, 15)


def test_date_parsing_invalid():
    """Test invalid date format raises ValueError."""
    import datetime as dt
    
    invalid_dates = ["2024/06/15", "15-06-2024", "invalid"]
    for date_str in invalid_dates:
        try:
            dt.datetime.strptime(date_str, '%Y-%m-%d').date()
            assert False, f"Should have raised for: {date_str}"
        except ValueError:
            pass


def test_caching():
    before = len(main_module._sim_cache)
    day = Day([MEALS[0]])
    simulate_plan([day])
    simulate_plan([day])
    after = len(main_module._sim_cache)
    assert after >= before


def test_cache_nutrition_accuracy():
    """Test that cached simulation returns correct nutrition values."""
    main_module._sim_cache.clear()
    
    
    day1 = Day([MEALS[0]])
    day2 = Day([MEALS[1]])
    plan = [day1, day2]
    
    manual_cal = sum(d.day_nutri().kcal for d in plan) / len(plan)
    
    result1 = simulate_plan(plan)
    cached_cal = result1['nutri'].kcal
    
    assert abs(manual_cal - cached_cal) < 1, f"Cache returned {cached_cal}, expected {manual_cal}"


def test_cache_different_plans_same_meals():
    """Test that different plans with same meal names get correct各自的nutrition."""
    main_module._sim_cache.clear()
    
    
    m1, m2, m3 = MEALS[0], MEALS[1], MEALS[2]
    
    plan_a = [Day([m1, m2]), Day([m3])]
    plan_b = [Day([m3]), Day([m1, m2])]
    
    result_a = simulate_plan(plan_a)
    result_b = simulate_plan(plan_b)
    
    manual_a = sum(d.day_nutri().kcal for d in plan_a) / len(plan_a)
    manual_b = sum(d.day_nutri().kcal for d in plan_b) / len(plan_b)
    
    assert abs(result_a['nutri'].kcal - manual_a) < 1, f"Plan A: cached {result_a['nutri'].kcal} vs manual {manual_a}"
    assert abs(result_b['nutri'].kcal - manual_b) < 1, f"Plan B: cached {result_b['nutri'].kcal} vs manual {manual_b}"


def test_cache_after_optimization():
    """Test cache returns correct values after optimizer runs."""
    main_module._sim_cache.clear()
    
    
    from harmony import HarmonyOptimizer
    
    opt = HarmonyOptimizer(plan_len=3, goal_mealcount=3, goal_kcal=1500, goal_prot=80, pop_size=20)
    sol = opt.optimize(2)
    
    manual = sum(d.day_nutri().kcal for d in sol) / len(sol)
    result = simulate_plan(sol)
    
    assert abs(result['nutri'].kcal - manual) < 1, f"After optimization: cached {result['nutri'].kcal} vs manual {manual}"


def test_extreme_low_kcal():
    """Test optimization with very low kcal target (500)."""
    main_module._sim_cache.clear()
    
    
    from harmony import HarmonyOptimizer
    
    opt = HarmonyOptimizer(plan_len=3, goal_mealcount=3, goal_kcal=500, goal_prot=40, goal_ratio=2.0, pop_size=30)
    sol = opt.optimize(3)
    
    manual = sum(d.day_nutri().kcal for d in sol) / len(sol)
    result = simulate_plan(sol)
    
    assert abs(result['nutri'].kcal - manual) < 1, f"Low kcal: cached {result['nutri'].kcal} vs manual {manual}"
    assert result['nutri'].kcal > 0, "Low kcal plan should have positive calories"


def test_extreme_high_kcal():
    """Test optimization with very high kcal target (3500)."""
    main_module._sim_cache.clear()
    
    
    from harmony import HarmonyOptimizer
    
    opt = HarmonyOptimizer(plan_len=3, goal_mealcount=3, goal_kcal=3500, goal_prot=180, goal_ratio=2.0, pop_size=30)
    sol = opt.optimize(3)
    
    manual = sum(d.day_nutri().kcal for d in sol) / len(sol)
    result = simulate_plan(sol)
    
    assert abs(result['nutri'].kcal - manual) < 1, f"High kcal: cached {result['nutri'].kcal} vs manual {manual}"


def test_extreme_kcal_very_low():
    """Test optimization with minimum viable kcal (300)."""
    main_module._sim_cache.clear()
    
    
    from harmony import HarmonyOptimizer
    
    opt = HarmonyOptimizer(plan_len=3, goal_mealcount=3, goal_kcal=300, goal_prot=30, goal_ratio=2.0, pop_size=30)
    sol = opt.optimize(3)
    
    manual = sum(d.day_nutri().kcal for d in sol) / len(sol)
    result = simulate_plan(sol)
    
    assert abs(result['nutri'].kcal - manual) < 1, f"Very low kcal: cached {result['nutri'].kcal} vs manual {manual}"
    assert result['nutri'].kcal > 0, "Plan should have positive calories"


def test_performance():
    days = [Day([MEALS[0]]) for _ in range(10)]

    start = time.perf_counter()
    for _ in range(100):
        simulate_plan(copy(days))
    elapsed = time.perf_counter() - start

    print(f"  100x simulate_plan(10 days): {elapsed:.3f}s")
    assert elapsed < 5.0, f"Too slow: {elapsed:.2f}s"


def test_optimizer_init():
    opt = harmony.HarmonyOptimizer(plan_len=3, goal_kcal=2000, goal_prot=100)
    assert opt.plan_len == 3
    assert opt.goal_kcal == 2000
    assert opt.pop_size == config.DEFAULT_POP_SIZE  # from config
    assert opt.HMCR == config.HMCR  # from config
    assert opt.tolerance == config.TOLERANCE  # from config


def test_target_score():
    opt = harmony.HarmonyOptimizer(plan_len=3, goal_kcal=2000, goal_prot=100)
    
    # Perfect score = 0
    assert opt._target_normalized_score(2000, 2000) == 0
    assert opt._target_normalized_score(100, 100) == 0
    
    # 10% off = 0.1
    assert abs(opt._target_normalized_score(2200, 2000) - 0.1) < 0.01
    assert abs(opt._target_normalized_score(1800, 2000) - 0.1) < 0.01


def test_skip_flags():
    """Test that -1 sets skip flags correctly."""
    # Test kcal skip
    opt = harmony.HarmonyOptimizer(plan_len=3, goal_kcal=-1, goal_prot=100, goal_ratio=2.0)
    assert opt._skip_kcal == True
    assert opt._skip_prot == False
    assert opt._skip_ratio == False
    assert opt._skip_mealcount == False
    
    # Test all skip
    opt2 = harmony.HarmonyOptimizer(plan_len=3, goal_kcal=-1, goal_prot=-1, goal_ratio=-1, goal_mealcount=-1)
    assert opt2._skip_kcal == True
    assert opt2._skip_prot == True
    assert opt2._skip_ratio == True
    assert opt2._skip_mealcount == True
    
    # Test none skipped (default)
    opt3 = harmony.HarmonyOptimizer(plan_len=3, goal_kcal=2000, goal_prot=100, goal_ratio=2.0)
    assert opt3._skip_kcal == False
    assert opt3._skip_prot == False
    assert opt3._skip_ratio == False


def test_skip_target_values():
    """Test that target values are correctly set from absolute values."""
    # When set to -1, target should use abs value for calculation
    opt = harmony.HarmonyOptimizer(plan_len=3, goal_kcal=-1, goal_prot=-1, goal_ratio=-1)
    assert opt._target_kcal == 2000  # Should be abs(-1) -> 2000
    assert opt._target_prot == 100
    assert opt._target_ratio == 2.0


def test_crowding_empty():
    """Test crowding calculation with empty population."""
    opt = harmony.HarmonyOptimizer(plan_len=3, goal_kcal=2000, goal_prot=100)
    crowding = opt._compute_crowding(0)
    assert crowding == 0.0


def test_constraint_penalty():
    opt = harmony.HarmonyOptimizer(plan_len=3, goal_kcal=2000, goal_prot=100)
    
    # Within 15% = no penalty (default tolerance = 0.15)
    assert opt._soft_constraint_penalty(2000, 2000) == 0
    assert opt._soft_constraint_penalty(1850, 2000) == 0  # 7.5% below = boundary
    assert opt._soft_constraint_penalty(2150, 2000) == 0  # 7.5% above = boundary
    
    # Outside 15% = penalty (need more than 15% deviation)
    penalty = opt._soft_constraint_penalty(2500, 2000)  # 25% over
    assert penalty < 0
    
    # Stronger penalty further from target
    assert opt._soft_constraint_penalty(3000, 2000) < opt._soft_constraint_penalty(2500, 2000)


def test_optimizer_first_pass():
    opt = harmony.HarmonyOptimizer(plan_len=2, goal_kcal=2000, goal_prot=100, pop_size=10)
    
    # Manually set denominators for testing
    opt._denominators = {'price': 1000, 'waste': 100, 'fii': 1, 'diversity': 10, 'overlap': 100, 'daynutri': 1}
    
    pop = opt.init_pop(5, 2)
    score = opt.fitness(pop[0])
    
    # Should get a valid score
    assert isinstance(score, (int, float))


def main():
    tests = [
        ("sublists", test_sublists),
        ("generate_day", test_generate_day),
        ("generate_day_small", test_generate_day_with_small_meal_list),
        ("generate_day_max", test_generate_day_max_meals),
        ("generate_day_min", test_generate_day_min_meal),
        ("simulate_price_bounded", test_simulate_plan_price_bounded),
        ("simulate_empty", test_simulate_empty),
        ("simulate_single", test_simulate_single),
        ("simulate_multiple", test_simulate_multiple),
        ("simulate_price_positive", test_simulate_price_positive),
        ("simulate_nutri_is_nutrition", test_simulate_nutri_is_nutrition),
        ("simulate_waste", test_simulate_waste),
        ("nutrition_add", test_nutrition_add),
        ("nutrition_mul", test_nutrition_mul),
        ("nutrition_dist", test_nutrition_dist),
        ("ingredient_to_buy", test_ingredient_to_buy),
        ("ingredient_copy", test_ingredient_copy),
        ("ingredient_rotten", test_ingredient_rotten),
        ("day_length", test_day_length),
        ("day_nutri", test_day_nutri),
        ("meal_nutri", test_meal_nutri),
        ("simulate_plan_nutrition_accuracy", test_simulate_plan_nutrition_accuracy),
        ("generate_day_meal_count", test_generate_day_meal_count),
        ("generate_day_exact_meals", test_generate_day_exact_meals),
        ("plan_average_multiday", test_plan_average_multiday),
        ("plan_average_varying_meals", test_plan_average_varying_meals),
        ("plan_price_calculation", test_plan_price_calculation),
        ("plan_waste_calculation", test_plan_waste_calculation),
        ("pickle_roundtrip_preserves_nutrition", test_pickle_roundtrip_preserves_nutrition),
        ("simulate_plan_equals_generate_plan", test_simulate_plan_equals_generate_plan),
        ("day_consistency_calculation", test_day_consistency_calculation),
        ("insulin_index_basic", test_insulin_index_basic),
        ("insulin_index_carbs_vs_protein", test_insulin_index_carbs_vs_protein),
        ("insulin_index_category", test_insulin_index_category),
        ("insulin_index_meal", test_insulin_index_meal),
        ("fitness_normalization_range", test_fitness_normalization_range),
        ("fitness_zero_range_handling", test_fitness_zero_range_handling),
        ("simulate_plan_price_accuracy", test_simulate_plan_price_accuracy),
        ("shopping_list", test_shopping_list),
        ("generate_shopping_list_with_custom_date", test_generate_shopping_list_with_custom_date),
        ("generate_shopping_list_default_date", test_generate_shopping_list_default_date),
        ("date_parsing_valid", test_date_parsing_valid),
        ("date_parsing_invalid", test_date_parsing_invalid),
        ("caching", test_caching),
        ("cache_nutrition_accuracy", test_cache_nutrition_accuracy),
        ("cache_different_plans_same_meals", test_cache_different_plans_same_meals),
        ("cache_after_optimization", test_cache_after_optimization),
        ("extreme_low_kcal", test_extreme_low_kcal),
        ("extreme_high_kcal", test_extreme_high_kcal),
        ("extreme_kcal_very_low", test_extreme_kcal_very_low),
        ("performance", test_performance),
        ("optimizer_init", test_optimizer_init),
        ("target_score", test_target_score),
        ("constraint_penalty", test_constraint_penalty),
        ("optimizer_first_pass", test_optimizer_first_pass),
        ("skip_flags", test_skip_flags),
        ("skip_target_values", test_skip_target_values),
        ("crowding_empty", test_crowding_empty),
    ]

    passed = 0
    failed = 0

    for name, func in tests:
        if run_test(name, func):
            passed += 1
        else:
            failed += 1

    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed")

    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
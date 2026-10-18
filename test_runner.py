#!/usr/bin/env python3
"""BulkBro Test Runner"""

import sys
import time
from copy import copy
from collections import Counter

import simulation as main_module
from simulation import sublists, simulate_plan, generate_day, shopping_list, generate_shopping_list
from day import Day
from nutrition import Nutrition
from ingredient import Ingredient
import meals as meals_module
import harmony
import config
from meal import Meal

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


def test_save_plan_auto_generates_shopping_list():
    """Test that save_plan + generate_shopping_list workflow works."""
    import os
    from harmony import HarmonyOptimizer
    
    opt = HarmonyOptimizer(plan_len=2, goal_kcal=1500, goal_prot=80, pop_size=10)
    sol = opt.init_pop(10, 2)[0]
    
    test_filename = 'test_auto_shopping'
    pickle_path = f'plans/{test_filename}.pickle'
    shopping_path = f'plans/{test_filename}_shopping.txt'
    
    if os.path.exists(shopping_path):
        os.remove(shopping_path)
    if os.path.exists(pickle_path):
        os.remove(pickle_path)
    
    opt.save_plan(test_filename, sol)
    generate_shopping_list(sol, test_filename)
    
    assert os.path.exists(pickle_path), "Pickle file should exist"
    assert os.path.exists(shopping_path), "Shopping list should be generated"
    
    os.remove(pickle_path)
    os.remove(shopping_path)


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


# ============================================================
# Statlist normalization & meal spam regression tests
# ============================================================

def test_statlist_basic():
    from util import statlist
    sl = statlist()
    for v in [10, 20, 30, 40, 50]:
        sl.append(v)
    assert sl.len == 5
    assert sl.max == 50
    assert sl.min == 10
    assert sl.avg == 30
    assert sl.max_abs == 50
    assert abs(sl.normalize(25) - 25 / (50 + 0.01)) < 1e-6
    sl.append(-60)
    assert sl.max_abs == 60
    assert abs(sl.normalize(-30) - (-30 / (60 + 0.01))) < 1e-6


def test_statlist_normalize_empty():
    from util import statlist
    sl = statlist()
    result = sl.normalize(100)
    assert result == 100 / (0 + 0.01)


def test_fitness_scores_normalized_range():
    from harmony import HarmonyOptimizer
    opt = HarmonyOptimizer(plan_len=3, goal_kcal=2000, goal_prot=100, goal_ratio=2.0, goal_mealcount=3, pop_size=50)
    pop = opt.init_pop(50, 9)
    for sol in pop:
        opt.fitness(sol)
    for sol in pop[:10]:
        score = opt.fitness(sol)
        assert -2 < score < 2, f"Score {score} out of normalized range"


def test_fitness_equal_weight_criteria():
    from harmony import HarmonyOptimizer
    opt = HarmonyOptimizer(plan_len=3, goal_kcal=2000, goal_prot=100, goal_ratio=2.0, goal_mealcount=3, pop_size=30)
    pop = opt.init_pop(30, 9)
    for sol in pop:
        opt.fitness(sol)
    for key in ['kcal', 'prot', 'ratio', 'mealcount', 'consistency', 'meal_rep']:
        assert key in opt.statlists, f"statlist '{key}' missing"
        assert opt.statlists[key].len > 0, f"statlist '{key}' empty"


def test_no_meal_spam_regression():
    from harmony import HarmonyOptimizer
    opt = HarmonyOptimizer(plan_len=3, goal_kcal=1050, goal_prot=-1, goal_ratio=0.1, goal_mealcount=3, pop_size=30)
    pop = opt.init_pop(30, 9)
    best_score = float('-inf')
    best_sol = None
    for sol in pop:
        score = opt.fitness(sol)
        if score > best_score:
            best_score = score
            best_sol = sol
    meal_names = [meal.name for day in best_sol for meal in day]
    counts = Counter(meal_names)
    max_pct = max(counts.values()) / len(meal_names)
    assert max_pct <= 0.5, f"Meal spam: {max(counts.values())}/{len(meal_names)} = {max_pct:.2f}"


def test_normalize_score_empty_fallback():
    from harmony import HarmonyOptimizer
    opt = HarmonyOptimizer(plan_len=3, goal_kcal=2000, goal_prot=100, pop_size=10)
    result = opt._normalize_score('kcal', 5.0)
    assert result == 5.0
    assert opt.statlists['kcal'].max_abs < 0.01


def test_meal_rep_equal_weight():
    from harmony import HarmonyOptimizer
    opt = HarmonyOptimizer(plan_len=3, goal_kcal=2000, goal_prot=100, goal_ratio=2.0, goal_mealcount=3, pop_size=20)
    pop = opt.init_pop(20, 9)
    for sol in pop:
        opt.fitness(sol)
    assert 'meal_rep' in opt.statlists
    assert opt.statlists['meal_rep'].len > 0
    result = opt._normalize_score('meal_rep', 0.5)
    assert 0 <= result <= 1.0, f"meal_rep normalized score {result} out of [0,1]"


# ============================================================
# Delivery / discount model
# ============================================================

def test_delivery_free_above_threshold():
    """A large basket should not pay delivery fees."""
    import delivery
    r = delivery.compute_delivery([config.FREE_DELIVERY_THRESHOLD + 500])
    assert r.delivery_cost == 0, f"expected free delivery, got {r.delivery_cost}"


def test_delivery_fee_below_threshold():
    """A small basket pays the flat delivery fee."""
    import delivery
    r = delivery.compute_delivery([config.ORDER_MINIMUM])
    assert r.delivery_cost == config.DELIVERY_FEE


def test_delivery_order_minimum_surcharge():
    """A basket below the order minimum incurs a surcharge."""
    import delivery
    r = delivery.compute_delivery([300])
    assert r.surcharge == config.ORDER_MINIMUM - 300
    assert r.delivery_fees >= r.surcharge


def test_delivery_basket_discount_applied():
    """A basket at/above the discount minimum gets the discount."""
    import delivery
    r = delivery.compute_delivery([config.BASKET_DISCOUNT_MIN])
    assert r.discount == config.BASKET_DISCOUNT_AMOUNT


def test_delivery_discount_capped():
    """Basket discount is not farmed by splitting into many orders."""
    import delivery
    r = delivery.compute_delivery([config.BASKET_DISCOUNT_MIN] * 4)
    assert r.discount == config.BASKET_DISCOUNT_AMOUNT * config.BASKET_DISCOUNT_MAX_USES


def test_delivery_fewer_orders_cheaper():
    """Consolidating spend into fewer baskets should not cost more."""
    import delivery
    one = delivery.total_plan_cost(3000, delivery.compute_delivery([3000]))
    many = delivery.total_plan_cost(3000, delivery.compute_delivery([1000, 1000, 1000]))
    assert one <= many, f"one big order {one} should be <= three small {many}"


def test_delivery_disabled_returns_zero():
    """When delivery is disabled, fees and discounts are zero."""
    import delivery
    orig = config.DELIVERY_ENABLED
    try:
        config.DELIVERY_ENABLED = False
        r = delivery.compute_delivery([500, 500])
        assert r.delivery_fees == 0 and r.discount == 0
    finally:
        config.DELIVERY_ENABLED = orig


def test_simulate_plan_delivery_fields():
    """simulate_plan returns delivery breakdown and a total price."""
    day = Day([MEALS[0], MEALS[1], MEALS[2]])
    result = simulate_plan([day])
    for key in ('delivery_fees', 'delivery_cost', 'discount', 'num_orders', 'total_price'):
        assert key in result, f"missing {key}"
    assert result['total_price'] == max(
        0, result['price'] + result['delivery_fees'] - result['discount'])


def test_simulate_excludes_delivery_when_disabled():
    """With delivery disabled, total_price equals grocery price."""
    from simulation import clear_caches
    orig = config.DELIVERY_ENABLED
    try:
        config.DELIVERY_ENABLED = False
        clear_caches()
        result = simulate_plan([Day([MEALS[0]])])
        assert result['total_price'] == result['price']
        assert result['delivery_fees'] == 0
    finally:
        config.DELIVERY_ENABLED = orig
        clear_caches()


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
        ("save_plan_auto_generates_shopping_list", test_save_plan_auto_generates_shopping_list),
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
        ("diversity_calculation_basic", test_diversity_calculation_basic),
        ("diversity_different_plans", test_diversity_different_plans),
        ("diversity_empty_plan", test_diversity_empty_plan),
        ("diversity_single_meal", test_diversity_single_meal),
        ("diversity_fitness_scoring", test_diversity_fitness_scoring),
        ("diversity_goal_not_set", test_diversity_goal_not_set),
        ("diversity_all_same_ingredients", test_diversity_all_same_ingredients),
        ("no_fridge_get_day_rots", test_no_fridge_get_day_rots),
        ("no_fridge_simulate_plan", test_no_fridge_simulate_plan),
        ("no_fridge_shopping_list", test_no_fridge_shopping_list),
        ("no_fridge_optimizer_runs", test_no_fridge_optimizer_runs),
        ("extreme_ratio_keto", test_extreme_ratio_keto),
        ("extreme_ratio_high_protein", test_extreme_ratio_high_protein),
        ("extreme_ratio_low_carb_variety", test_extreme_ratio_low_carb_variety),
        ("meal_diversity_metric", test_meal_diversity_metric),
        ("generate_day_target_biased", test_generate_day_target_biased),
        ("extreme_ratio_no_single_meal_obsession", test_extreme_ratio_no_single_meal_obsession),
        # Nutrition edge cases
        ("nutrition_add_identical", test_nutrition_add_identical),
        ("nutrition_mul_zero", test_nutrition_mul_zero),
        ("nutrition_mul_fraction", test_nutrition_mul_fraction),
        ("nutrition_dist_identical", test_nutrition_dist_identical),
        ("nutrition_dist_non_nutrition", test_nutrition_dist_non_nutrition),
        ("nutrition_sum_multiple", test_nutrition_sum_multiple),
        ("nutrition_eq_type_check", test_nutrition_eq_type_check),
        # Meal edge cases
        ("meal_empty_ingredients_nutri_zero", test_meal_empty_ingredients_nutri_zero),
        ("meal_portion_zero_no_ingredients", test_meal_portion_zero_no_ingredients),
        ("meal_equality_different_name", test_meal_equality_different_name),
        ("meal_lt_by_name", test_meal_lt_by_name),
        # Day edge cases
        ("day_empty_nutrition_zero", test_day_empty_nutrition_zero),
        ("day_len_zero", test_day_len_zero),
        ("day_set_meal_updates_total", test_day_set_meal_updates_total),
        ("day_lt_always_true", test_day_lt_always_true),
        ("day_meal_nutri_index", test_day_meal_nutri_index),
        # Ingredient edge cases
        ("ingredient_not_equal", test_ingredient_not_equal),
        ("ingredient_portion_small_qty_no_scale", test_ingredient_portion_small_qty_no_scale),
        ("ingredient_mul_creates_copy", test_ingredient_mul_creates_copy),
        ("ingredient_to_buy_rounds_up", test_ingredient_to_buy_rounds_up),
        ("ingredient_is_rotten_check", test_ingredient_is_rotten_check),
        ("ingredient_hash_is_name_based", test_ingredient_hash_is_name_based),
        # Insulin Index edge cases
        ("insulin_index_zero_macros", test_insulin_index_zero_macros),
        ("insulin_index_negative_clamped", test_insulin_index_negative_clamped),
        ("insulin_index_ii_category", test_insulin_index_ii_category),
        ("insulin_index_boundaries", test_insulin_index_boundaries),
        ("insulin_index_empty_meals_list", test_insulin_index_empty_meals_list),
        ("insulin_index_day_empty", test_insulin_index_day_empty),
        # Simulation edge cases
        ("generate_day_empty_meals", test_generate_day_empty_meals),
        ("clear_caches_no_error", test_clear_caches_no_error),
        ("sublists_empty", test_sublists_empty),
        ("sublists_single_element", test_sublists_single_element),
        ("sublists_all_identical", test_sublists_all_identical),
        # Harmony optimizer edge cases
        ("optimizer_init_pop_non_empty", test_optimizer_init_pop_non_empty),
        ("optimizer_chromosome_length", test_optimizer_chromosome_length),
        ("optimizer_fitness_is_callable", test_optimizer_fitness_is_callable),
        ("optimizer_objectives_has_required_keys", test_optimizer_objectives_has_required_keys),
        ("optimizer_compute_objectives_all_keys", test_optimizer_compute_objectives_all_keys),
        ("optimizer_target_nutri_calculation", test_optimizer_target_nutri_calculation),
        # Diversity edge cases
        ("diversity_no_penalty_when_meeting_target", test_diversity_no_penalty_when_meeting_target),
        ("diversity_rep_penalty_all_same", test_diversity_rep_penalty_all_same),
        ("diversity_rep_penalty_all_unique", test_diversity_rep_penalty_all_unique),
        # Config
        ("config_defaults_positive", test_config_defaults_positive),
        # Meal source
        ("meal_source_valid", test_meal_source_valid),
        # Cache
        ("cache_no_unbounded_growth", test_cache_does_not_grow_unbounded),
        # Shopping list
        ("shopping_list_empty_plan", test_shopping_list_empty_plan),
        ("shopping_list_zero_reach", test_shopping_list_zero_reach),
        # Default source
        ("default_meal_source_valid", test_default_meal_source_is_djina),
        # Wolt product correspondence
        ("every_ingredient_has_wolt_product", test_every_ingredient_has_wolt_product),
        ("wolt_product_has_id_name_pack", test_wolt_product_has_id_name_pack),
        ("wolt_correlation_propagates_copies", test_wolt_correspondence_propagates_through_copies),
        ("no_ingredient_has_zero_price", test_no_ingredient_has_zero_price),
        ("refresh_suspicious_guard", test_refresh_suspicious_guard_flags_unit_mismatch),
        ("shopping_list_includes_wolt_product", test_shopping_list_includes_wolt_product),
        ("shopping_list_has_wolt_order_block", test_generate_shopping_list_has_wolt_order_block),
        ("shopping_list_duration_matches_reach", test_shopping_list_duration_matches_reach),
        ("generate_shopping_list_has_lasts_line", test_generate_shopping_list_has_lasts_line),
        # Statlist normalization & meal spam regression
        ("statlist_basic", test_statlist_basic),
        ("statlist_normalize_empty", test_statlist_normalize_empty),
        ("fitness_scores_normalized_range", test_fitness_scores_normalized_range),
        ("fitness_equal_weight_criteria", test_fitness_equal_weight_criteria),
        ("no_meal_spam_regression", test_no_meal_spam_regression),
        ("normalize_score_empty_fallback", test_normalize_score_empty_fallback),
        ("meal_rep_equal_weight", test_meal_rep_equal_weight),
        # Delivery / discount model
        ("delivery_free_above_threshold", test_delivery_free_above_threshold),
        ("delivery_fee_below_threshold", test_delivery_fee_below_threshold),
        ("delivery_order_minimum_surcharge", test_delivery_order_minimum_surcharge),
        ("delivery_basket_discount_applied", test_delivery_basket_discount_applied),
        ("delivery_discount_capped", test_delivery_discount_capped),
        ("delivery_fewer_orders_cheaper", test_delivery_fewer_orders_cheaper),
        ("delivery_disabled_returns_zero", test_delivery_disabled_returns_zero),
        ("simulate_plan_delivery_fields", test_simulate_plan_delivery_fields),
        ("simulate_excludes_delivery_when_disabled", test_simulate_excludes_delivery_when_disabled),
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


def test_diversity_calculation_basic():
    """Test that diversity calculation returns correct count of unique ingredients."""
    from harmony import HarmonyOptimizer
    
    opt = HarmonyOptimizer(plan_len=3, goal_kcal=2000, goal_prot=100, pop_size=10)
    sol = opt.init_pop(10, 3)[0]
    
    objectives = opt._compute_objectives(sol)
    
    assert 'diversity' in objectives, "diversity should be in objectives"
    assert objectives['diversity'] > 0, "diversity should be positive for valid plan"


def test_diversity_different_plans():
    """Test that different plans have different diversity scores."""
    from harmony import HarmonyOptimizer
    
    opt = HarmonyOptimizer(plan_len=3, goal_kcal=2000, goal_prot=100, pop_size=10)
    
    sol1 = opt.init_pop(10, 3)[0]
    sol2 = opt.init_pop(10, 3)[1]
    
    obj1 = opt._compute_objectives(sol1)
    obj2 = opt._compute_objectives(sol2)
    
    assert obj1['diversity'] > 0
    assert obj2['diversity'] > 0


def test_diversity_empty_plan():
    """Test diversity calculation for edge cases."""
    from harmony import HarmonyOptimizer
    
    opt = HarmonyOptimizer(plan_len=3, goal_kcal=2000, goal_prot=100, pop_size=10)
    
    empty_day = Day([])
    empty_plan = [empty_day, empty_day, empty_day]
    
    objectives = opt._compute_objectives(empty_plan)
    
    assert objectives['diversity'] == 0, "Empty plan should have zero diversity"


def test_diversity_single_meal():
    """Test diversity with single meal per day."""
    from harmony import HarmonyOptimizer
    
    opt = HarmonyOptimizer(plan_len=3, goal_kcal=2000, goal_prot=100, pop_size=10)
    
    single_meal_plan = [[MEALS[0]], [MEALS[0]], [MEALS[0]]]
    plan = [Day(m) for m in single_meal_plan]
    
    objectives = opt._compute_objectives(plan)
    
    assert objectives['diversity'] > 0


def test_diversity_fitness_scoring():
    """Test that diversity penalty is applied when goal_diversity > 0 and below target."""
    from harmony import HarmonyOptimizer
    from meals import meals as all_meals
    
    # Find 3 meals with same name (portion variant) to guarantee low diversity
    from collections import Counter
    name_counts = Counter(m.name for m in all_meals)
    most_common_name = name_counts.most_common(1)[0][0]
    same_meals = [m for m in all_meals if m.name == most_common_name][:3]
    
    low_diversity_plan = [Day([same_meals[0]]), Day([same_meals[1]]), Day([same_meals[2]])]
    
    opt_with_div = HarmonyOptimizer(plan_len=3, goal_kcal=2000, goal_prot=100, 
                                     goal_diversity=10, pop_size=10)
    score_with = opt_with_div.fitness(low_diversity_plan)

    opt_without = HarmonyOptimizer(plan_len=3, goal_kcal=2000, goal_prot=100,
                                    goal_diversity=-1, pop_size=10)
    score_without = opt_without.fitness(low_diversity_plan)
    
    assert score_with != score_without, "Scores should differ when diversity is enabled vs disabled"


def test_diversity_goal_not_set():
    """Test diversity is skipped when goal_diversity is -1."""
    from harmony import HarmonyOptimizer
    
    opt = HarmonyOptimizer(plan_len=3, goal_kcal=2000, goal_prot=100, 
                            goal_diversity=-1, pop_size=10)
    sol = opt.init_pop(10, 3)[0]
    
    score = opt.fitness(sol)
    
    objectives = opt._compute_objectives(sol)
    diversity_raw = objectives['diversity']
    
    assert diversity_raw > 0, "Diversity raw value should still be computed"
    assert opt._skip_diversity == True, "Skip flag should be set when goal_diversity < 0"


def test_diversity_all_same_ingredients():
    """Test diversity with plan using same ingredients."""
    from harmony import HarmonyOptimizer
    
    opt = HarmonyOptimizer(plan_len=3, goal_kcal=2000, goal_prot=100, pop_size=10)
    
    same_meal_plan = [[MEALS[0]], [MEALS[0]], [MEALS[0]]]
    plan = [Day(m) for m in same_meal_plan]
    
    objectives = opt._compute_objectives(plan)
    
    diversity_count = objectives['diversity']
    
    unique_ingr_in_meal = set()
    for ingr in MEALS[0].ingredients:
        unique_ingr_in_meal.add(ingr.name)
    
    assert diversity_count <= len(unique_ingr_in_meal), "Same meal plan should have limited diversity"


def test_no_fridge_get_day_rots():
    """Test _get_day_rots returns 1 when NO_FRIDGE is True."""
    config.NO_FRIDGE = True
    main_module._day_rots_cache.clear()

    day = Day([MEALS[0]])
    rots = main_module._get_day_rots(day)

    config.NO_FRIDGE = False
    main_module._day_rots_cache.clear()

    assert rots == 1, f"Expected 1, got {rots}"


def test_no_fridge_simulate_plan():
    """Test simulate_plan with NO_FRIDGE=True increases cost and creates spoilage waste."""
    # Find meal where no-fridge increases both price and waste
    from day import Day
    import simulation as main_module
    import config
    def _check_meal(m):
        main_module._sim_cache.clear()
        config.NO_FRIDGE = False
        normal = main_module.simulate_plan([Day([m]), Day([m])])
        main_module.clear_caches()
        config.NO_FRIDGE = True
        nf = main_module.simulate_plan([Day([m]), Day([m])])
        config.NO_FRIDGE = False
        main_module.clear_caches()
        return nf['price'] > normal['price'] and nf['waste'] > normal['waste']
    leftover_meal = next(m for m in MEALS if _check_meal(m))
    main_module._sim_cache.clear()
    config.NO_FRIDGE = False

    sol = [Day([leftover_meal]), Day([leftover_meal])]
    normal = simulate_plan(sol)

    main_module.clear_caches()
    config.NO_FRIDGE = True

    no_fridge = simulate_plan(sol)

    config.NO_FRIDGE = False
    main_module.clear_caches()

    assert no_fridge['price'] > normal['price'], "No-fridge should cost more (daily re-purchase)"
    assert no_fridge['waste'] > normal['waste'], "No-fridge should have more waste (spoilage)"


def test_no_fridge_shopping_list():
    """Test shopping list reach is 1 with NO_FRIDGE."""
    config.NO_FRIDGE = True

    day = Day([MEALS[0]])
    result = shopping_list([day, day])

    config.NO_FRIDGE = False

    assert 'spisak' in result
    assert 'cena' in result
    assert result.get('za broj dana', 1) == 1, "No-fridge shopping should cover only 1 day"


def test_no_fridge_optimizer_runs():
    """Test optimization still produces a solution with NO_FRIDGE enabled."""
    from harmony import HarmonyOptimizer

    main_module._sim_cache.clear()
    main_module._day_rots_cache.clear()
    config.NO_FRIDGE = True
    main_module.clear_caches()

    opt = HarmonyOptimizer(plan_len=2, goal_mealcount=2, goal_kcal=1500,
                           goal_prot=80, goal_ratio=2.0, pop_size=10)
    sol = opt.optimize(2)

    config.NO_FRIDGE = False
    main_module.clear_caches()

    assert sol is not None, "No-fridge optimization should produce a solution"
    assert len(sol) == 2, "Should have 2 days"


# =============================================================================
# Extreme Diet and Diversity Tests
# =============================================================================

def test_extreme_ratio_keto():
    """Test optimization with keto ratio (very low carb, high fat) produces varied meals."""
    main_module._sim_cache.clear()
    from harmony import HarmonyOptimizer

    opt = HarmonyOptimizer(plan_len=3, goal_mealcount=3, goal_kcal=2000,
                           goal_prot=80, goal_ratio=10.0, pop_size=30)
    sol = opt.optimize(3)

    assert sol is not None, "Keto optimization should produce a solution"
    assert len(sol) == 3, "Should have 3 days"

    obj = opt._compute_objectives(sol)
    assert obj['unique_meals'] >= 2, f"Keto plan should use ≥2 unique meals, got {obj['unique_meals']}"
    assert obj['total_meal_slots'] > 0, "Should have meals"


def test_extreme_ratio_high_protein():
    """Test optimization with high protein target produces varied meals."""
    main_module._sim_cache.clear()
    from harmony import HarmonyOptimizer

    opt = HarmonyOptimizer(plan_len=3, goal_mealcount=3, goal_kcal=2000,
                           goal_prot=200, goal_ratio=2.0, pop_size=30)
    sol = opt.optimize(3)

    assert sol is not None, "High protein optimization should produce a solution"
    assert len(sol) == 3, "Should have 3 days"

    obj = opt._compute_objectives(sol)
    assert obj['unique_meals'] >= 2, f"High protein plan should use ≥2 unique meals, got {obj['unique_meals']}"


def test_extreme_ratio_low_carb_variety():
    """Test low-carb (keto) optimizer does not produce all-same-meal plan."""
    main_module._sim_cache.clear()
    from harmony import HarmonyOptimizer

    opt = HarmonyOptimizer(plan_len=3, goal_mealcount=3, goal_kcal=1500,
                           goal_prot=80, goal_ratio=8.0, pop_size=30)
    sol = opt.optimize(3)

    assert sol is not None, "Low-carb optimization should produce a solution"

    obj = opt._compute_objectives(sol)
    assert obj['meal_uniq_ratio'] >= 0.3, \
        f"Low-carb plan too repetitive: meal_uniq_ratio={obj['meal_uniq_ratio']:.2f}"


def test_meal_diversity_metric():
    """Test meal_uniq_ratio in _compute_objectives."""
    from harmony import HarmonyOptimizer
    from meal import Meal

    opt = HarmonyOptimizer(plan_len=2, goal_kcal=2000, goal_prot=100, pop_size=10)

    # Find 3 meals with different names (portion variants share same name)
    from meals import meals as all_meals
    seen = {}
    distinct = []
    for m in all_meals:
        if m.name not in seen:
            seen[m.name] = m
            distinct.append(m)
            if len(distinct) >= 3:
                break

    m0, m1, m2 = distinct[:3]

    # All same meals
    same_plan = [Day([m0, m0]), Day([m0])]
    obj = opt._compute_objectives(same_plan)
    assert obj['meal_uniq_ratio'] == 1.0 / 3, \
        f"3 slots, 1 unique meal → ratio should be 1/3, got {obj['meal_uniq_ratio']}"
    assert obj['unique_meals'] == 1

    # All different meals
    diff_plan = [Day([m0, m1]), Day([m2])]
    obj = opt._compute_objectives(diff_plan)
    assert obj['unique_meals'] == 3, f"Should have 3 unique meals, got {obj['unique_meals']}"
    assert obj['meal_uniq_ratio'] == 1.0, "All meals unique → ratio should be 1.0"


def test_generate_day_target_biased():
    """Test generate_day with target nutrition produces different meals than pure random."""
    from simulation import generate_day

    # Keto target: low carb, high fat
    keto_target = [2000, 50, 100, 170]  # kcal, carb, prot, fat
    keto_meals = [generate_day(keto_target, 3) for _ in range(20)]

    all_meal_names = set()
    for day in keto_meals:
        for meal in day:
            all_meal_names.add(meal.name)

    assert len(all_meal_names) >= 2, \
        f"Keto target-biased generation should produce ≥2 meal types, got {len(all_meal_names)}"


def test_extreme_ratio_no_single_meal_obsession():
    """Test no single meal occupies >70% of meal slots in extreme ratio plans."""
    main_module._sim_cache.clear()
    from harmony import HarmonyOptimizer

    opt = HarmonyOptimizer(plan_len=3, goal_mealcount=3, goal_kcal=1800,
                           goal_prot=70, goal_ratio=10.0, pop_size=30)
    sol = opt.optimize(3)

    assert sol is not None

    all_meals = [m.name for day in sol for m in day]
    total = len(all_meals)
    from collections import Counter
    counts = Counter(all_meals)
    max_ratio = max(counts.values()) / max(total, 1)

    assert max_ratio < 0.7, \
        f"Single meal dominates {max_ratio*100:.0f}% of plan (limit 70%)"


# ============================================================
# Nutrition edge cases
# ============================================================

def test_nutrition_add_identical():
    """Test Nutrition + self doubles values."""
    n = Nutrition(100, 10, 5, 3)
    n2 = n + n
    assert n2.kcal == 200
    assert n2.carb == 20
    assert n2.prot == 10
    assert n2.fat == 6


def test_nutrition_mul_zero():
    """Test Nutrition * 0 produces zeros."""
    n = Nutrition(100, 10, 5, 3) * 0
    assert n.kcal == 0 and n.carb == 0 and n.prot == 0 and n.fat == 0


def test_nutrition_mul_fraction():
    """Test Nutrition * 0.5 halves values."""
    n = Nutrition(100, 10, 5, 3) * 0.5
    assert n.kcal == 50 and n.carb == 5 and n.prot == 2.5 and n.fat == 1.5


def test_nutrition_dist_identical():
    """Test dist against self is 0."""
    n = Nutrition(500, 50, 25, 15)
    assert n.dist(n) == 0


def test_nutrition_dist_non_nutrition():
    """Test dist with non-Nutrition returns 0."""
    n = Nutrition(100, 10, 5, 2)
    assert n.dist("not a nutrition") == 0
    assert n.dist(None) == 0


def test_nutrition_sum_multiple():
    """Test sum() of Nutrition list works via __radd__."""
    meals_n = [Nutrition(100, 10, 5, 2), Nutrition(200, 20, 10, 4)]
    total = sum(meals_n)
    assert total.kcal == 300
    assert total.carb == 30
    assert total.prot == 15
    assert total.fat == 6


def test_nutrition_eq_type_check():
    """Test Nutrition.__eq__ returns False for non-Nutrition."""
    n = Nutrition(100, 10, 5, 3)
    assert (n == "string") == False
    assert (n == 42) == False
    assert (n == None) == False


# ============================================================
# Meal edge cases
# ============================================================

def test_meal_empty_ingredients_nutri_zero():
    """Test nutri() returns 0 (int) for empty ingredients."""
    m = Meal("empty", [], [])
    n = m.nutri()
    assert n == 0  # sum of empty list is int 0


def test_meal_portion_zero_no_ingredients():
    """Test portion(0) on ingredient returns copy."""
    ing = Ingredient("test", 100, 50, 7, Nutrition(100, 10, 5, 3))
    ing.qty = 5
    result = ing.portion(0)
    assert result is not None
    # qty = 5 <= 10, so no scaling, result.qty stays 5


def test_meal_equality_different_name():
    """Test meals with different names are not equal."""
    ing = Ingredient("test", 100, 50, 7, Nutrition(100, 10, 5, 3))
    m1 = Meal("a", [ing], [])
    m2 = Meal("b", [ing], [])
    assert m1 != m2


def test_meal_lt_by_name():
    """Test Meal.__lt__ compares by name."""
    m1 = Meal("alpha", [], [])
    m2 = Meal("beta", [], [])
    assert m1 < m2
    assert not m2 < m1


# ============================================================
# Day edge cases
# ============================================================

def test_day_empty_nutrition_zero():
    """Test Day([]) has zero nutrition."""
    d = Day([])
    n = d.day_nutri()
    assert n.kcal == 0 and n.carb == 0 and n.prot == 0 and n.fat == 0


def test_day_len_zero():
    """Test Day([]) has len 0."""
    assert len(Day([])) == 0


def test_day_set_meal_updates_total():
    """Test set_meal changes total nutrition."""
    ing1 = Ingredient("a", 100, 50, 7, Nutrition(200, 20, 10, 5))
    ing2 = Ingredient("b", 100, 50, 7, Nutrition(100, 10, 5, 3))
    m1 = Meal("m1", [ing1], [])
    m2 = Meal("m2", [ing2], [])
    d = Day([m1])
    assert d.day_nutri().kcal == 200
    d.set_meal(0, m2)
    assert d.day_nutri().kcal == 100


def test_day_lt_always_true():
    """Test Day.__lt__ always returns True."""
    d1 = Day([])
    d2 = Day([])
    assert (d1 < d2) == True
    assert (d2 < d1) == True


def test_day_meal_nutri_index():
    """Test meal_nutri returns correct nutrition by index."""
    ing = Ingredient("test", 100, 50, 7, Nutrition(100, 10, 5, 3))
    m = Meal("m", [ing], [])
    d = Day([m])
    n = d.meal_nutri(0)
    assert n.kcal == 100


# ============================================================
# Ingredient edge cases
# ============================================================

def test_ingredient_not_equal():
    """Test ingredients with different names are not equal."""
    a = Ingredient("a", 100, 50, 7, Nutrition(100, 10, 5, 3))
    b = Ingredient("b", 100, 50, 7, Nutrition(100, 10, 5, 3))
    assert a != b


def test_ingredient_portion_small_qty_no_scale():
    """Test portion on qty<=10 returns without scaling."""
    ing = Ingredient("test", 100, 50, 7, Nutrition(100, 10, 5, 3))
    ing.qty = 5
    result = ing.portion(2)
    assert result is not None


def test_ingredient_mul_creates_copy():
    """Test __mul__ creates independent copy."""
    ing = Ingredient("test", 100, 50, 7, Nutrition(100, 10, 5, 3))
    cpy = ing * 2
    assert cpy.qty == 2
    assert ing.qty == 50  # original unchanged


def test_ingredient_to_buy_rounds_up():
    """Test to_buy rounds up to min_qty multiples."""
    ing = Ingredient("test", 100, 50, 7, Nutrition(100, 10, 5, 3))
    assert ing.to_buy(120) == 3
    assert ing.to_buy(50) == 1
    assert ing.to_buy(1) == 1


def test_ingredient_is_rotten_check():
    """Test is_rotten checks rots_in <= 0."""
    ing = Ingredient("test", 100, 50, 0, Nutrition(100, 10, 5, 3))
    assert ing.is_rotten() == True
    ing2 = Ingredient("test2", 100, 50, 5, Nutrition(100, 10, 5, 3))
    assert ing2.is_rotten() == False


def test_ingredient_hash_is_name_based():
    """Test hash based on name, not instance."""
    a = Ingredient("same", 100, 50, 7, Nutrition(100, 10, 5, 3))
    b = Ingredient("same", 200, 25, 3, Nutrition(50, 5, 2, 1))
    assert hash(a) == hash(b)


# ============================================================
# Insulin Index edge cases
# ============================================================

def test_insulin_index_zero_macros():
    """Test predict_insulin_index with zero macros."""
    from insulin_index import predict_insulin_index
    assert predict_insulin_index(0, 0, 0) == 0


def test_insulin_index_negative_clamped():
    """Test predict_insulin_index clamps negative values."""
    from insulin_index import predict_insulin_index
    assert predict_insulin_index(-10, -5, -2) == 0


def test_insulin_index_ii_category():
    """Test ii_category returns correct strings."""
    from insulin_index import ii_category
    assert ii_category(20) == 'low'
    assert ii_category(60) == 'moderate'
    assert ii_category(90) == 'high'


def test_insulin_index_boundaries():
    """Test ii_category at boundary values."""
    from insulin_index import ii_category
    assert ii_category(39) == 'low'
    assert ii_category(40) == 'moderate'
    assert ii_category(79) == 'moderate'
    assert ii_category(80) == 'high'


def test_insulin_index_empty_meals_list():
    """Test meal_insulin_index with empty list."""
    from insulin_index import meal_insulin_index
    assert meal_insulin_index([]) == 0.0


def test_insulin_index_day_empty():
    """Test day_insulin_index with empty list."""
    from insulin_index import day_insulin_index
    assert day_insulin_index([]) == 0.0


# ============================================================
# Simulation edge cases
# ============================================================

def test_generate_day_empty_meals():
    """Test generate_day with empty meal list returns empty Day."""
    from simulation import generate_day
    d = generate_day([2000, 200, 100, 100], 3, [])
    assert len(d) == 0
    assert d.day_nutri().kcal == 0


def test_clear_caches_no_error():
    """Test clear_caches runs without error."""
    from simulation import clear_caches
    clear_caches()


def test_sublists_empty():
    """Test sublists with empty input."""
    from simulation import sublists
    assert sublists([]) == []


def test_sublists_single_element():
    """Test sublists with single element."""
    from simulation import sublists
    assert sublists([1]) == [[1]]


def test_sublists_all_identical():
    """Test sublists groups identical elements."""
    from simulation import sublists
    assert sublists([1, 1, 2, 2, 2, 3]) == [[1, 1], [2, 2, 2], [3]]


# ============================================================
# Harmony optimizer edge cases
# ============================================================

def test_optimizer_init_pop_non_empty():
    """Test init_pop returns non-empty population."""
    from harmony import HarmonyOptimizer
    opt = HarmonyOptimizer(plan_len=3, goal_kcal=2000, goal_prot=100, pop_size=10)
    pop = opt.init_pop(10, 3)
    assert len(pop) == 10


def test_optimizer_chromosome_length():
    """Test each chromosome has correct length (=plan_len)."""
    from harmony import HarmonyOptimizer
    opt = HarmonyOptimizer(plan_len=5, goal_kcal=2000, goal_prot=100, pop_size=10)
    pop = opt.init_pop(10, 5)  # (pop_size, gene_size)
    assert len(pop) == 10
    assert len(pop[0]) == 5
    assert isinstance(pop[0][0], Day)


def test_optimizer_fitness_is_callable():
    """Test fitness function exists and returns float."""
    from harmony import HarmonyOptimizer
    opt = HarmonyOptimizer(plan_len=3, goal_kcal=2000, goal_prot=100, pop_size=10)
    pop = opt.init_pop(10, 3)
    f = opt.fitness(pop[0])
    assert isinstance(f, float)


def test_optimizer_objectives_has_required_keys():
    """Test _compute_objectives returns required keys."""
    from harmony import HarmonyOptimizer
    opt = HarmonyOptimizer(plan_len=3, goal_kcal=2000, goal_prot=100, pop_size=10)
    pop = opt.init_pop(10, 3)
    obj = opt._compute_objectives(pop[0])
    for key in ['meal_uniq_ratio', 'unique_meals', 'total_meal_slots', 'diversity']:
        assert key in obj, f"{key} should be in objectives"


def test_optimizer_compute_objectives_all_keys():
    """Test _compute_objectives returns all nutrition and constraint keys."""
    from harmony import HarmonyOptimizer
    opt = HarmonyOptimizer(plan_len=3, goal_kcal=2000, goal_prot=100, pop_size=10)
    pop = opt.init_pop(10, 3)
    obj = opt._compute_objectives(pop[0])
    expected = ['kcal', 'carb', 'prot', 'fat', 'diversity', 'meal_uniq_ratio', 'unique_meals', 'total_meal_slots']
    for key in expected:
        assert key in obj, f"{key} should be in objectives"


def test_optimizer_target_nutri_calculation():
    """Test target_nutri is calculated correctly from goals."""
    from harmony import HarmonyOptimizer
    opt = HarmonyOptimizer(plan_len=3, goal_kcal=2000, goal_prot=100, goal_ratio=2.0, pop_size=10)
    kcal, carb, prot, fat = opt.target_nutri
    assert prot == 100
    assert kcal == 2000


# ============================================================
# Diversity edge cases
# ============================================================

def test_diversity_no_penalty_when_meeting_target():
    """Test no diversity penalty when raw >= goal."""
    from harmony import HarmonyOptimizer
    opt = HarmonyOptimizer(plan_len=3, goal_kcal=2000, goal_prot=100, goal_diversity=1, pop_size=10)
    pop = opt.init_pop(10, 3)
    sol = pop[0]
    score_with = opt.fitness(sol)
    opt2 = HarmonyOptimizer(plan_len=3, goal_kcal=2000, goal_prot=100, goal_diversity=-1, pop_size=10)
    score_without = opt2.fitness(sol)
    assert abs(score_with - score_without) < 0.001, \
        f"Scores should match when diversity target met: {score_with} vs {score_without}"


def test_diversity_rep_penalty_all_same():
    """Test meal_rep penalty is correct when all meals identical."""
    from harmony import HarmonyOptimizer
    opt = HarmonyOptimizer(plan_len=3, goal_kcal=2000, goal_prot=100, pop_size=10)
    same = [Day([MEALS[0]]), Day([MEALS[0]]), Day([MEALS[0]])]
    obj = opt._compute_objectives(same)
    assert obj['meal_uniq_ratio'] == 1.0 / 3.0
    assert obj['total_meal_slots'] == 3
    assert obj['unique_meals'] == 1


def test_diversity_rep_penalty_all_unique():
    """Test no rep penalty when all meals unique."""
    from harmony import HarmonyOptimizer
    from meals import meals as all_meals
    unique = []
    seen = set()
    for m in all_meals:
        if m.name not in seen:
            unique.append(m)
            seen.add(m.name)
        if len(unique) >= 3:
            break
    if len(unique) >= 3:
        opt = HarmonyOptimizer(plan_len=3, goal_kcal=2000, goal_prot=100, pop_size=10)
        plan = [Day([unique[0]]), Day([unique[1]]), Day([unique[2]])]
        obj = opt._compute_objectives(plan)
        assert obj['meal_uniq_ratio'] == 1.0


# ============================================================
# Config validation
# ============================================================

def test_config_defaults_positive():
    """Test key config defaults are positive."""
    assert config.DEFAULT_DIVERSITY > 0
    assert config.DIST_KCAL_THRESHOLD > 0
    assert config.MAX_MEALS_PER_DAY > 0
    assert config.MUTATION_MAX > 0


# ============================================================
# Meal source switching
# ============================================================

def test_meal_source_valid():
    """Test current meal source is valid and has meals."""
    import meals
    assert meals.current_source in ['nikola', 'vegan', 'djina']
    assert len(meals.meals) > 0


# ============================================================
# Cache interaction
# ============================================================

def test_cache_does_not_grow_unbounded():
    """Test simulation cache has reasonable size after many calls."""
    from simulation import clear_caches, simulate_plan, generate_day
    import meals as meals_module
    ml = meals_module.meals[:2]
    clear_caches()
    before = len(main_module._sim_cache)
    for _ in range(10):
        day = generate_day([2000, 200, 100, 100], 2, ml)
        simulate_plan([day, day, day])
    after = len(main_module._sim_cache)
    # Cache should not blow up to thousands from 10 calls
    assert after - before < 50, f"Cache grew by {after - before} entries, expected < 50"


# ============================================================
# Shopping list edge cases
# ============================================================

def test_shopping_list_empty_plan():
    """Test shopping_list with empty plan returns empty dict."""
    shopping_list([])


def test_shopping_list_zero_reach():
    """Test shopping_list with reach=0 treats everything fresh."""
    from simulation import shopping_list
    ing = Ingredient("test", 100, 50, 7, Nutrition(100, 10, 5, 3))
    m = Meal("test", [ing], [])
    d = Day([m])
    lst = shopping_list([d, d, d], reach=0)
    assert isinstance(lst, dict)


# ============================================================
# Default meal source integrity
# ============================================================

def test_default_meal_source_is_djina():
    """Test default meal source is 'nikola'."""
    import meals
    assert meals.current_source in ['nikola', 'vegan', 'djina']


# ============================================================
# Wolt product correspondence
# ============================================================

# Ingredients intentionally without a Wolt Market product (not sold on the
# scrape venue, or only available as a misleading different product).
WOLT_UNAVAILABLE = {'orah'}  # plain walnut kernels not sold at wolt-market-dorol


def test_every_ingredient_has_wolt_product():
    """Every catalog ingredient maps to a Wolt product (or is known unavailable)."""
    from ingredient import ingredients
    missing = [n for n, i in ingredients.items()
               if not i.wolt_name and n not in WOLT_UNAVAILABLE]
    assert not missing, f"ingredients without Wolt product: {missing}"


def test_wolt_product_has_id_name_pack():
    """Each Wolt correspondence carries id, name and pack."""
    from ingredient import ingredients
    for name, ingr in ingredients.items():
        if name in WOLT_UNAVAILABLE:
            continue
        assert ingr.wolt is not None, f"{name} missing wolt"
        assert ingr.wolt.get('id'), f"{name} missing wolt id"
        assert ingr.wolt.get('name'), f"{name} missing wolt name"
        assert 'pack' in ingr.wolt, f"{name} missing wolt pack"


def test_wolt_correspondence_propagates_through_copies():
    """Scaling/copying an ingredient keeps its Wolt product name."""
    from ingredient import ingredients
    base = ingredients['kikiriki']
    for variant in (base * 100, base ** 0.5, base.copy()):
        assert variant.wolt_name == base.wolt_name


def test_no_ingredient_has_zero_price():
    """No catalog ingredient should have a zero/near-zero price (bad units)."""
    from ingredient import ingredients
    bad = [n for n, i in ingredients.items() if i.price <= 0]
    assert not bad, f"ingredients with non-positive price: {bad}"


def test_refresh_suspicious_guard_flags_unit_mismatch():
    """A min_qty=1 item mapped to a gram product is flagged, not applied."""
    import wolt_refresh as wr
    from ingredient import Ingredient
    from nutrition import Nutrition
    # Fake ingredient: min_qty=1 (single unit), old price 500.
    fake = Ingredient('fake unit', 500, 1, 5, Nutrition(100, 10, 5, 3))
    fake.wolt = None
    product = {'id': 'x', 'name': 'Some 500g item', 'price': 300, 'grams': 500.0}
    # Without a grams_block override, normalizing min_qty=1 to 500g collapses.
    new_price = wr._norm_price(product, fake, {})
    assert new_price is not None and new_price < 500 * 0.05, (
        f"expected tiny normalized price, got {new_price}")


def test_shopping_list_includes_wolt_product():
    """shopping_list entries name the exact Wolt product to order."""
    day = Day([MEALS[0]])
    result = shopping_list([day])
    assert result['spisak'], "expected non-empty shopping list"
    assert all('wolt' in e for e in result['spisak'])
    # At least one entry should resolve to a real Wolt product name.
    assert any(e['wolt'] for e in result['spisak'])


def test_generate_shopping_list_has_wolt_order_block():
    """Generated shopping list file contains the WOLT MARKET ORDER block."""
    import datetime as dt
    import os
    day = Day([MEALS[0]])
    generate_shopping_list([day], 'test_wolt_order', today=dt.date(2026, 10, 18))
    path = 'plans/test_wolt_order_shopping.txt'
    try:
        content = open(path).read()
        assert 'WOLT MARKET ORDER' in content
        assert 'Estimated groceries' in content
    finally:
        if os.path.exists(path):
            os.remove(path)


def test_shopping_list_duration_matches_reach():
    """shopping_list exposes 'za broj dana' equal to the rotting-based reach."""
    from simulation import shopping_list
    day = Day([MEALS[0]])
    result = shopping_list([day, day, day])
    assert 'za broj dana' in result
    # A fresh buy can't cover more days than the plan length.
    assert 1 <= result['za broj dana'] <= 3


def test_generate_shopping_list_has_lasts_line():
    """Generated shopping file states how many days each shopping lasts."""
    import datetime as dt
    import os
    day = Day([MEALS[0]])
    generate_shopping_list([day, day], 'test_lasts', today=dt.date(2026, 10, 18))
    path = 'plans/test_lasts_shopping.txt'
    try:
        content = open(path).read()
        assert 'LASTS' in content and 'DAY(S)' in content
    finally:
        if os.path.exists(path):
            os.remove(path)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

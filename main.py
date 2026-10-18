"""BulkBro - CLI entry point for meal planning."""

import argparse
import pickle
import os

import numpy as np
from simulation import simulate_plan, generate_shopping_list, clear_caches
import config


def print_plan_summary(solution, targets):
    """Print a formatted summary of the optimized plan.
    
    Parameters
    ----------
    solution : list
        List of Day objects
    targets : dict
        Dict with keys: days, meals, kcal, prot, ratio
    """
    sim = simulate_plan(solution)
    nutri = sim['nutri']
    
    achieved_kcal = nutri.kcal / targets['kcal'] * 100 if targets['kcal'] > 0 else 0
    achieved_prot = nutri.prot / targets['prot'] * 100 if targets['prot'] > 0 else 0
    achieved_ratio = nutri.carb / nutri.fat if nutri.fat > 0 else 0
    
    day_kcals = [d.day_nutri().kcal for d in solution]
    day_prots = [d.day_nutri().prot for d in solution]
    var_kcal = np.std(day_kcals) / np.mean(day_kcals) * 100 if day_kcals else 0
    var_prot = np.std(day_prots) / np.mean(day_prots) * 100 if day_prots else 0
    
    var_desc = ("good" if var_kcal < config.VARIANCE_GOOD 
                else "moderate" if var_kcal < config.VARIANCE_MODERATE 
                else "poor")
    
    print("=" * config.PRINT_WIDTH)
    print("OPTIMIZATION COMPLETE".center(config.PRINT_WIDTH))
    print("=" * config.PRINT_WIDTH)
    print(f"Targets:     {targets['days']} days, {targets['meals']} meals/day, "
          f"{targets['kcal']}kcal, {targets['prot']}g prot, {targets['ratio']:.1f} c/f")
    print("-" * config.PRINT_WIDTH)
    print(f"Achieved:    {nutri.kcal:.0f}kcal ({achieved_kcal:.0f}%)   "
          f"{nutri.carb:.0f}g carb   {nutri.prot:.0f}g prot ({achieved_prot:.0f}%)   "
          f"{nutri.fat:.0f}g fat   {achieved_ratio:.1f} c/f ratio")
    print(f"Total Price: {sim['price']:.0f} RSD")
    if config.DELIVERY_ENABLED and sim.get('num_orders', 0) > 0:
        net_delivery = sim.get('delivery_fees', 0) - sim.get('discount', 0)
        print(f"Delivery:    {sim['delivery_fees']:.0f} RSD in {sim['num_orders']} order(s)"
              f"   Discount: -{sim.get('discount', 0):.0f} RSD")
        print(f"Grand Total: {sim.get('total_price', sim['price']):.0f} RSD "
              f"(items {sim['price']:.0f} {'+' if net_delivery >= 0 else '-'} "
              f"{abs(net_delivery):.0f})")
    print(f"Variance:    kcal ±{var_kcal:.0f}%, prot ±{var_prot:.0f}%  ({var_desc})")
    try:
        from simulation import shopping_list
        reach_days = shopping_list(solution)["za broj dana"]
        print(f"Shopping:    earliest fresh buy lasts {reach_days} day(s) "
              f"(limited by fastest-spoiling item)")
    except Exception:
        pass
    print("=" * config.PRINT_WIDTH)
    
    for i, day in enumerate(solution[:config.DAYS_PREVIEW]):
        dn = day.day_nutri()
        print(f"DAY {i+1}  {day}")
        print(f"      {dn.kcal:.0f}kcal | {dn.carb:.0f}c | {dn.prot:.0f}p | {dn.fat:.0f}f")
    
    if len(solution) > config.DAYS_PREVIEW:
        print(f"... ({len(solution) - config.DAYS_PREVIEW} more days)")
    print("=" * config.PRINT_WIDTH)


def main():
    parser = argparse.ArgumentParser(
        prog='bulkbro',
        description='BulkBro Meal Planner - Optimize meal plans for nutrition and cost'
    )

    parser.add_argument('--no-fridge', action='store_true',
                        help='Simulate no refrigerator (all ingredients spoil in 1 day)')
    parser.add_argument('--no-delivery', action='store_true',
                        help='Ignore delivery fees and basket discounts')

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # run subcommand
    run_parser = subparsers.add_parser('run', help='Run optimization')
    run_parser.add_argument('-d', '--days', type=int, default=config.DEFAULT_DAYS,
                           help=f'Number of days to plan (default: {config.DEFAULT_DAYS})')
    run_parser.add_argument('-m', '--meals', type=int, default=config.DEFAULT_MEALS_PER_DAY,
                          help=f'Meals per day (-1 to ignore, default: {config.DEFAULT_MEALS_PER_DAY})')
    run_parser.add_argument('-k', '--kcal', type=int, default=config.DEFAULT_KCAL,
                          help=f'Target daily calories (-1 to ignore, default: {config.DEFAULT_KCAL})')
    run_parser.add_argument('-p', '--protein', type=int, default=config.DEFAULT_PROTEIN,
                          help=f'Target daily protein in grams (-1 to ignore, default: {config.DEFAULT_PROTEIN})')
    run_parser.add_argument('-r', '--ratio', type=float, default=config.DEFAULT_RATIO,
                           help=f'Target carb/fat ratio (-1 to ignore, default: {config.DEFAULT_RATIO})')
    run_parser.add_argument('-i', '--diversity', type=int, default=config.DEFAULT_DIVERSITY,
                           help=f'Target number of unique ingredients (default: {config.DEFAULT_DIVERSITY})')
    run_parser.add_argument('-t', '--time-limit', type=int, default=config.DEFAULT_TIME_LIMIT,
                          help=f'Optimization time limit in seconds (default: {config.DEFAULT_TIME_LIMIT})')
    run_parser.add_argument('-o', '--output', type=str, default='meal_plan',
                          help='Output filename (default: meal_plan)')
    run_parser.add_argument('--pop-size', type=int, default=config.DEFAULT_POP_SIZE,
                          help=f'Population size (default: {config.DEFAULT_POP_SIZE})')
    run_parser.add_argument('--no-fridge', action='store_true',
                          help='Simulate no refrigerator (all ingredients spoil in 1 day)')
    run_parser.add_argument('--no-delivery', action='store_true',
                          help='Ignore delivery fees and basket discounts')

    # load subcommand
    load_parser = subparsers.add_parser('load', help='Load and display solution')
    load_parser.add_argument('solution', type=str, help='Solution pickle file')

    # wolt subcommand: show ingredient -> Wolt product correspondence
    wolt_parser = subparsers.add_parser(
        'wolt', help='Show ingredient -> Wolt Market product correspondence')
    wolt_parser.add_argument('-f', '--filter', type=str, default=None,
                            help='Only show ingredients whose name or Wolt product contains this text')

    args = parser.parse_args()

    if args.command is None:
        do_run_interactive(no_fridge=args.no_fridge, no_delivery=args.no_delivery)
        return

    if args.command == 'run':
        do_run(args)
    elif args.command == 'load':
        do_load(args)
    elif args.command == 'wolt':
        do_wolt(args)


def do_run(args):
    from harmony import HarmonyOptimizer

    if args.no_fridge:
        config.NO_FRIDGE = True
        clear_caches()
    if args.no_delivery:
        config.DELIVERY_ENABLED = False
        clear_caches()

    print("BulkBro Meal Planner")
    print("=" * 40)
    print(f"Days: {args.days}")
    print(f"Meals/day: {args.meals}")
    print(f"Target kcal: {args.kcal}")
    print(f"Target protein: {args.protein}g")
    print(f"Carb/fat ratio: {args.ratio}")
    print(f"Target diversity: {args.diversity}" if args.diversity > 0 else "Target diversity: -1 (ignored)")
    print(f"Time limit: {args.time_limit}s")
    print(f"No fridge: {args.no_fridge}")
    print(f"Delivery: {'off' if not config.DELIVERY_ENABLED else 'on'}")
    print("=" * 40)

    optimizer = HarmonyOptimizer(
        plan_len=args.days,
        goal_mealcount=args.meals,
        goal_kcal=args.kcal,
        goal_prot=args.protein,
        goal_ratio=args.ratio,
        goal_diversity=args.diversity,
        pop_size=args.pop_size
    )

    solution = optimizer.optimize(args.time_limit)

    if solution:
        print(f"\nOptimization complete!")
        print(f"Best fitness: {optimizer.best_fitness:.4f}")
        print_plan_summary(solution, {
            'days': args.days,
            'meals': args.meals,
            'kcal': args.kcal,
            'prot': args.protein,
            'ratio': args.ratio
        })
        filename = args.output
        optimizer.save_plan(filename, solution)
        generate_shopping_list(solution, filename)
        print(f"\nPlan saved to plans/{filename}_shopping.txt")
    else:
        print("No solution found")


def do_load(args):
    filename = args.solution
    if not filename.endswith('.pickle'):
        filename = f"plans/{filename}.pickle"

    try:
        sol = pickle.load(open(filename, 'rb'))
    except FileNotFoundError:
        print(f"Error: Solution file not found: {filename}")
        return

    print(f"Loaded solution from {filename}")
    print(f"Days: {len(sol)}")

    sim = simulate_plan(sol)
    print(f"Price: {sim['price']:.2f}")
    print(f"Nutrition: {sim['nutri']}")

    from simulation import shopping_list
    sl = shopping_list(sol)
    print(f"First shopping list lasts: {sl['za broj dana']} day(s) "
          f"(rotting-limited), {sl['cena']:.0f} RSD")

    for i, day in enumerate(sol):
        print(f"\nDay {i + 1}:")
        for meal in day:
            print(f"  - {meal.name}: {meal.nutri()}")


def do_wolt(args):
    """Print the ingredient -> Wolt Market product correspondence table."""
    from ingredient import ingredients

    rows = []
    for name, ingr in ingredients.items():
        if not ingr.wolt_name:
            continue
        if args.filter:
            needle = args.filter.lower()
            if needle not in name.lower() and needle not in ingr.wolt_name.lower():
                continue
        rows.append((name, ingr.wolt_name, ingr.wolt.get("pack", "")))
    rows.sort()

    print("=" * 96)
    print("INGREDIENT -> WOLT MARKET PRODUCT".center(96))
    print("=" * 96)
    print(f"{'ingredient':26} {'wolt product':44} {'pack':>10}")
    print("-" * 96)
    for name, wname, pack in rows:
        print(f"{name[:26]:26} {wname[:44]:44} {pack:>10}")
    print("-" * 96)
    print(f"{len(rows)} ingredient(s) shown")


def do_run_interactive(no_fridge=False, no_delivery=False):
    from harmony import HarmonyOptimizer

    print("BulkBro Meal Planner")
    print("=" * 40)

    plan_len = int(input("Generate for numof. days: "))
    goal_mealcount = int(input("Goal daily meal count: "))
    goal_kcal = int(input("Goal kcal: "))
    goal_prot = int(input("Goal prot: "))
    goal_ratio = float(input("Goal carb/fat ratio: "))
    if not no_fridge:
        no_fridge = input("No fridge (ingredients spoil daily)? (y/n): ").strip().lower() == 'y'
    else:
        print("No fridge: yes (from --no-fridge flag)")
    if not no_delivery:
        delivery_on = input("Include Wolt delivery fees/discounts? (y/n): ").strip().lower() != 'n'
    else:
        delivery_on = False
        print("Delivery: off (from --no-delivery flag)")
    time_limit = int(input("Improvement time limit (sec)?: "))

    print()

    if no_fridge:
        config.NO_FRIDGE = True
        clear_caches()
    if not delivery_on:
        config.DELIVERY_ENABLED = False
        clear_caches()

    optimizer = HarmonyOptimizer(
        plan_len=plan_len,
        goal_mealcount=goal_mealcount,
        goal_kcal=goal_kcal,
        goal_prot=goal_prot,
        goal_ratio=goal_ratio
    )

    solution = optimizer.optimize(time_limit)

    if solution:
        print(f"\nOptimization complete!")
        print(f"Best fitness: {optimizer.best_fitness:.4f}")
        print_plan_summary(solution, {
            'days': plan_len,
            'meals': goal_mealcount,
            'kcal': goal_kcal,
            'prot': goal_prot,
            'ratio': goal_ratio
        })

        save = input("Save plan? (y/n): ").strip().lower()
        if save == 'y':
            filename = input("Filename: ").strip()
            optimizer.save_plan(filename, solution)
            generate_shopping_list(solution, filename)
            print(f"Plan saved to plans/{filename}_shopping.txt")


if __name__ == '__main__':
    main()

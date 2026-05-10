"""BulkBro - CLI entry point for meal planning."""

import argparse
import pickle
import os

import numpy as np
from simulation import simulate_plan, generate_shopping_list
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
          f"{nutri.prot:.0f}g prot ({achieved_prot:.0f}%)   "
          f"{achieved_ratio:.1f} c/f ratio")
    print(f"Total Price: {sim['price']:.0f} RSD")
    print(f"Variance:    kcal ±{var_kcal:.0f}%, prot ±{var_prot:.0f}%  ({var_desc})")
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
    run_parser.add_argument('-i', '--diversity', type=int, default=-1,
                           help='Target number of unique ingredients (-1 to ignore, default: -1)')
    run_parser.add_argument('-t', '--time-limit', type=int, default=config.DEFAULT_TIME_LIMIT,
                          help=f'Optimization time limit in seconds (default: {config.DEFAULT_TIME_LIMIT})')
    run_parser.add_argument('-o', '--output', type=str, default='meal_plan',
                          help='Output filename (default: meal_plan)')
    run_parser.add_argument('--pop-size', type=int, default=config.DEFAULT_POP_SIZE,
                          help=f'Population size (default: {config.DEFAULT_POP_SIZE})')

    # shop subcommand
    shop_parser = subparsers.add_parser('shop', help='Generate shopping list')
    shop_parser.add_argument('solution', type=str, help='Solution pickle file')
    shop_parser.add_argument('-r', '--reach', type=int, default=-1,
                           help='Days to generate shopping for')
    shop_parser.add_argument('-s', '--start-date', type=str, default=None,
                           help='Starting date (YYYY-MM-DD, default: today)')

    # load subcommand
    load_parser = subparsers.add_parser('load', help='Load and display solution')
    load_parser.add_argument('solution', type=str, help='Solution pickle file')

    args = parser.parse_args()

    if args.command is None:
        do_run_interactive()
        return

    if args.command == 'run':
        do_run(args)
    elif args.command == 'shop':
        do_shop(args)
    elif args.command == 'load':
        do_load(args)


def do_run(args):
    from harmony import HarmonyOptimizer

    print("BulkBro Meal Planner")
    print("=" * 40)
    print(f"Days: {args.days}")
    print(f"Meals/day: {args.meals}")
    print(f"Target kcal: {args.kcal}")
    print(f"Target protein: {args.protein}g")
    print(f"Carb/fat ratio: {args.ratio}")
    print(f"Target diversity: {args.diversity}" if args.diversity > 0 else "Target diversity: -1 (ignored)")
    print(f"Time limit: {args.time_limit}s")
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
        print(f"\nSolution saved to plans/{filename}")
    else:
        print("No solution found")


def do_shop(args):
    import datetime as dt

    filename = args.solution
    if not filename.endswith('.pickle'):
        filename = f"plans/{filename}.pickle"

    try:
        sol = pickle.load(open(filename, 'rb'))
    except FileNotFoundError:
        print(f"Error: Solution file not found: {filename}")
        return

    print(f"Loaded solution from {filename}")
    name = args.solution.replace('.pickle', '')

    today = dt.date.today()
    date_input = input(f"Starting date (YYYY-MM-DD) [{today.isoformat()}]: ").strip()
    if date_input:
        try:
            start_date = dt.datetime.strptime(date_input, '%Y-%m-%d').date()
        except ValueError:
            print("Invalid date format. Using today.")
            start_date = today
    else:
        start_date = today

    generate_shopping_list(sol, name, args.reach, today=start_date)
    print("Shopping list saved")


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

    for i, day in enumerate(sol):
        print(f"\nDay {i + 1}:")
        for meal in day:
            print(f"  - {meal.name}: {meal.nutri()}")


def do_run_interactive():
    from harmony import HarmonyOptimizer

    print("BulkBro Meal Planner")
    print("=" * 40)

    plan_len = int(input("Generate for numof. days: "))
    goal_mealcount = int(input("Goal daily meal count: "))
    goal_kcal = int(input("Goal kcal: "))
    goal_prot = int(input("Goal prot: "))
    goal_ratio = float(input("Goal carb/fat ratio: "))
    time_limit = int(input("Improvement time limit (sec)?: "))

    print()

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
            print("Saved!")


if __name__ == '__main__':
    main()

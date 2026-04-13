"""BulkBro - CLI entry point for meal planning."""

import argparse
import pickle
import os

from simulation import simulate_plan, generate_shopping_list


def main():
    parser = argparse.ArgumentParser(
        prog='bulkbro',
        description='BulkBro Meal Planner - Optimize meal plans for nutrition and cost'
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # run subcommand
    run_parser = subparsers.add_parser('run', help='Run optimization')
    run_parser.add_argument('-d', '--days', type=int, default=3,
                           help='Number of days to plan (default: 3)')
    run_parser.add_argument('-m', '--meals', type=int, default=3,
                          help='Meals per day (-1 to ignore, default: 3)')
    run_parser.add_argument('-k', '--kcal', type=int, default=2000,
                          help='Target daily calories (-1 to ignore, default: 2000)')
    run_parser.add_argument('-p', '--protein', type=int, default=100,
                          help='Target daily protein in grams (-1 to ignore, default: 100)')
    run_parser.add_argument('-r', '--ratio', type=float, default=2.0,
                           help='Target carb/fat ratio (-1 to ignore, default: 2.0)')
    run_parser.add_argument('-t', '--time-limit', type=int, default=60,
                          help='Optimization time limit in seconds (default: 60)')
    run_parser.add_argument('-o', '--output', type=str, default='meal_plan',
                          help='Output filename (default: meal_plan)')
    run_parser.add_argument('--pop-size', type=int, default=150,
                         help='Population size (default: 150)')

    # shop subcommand
    shop_parser = subparsers.add_parser('shop', help='Generate shopping list')
    shop_parser.add_argument('solution', type=str, help='Solution pickle file')
    shop_parser.add_argument('-r', '--reach', type=int, default=-1,
                           help='Days to generate shopping for')

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
    print(f"Time limit: {args.time_limit}s")
    print("=" * 40)

    optimizer = HarmonyOptimizer(
        plan_len=args.days,
        goal_mealcount=args.meals,
        goal_kcal=args.kcal,
        goal_prot=args.protein,
        goal_ratio=args.ratio,
        pop_size=args.pop_size
    )

    solution = optimizer.optimize(args.time_limit)

    if solution:
        print(f"\nOptimization complete!")
        print(f"Best fitness: {optimizer.best_fitness:.4f}")
        filename = args.output
        optimizer.save_plan(filename, solution)
        print(f"\nSolution saved to plans/{filename}")
    else:
        print("No solution found")


def do_shop(args):
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
    generate_shopping_list(sol, name, args.reach)
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

        save = input("Save plan? (y/n): ").strip().lower()
        if save == 'y':
            filename = input("Filename: ").strip()
            optimizer.save_plan(filename, solution)
            print("Saved!")


if __name__ == '__main__':
    main()

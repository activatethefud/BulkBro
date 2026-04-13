"""Harmony Search Optimizer for BulkBro - Mathematically Improved."""

import time
import heapq
import functools
import random as rd
import numpy as np
from nutrition import Nutrition
from copy import copy
import datetime as dt
import threading
import os

import main
from day import Day
from meals import meals, ingredients_in_meals, ingredients_in_meals_list, meals_complement


class HarmonyOptimizer:
    """Harmony search optimizer for meal planning with improved mathematics."""
    
    def __init__(self, plan_len=3, goal_mealcount=3, goal_kcal=2000, goal_prot=100, goal_ratio=2.0, goal_price=-1, goal_waste=-1, goal_diversity=-1, pop_size=200):
        """Initialize optimizer.
        
        Args:
            plan_len: Number of days to plan
            goal_mealcount: Target meals per day (-1 to ignore)
            goal_kcal: Target daily calories (-1 to ignore)
            goal_prot: Target daily protein (g) (-1 to ignore)
            goal_ratio: Target carb/fat ratio (-1 to ignore)
            pop_size: Population size for harmony memory
        
        Note: Use -1 for any target to skip scoring for that criterion.
        """
        self.plan_len = plan_len
        self.goal_mealcount = goal_mealcount
        self.goal_kcal = goal_kcal
        self.goal_prot = goal_prot
        self.goal_ratio = goal_ratio
        self.goal_price = goal_price
        self.goal_waste = goal_waste
        self.goal_diversity = goal_diversity
        self.pop_size = pop_size
        
        # Skip flags: -1 means skip scoring for that target
        self._skip_kcal = goal_kcal < 0
        self._skip_prot = goal_prot < 0
        self._skip_ratio = goal_ratio < 0
        self._skip_mealcount = goal_mealcount < 0
        
        # Actual target values (use absolute values for calculation)
        target_kcal = abs(goal_kcal) if goal_kcal > 0 else 2000
        target_prot = abs(goal_prot) if goal_prot > 0 else 100
        target_ratio = abs(goal_ratio) if goal_ratio > 0 else 2.0
        # For meal count with -1, use a soft target (random 1-5, scored loosely)
        if goal_mealcount < 0:
            target_mealcount = 3  # Used for scoring as base, but generation is random
        else:
            target_mealcount = abs(goal_mealcount)
        
        self.goal_nutri = Nutrition(target_kcal, 200, target_prot, 200)
        
        self.gene_size = plan_len
        self.n_threads = os.cpu_count() or 4
        
        # Target values for normalization
        self._target_kcal = target_kcal
        self._target_prot = target_prot
        self._target_ratio = target_ratio
        self._target_mealcount = target_mealcount
        self._typical_budget = target_kcal * 0.5  # rough estimate
        
        # Target values array for day generation
        carbfat_kcals = target_kcal - 4 * target_prot
        self.target_nutri = [
            target_kcal,
            carbfat_kcals * target_ratio / (target_ratio + 2) / 4,
            target_prot,
            carbfat_kcals / (target_ratio + 2) / 4
        ]
        
        # Algorithm parameters (improved)
        self.HMCR = 0.90  # Lower = more exploration initially
        self.HMCR_min = 0.70
        self.HMCR_max = 0.95
        self.base_mutation_rate = 0.15  # Higher base for more exploration
        self.mutation_rate = self.base_mutation_rate
        self.elite_ratio = 0.10  # Keep top 10%
        
        # Caches and state
        self.fitness_cache = {}
        self.generate_day_cache = {}
        self.solutions_with_fitness = []
        
        self.solution = None
        
        # Optimization state
        self.best_fitness = None
        self.last_best_fitness = None
        self.plateau_counter = 0
        self.iteration = 0
        
        # Constraints (soft)
        self.tolerance = 0.15  # 15% tolerance = no penalty if within 85%-115%
    
    def _soft_constraint_penalty(self, actual, target, penalty_multiplier=5.0):
        """Apply soft constraint penalty if beyond tolerance.
        
        Returns 0 if within tolerance, else negative penalty.
        """
        ratio = actual / target
        if ratio < 1 - self.tolerance or ratio > 1 + self.tolerance:
            return -abs(actual - target) / target * penalty_multiplier
        return 0
    
    def _target_normalized_score(self, actual, target):
        """Normalize to target: 0 = perfect, higher = worse."""
        return abs(actual - target) / target
    
    def _normalize_price(self, price):
        """Normalize price score to typical budget."""
        return min(1.0, price / self._typical_budget)
    
    def generate_chromosome(self, gene_size, meals_used=meals):
        """Generate a chromosome (day plan)."""
        # Use random meal count around 3 (1-5) when skipped, else use target
        if self._skip_mealcount:
            target_meals = rd.randint(1, 5)
        else:
            target_meals = self.goal_mealcount
        
        key = (tuple(self.target_nutri), target_meals, id(meals_used))
        if key in self.generate_day_cache:
            return [rd.choice(self.generate_day_cache[key]) for _ in range(gene_size)]
        
        result = [
            main.generate_day(self.target_nutri, target_meals, meals=meals_used)
            for _ in range(gene_size)
        ]
        if len(self.generate_day_cache) < 1000:
            self.generate_day_cache[key] = result
        return result
    
    def _mask_ingredients(self):
        """Create masked ingredient set for diversity."""
        n = len(ingredients_in_meals_list) // 5
        
        if not hasattr(self, '_ingredients_masked'):
            self._ingredients_masked = []
            self._meals_masked = {}
            self._ingredients_include_counter = 0
        
        if self._ingredients_include_counter < n:
            self._ingredients_masked.append(
                ingredients_in_meals_list[self._ingredients_include_counter]
            )
        
        self._ingredients_include_counter += 1
        iic = self._ingredients_include_counter
        
        if iic not in self._meals_masked:
            ingredients_subset = self._ingredients_masked[:self._ingredients_include_counter % n + 1]
            self._meals_masked[iic] = sorted(
                list(functools.reduce(
                    set.intersection,
                    (meals_complement[ingr_name] for ingr_name in ingredients_subset)
                )),
                key=lambda x: x.nutri().kcal
            )
        
        return self._meals_masked[iic]
    
    def init_pop(self, pop_size, gene_size):
        """Initialize population using stratified initialization."""
        # 40% diverse (masked ingredients for variety)
        diverse = [
            self.generate_chromosome(gene_size, self._mask_ingredients())
            for _ in range(pop_size * 2 // 5)
        ]
        # 60% standard
        standard = [
            self.generate_chromosome(gene_size, meals)
            for _ in range(pop_size * 3 // 5)
        ]
        return diverse + standard
    
    def _compute_objectives(self, sol):
        """Compute objective values for a solution."""
        # Nutrition objectives
        day_nutris = []
        ingredients_per_day = []
        
        for day in sol:
            day_nutris.append(day.day_nutri())
            day_ingredients = set()
            for meal in day:
                for ingr in meal.ingredients:
                    day_ingredients.add(ingr.name)
            ingredients_per_day.append(day_ingredients)
        
        # Compute daily averages
        avg_kcal = np.mean([dn.kcal for dn in day_nutris])
        avg_prot = np.mean([dn.prot for dn in day_nutris])
        avg_carb = np.mean([dn.carb for dn in day_nutris])
        avg_fat = np.mean([dn.fat for dn in day_nutris])
        
        # Compute diversity
        all_ingredients = set()
        for day_ingrs in ingredients_per_day:
            all_ingredients.update(day_ingrs)
        
        # Count overlaps within days
        overlap_count = 0
        for day_ingrs in ingredients_per_day:
            overlap_count += len(day_ingrs)
        overlap_ratio = overlap_count / (len(ingredients_per_day) * len(meals))
        
        return {
            'kcal': avg_kcal,
            'prot': avg_prot,
            'carb': avg_carb,
            'fat': avg_fat,
            'diversity': len(all_ingredients),
            'overlap': overlap_ratio
        }
    
    def _compute_crowding(self, idx):
        """Compute crowding distance for diversity preservation.
        
        Higher crowding = more isolated = better for exploration.
        """
        if len(self.solutions_with_fitness) < 3 or idx >= len(self.solutions_with_fitness):
            return 0.0
        
        objectives = ['kcal', 'prot', 'diversity']
        
        distances = []
        current_obj = self.solutions_with_fitness[idx][2]
        
        for i, (score, sol, obj) in enumerate(self.solutions_with_fitness):
            if i == idx:
                continue
            
            # Euclidean distance in objective space
            dist = sum(
                (current_obj.get(k, 0) - obj.get(k, 0)) ** 2
                for k in objectives
            )
            distances.append(np.sqrt(dist))
        
        if not distances:
            return 0.0
        
        return np.mean(distances)
    
    def fitness(self, sol):
        """Compute fitness with target-based scoring and consistency penalty.
        
        Each criterion: |actual - target| / target (distance as fraction)
        Also penalizes variance between days for consistency.
        
        Args:
            sol: Solution to evaluate
        """
        sol_hash = hash(''.join([meal.name for day in sol for meal in day]))
        
        if sol_hash in self.fitness_cache:
            return self.fitness_cache[sol_hash]
        
        # Simulate plan
        simulation = main.simulate_plan(sol)
        
        # Compute objectives
        objectives = self._compute_objectives(sol)
        
        # Get raw values from simulation
        price = simulation['price']
        nutri = simulation['nutri']
        waste = simulation.get('waste', 0) / max(price, 1)
        
        # Get raw values for scoring
        kcal_raw = nutri.kcal
        prot_raw = nutri.prot
        price_raw = price
        waste_raw = waste
        
        # Ratio (only if not skipped)
        if self._skip_ratio:
            ratio_raw = 0
        else:
            ratio_raw = nutri.carb / nutri.fat if nutri.fat > 0 else 1
        
        # Meal count
        mealcount_arr = np.array([len(day) for day in sol])
        mealcount_raw = mealcount_arr.mean()
        
        # Day-to-day consistency (variance penalization)
        day_kcals = np.array([d.day_nutri().kcal for d in sol])
        day_prots = np.array([d.day_nutri().prot for d in sol])
        day_carbs = np.array([d.day_nutri().carb for d in sol])
        day_fats = np.array([d.day_nutri().fat for d in sol])
        
        consistency_kcal = day_kcals.std() / (day_kcals.mean() + 0.01)
        consistency_prot = day_prots.std() / (day_prots.mean() + 0.01)
        consistency_carb = day_carbs.std() / (day_carbs.mean() + 0.01)
        consistency_fat = day_fats.std() / (day_fats.mean() + 0.01)
        consistency_score = (consistency_kcal + consistency_prot + consistency_carb + consistency_fat) / 4
        
        # Diversity
        diversity_raw = objectives['diversity']
        
        # =========================================================================
        # COMPUTE TARGET-BASED SCORES
        # =========================================================================
        
        def target_score(key, raw_value, target):
            """Score based on distance to target (0-1 scale per criterion)."""
            if target <= 0:
                return 0
            return abs(raw_value - target) / target
        
        # Score each criterion
        if self._skip_kcal:
            kcal_score = 0
        else:
            kcal_score = target_score('kcal', kcal_raw, self.goal_kcal)
        
        if self._skip_prot:
            prot_score = 0
        else:
            prot_score = target_score('prot', prot_raw, self.goal_prot)
        
        if self._skip_ratio:
            ratio_score = 0
        else:
            ratio_score = target_score('ratio', ratio_raw, self.goal_ratio)
        
        if self._skip_mealcount:
            mealcount_score = 0
        else:
            mealcount_score = target_score('mealcount', mealcount_raw, self.goal_mealcount)
        
        # Price and waste always tracked
        price_score = target_score('price', price_raw, self.goal_price) if self.goal_price > 0 else 0
        waste_score = target_score('waste', waste_raw, self.goal_waste) if self.goal_waste > 0 else 0
        diversity_score = target_score('diversity', diversity_raw, self.goal_diversity) if self.goal_diversity > 0 else 0
        
        # =========================================================================
        # COMBINE SCORES (equal weights - 1/8 each)
        # =========================================================================
        
        weight = 1.0 / 9.0  # 9 criteria now (added consistency)
        
        score = 0
        if not self._skip_kcal:
            score += -weight * kcal_score
        if not self._skip_prot:
            score += -weight * prot_score
        if not self._skip_ratio:
            score += -weight * ratio_score
        if not self._skip_mealcount:
            score += -weight * mealcount_score
        if self.goal_price > 0:
            score += -weight * price_score
        if self.goal_waste > 0:
            score += -weight * waste_score
        if self.goal_diversity > 0:
            score += weight * (1 - diversity_score)
        
        score += -weight * consistency_score
        
        # Store in cache
        self.fitness_cache[sol_hash] = score
        
        return score
    
    def _adaptive_hmcr(self):
        """Adapt HMCR based on plateau detection."""
        if self.plateau_counter > 3:
            # More exploration when stuck
            self.HMCR = max(self.HMCR_min, self.HMCR * 0.95)
        else:
            # Slowly increase HMCR (more exploitation of good solutions)
            self.HMCR = min(self.HMCR_max, self.HMCR * 1.01)
    
    def _elitism_selection(self, harmony_memory):
        """Select elite solutions to preserve."""
        elite_count = max(1, int(self.pop_size * self.elite_ratio))
        return heapq.nlargest(elite_count, harmony_memory)
    
    def optimize(self, time_limit):
        """Run optimization with mathematical improvements.
        
        Args:
            time_limit: Time limit in seconds
            
        Returns:
            Best solution found
        """
        print(f"Initializing population of {self.pop_size} solutions...")
        pop = self.init_pop(self.pop_size, self.gene_size)
        print("Computing initial fitness...")
        
        # Initialize population with fitness tracking
        for i, elem in enumerate(pop):
            self.fitness(elem)
            if i % 50 == 0:
                print(f"  {i}/{self.pop_size}")
        
        print("Building harmony memory...")
        
        # Initialize with fitness
        harmony_memory = [(self.fitness(elem), elem) for elem in pop]
        heapq.heapify(harmony_memory)
        
        self.best_fitness = harmony_memory[0][0]
        self.last_best_fitness = self.best_fitness
        
        counter = 0
        thread_lock = threading.Lock()
        memory_lock = threading.Lock()
        threads_should_end = False
        convergence_time_limit = time_limit
        
        # Track convergence
        no_improvement_count = 0
        
        def loop_body():
            nonlocal counter, no_improvement_count
            
            while not threads_should_end:
                # Use adaptive HMCR
                if rd.random() < self.HMCR:
                    # Harmony memory consideration
                    picked = []
                    for gene_idx in range(self.gene_size):
                        elem1 = rd.choice(harmony_memory)[1]
                        new_gene = []
                        for aa_idx in range(len(elem1[gene_idx])):
                            elem2 = rd.choice(harmony_memory)[1]
                            aa = elem2[gene_idx][aa_idx]
                            new_gene.append(aa)
                        picked.append(Day(new_gene))
                else:
                    # Random new solution for diversity
                    picked = self.generate_chromosome(self.gene_size)
                
                # Mutation with adaptive rate
                for idx, elem in enumerate(picked):
                    if rd.random() < self.mutation_rate:
                        target = elem.day_nutri()
                        target = (
                            np.array([target.kcal, target.carb, target.prot, target.fat])
                            * (1 + np.random.normal(1, 0))
                        ).tolist()
                        # Use random meal count when skipped
                        mutate_meals = rd.randint(1, 5) if self._skip_mealcount else self.goal_mealcount
                        picked[idx] = main.generate_day(target, mutate_meals)
                
                # Add to statlists periodically for current normals
                if counter % 10 == 0:
                    self.fitness(picked)
                
                picked_fitness = self.fitness(picked)
                
                thread_lock.acquire()
                if picked_fitness > self.best_fitness:
                    print(f"New best fitness: {picked_fitness:.4f}")
                    self.best_fitness = picked_fitness
                    time_limit = convergence_time_limit
                    self.solution = picked
                    no_improvement_count = 0
                thread_lock.release()
                
                memory_lock.acquire()
                heapq.heappushpop(harmony_memory, (picked_fitness, picked))
                memory_lock.release()
        
        threads = [
            threading.Thread(target=loop_body)
            for _ in range(self.n_threads)
        ]
        
        for thread in threads:
            thread.start()
        
        try:
            while time_limit > 0:
                counter += 1
                self.iteration += 1
                
                if counter % 10 == 0:
                    # Check for plateau
                    if self.best_fitness == self.last_best_fitness:
                        self.plateau_counter += 1
                        no_improvement_count += 1
                        
                        # Adaptive HMCR
                        self._adaptive_hmcr()
                        
                        # Increase mutation on plateau
                        if self.plateau_counter > 3:
                            self.mutation_rate = min(0.3, self.mutation_rate * 1.2)
                    else:
                        self.plateau_counter = 0
                        no_improvement_count = 0
                        self.mutation_rate = self.base_mutation_rate
                        self.HMCR = min(self.HMCR_max, self.HMCR * 1.02)  # Slight exploitation
                    
                    self.last_best_fitness = self.best_fitness
                    
                    # Logging
                    print(f"  iter={counter} HMCR={self.HMCR:.3f} mut={self.mutation_rate:.3f} best={self.best_fitness:.4f}")
                
                time.sleep(1)
                time_limit -= 1
        except KeyboardInterrupt:
            threads_should_end = True
        
        threads_should_end = True
        for thread in threads:
            thread.join()
        
        print(f"Iterations: {self.iteration}")
        print(f"Cache hits: {len(self.fitness_cache)}")
        
        return self.solution
    
    def generate_plan(self, sol, date_from=None):
        """Generate dated plan from solution."""
        if date_from is None:
            date_from = dt.date.today()
        
        plan = []
        for day in sol:
            plan.append((date_from, day))
            date_from += dt.timedelta(days=1)
        
        simulation = main.simulate_plan(sol)
        plan.append(simulation['price'])
        plan.append(simulation['nutri'])
        return plan
    
    def save_plan(self, filename, sol):
        """Save solution to file."""
        import pprint as pp
        import pickle
        
        plans_dir = "plans"
        os.makedirs(plans_dir, exist_ok=True)
        
        pickle.dump(sol, open(f"{plans_dir}/{filename}.pickle", "wb"))
        
        plan = self.generate_plan(sol)
        s = pp.pformat(plan)
        
        with open(f"{plans_dir}/{filename}", 'w') as f:
            f.write(s)
        
        print(f"Saved to {plans_dir}/{filename}")


def optimize(**kwargs):
    """Convenience function to run optimization."""
    optimizer = HarmonyOptimizer(**kwargs)
    solution = optimizer.optimize(kwargs.get('time_limit', 60))
    return optimizer, solution
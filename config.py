"""BulkBro Configuration - Central place for all tunable parameters.

This module contains all magic numbers and defaults used throughout the project.
Edit this file to customize behavior without touching core logic.

Parameters
----------
None - this module only defines constants
"""

# =============================================================================
# Default Targets (CLI defaults)
# =============================================================================
DEFAULT_DAYS = 3
DEFAULT_MEALS_PER_DAY = 3
DEFAULT_KCAL = 2000
DEFAULT_PROTEIN = 100
DEFAULT_RATIO = 2.0
DEFAULT_TIME_LIMIT = 60
DEFAULT_DIVERSITY = 10
DEFAULT_POP_SIZE = 150

# =============================================================================
# Algorithm Parameters (HarmonyOptimizer)
# =============================================================================
HMCR = 0.90
"""float: Harmony memory consideration rate (0.0-1.0)"""

HMCR_MIN = 0.70
"""float: Minimum HMCR during adaptation"""

HMCR_MAX = 0.95
"""float: Maximum HMCR during adaptation"""

MUTATION_RATE = 0.15
"""float: Base mutation rate"""

MUTATION_MAX = 0.30
"""float: Maximum mutation rate on plateau"""

ELITE_RATIO = 0.10
"""float: Top fraction preserved as elite (0.0-1.0)"""

TOLERANCE = 0.15
"""float: 15% tolerance = no penalty if within 85%-115% of target"""

# =============================================================================
# Simulation Parameters
# =============================================================================
MAX_MEALS_PER_DAY = 7
"""int: Maximum meals per day"""

DEFAULT_ROTS_IN = 999
"""int: Fallback rots_in for unknown ingredients"""

DEFAULT_MIN_QTY = 1
"""int: Fallback minimum quantity"""

PRICE_CACHE_SIZE = 500
"""int: Max entries in simulation cache"""

# =============================================================================
# Delivery / Wolt Market Economics
# =============================================================================
DELIVERY_ENABLED = True
"""bool: Include delivery fees and basket discounts in the objective"""

ORDER_MINIMUM = 1500
"""int: Minimum order value in RSD; shortfalls incur a surcharge"""

DELIVERY_FEE = 119
"""int: Flat delivery fee in RSD (waived above the free-delivery threshold)"""

FREE_DELIVERY_THRESHOLD = 2500
"""int: Order value in RSD above which delivery is free"""

BASKET_DISCOUNT_AMOUNT = 400
"""int: Fixed discount in RSD applied once a basket reaches the minimum"""

BASKET_DISCOUNT_MIN = 1000
"""int: Minimum basket value in RSD to unlock the basket discount"""

BASKET_DISCOUNT_MAX_USES = 1
"""int: Max number of orders per plan that can claim the basket discount"""

# =============================================================================
# Variance Thresholds
# =============================================================================
VARIANCE_GOOD = 10
"""int: <10% variance = good consistency"""

VARIANCE_MODERATE = 20
"""int: 10-20% variance = moderate (above = poor)"""

# =============================================================================
# Display Parameters
# =============================================================================
DAYS_PREVIEW = 3
"""int: Days to show in plan summary"""

PRINT_WIDTH = 80
"""int: Width of separator lines"""

# =============================================================================
# Nutrition Calculation
# =============================================================================
DIST_KCAL_THRESHOLD = 65
"""int: kcal difference threshold for squared penalty in dist()"""

NO_FRIDGE = False
"""bool: When True, all ingredients spoil in 1 day (simulates no refrigerator)"""

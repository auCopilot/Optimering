from CustomFunctions import LPFeasibleRegionPlotter
#
# Example LP Problem, Slide Kap6, week 9:

# 1. Define Coefficients for constraints
coef_matrix = [
    [1, 1],
    [2, 1],
    [-1, 4],
    [1, 0], # Defines postive x1
    [0, 1]  # Defines positive x2
]

# 2. Define RHS values
rhs = [4, 5, 2, 0, 0]

# 3. Define Types
types = ["<=", "<=", ">=", ">=", ">="]

# 4. Instantiate Plotter
plotter = LPFeasibleRegionPlotter(
    coef_matrix,
    rhs,
    types,
    x1_bounds=(-1, 5),
    x2_bounds=(-1, 5)
)

# 5. Plot with Optimal Solution Line (Z* approx 180 at x1=20, x2=60? or intersection points)
# Intersection A: x1+x2=80 & x2=60 -> x1=20. Z=3(20)+2(60)=180.
# Intersection B: x1+x2=80 & 2x1=100 -> x1=50, x2=30. Z=3(50)+2(30)=210.
# Let's say optimal is 210
plotter.plot()

import pulp as PLP
from modeller.dual_lp import dual_lp
from modeller.feasible_region import LPFeasibleRegionPlotter

# Primary LP:
model = PLP.LpProblem("Primary", sense=PLP.LpMinimize)
x = PLP.LpVariable.dicts("x", indices=range(3), lowBound=0)
model += 40*x[0] + 40*x[1] + 30*x[2]
model += 8*x[0] + 5*x[1] + 5*x[2] >= 5
model += 5*x[0] + 10*x[1] + 6*x[2] >= 4
model.solve()
for v in model.variables():
    print(v.name, v.varValue)
print(PLP.value(model.objective))

# Dual
dual_model, latex = dual_lp(model, var_bounds= [">=", ">=", ">="])

# 1) Plot
region = LPFeasibleRegionPlotter(coef_matrix=None, rhs=None, equality_types= None, x1_bounds=(0,5), x2_bounds=(0,5))
region.constraints_from_model(dual_model)
region.plot()

# 2) Solution ( Solves in region.constraints_from_model(dual_model) )
for v in dual_model.variables():
    print(v.name, "=", v.varValue)
# 3) The second constraint has positive slack, so the second variable in the primary can be set to zero

# 4 ) Removing the third variable would remove the third constraint (green)
# This would push the solution in the dual lp up to the intersection of the blue and orange line.
# We can solve this system of equation to get the solution
import numpy as np
A = np.array([[8,5],[5,10]])
b = np.array([40,40])
sol = np.linalg.solve(A,b)
print(sol) # x1 = 3.62 , x2 = 2.18

# It has an impact because it restricts the feasible region
# That is prevents us from using that intersection of the blue and orange line
# Creating a new more restricted solution vertex.
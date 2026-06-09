import numpy as np
import pulp as PLP


products = range(4)
depts = range(2)

hours = [400, 300]
time_usages = [[2,5,3,4,2],
               [6,9,5,1,3]]
profit = [700, 500, 1200, 1000, 766]
model = PLP.LpProblem("Planning", sense=PLP.LpMaximize)
# How much of each product is made
p = PLP.LpVariable.dicts("Product", indices=products, lowBound=0)

# Max profit
model += PLP.lpSum(profit[i]*p[i] for i in products)

# Constraint the time used by each department
for d in depts:
    model += PLP.lpSum(p[i]*time_usages[d][i] for i in products) <= hours[d], f"TimeConstraint{d}"

model.solve()
print("Cost", PLP.value(model.objective))
for v in model.variables():
    if v.varValue > 0:
        print(v.name,"=", v.varValue)

# Duals (shadow prices)
# These can be interpreted as the profit we would gain/lose for a small relaxation/restriction in the constraint
for name, constraint in model.constraints.items():
    print(name, "dual =", constraint.pi)
# 4) This information is not available from pulp

# 5)
# We can using the shadow prices anwser this question since a positive differene indicates profitablity and
# a negative, un-profitablility
# This is profitable since the difference between the shadow price and the work price is postive.

# 6)
# We would need the profit from the hours in A to be greater than 224 pr. hour spend and from departement B 106 pr.
# hour spend so 224 * 2 + 106 * 3 = 448 + 318 = 766

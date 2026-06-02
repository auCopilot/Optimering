import pulp as PLP
product_range = range(2) # Normal, Luxury
profit = [70, 100]

dep_range = range(3) # Wood, Plastic, Assembly
employees = [30, 10, 20]
hours = 30

hours_bound = [hours * employees[i] for i in dep_range]

p = PLP.LpVariable.dicts("product", indices=product_range, lowBound=0)
d = PLP.LpVariable.dicts("department", indices=dep_range, lowBound=0)

model = PLP.LpProblem("Model", PLP.LpMaximize)

# Max profit
model += PLP.lpSum(p[i] * profit[i] for i in product_range), "Profit"

# Marketing constraints
model += (p[0] + p[1]) / 3 <= p[0], "Luxury_min"
model += 2 * (p[0] + p[1]) / 3 >= p[0], "Luxury_max"

coef_matrix = [[2.25, 2.5],
               [1.0, 0.5],
                [1., 2.]]

for i in dep_range:
    model += PLP.lpSum(coef_matrix[i][j] * p[j] for j in product_range) <= hours_bound[i], f"Hours{i}"

model.solve()

print("Objective:", PLP.value( model.objective))

for var in model.variables():
    print(var.name, "=", var.value())
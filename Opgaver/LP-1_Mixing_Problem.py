import pulp as PLP

material_range = range(4)
material_prices = [0.3, 0.7 , 0.4, 0.8]
material_bound = [150, 170, 120, 140]


products = ["A", "B", "C"]
product_prices = [8, 16, 12]
product_prices = dict(zip(products, product_prices))

R = PLP.LpVariable.dicts("R", indices= material_range, cat = PLP.LpContinuous, lowBound=0)
P = PLP.LpVariable.dicts("P", indices= products, cat = PLP.LpContinuous, lowBound= 0)
         #A B C
usage = [[0,3,2], # R1
         [2,5,4], # R2
         [3,1,2], # R3
         [2,4,3]] # R4


model = PLP.LpProblem("Mixing_problem", sense = PLP.LpMaximize)

sales_price = PLP.lpSum(product_prices[product] * P[product] for product in products)
material_costs = PLP.lpSum(R[i]*material_prices[i] for i in material_range)
# Objective: Maximize profit = sales_prices - material_costs
model += sales_price - material_costs, "Obj"

# Constraints on material usage and bound for resources
for i in material_range:
    model += R[i] <= material_bound[i], f"Bound{i}"
    model += R[i] == PLP.lpSum(P[p] * usage[i][j] for j, p in enumerate(products)), f"Usage{i}"

model.solve()

print("Objective:", PLP.value( model.objective))

for var in model.variables():
    print(var.name, "=", var.value())


import pulp as PLP

from week03.LP3 import total_weight

product_range = range(4)
capacity = [1000, 800, 1250, 650]
vol_pr_ton = [5, 7, 6, 4]
profit_pr_ton = [1400, 1800, 1600, 1250]

sections = range(3)
conditions = ["weight", "volume"]
max_weight = [300, 450, 250]
max_vol = [2200, 2800, 1600]

# Variable for each section and condition
S = PLP.LpVariable.dicts("section", indices= (sections, conditions), lowBound=0)
# Variable for how much product[i] is assigned to a section[j]
P = PLP.LpVariable.dicts("product", indices= (product_range, sections), lowBound=0)

model = PLP.LpProblem("Shipment", sense= PLP.LpMaximize)

# Max profit
model += PLP.lpSum(P[i][j] * profit_pr_ton[i] for i in product_range for j in sections)

# Capacity constraints
for i, c in enumerate(capacity):
    model += PLP.lpSum(P[i][j] for j in sections) <= c, f"Capacity_{i}"

# Weight and Volume constraints
for j, c in enumerate(max_weight):
    model += S[j]["weight"] == PLP.lpSum(P[i][j] for i in product_range)
    model += S[j]["weight"] <= c, f"Weight_{(j)}"

for j, c in enumerate(max_vol):
    model += S[j]["volume"] == PLP.lpSum(P[i][j]*vol_pr_ton[i] for i in product_range)
    model += S[j]["volume"] <= c,  f"Volume_{j}"

# Balance constraints by weight
fractions = [0.3, 0.45, 0.25]
total_weight = PLP.lpSum(P[i][j] for i in product_range for j in sections)
for j in sections:
    model += S[j]["weight"] == total_weight*fractions[j], f"Fraction{j}"

model.solve()

print("Objective:", PLP.value( model.objective))

for var in model.variables():
    print(var.name, "=", var.value())
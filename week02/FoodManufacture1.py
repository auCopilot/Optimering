import pulp as PLP
from CustomFunctions import construct_constraints
from CustomFunctions import print_solution
# Maximization problem
model = PLP.LpProblem(name="FoodManufacture1", sense=PLP.LpMaximize)
# Decision variable ranges (zero indexed)
# 5 types of oils
type_range = range(5)
veg = range(2) # 2 types of vegetable oils
oil = range(2, 5) # 3 types of animal oils
month_range = range(6) # January to June
# Create decision variables that are of dimension month x type x number

bought = PLP.LpVariable.dicts("VEG", (month_range, type_range), lowBound=0)
used = PLP.LpVariable.dicts("USED_VEG", (month_range, type_range), lowBound=0)
stored = PLP.LpVariable.dicts("STORED_VEG", (month_range[:5], type_range),
                              lowBound=0)

# Decision variable PROD for each month
prod = PLP.LpVariable.dicts("PROD", month_range, lowBound=0)

# Same price every month for finished product
prod_price = 150
# Cost of storing raw materials
storage_cost = 5 # per ton per month

# Objective function construction


# Objective function coefficients for each month
coef = [[110, 120, 130, 110, 115],
        [130, 130, 110, 90, 115],
        [110, 140, 130, 100, 95],
        [120,110, 120, 120, 125],
        [100, 120, 150, 110, 105],
        [90, 100, 140, 80, 135]]


# 1. Sales revenue: Sum of monthly sales revenue
revenue_prod = PLP.lpSum(prod_price * prod[m] for m in month_range)
# 2. Cost of raw materials: Sum of costs for vegetable oils and oils at a
# given month for production
cost_bought = PLP.lpSum(bought[m][t] * coef[m][t]
                       for m in month_range
                       for t in type_range)
cost_stored = PLP.lpSum( stored[m][t] * storage_cost
                        for m in month_range[:5]
                        for t in type_range)



# Objective function: Maximize profit = revenue - costs.

model += revenue_prod - (cost_bought + cost_stored), "Objective"

# Constraints construction


# Continuity constraints for raw materials for each month, assumes no losses
for m in month_range:
    model += (PLP.lpSum(used[m][t] for t in type_range) - prod[m] == 0,
             (f"Continuit{m+1}"))

# Hardness values for raw materials
hardness_veg = [8.8, 6.1]
hardness_oil = [2.0, 4.2, 5.0]
hardness_values = hardness_veg + hardness_oil
# Hardness limits for finished product
hardness_min = 3.0
hardness_max = 6.0
# Hardness constraints for each month
for m in month_range:
    model += (PLP.lpSum(used[m][t] * hardness_values[t] for t in type_range)
              - hardness_min * prod[m]) >= 0, f"HardnessMin{m+1}"
    model += (PLP.lpSum(used[m][t] * hardness_values[t] for t in type_range)
              - hardness_max * prod[m]) <= 0, f"HardnessMax{m+1}"
# Production capacity per month
capacity_oil = 250
capacity_veg = 200
# Production capacity constraints for each month
for m in month_range:
    model += PLP.lpSum(used[m][t] for t in veg) <= capacity_veg, f"CapVeg{m+1}"
    model += PLP.lpSum(used[m][t] for t in oil) <= capacity_oil, f"CapOil{m+1}"

# Storage constrains, max 1000 tons per type
max_storage = 1000

# Book doesnt wan't to cap storage in the solution even though it is in the
# text?
for m in month_range[:5]:
    for t in type_range:
        model += stored[m][t] <= max_storage, f"MaxStorage_M{m+1}_T{t+1}"

# Initial storage constraints for January
initial_storage = [500, 500, 500, 500, 500]
for t in type_range:
    # January storage constraints
    # What we have stored by end of january = initial + bought - used
    model += (stored[0][t] == initial_storage[t] + bought[0][t] - used[0][t],
              (f"InitStorage_T{t+1}"))

# Intermidate storage = previous month storage + bought - used
for m in month_range[1:5]:
    for t in type_range:
        model += (stored[m-1][t] + bought[m][t] - used[m][t]
                  - stored[m][t] == 0,
                  f"InterStorage_M{m+1}_T{t+1}")

# June stotage constraints
end_storage = [500, 500, 500, 500, 500]
for t in type_range:
    model += (stored[5 - 1][t] + bought[5][t] - used[5][t] == end_storage[t],
              (f"EndStorage_T{t+1}"))
# Solve and print solution
print_solution(model)

# Make lp file
model.writeLP("FoodManufacture1.lp")

# Number of variables and constraints
n_vars = len(model.variables())
n_constraints = len(model.constraints)
print(f"Number of variables: {n_vars}")
print(f"Number of constraints: {n_constraints}")



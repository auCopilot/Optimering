import pulp as  PLP
import numpy as np
from CustomFunctions import *
""" Problem information given."""
# Maximization problem
model = PLP.LpProblem(name="FactoryPlanning1", sense=PLP.LpMaximize)

# The productrange consists of seven products.
product_range = list(range(7))

# Define the month range
month_range = list(range(6))

# Tool range
tool_range = list(range(5))

# Define the production variables, which tracks the amount of each product produced in each month.
prod = PLP.LpVariable.dicts("prod", (month_range, product_range), lowBound=0)
sold = PLP.LpVariable.dicts("sold", (month_range, product_range), lowBound=0)
stock = PLP.LpVariable.dicts("stock", (month_range, product_range), lowBound=0)
# Upper bound of storage is 100 units for each product, each month.
for m in month_range:
    for i in product_range:
        stock[m][i].bounds(0, 100)
# Zero initial stock for all products. Treat intial stock as what we have
# BEFORE the first month
intial_stock = [0, 0, 0, 0, 0, 0, 0]
for i in product_range:
    model += (stock[0][i] == intial_stock[i] + prod[0][i] - sold[0][i],
              f"StockBalanceConstraint0_{i}")
# Target stock for all products at end of June is 50 units.
target_stock_june = 50



# Define machines number of respective machines available each month.
# Due to maintenance, the number of machines available each month is different.
grinders = [3,4,4,4,3,4]
vertical_drills = [2, 2, 2, 1, 1, 2]
horizontal_drills = [3, 1, 3, 3, 3, 2]
borers = [1, 1, 0, 1, 1, 1]
planers = [1, 1, 1, 1, 1, 0]

# Each product must be made within working times.
working_days_pr_month = 24
shifts_pr_day = 2
hours_pr_shift = 8
hours_pr_day = shifts_pr_day * hours_pr_shift
hours_pr_month = working_days_pr_month * hours_pr_day

profits_contribution = [10, 6, 8, 4, 11, 9, 3] # GBP / unit

# Storage price for keeping stock.
storage_price = 0.5 # GBP / unit / month

# Hours / Unit / machine.
production_time = [
    [0.5,  0.7,  0,     0,     0.3,  0.2,  0.5],
    [0.1,  0.2,  0,     0.3,   0,    0.6,  0],
    [0.2,  0,    0.8,   0,     0,    0,    0.6],
    [0.05, 0.03, 0,     0.07,  0.1,  0,    0.08],
    [0,    0,    0.01,  0,     0.05, 0,    0.05]
]

# Tools capacities each month, for each machine type.
tools_capacity = np.zeros((len(month_range), len(tool_range)))
for m in month_range:
    tools_capacity[m][0] = grinders[m] * hours_pr_month
    tools_capacity[m][1] = vertical_drills[m] * hours_pr_month
    tools_capacity[m][2] = horizontal_drills[m] * hours_pr_month
    tools_capacity[m][3] = borers[m] * hours_pr_month
    tools_capacity[m][4] = planers[m] * hours_pr_month

# Marketing constraints on amount produced each month for each product.
marketing_constraints = [
    [500, 1000, 300, 300, 800, 200, 100],
    [600, 500, 200, 0,   400, 300, 150],
    [300, 600, 0,   0,   500, 400, 100],
    [200, 300, 400, 500, 200, 0,   100],
    [0,   100, 500, 100, 1000, 300, 0],
    [500, 500, 100, 300, 1100, 500, 60]
]
"""Optimization problem formulation."""

# Profits for each month for each product.
sales_profit = PLP.lpSum(profits_contribution[i]*sold[m][i]
                   for m in month_range
                    for i in product_range)
# Eventual storage costs
storage_cost = PLP.lpSum(storage_price*stock[m][i]
                         for m in month_range
                         for i in product_range)
# Objective is to maximize profits, minus storage costs.
model += sales_profit - storage_cost, "TotalProfit"

for m in month_range:
    for i in product_range:
        # Marketing contraints for each month, for each product.
        model += (sold[m][i] <= marketing_constraints[m][i],
                  f"MarketingConstraint{m}_{i}")

# Tools work in parallel, so we just need to make sure that the total hours
# used for EACH tool type does not exceed the available hours for that month.

for m in month_range:
    for t in tool_range:
        # Limit production such that the total hours used for each machine type
        # does not exceed the available hours for that month, for each machine type.
        # This accounts for maintenance, which reduces the number of machines
        # available each month.
        # We assume that all machines are manned at all times.
        model += (PLP.lpSum(production_time[t][i]*prod[m][i]
                for i in product_range) <= tools_capacity[m][t],
                  f"ToolCapacityConstraint{m}_{t}")

for m in month_range[1:]:
    for i in product_range:
        # Stock balance constraints, for each month, for each product.
        model += (stock[m][i] == stock[m-1][i] + prod[m][i] - sold[m][i],
                  f"StockBalanceConstraint{m}_{i}")

for i in product_range:
    # Target stock constraint for June, for each product.
    model += (stock[5][i] == target_stock_june, f"TargetStockConstraint_{i}")
print(tools_capacity)
print_solution(model)


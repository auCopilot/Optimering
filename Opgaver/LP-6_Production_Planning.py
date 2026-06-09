
import numpy as np
import pulp as PLP

months = range(4)
work_type = range(2)
regular = [150, 150, 140, 160]
regular = [r * 1000 for r in regular]
overtime = [75 , 75 , 70 , 80]
overtime = [o * 1000 for o in overtime]

demand = [80, 200, 300, 200]
demand = [d * 1000 for d in demand]

price_regular = 1.0
price_overtime = 1.5
storage_price = 0.3

cost = np.zeros((4,4,2))
for w in work_type:
    for m in months:
        for n in months:
            sp = (n-m)*storage_price if m <= n else 10**3
            wp = price_regular if w == 0 else price_overtime
            cost[m,n,w] = sp + wp
# Production to month x from month x from work type x
x = PLP.LpVariable.dicts("x", indices=(months,months, work_type), lowBound=0)
l = PLP.LpVariable.dicts("l", indices=(months), lowBound=0)
u = PLP.LpVariable.dicts("u", indices=(months), lowBound=0)

# Minimize cost of production with soft constraint punishment
L = 190*1000
L_prime = 0
U = 200*1000
U_prime = 400*1000
D = 0.2
model = PLP.LpProblem("LP6", sense=PLP.LpMinimize)


planned_price = PLP.lpSum(x[m][n][w] * cost[m][n][w] for m in months for n in months for w in work_type)
punished_price = PLP.lpSum(u[m]*D + l[m]*D for m in months)
model += planned_price + punished_price

for m in months:
    # Track how far production deviates to month n from month m
    model += PLP.lpSum(x[n][m][w] for n in months for w in work_type) <= U + u[m]
    model += PLP.lpSum(x[n][m][w] for n in months for w in work_type) >= L - l[m]
model += PLP.lpSum(u[m] for m in months) <= U_prime - U
model += PLP.lpSum(l[m] for m in months) <= L - L_prime

# Meet demands such that aggregate production meets the demand
for m in months:
    model += PLP.lpSum(x[m][n][w] for n in months if n <= m for w in work_type ) == demand[m]

# Bounds on work available
for w in work_type:
    for m in months:
        if w == 0:
            model += PLP.lpSum(x[n][m][w] for n in months) <= regular[m]
        else:
            model += x[m][m][w] <= overtime[m]

model.solve()
print("Cost", PLP.value(model.objective))
for v in model.variables():
    if v.varValue > 0:
        print(v.name,"=", v.varValue)

for n in months:
    val = 0
    for m in months:
        for w in work_type:
            val += x[m][n][w].varValue
    print("Production from month", m, "is:", val)





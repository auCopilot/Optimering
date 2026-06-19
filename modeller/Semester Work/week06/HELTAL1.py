import numpy as np
import pulp as PLP
fra = range(5)
til = range(5)
M = 10**6

cost = np.array([
    [M,  4,  9, 13,  7],
    [14, M, 12,  8,  5],
    [10, 18, M, 18, 17],
    [11, 16,  8, M, 15],
    [ 3,  5,  2, 20, M]
])

x = PLP.LpVariable.dicts("x",(fra, til),0,1,PLP.LpInteger)

model = PLP.LpProblem("HELTAL-1", PLP.LpMinimize)

# objektfunktion from ASTP
model += PLP.lpSum( cost[i][j]*x[i][j]
                    for i in fra
                    for j in til)

# Outflow/Inflow restriction
for i in fra:
    model += PLP.lpSum( x[i][j] for j in til) == 0, f"Outflow{i}"
for j in til:
    model += PLP.lpSum( x[i][j] for i in fra) == 0, f"Inflow{j}"

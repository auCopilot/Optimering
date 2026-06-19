import numpy as np
import pulp as PLP
level_costs = [3000, 6000, 8000, 10000]
market_price = 2*10**5
M = -10000
level_1 = np.array([
    [1.5, 1.5, 1.5, 0.75],
    [1.5, 2.0, 1.5, 0.75],
    [1.0, 1.0, 0.75, 0.5],
    [0.75, 0.75, 0.5, 0.25]
])

level_2 = np.array([
    [4.0, 4.0, 2.0],
    [3.0, 3.0, 1.0],
    [2.0, 2.0, 0.5]])

level_3 = np.array([
     [12.0, 6.0],
     [5.0, 4.0]])

level_4 = np.array([
[6.0]])

m = len(level_costs)
n, p = level_1.shape

depth = range(m)
width = range(n)
length = range(p)

def value(level, i, j):

    if level == 0:
        return level_1[i][j] * market_price / 100 - level_costs[level]
    elif level == 1:
        return level_2[i][j] * market_price / 100 - level_costs[level]
    elif level == 2:
        return level_3[i][j] * market_price / 100 - level_costs[level]
    elif level == 3:
        return level_4[i][j] * market_price / 100 - level_costs[level]
    else:
        raise ValueError("Invalid level")



model = PLP.LpProblem("OpencastMining", PLP.LpMaximize)

# Binary decision variables x(i,j,k) for level i, block (j,k)
x = PLP.LpVariable.dicts("x", (depth, width, length), 0, 1, PLP.LpBinary)

# Binary indicator variable delta(i,j,k) to indicate if blocks (i-1 .. i, j-1 .. j, k-1 .. k)
# available for mining (i.e., if the neighboring blocks above are mined)

# Objective function: Maximize total profit
model += PLP.lpSum(value(i, j, k) * x[i][j][k]
                   for i in depth
                   for j in width[:(-i) if i > 0 else None]
                   for k in length[:(-i) if i > 0 else None] ), "TotalProfit"

### Constraints ###
def available_for_mining(i, j, k):
    n_blocks_above = 4
    # If sum of x(i-1, j-1..j, k-1..k) == 4, then block (i,j,k) can be mined
    # If not, then block (i,j,k) cannot be mined
    sum = PLP.lpSum(x[i-1][jj][kk]
                    for jj in width[j:j+2]
                    for kk in length[k:k+2])
    # If sum >= n_blocks_above, then x(i,j,k) can be 1, if the sum is 4.
    # If the sum is less than for then: sum >= 4 * x(i,j,k) => x(i,j,k) must be 0,
    # because it can only take 0, 1 values.
    return sum >= n_blocks_above * x[i][j][k]




for i in depth:
    for j in width[:-i]:
        for k in length[:-i]:
                model += (available_for_mining(i, j, k),
                          f"Availability_Constraint_{i}_{j}_{k}")

from CustomFunctions import print_solution

# Solve the model
print_solution(model, condition = lambda x: abs(x.varValue) >= 0.1)


# This problem can be modelled as a network probelm. Specifically, a transport problem
from modeller.network.transport_problem import TransportProblem
#1)
demand = [2,3,2,7]
supply = [6,3,5]
cost = [[7, 11, 3, 8],
        [2, 10 ,1, 2],
        [14, 18 ,8 ,5]]

TP = TransportProblem(cost, supply, demand)

#2)
TP.construct_constraints()
TP.solve()
TP.print_transport_details(one_indexed = True)

from modeller.nordvest import NordVest
NV = NordVest(supply, demand)
NV.solve()
initial_sol = NV.x

for k, v in initial_sol.items():
        print(k, v)

def stepping_stone(supply, demand, cost, x):
    m = len(supply)
    n = len(demand)

    # Header
    header = [""] + [f"T{j+1}" for j in range(n)] + ["Supply"]
    print("".join(f"{h:>8}" for h in header))

    # Rows
    for i in range(m):
        row = [f"S{i+1}"]

        for j in range(n):
            value = x.get((i, j), 0)
            row.append("" if value == 0 else str(value))

        row.append(str(supply[i]))
        print("".join(f"{c:>8}" for c in row))

    # Demand row
    row = ["Demand"] + [str(d) for d in demand] + [str(sum(demand))]
    print("".join(f"{c:>8}" for c in row))

    sol_val = 0
    for i in range(m):
        for j in range(n):
            sol_val += x[(i, j)] * cost[i][j]

    print("Solution cost =", sol_val)

stepping_stone(supply, demand, cost, initial_sol)
# Use x(0,0) = 1 and x(1,0) = 1 instead. To balance, remove from x(0,0) to x(0,2) and x(1,2) to x(1,0)
# This gives an optimal solution.
delta = 1
initial_sol[(0,0)] -= delta
initial_sol[(0,2)] += delta
initial_sol[(1,0)] += delta
initial_sol[(1,2)] -= delta

stepping_stone(supply, demand, cost, initial_sol)

# solve again with different cost
demand = [2,3,2,7]
supply = [6,3,5]
cost = [[7, 11, 3, 5],
        [2, 10 ,1, 2],
        [14, 18 ,8 ,5]]

TP = TransportProblem(cost, supply, demand)

#2)
TP.construct_constraints()
TP.solve()


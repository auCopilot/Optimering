import pulp as PLP
from CustomFunctions import construct_constraints
from CustomFunctions import print_solution

h = [10.3, 11.1, 11.2, 11.9, 12.1, 12.2, 13.4, 15.2, 16.1, 16.7, 17.1, 17.2,
     17.5, 18.4, 19.5, 20.1, 22.1, 23.7, 25.8, 26.4, 27.1, 28.2]
N = range(len(h) + 1)
increments = [3,4]
connections = [(j, j + i) for j in N for i in increments if j + i < len(N)]
costs = [(h[j - 1] - h[i])/(j - i) for (i, j) in connections]

start = 0
target = len(N) - 1


# Minimization problem
model = PLP.LpProblem(name="NET2", sense=PLP.LpMinimize)

# Obejctive function a shortest path problem
# Define the decision variable x.
x = PLP.LpVariable.dicts("x", connections, lowBound=0)
# Index into decision variable x using the tuples of connections,
# and multiply by the corresponding costs to get the objective function.
model += PLP.lpSum(costs[i]*x[connections[i]] for i in range(len(connections))), "Objective"

# Contraints, positivity assumed:

# One unit of flow is sent from the start node.
model += PLP.lpSum(x[(i, j)] for (i, j) in connections if i ==
                                            start) == 1, "StartConstraint"
# One unit of flow is received at the target node.
model += PLP.lpSum(x[(i, j)] for (i, j) in connections if j == target) == 1,"TargetConstraint"
# Flow balance constraints for all other nodes.
for k in N:
     if k != start and k != target:
          model += ((PLP.lpSum(x[(i,j)]
                             for (i,j) in connections if i == k)-
                    PLP.lpSum(x[(i,j)]
                             for (i,j) in connections if j == k) == 0,
                    f"OutInNode{k}"))
print_solution(model, condition = lambda x: abs(x.varValue) >= 0.1)

# a) Optimal solution
objective_function_value_a = model.objective.value()
group_idx = [idx for idx, var in x.items() if var.value() > 1e-6]

for g in range(len(group_idx)):
     print(f"players in group {g + 1} are: \n")
     for i in range(*group_idx[g]):
          print(f"player{i + 1}")
     print("\n")

# Print af dual information
print("Duale priser:")
for name, c in list(model.constraints.items()):
     print(name,":",c.pi)

# b)
# Add constraint that we have 6 groups

model += PLP.lpSum(x[c] for c in connections) == 6, "GroupingConstraint"

print_solution(model, condition = lambda x: abs(x.varValue) >= 0.1)
objective_function_value_b = model.objective.value()
group_idx = [idx for idx, var in x.items() if var.value() > 1e-6]

for g in range(len(group_idx)):
     print(f"players in group {g + 1} are: \n")
     for i in range(*group_idx[g]):
          print(f"player{i + 1}")
     print("\n")
# Difference in objective function values
print(f"Difference in objective function values: {objective_function_value_b - objective_function_value_a}")



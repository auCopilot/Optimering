import pulp as PLP
from CustomFunctions import construct_constraints

# Maximization problem
model = PLP.LpProblem(name="LP2", sense=PLP.LpMaximize)

variable_names = ["N", "L"]
n_variables = len(variable_names)
objective_coefficients = [70, 100]
lower_bounds = [0, 0]

# Define decision variables using dictionaries
x = {
    name: PLP.LpVariable(name=name, lowBound=lb)
    for name, lb in zip(variable_names, lower_bounds)
}
# Define objective function coefficients
model += PLP.lpSum(objective_coefficients[i] * x[variable_names[i]] for i in
                   range(n_variables)), "Objective"

# Coefficient matrix for constraints
coef_matrix = [[2.25, 2.5],
               [1.0, 0.5],
                [1., 2.],
               [1/3, -2/3],
               [-1/3, 2/3]]
# all are less than or equal to constraints
constraint_types = ["<="] * len(coef_matrix)
# Right-hand side values for constraints
rhs = [30*30, 10*30, 20*30, 0, 0]
# Construct constraints
construct_constraints(model,
                      x,
                      variable_names,
                      coef_matrix,
                      rhs,
                      constraint_types)

from CustomFunctions import print_solution
print_solution(model)



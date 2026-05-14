import pulp as PLP
import numpy as np
from math import ceil, floor
import copy
from pyexpat import model


def branch_and_bound(LPmodel, sense, best_so_far = [None], objectives = [None], problem = [0]):

    """

    :param LPmodel:
    input a Linear Programming relaxation of the ILP problem.
    Note it is import to keep track of if it is a minimization or maximization problem, as this will determine the
    branching strategy and pruning strategy.
    :return:
    Iterative Branch and Bound solution to the ILP problem.
    """
    if best_so_far[0] is None:
        if sense == "maximize":
            best_so_far[0] = -10 ** 6
        else:
            best_so_far[0] = 10 ** 6

    if sense != "maximize" and sense != "minimize":
        raise ValueError("sense must be either 'maximize' or 'minimize'")
    if sense == "maximize":
        def objective_is_not_better(obj):
            return obj < best_so_far[0]
    if sense == "minimize":
        def objective_is_not_better(obj):
            return obj > best_so_far[0]


    def is_integer_value():
        """
        :return:
        dict where keys are variable names and values are boolean values indicating whether variable is integer.
        """
        eps = 10**-4
        vars = LPmodel.variables()

        d = dict()
        # Assign boolean values to the decision variables based on whether they are integer or not
        for var in vars:
            if abs(var.varValue - ceil(var.varValue)) > eps and abs(var.varValue - floor(var.varValue)) > eps:
                d[var.name] = False
            else:
                d[var.name] = True
        return d
    print(20*"#")
    print("Problem : ", problem[0])
    print(20 * "#")
    print()
    ### Step 1 - Solve problem ###
    LPmodel.solve(PLP.PULP_CBC_CMD(msg = 0))
    obj = PLP.value(LPmodel.objective)
    ### Step 2 - Branch on non-integer decision variable
    vars = is_integer_value()
    if LPmodel.status == PLP.LpStatusInfeasible:
        print("Pruning branch, infeasible\n")
        return objectives
    if objective_is_not_better(obj):
        print("Pruning branch with objective value ", obj, " which is worse than best so far ", best_so_far[0])
        print("Decision variables: ")
        for v in LPmodel.variables():
            print(v.name, "=", v.varValue)
        print("Objective value: ", obj)
        print()
        return objectives
    if all([v for v in vars.values()]):
        print("Found feasible branch, backtracking")
        print("Decision variables: ")
        for v in LPmodel.variables():
            print(v.name, "=", v.varValue)
        print("Objective value: ", obj)
        print()
        best_so_far[0] = obj
        objectives[0] = obj
        return objectives


    for name, value in vars.items():
        if value:
            continue
        else:
            branch_name = name
            branch_value = LPmodel.variablesDict()[branch_name].varValue
            break
    ### Step 3 - Create two branches and solve recursively ###
    ### Base case - All decision variables or the problem is not feasible or objective does not become better ###


    # Left branch
    left_model = copy.deepcopy(LPmodel)
    left_model += left_model.variablesDict()[branch_name] <= floor(branch_value)

    for v in LPmodel.variables():
        print(v.name, "=", v.varValue)
    print("Objective: ", obj)
    print("Adding constraint ", branch_name, " <= ", floor(branch_value), " to left branch")
    print()
    problem[0] = problem[0] + 1
    branch_and_bound(left_model, sense, best_so_far, objectives, problem)

    # Right branch
    right_model = copy.deepcopy(LPmodel)
    right_model += right_model.variablesDict()[branch_name] >= ceil(branch_value)
    print("Adding constraint ", branch_name, " >= ", ceil(branch_value), " to left branch")
    print()
    problem[0] = problem[0] + 1
    branch_and_bound(right_model, sense, best_so_far, objectives, problem)

    return objectives




### Example ###

if __name__ == "__main__":
    model = PLP.LpProblem("Example", sense = PLP.LpMaximize)

    x_range = range(3)
    coef = [55, 53, 81]
    x = PLP.LpVariable.dicts("x", x_range, lowBound= 0, cat = PLP.LpContinuous)
    model += PLP.lpSum(coef[i]*x[i] for i in x_range), "Objective"

    c1 = [8, 2, 4]
    model += PLP.lpSum(c1[i]*x[i] for i in x_range) <= 50, "Constraint1"
    c2 = [1, 8 , 7]
    model += PLP.lpSum(c2[i]*x[i] for i in x_range) <= 60, "Constraint2"
    c3 = [4, 5, 4]
    model += PLP.lpSum(c3[i]*x[i] for i in x_range) <= 50, "Constraint3"

    sol = branch_and_bound(model, "minimize")
    print("Best solution: ", sol[0])
    print()



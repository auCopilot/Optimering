import numpy as np
import pulp as PLP


def latex_lp(objective, constraints, sense):
    """
    constraints should be tuples:
        (lhs, operator, rhs)

    Example:
        ("x + y", "<=", 5)
    """

    op_map = {
        "<=": r"\leq",
        ">=": r"\geq",
        "=": "="
    }

    lines = [
        r"\begin{align*}",
        rf"\text{{{sense}}} \quad & {objective} \\",
        r"\text{subject to} \quad"
    ]

    for i, (lhs, op, rhs) in enumerate(constraints):

        latex_op = op_map.get(op, op)
        line = rf"& {lhs} {latex_op} {rhs}"

        if i < len(constraints) - 1:
            line += r" \\"

        lines.append(line)

    lines.append(r"\end{align*}")

    return "\n".join(lines)

def dual_lp(model, var_bounds, quiet = True):
    """Input a pulp model, and get the dual problem.
    Implementation follows Uge 9 Kap6  Dualitet og følsomhedsanalyse and Det duale lp

    Input:
    primal linear problem model
    var bounds - e.g if x1 >= 0 and x2 <= 0 and x3 is free, then var_bounds = [">=", "<=", None], positive, negative, free.
    Note if you get a key error, then remember to have to add zero coefficient variables explicitly
    """
    # -1 for max in original problem -> minimize dual
    #  1 for min in original problem -> maximize dual
    sense = model.sense
    if sense not in (1, -1):
        raise ValueError("Sense must be -1 or 1")
    if sense == -1:
        sense = "MAX"
    else:
        sense = "MIN"
    model.solve(PLP.PULP_CBC_CMD(msg = 0 if quiet else 1))

    # Duals (shadow prices)
    for name, constraint in model.constraints.items():
        print(name, "dual =", constraint.pi)

    # Reduced costs
    for v in model.variables():
        print(v.name, "reduced cost =", v.dj)

    if sense == "MAX":
        print("Primal LP is MAXIMIZATION, so DUAL LP is MINIMIZATION\n")
        dual_model = PLP.LpProblem("DUAL", sense=PLP.LpMinimize)
    elif sense == "MIN":
        print("Primal LP is MINIMIZATION, so DUAL LP is MAXIMIZATION\n")
        dual_model = PLP.LpProblem("DUAL", sense=PLP.LpMaximize)

    # Construct coefficient matrix for later use, and assign dummy obejctive function
    dual_model += 0, "Objective"
    n_constraints = len(model.constraints.items())
    n_coef = len(model.variables())
    coef_matrix = np.zeros((n_constraints, n_coef))

    # Loop over each constraint and variable to fill the coefficient matrix, if variable is not in constraint, assign 0
    for i, val in enumerate(model.constraints.values()):
        for j, var in enumerate(model.variables()):
            try:
                coef_matrix[i, j] = val[var]
            except KeyError:
                coef_matrix[i, j] = 0


    ### CREATE OBJECTIVE FOR DUAL LP ###
    i = 0
    for name, c in model.constraints.items():
        # RHS
        rhs = -c.constant
        # Sense
        # lhs <= c_i
        if c.sense == -1:
            y = PLP.LpVariable(f"y{i}",
                               lowBound= 0 if sense == "MAX" else None,
                               upBound= 0 if sense == "MIN" else None,
                            )
            # print("  sense = <=")
            term = y * rhs
        # lhs >= c_i
        elif c.sense == 1:
            y = PLP.LpVariable(f"y{i}",
                               upBound=0 if sense == "MAX" else None,
                               lowBound=0 if sense == "MIN" else None)
            # print("  sense = >=")
            term = y * rhs
        # lhs == c_i
        elif c.sense == 0:
            # No bounds on equaility constraints
            y = PLP.LpVariable(f"y{i}")
            # print("  sense = =")
            term = y * rhs
        # Update objective
        dual_model.objective = dual_model.objective + term
        i += 1

    ### CREATE CONSTRAINTS FOR DUAL LP ###
    # Get
    dual_coef_matrix = coef_matrix.T
    objective_coefs = [model.objective[var] for var in model.variables()]
    rows, cols = dual_coef_matrix.shape

    for i in range(rows):
        lhs = PLP.lpSum(dual_coef_matrix[i][j] * dual_model.variables()[j] for j in range(cols))
        if var_bounds[i] == ">=":
            if sense == "MAX":
                dual_model += lhs >= objective_coefs[i], f"dual_constraint{i + 1}"
            else:
                dual_model += lhs <= objective_coefs[i], f"dual_constraint{i + 1}"
        elif var_bounds[i] == "<=":
            if sense == "MAX":
                dual_model += lhs <= objective_coefs[i], f"dual_constraint{i + 1}"
            else:
                dual_model += lhs >= objective_coefs[i], f"dual_constraint{i + 1}"

        elif var_bounds[i] is None:
            dual_model += lhs == objective_coefs[i], f"dual_constraint{i + 1}"
    # print objective and constraint for dual problem
    print("MINIMIZE" if sense == "MAX" else "MAXIMIZE")
    dual_obj = dual_model.objective
    print(dual_obj)
    print("SUBJECT TO")
    constraint_list = []
    for name, constraint in dual_model.constraints.items():

        lhs = str(constraint.expr)
        rhs = -constraint.constant

        if constraint.sense == -1:
            op = "<="
        elif constraint.sense == 1:
            op = ">="
        else:
            op = "="
        print(lhs, op, rhs)

        constraint_list.append((lhs, op, rhs))

    for var in dual_model.variables():

        if var.lowBound is not None:
            print(str(var), ">=", var.lowBound)
            constraint_list.append(
                (str(var), ">=", var.lowBound)
            )

        if var.upBound is not None:
            print(str(var), "<=", var.upBound)
            constraint_list.append(
                (str(var), "<=", var.upBound)
            )

    latex = latex_lp(dual_obj, constraint_list, "MINIMIZE" if sense == "MAX" else "MAXIMIZE")







    return dual_model, latex


if __name__ == "__main__":
    prob = PLP.LpProblem("Example", PLP.LpMaximize)

    x = PLP.LpVariable("x", lowBound=0)
    y = PLP.LpVariable("y", lowBound=0)

    prob += 3*x + 2*y

    prob += x + y <= 4, "c1"
    prob += 2*x + y >= 5, "c2"

    dual_lp(prob, var_bounds= 2*[">="])
    # Create model
    prob = PLP.LpProblem("Production_Problem", PLP.LpMaximize)

    # Decision variables
    x1 = PLP.LpVariable("x1", lowBound=0)
    x2 = PLP.LpVariable("x2", lowBound=0)
    x3 = PLP.LpVariable("x3", lowBound=0)
    x4 = PLP.LpVariable("x4", lowBound=0)
    x5 = PLP.LpVariable("x5", lowBound=0)

    # Objective function
    prob += (
    550*x1 +
    600*x2 +
    350*x3 +
    400*x4 +
    200*x5
    ), "Profit"

    # Constraints
    prob += (
    12*x1 +
    20*x2 +
    25*x4 +
    15*x5
    <= 288
    ), "Slibning"

    prob += (
    10*x1 +
    8*x2 +
    16*x3
    <= 192
    ), "Boring"

    prob += (
    20*x1 +
    20*x2 +
    20*x3 +
    20*x4 +
    20*x5
    <= 384
    ), "Samling"

    dual, latex = dual_lp(prob, var_bounds= 5*[">="])

    dual.solve()
    print(latex)

    # Create model
    prob = PLP.LpProblem("LP_Problem", PLP.LpMaximize)

    # Decision variables
    x1 = PLP.LpVariable("x1", lowBound=0)
    x2 = PLP.LpVariable("x2", lowBound=0)
    x3 = PLP.LpVariable("x3", lowBound=0)

    # Objective function
    prob += (
            6 * x1 +
            14 * x2 +
            13 * x3
    ), "Objective"

    # Constraints
    prob += (
            0.5 * x1 +
            2 * x2 +
            x3
            <= 24
    ), "Constraint1"

    prob += (
            x1 +
            2 * x2 +
            4 * x3
            <= 60
    ), "Constraint2"

    dual, latex = dual_lp(prob, var_bounds= 3*[">="])

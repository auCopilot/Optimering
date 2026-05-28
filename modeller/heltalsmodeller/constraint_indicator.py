import pulp as PLP

def constraint_indicator(model_wrapper, constraint_name, eps = 10**-3, large_upper = 9999, small_lower = -9999):

    delta = PLP.LpVariable("delta_" + constraint_name, cat= PLP.LpBinary, lowBound= 0, upBound= 1)

    # Extract the expression and the constant from the constraint, pulp moves constant to lhs
    constraint = model_wrapper.model.constraints[constraint_name]
    expr = constraint.expr + constraint.constant


    # Add an upper bound inequality that does not restrict the solution if delta = 0
    model_wrapper.model +=  expr <= large_upper * (1 - delta),"UpperBoundIndicator" + constraint_name

    model_wrapper.model += expr >= (small_lower - eps) * delta + eps, "LowerBoundIndicator" + constraint_name




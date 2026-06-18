import pulp as PLP
from copy import deepcopy

def limit_number_of_positive_variables(model_wrapper, var_name, k,  M = 10**6 ):
    """
    This function adds a constraint to the model that limits the number of positive variables to k.
    :param model: ILP/LP model from a class wrapper
    :param k: The maximum number of positive variables allowed
    :return: ILP model where the constraint is added. The model is modified in place
    """

    model_wrapper = deepcopy(model_wrapper)
    var_of_interest = [var for var in model_wrapper.model.variables() if  var_name in var.name]
    var_of_interest_names = [str(var.name) for var in var_of_interest]
    # We introduce binary variables to indicate if a variable is positive or not for each variable of interest
    delta_limit = PLP.LpVariable.dicts("delta_limit", var_of_interest_names, cat=PLP.LpBinary)

    for v in var_of_interest:
        # If v is positive, then delta[v] must be 1
        model_wrapper.model += v <= delta_limit[v.name] * M, f"delta_limit_{v}"
    # We add the constraint that at most k variables can be positive
    model_wrapper.model += PLP.lpSum(delta_limit[v.name] for v in var_of_interest) <= k, "LimitPositiveVariables_" + var_name
    return model_wrapper
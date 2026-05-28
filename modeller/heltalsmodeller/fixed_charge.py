import pulp as PLP

def fixed_charge(model_wrapper, F, model_var, large_value = 999):
    """
    Implementation follows uge 11 Kap9 - Heltalsmodeller
    :param model_wrapper: Class wrapper for the model
    :param F: Fixed charge value
    :param model_var: Model variable we want to charge a fixed charge for being positive
    :param large_value: Upper bound for x
    :return: Adds fixed charge inplace to the model
    """

    indicator = PLP.LpVariable("indicator", cat = PLP.LpBinary)

    model_wrapper.model += model_var <= large_value * indicator, "FixedChargeConstraint"

    model_wrapper.model.objective = model_wrapper.model.objective + F * indicator
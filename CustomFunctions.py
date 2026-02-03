import pulp as PLP

def construct_constraints(model,
                          x,
                          variable_names,
                          coef_matrix,
                          rhs,
                          equality_types):

    """Construct constraints for a LP model.
    Inputs:
        model: PuLP LpProblem instance
        x: dictionary of PuLP LpVariable instances
        variable_names: list of variable names corresponding to x
        coef_matrix: list of lists, where each inner list contains coefficients
                     for the variables in a constraint.
        rhs: list of right-hand side values for each constraint.
        equality_types: list of strings indicating the type of each constraint
                        ("<=", ">=", "==").

    """
    # Determine number of constraints from length of rhs
    n_constraints = len(rhs)
    n_variables = len(variable_names)
    # Define constraints according to their types.
    for i in range(n_constraints):
        constraint_expr = PLP.lpSum(coef_matrix[i][j] * x[variable_names[j]]
                                    for j in range(n_variables))
        if equality_types[i] == "<=":
            model += constraint_expr <= rhs[i], f"Constraint_{i+1}"
        elif equality_types[i] == ">=":
            model += constraint_expr >= rhs[i], f"Constraint_{i+1}"
        elif equality_types[i] == "==":
            model += constraint_expr == rhs[i], f"Constraint_{i+1}"

    print("Constraints constructed.")


def print_solution(Model):
    # Loesning af modellen vha. PuLP's valg af Solver
    Model.solve()
    # Print af loesningens status
    print("Status:", PLP.LpStatus[Model.status])
    # Print af hver variabel med navn og loesningsvaerdi
    for v in Model.variables():
        print(v.name, "=", v.varValue)
    # Print af den optimale objektfunktionsvaerdi
    print("Obj. = ", PLP.value(Model.objective))

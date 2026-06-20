from KnapSack import knap_sack
import pulp as PLP
import numpy as np
from CustomFunctions import print_solution
from CuttingStockMasterLP import cutting_stock_master_lp

def generate_column(model, pattern, desired_amounts, weights, capacity):
    # Dual values
    values = [c.pi for c in model.constraints.values()]
    print("\nDual values:", values)

    # Solve unbounded knapsack problem to find improving pattern
    dual_model, n = knap_sack(weights, values, capacity, kp_type = "unbounded")
    dual_model.solve(PLP.PULP_CBC_CMD(msg = 0))
    # Extract values
    dual_objective_value = PLP.value(dual_model.objective)
    variable_values = [v.varValue for v in dual_model.variables()]

    if dual_objective_value <= 1:
        # Keep last solution if no improvements.
        print("No further LP-Relaxation improvement possible, final version "
              "is "
              "previous "
              "model.")
        print("Dual objective value:", dual_objective_value)

    else:
        # Update solution
        print("\nUPDATED SOLUTION")
        print("Dual objective value:", dual_objective_value)
        print("Adding improving pattern")
        print(np.array(variable_values))

        # Update pattern
        pattern = np.hstack(
            (pattern, np.array(variable_values)[:, np.newaxis]))
        print("Updated Pattern")
        print(pattern)

        # Update master problem
        model, pattern = cutting_stock_master_lp(capacity,
                                                 desired_amounts,
                                                 weights,
                                                 pattern)

    return model, pattern, dual_objective_value
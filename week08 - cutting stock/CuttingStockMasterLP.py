import pulp as PLP
from CustomFunctions import print_solution, construct_constraints
import numpy as np

def cutting_stock_master_lp(stock_length, desired_amounts, lengths, pattern = None):

    """Formulate the master LP for the cutting stock problem.
    Inputs:
    stock_length: int, the length of the stock material
    desired_amounts: list of ints, the desired amounts of each length
    lengths: list of ints, the lengths of the pieces to be cut"""

    model = PLP.LpProblem(name="CuttingStock", sense=PLP.LpMinimize)
    n = len(desired_amounts)
    # Naive pattern, cut as many pieces as possible of each length
    if pattern is None:
        pattern = np.zeros((n,n))
        for idx in range(n):
            pattern[idx][idx] = stock_length // lengths[idx]

    j = pattern.shape[1]
    pattern_range = range(j)
    gamma = PLP.LpVariable.dicts("gamma",pattern_range, lowBound=0)

    model += PLP.lpSum(gamma[j] for j in pattern_range), "Objective"

    for i in range(n):
        model += (PLP.lpSum(pattern[i][j] * gamma[j] for j in pattern_range ) >=
                  desired_amounts[i]), f"PatternConstraint{i}"
    model.solve(PLP.PULP_CBC_CMD(msg = 0))
    return model, pattern
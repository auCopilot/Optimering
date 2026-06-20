import pulp as PLP
from CustomFunctions import print_solution
def cutting_stock_feasible_soution(stock_length, desired_amounts, lengths):
    """
    Feasible solution to the cutting stock problem, using the weak formulation.
    Upper bound on the number of stock needed is found by cutting as many
    pieces as possible of each length, and then summing the number of stocks
    needed for each length.
    """
    lengths_pr_stock = [stock_length // l for l in lengths]
    n_each_length = [desired_amounts[i] // lengths_pr_stock[i] + 1 for i in range(len(desired_amounts))]
    stock_needed = sum(n_each_length)
    return stock_needed


def cutting_stock_weak_formulation(stock_length, desired_amounts, lengths,
                                   low_indicies = True):

    m = cutting_stock_feasible_soution(stock_length, desired_amounts, lengths)
    model = PLP.LpProblem(name="CuttingStockWeakFormulation", sense=PLP.LpMinimize)
    n = len(desired_amounts)
    pipe_range = range(m)
    length_range = range(n)
    x = PLP.LpVariable.dicts("x",
                             (length_range, pipe_range),
                             lowBound= 0,
                             upBound = None,
                             cat = PLP.LpInteger)
    delta = PLP.LpVariable.dicts("delta", pipe_range, lowBound=0, upBound=1, cat=PLP.LpBinary)

    sections = [stock_length // l for l in lengths]

    for i in length_range:
        for j in pipe_range:
            model += x[i][j] <= sections[i] * delta[j]

    for j in pipe_range:
        model += (PLP.lpSum(lengths[i] * x[i][j] for i in length_range) <=
                  stock_length, f"PipeConstraint{j}")

    for i  in length_range:
        model += (PLP.lpSum(x[i][j] for j in pipe_range) >= desired_amounts[
            i], f"DemandConstraint{i}")

    model += PLP.lpSum(delta[p] for p in pipe_range), "Objective"

    # If low indicies is True, we add the constraint that a pipe can only be
    # used if the previous pipe is used, to break symmetries.
    if low_indicies:
        for idx in pipe_range[1:]:
            model += delta[idx - 1] >= delta[idx]

    print_solution(model, condition = lambda x: abs(x.varValue) >= 0.1 )
    return model

""" Example usage from slides Uge 12"""

# Only run if called in this file, not if imported as a module
if __name__ == "__main__":
    # Capacity / length of the stock material
    stock_length = 19
    # Desired amounts of each length
    desired_amounts = [12, 15, 22]
    # Respective lengths
    lengths = [4,5,6]

    cutting_stock_weak_formulation(stock_length, desired_amounts, lengths)




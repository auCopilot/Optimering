import pulp as PLP
from CustomFunctions import print_solution, construct_constraints
from CuttingStockMasterLP import cutting_stock_master_lp

from CuttingStockColumnProblem import generate_column





"""Example usage from CuttingStock Slides Uge 12"""
# Dummy dual objective value to start the column generation loop
if __name__ == "__main__":
    dual_objective_value = 9999

    # Capacity / length of the stock material
    stock_length = 19
    # Desired amounts of each length
    desired_amounts = [12, 15, 22]
    # Respective lengths
    lengths = [4,5,6]
    model, pattern = cutting_stock_master_lp(stock_length, desired_amounts, lengths)

    print("INITIAL SOLUTION")
    print_solution(model)

    while dual_objective_value > 1:

        model, pattern, dual_objective_value = generate_column(model, # Model
                                                               pattern, # Pattern
                                                               desired_amounts, # Desired amounts
                                                               lengths, # Lengths of pieces - Weights in knapsack problem
                                                               stock_length # Capacity in knapsack problem
                                                               )


    print("\nFINAL SOLUTION")
    print_solution(model)
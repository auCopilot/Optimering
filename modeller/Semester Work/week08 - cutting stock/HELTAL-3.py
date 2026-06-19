"""1)
Weak fourmulation of the cutting stock problem
"""

from CuttingStockWeakFormulation import cutting_stock_weak_formulation

stock_length = 20
desired_amounts = [20, 31, 27, 23]
lengths = [7, 5, 4 , 3]

print("Weak forumaltion, EXACT SOLUTION:")
cutting_stock_weak_formulation(stock_length, desired_amounts, lengths)

print("\n\n2) Column generation for the cutting stock problem")
from CuttingStockLowerBoundLP import cutting_stock_master_lp
from CuttingStockColumnProblem import generate_column
from CustomFunctions import print_solution

# Dummy dual objective value to start the column generation loop
dual_objective_value = 9999
# No pattern to start with, so we use the default naive pattern in the master LP.
model, pattern = cutting_stock_master_lp(stock_length, desired_amounts, lengths)

""" 2)
 Lower bound LP formulation of the cutting stock problem,
 solved with column generation
 """

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

print("CLASS IMPLEMENTATION OF THE CUTTING STOCK PROBLEM")

from modeller.cutting_stock import cutting_stock
CSP = cutting_stock(stock_length, lengths, desired_amounts)
CSP.define_constraints()
CSP.solve_and_print_solution()

import pulp as plp
from knapsack import knapsack
class subsetsum(knapsack):
    """Special case of knapsack, where profits and weights are the same.
    Goal is to find a subset of items that maximize the total weight in the knapsack
    """
    def __init__(self, weights, capacity):
        super().__init__(profits = weights, weights = weights, capacity = capacity)
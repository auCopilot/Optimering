import math
import pulp as PLP

class cutting_stock:
    """
    This implementation follows week 12 CuttingStock
    Input:
    - standard_stock_length: The length of the stock material we have available
    - desired_stock_lengths: The lengths of the pieces we want to cut
    - desired_stock_amounts: The amount of pieces we want to cut of each length
    """
    def __init__(self, standard_stock_length, desired_stock_lengths, desired_stock_amounts):
        self.standard_stock_length = standard_stock_length
        self.desired_stock_lengths = desired_stock_lengths
        self.desired_amounts = desired_stock_amounts

        self.n = len(self.desired_stock_lengths)
        self.m = self.cutting_stock_feasible_soution() # Computes upper bound

        self.sections = [math.floor(self.standard_stock_length / self.desired_stock_lengths[i]) for i in range(self.n)]

        # General integer variables x
        self.x = PLP.LpVariable.dicts("x", indices= (range(self.n), range(self.m)), cat= PLP.LpInteger, lowBound=0, upBound= None)
        # Objective variable delta
        self.delta = PLP.LpVariable.dicts("delta", indices=(range(self.m)), cat= PLP.LpBinary)
        self.model = PLP.LpProblem(name="CuttingStockWeakFormulation", sense=PLP.LpMinimize)
        self.model += PLP.lpSum(self.delta[j] for j in range(self.m)), "Objective"

    def cutting_stock_feasible_soution(self):
        """
        Feasible solution to the cutting stock problem, using the weak formulation.
        Upper bound on the number of stock needed is found by cutting as many
        pieces as possible of each length, and then summing the number of stocks
        needed for each length.
        """
        lengths_pr_stock = [self.standard_stock_length // l for l in self.desired_stock_lengths]
        n_each_length = [self.desired_amounts[i] // lengths_pr_stock[i] + 1 for i in range(len(self.desired_amounts))]
        stock_needed = sum(n_each_length)
        return stock_needed

    def define_constraints(self, add_symmetry_constraint = True):

        for i in range(self.n):
            # Demand constraint
            self.model += PLP.lpSum(self.x[i][j] for j in range(self.m)) >= self.desired_amounts[i], f"Demand{i}"
            for j in range(self.m):
                self.model += self.x[i][j] <= self.sections[i] * self.delta[j], f"Section{i}_{j}"

        for j in range(self.m):
            # Capacity constraint
            self.model += (PLP.lpSum(self.desired_stock_lengths[i] * self.x[i][j] for i in range(self.n)) <=
                           self.standard_stock_length, f"Capacity{j}")
        self.constaints = "ADDED"

        if add_symmetry_constraint:
            for j in range(1, self.m):
                # First pipe must be used before the second pipe can be used, and so on, to break symmetries.
                self.model += self.delta[j - 1] >= self.delta[j]

    def solve_and_print_solution(self, msg = True, eps = 0.1):
        if self.constaints != "ADDED":
            raise ValueError("You must add constraints first")
        self.model.solve(PLP.PULP_CBC_CMD(msg=msg))
        print("Status:", PLP.LpStatus[self.model.status])

        for i in range(self.n):
            for j in range(self.m):
                x = self.x[i][j].varValue
                if x > eps:
                    print(f"Solution uses makes {x} cuts of length {self.desired_stock_lengths[i]} of the stock number {j + 1}")
        print("Amount of standard stock used:", PLP.value(self.model.objective))
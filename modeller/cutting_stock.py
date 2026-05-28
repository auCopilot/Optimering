import math
import pulp as PLP

class cutting_stock:
    """
    This implementation follows week 12 CuttingStock
    Input:



    """
    def __init__(self, standard_stock_length, amount_of_standard_stock, desired_stock_lengths, desired_stock_amounts):
        self.standard_stock_length = standard_stock_length
        self.desired_stock_lengths = desired_stock_lengths
        self.desired_stock_amounts = desired_stock_amounts

        self.n = len(self.desired_stock_lengths)
        self.m = amount_of_standard_stock

        self.sections = [math.floor(self.standard_stock_length / self.desired_stock_lengths[i]) for i in range(self.n)]

        # General integer variables x
        self.x = PLP.LpVariable.dicts("x", indices= (range(self.n), range(self.m)), cat= PLP.LpInteger, lowBound=0, upBound= None)
        # Objective variable delta
        self.delta = PLP.LpVariable.dicts("delta", indices=(range(self.n)), cat= PLP.LpBinary)
        self.model = PLP.LpProblem(name="CuttingStockWeakFormulation", sense=PLP.LpMinimize)

    def define_constraints(self):

        for i in range(self.n):
            # Demand constraint
            self.model += PLP.lpSum(self.x[i][j] for j in range(self.m)) >= self.desired_stock_lengths[i], f"Demand{i}"
            for j in range(self.m):
                self.model += self.x <= self.sections[i] * self.delta[j], f"Section{i}_{j}"

        for j in range(self.m):
            # Capacity constraint
            self.model += (PLP.lpSum(self.desired_stock_lengths[i] * self.x[i][j] for i in range(self.n)) <=
                           self.standard_stock_length, f"Capacity{j}")
        self.constaints = "ADDED"

    def solve_and_print_solution(self, msg = True, eps = 0.1):
        if self.constaints != "ADDED":
            raise ValueError("You must add constraints first")
        self.model.solve(PLP.PULP_CBC_CMD(msg=msg))
        print("Status:", PLP.LpStatus[self.model.status])

        for i in range(self.n):
            for j in range(self.m):
                x = self.x[i][j].varValue
                if x > eps:
                    print(f"Solution uses makes {x} cuts of length {self.desired_stock_lengths[i]} of the {j +1}th stock")
        print("Amount of standard stock used:", PLP.value(self.model.objective))
import pulp as PLP

class knapsack:
    """
    This class implements the 01-knapsack model from uge 12 Pakningsproblemer
    """
    def __init__(self, profits, weights, capacity):
        self.p = profits
        self.w = weights
        self.Q = capacity
        self.N = range(len(self.profits))
        self.model = PLP.LpProblem("01-knapsack", sense= PLP.LpMaximize)

        self.x = PLP.LpVariable.dicts("x", indices= self.N, cat= PLP.LpBinary)
        self.constraints = "NOT ADDED"

    def construct_constraints(self):
        self.model += PLP.lpSum(self.w[j] * self.x[j] for j in self.N) <= self.Q, "CapacityConstraint"
        self.constraints = "ADDED"
    def solve(self, quiet = True, one_indexed = True):
        idx = 1 if one_indexed else 0
        if self.constraints != "ADDED":
            raise ValueError("You must add the constraint before solving")

        self.model.solve(PLP.PULP_CBC_CMD(msg = 0 if quiet else 1))
        # Status and objective value
        print("Status:", PLP.LpStatus(self.model.status))
        print("Objective value:", PLP.value(self.model.objective))
        for i in self.N:
            if self.x[i].varValue > 0.5:
                print(f"Item{i + idx} is added to the knapsack")

import pulp as PLP

class generalized_assignment_problem:
    """
    This class implements the GAP from uge 12 Paknings problemer.
    """
    def __init__(self, profits, weights, capacities, sense = "maximize"):
        self.p = profits
        self.w = weights
        self.Q = capacities
        self.sense = sense
        if self.sense != "maximize" or self.sense != "minimize":
            raise ValueError("Sense must be 'maximize' or 'minimize'")
        self.M = range(len(self.p[0])) # bins
        self.N = range(len(self.p)) # items
        self.model = PLP.LpProblem("GAP", sense= PLP.LpMinimize if self.sense == "minimize"
        else PLP.LpMaximize)

        self.x = PLP.LpVariable.dicts("x", indices= (self.N, self.M), cat= PLP.LpBinary)
        self.constraints = "NOT ADDED"

        # Objective
        self.model += PLP.lpSum(self.p[i][j] * self.x[i][j] for i in self.N for j in self.M), "TotalProfit"


    def construct_constraints(self):

        # Each item is assigned to at most one bin
        for i in self.N:
            self.model += PLP.lpSum(self.x[i][j] for j in self.M) == 1, f"ItemAssignment_{i}"

        # Capacity constraints for each bin
        for j in self.M:
            self.model += PLP.lpSum(self.w[i][j] * self.x[i][j] for i in self.N) <= self.Q[j], f"CapacityConstraint_{j}"

        self.constraints = "ADDED"

    def solve_and_print(self, quiet = True, one_indexed = True, print_sol = True):
        idx = 1 if one_indexed else 0
        if self.constraints != "ADDED":
            raise ValueError("You must add the constraints before solving")

        self.model.solve(PLP.PULP_CBC_CMD(msg = 0 if quiet else 1))
        # Status and objective

        if print_sol:
            print("Status:", PLP.LpStatus[self.model.status])
            print("Objective value:", PLP.value(self.model.objective))
            for i in self.N:
                for j in self.M:
                    if self.x[i][j].varValue > 0.5:
                        print(f"Item {i + idx} is assigned to bin {j + idx}")


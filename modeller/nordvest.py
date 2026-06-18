import copy
class NordVest():
    """
    This implementation of Nordvesthjørneregelen follows from Uge 8 Transport - Steppingstone of Vogels
    Approksimation, slide 8

The Northwest Corner Rule is a method used to obtain an initial feasible solution to a transportation problem.

The idea is to start with the first supplier and the first customer, which corresponds to the top-left (northwest) corner of the transportation table.

Allocate as many units as possible from the current supplier to the current customer.

If the supplier's available supply is exhausted, move down to the next supplier. If the customer's demand is completely satisfied, move to the next customer on the right.

Continue this process, always allocating as much as possible between the current supply and demand, until all supply has been distributed and all demand has been satisfied.

The method focuses only on matching supply and demand in a systematic way and does not take transportation costs into account.

Its purpose is to quickly generate a feasible starting solution that can later be improved using optimization methods.


    """
    def __init__(self, supply, demand):
        self.supply = supply
        self.demand = demand
        if sum(self.supply) - sum(self.demand) != 0:
            raise ValueError("Sum of supply and demand must be equal")

        self.s_prime = copy.copy(self.supply)
        self.d_prime = copy.copy(self.demand)

        #Decision variable as dict
        self.n = len(self.supply)
        self.m = len(self.demand)
        self.x = {(i,j) : 0 for i in range(self.n) for j in range(self.m)}

    def solve(self, one_indexed = True):
        idx = 1 if one_indexed else 0
        i = 0
        j = 0
        while i < self.n and j < self.m:
            self.x[(i,j)] = min(self.s_prime[i], self.d_prime[j])
            if i < self.m or j < self.n - 1:
                self.s_prime[i] = self.s_prime[i] - self.x[(i,j)]
                self.d_prime[j] = self.d_prime[j] - self.x[(i,j)]
                if self.d_prime[j] > 0:
                    i = i + 1
                else:
                    j = j + 1
        for key, value in self.x.items():
            if value > 0:
                print(f"Assign {value} from supplier {key[0] + idx} to customer {key[1] + idx}")



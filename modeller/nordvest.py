import copy
class NordVest():
    """
    This implementation of Nordvesthjørneregelen follows from Uge 8 Transport - Steppingstone of Vogels
    Approksimation, slide 8
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

    def solve(self):
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



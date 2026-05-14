import numpy as np
import pulp as PLP


class min_cost_flow:
    """
    This implementation follows from Uge 7 Afsnit 5.3 Netværksmodeller,
    we have multiple sources and sinks, and we want to find the flow that minimizes the cost of the flow,
     while satisfying the flow conservation constraints at each node.

     Note if a nodes is just a flow through node, then the supply is zero. It is negative for sinks and postive for sources.

     Input:
     nodes - list of nodes
     edges - list of edges, where each edge is a tuple (i,j) representing a
     cost - dictionary, where key edge is associated with a value cost
     supply - list where index supply[k] where k E nodes gives supply for node k
     capacity - optional dictionary where key edge is associated with a maximum capacity


     Note 2:
     En til alle korteste veje problemet kan formuleres således:

    Der er givet en orienteret graf G=(N,A)
    For hver kant (i,j)∈A er der givet en længde (omkostning) c
    ij
        ​

    Her antages, at alle kantlængder er ikke-negative
    Længden af en vej (sti) mellem to punkter i netværket er givet ved summen af de kantlængder, som vejen er sammensat af
    Der ønskes identificeret den korteste vej fra et givet punkt s til hvert af de øvrige punkter i netværket
    Konkret kan problemet formuleres som et minimum cost flow problem ved at give punkt s et udbud på ∣N∣−1 enheder og
    hvert af de øvrige punkter en efterspørgsel på én enhed
    For hvert punkt j∈N∖{s} vil den enhed, som i en optimalløsning sendes fra s til j, følge den korteste vej fra s til j

    """
    def __init__(self, nodes, edges, cost, supply, capacity=None):
        self.nodes = nodes
        self.edges = edges
        self.cost = cost
        self.supply = supply
        self.capacity = capacity

        # Model, decision variable and objective
        self.model = PLP.LpProblem("Min_Cost_Flow", PLP.LpMinimize)
        self.x = PLP.LpVariable.dicts("x", self.edges, lowBound=0, cat=PLP.LpContinuous)
        self.model += PLP.lpSum([cost[e] * self.x[e] for e in self.edges]), "Objective"



    def construct_constraints(self):
        #Outflow - inflow = Supply for all nodes
        for node in self.nodes:
            self.model += (PLP.lpSum(self.x[e] for e in self.edges if e[0] == node) -
                           PLP.lpSum(self.x[e] for e in self.edges if e[1] == node) == self.supply[node],
                           f"Flow_Conservation_Constraint_{node}")
        if self.capacity is not None:
            for e in self.edges:
                try:
                    self.model += self.x[e] <= self.capacity[e], f"Capacity_Constraint_{e}"
                except KeyError:
                    print(f"No capacity costraint for edge {e}")
                    continue

    def solve_and_print(self):
        self.construct_constraints()
        self.model.solve()

        print("Status:", PLP.LpStatus[self.model.status])
        print("Objective value:", PLP.value(self.model.objective))
        for e in self.edges:
            if self.x[e].varValue is not None and self.x[e].varValue > 0:
                print(f"Edge {e} is included in the solution with cost {round(self.cost[e], 2)}")



# Example usage:

if "__main__" == __name__:
    print("EXAMPLE 5.4")
    FraPunkt = [0, 1, 2, 2, 2, 3, 3, 4, 4, 4, 7]
    TilPunkt = [2, 3, 3, 4, 5, 4, 7, 2, 5, 6, 6]
    Omk = [ 5, 4, 2, 6, 5, 1, 2, 4, 6, 3, 4]

    supply = [10, 15, 0, 0, 0, -9, -10, -6]
    nodes = range(8)
    edges = list(zip(FraPunkt, TilPunkt))
    cost = {}

    for i, e in enumerate(edges):
        cost[e] = Omk[i]
    MCF = min_cost_flow(nodes, edges, cost, supply)
    MCF.solve_and_print()

    print("EXAMPLE ONE TO ALL SHORTEST PATH")
    FraPunkt = [0, 0, 1, 1, 2, 2, 2, 3, 3, 4, 4, 4, 5, 6, 6, 7]
    TilPunkt = [1, 3, 2, 3, 3, 4, 5, 4, 6, 5, 6, 7, 7, 7, 8, 8]
    Omk = [1, 1, 1, 2, 1, 1, 3, 2, 4, 3, 2, 4, 1, 2, 1, 1]
    nodes = range(9)
    supply = [-1] * len(nodes)
    supply[0] = len(nodes) - 1
    edges = list(zip(FraPunkt, TilPunkt))

    cost = {}
    for i, e in enumerate(edges):
        cost[e] = Omk[i]

    OTASP = min_cost_flow(nodes, edges, cost, supply)
    OTASP.solve_and_print()


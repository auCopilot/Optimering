import numpy as np
import pulp as PLP

class shortest_path:
    """
    This implementation of the shortest path problem, follows from Uge 7 Afsnit 5.3 Netværksmodeller.

    Input:
    nodes - list of nodes
    edges - list of edges
    cost - the cost associated with each edge (i,j)
    start_node - the index of the starting node
    end_node - the index of the ending node
    """
    def __init__(self, nodes, edges, cost, start_node = None, end_node = None):
        self.nodes = nodes
        self.edges = edges
        self.cost = cost
        if start_node is not None:
            self.start_node = start_node
        else:
            self.start_node = nodes[0]
        if end_node is not None:
            self.end_node = end_node
        else:
            self.end_node = nodes[-1]

        self.model = PLP.LpProblem("Shortest_Path", PLP.LpMinimize)
        # Non negative continous decision variable.
        self.x = PLP.LpVariable.dicts("x", self.edges, lowBound=0, cat = PLP.LpContinuous)


        # Objective
        if type(self.cost) is not dict:
            self.model += PLP.lpSum(cost[k] * self.x[e] for k, e in enumerate(self.edges)), "Objective"
        if type(self.cost) is dict:
            self.model += PLP.lpSum(cost[e] * self.x[e] for e in self.edges), "Objective"


    def construct_constraints(self):

        # One output from start node
        self.model += PLP.lpSum(self.x[e] for e in self.edges if e[0] == self.start_node) == 1, "Start_Node_Constraint"
        # One input to end node
        self.model += PLP.lpSum(self.x[e] for e in self.edges if e[1] == self.end_node) == 1, "End_Node_Constraint"
        # Balance contraint, inflow = outflow, for all nodes that are not start or end
        for node in self.nodes:
            if node != self.start_node and node != self.end_node:
                self.model += ((PLP.lpSum(self.x[e] for e in self.edges if e[0] == node) -
                               PLP.lpSum(self.x[e] for e in self.edges if e[1] == node)) == 0,
                               f"Balance_Constraint_{node}")

    def solve_and_print(self):
        self.construct_constraints()
        self.model.solve()

        print("Status:", PLP.LpStatus[self.model.status])
        print("Objective value:", PLP.value(self.model.objective))
        for k, e in enumerate(self.edges):
            if self.x[e].varValue is not None and self.x[e].varValue > 0:
                print(f"Edge {e} is included in the solution with cost {self.cost[k] if type(self.cost) is not dict
                else self.cost[e]}")

# Example usage:

if __name__ == "__main__":
    print("EXAMPLE 5.5")
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
    print(type(cost))
    print(type(cost) is not dict)

    SP = shortest_path(nodes, edges, cost)
    SP.solve_and_print()



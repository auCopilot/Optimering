from modeller.shortest_path import *


class clustering_from_shortest_path(shortest_path):
    """
    This class implements a clustering algorithm based on shortest path from Uge 8 Klyingeinddeling Vha Korteste Veje
    Is uses the shortest_path class as a parent class.

    Input:
    Ascending ordered list of nodes.
    cost function that defines the cost of traveling from node i to node j.
    NOTE I MIGHT HAVE TO ADD 0 TO THE COST FUNCTION VALUES FOR ADDED START INDEX 0
    """
    def __init__(self, nodes, edges, cost_function):
        start_node = nodes[0]
        end_node = nodes[-1]
        cost = cost_function(edges)
        super().__init__(nodes, edges, cost, start_node, end_node)

    def solve_and_print(self):
        self.construct_constraints()
        self.model.solve()

        print("Status:", PLP.LpStatus[self.model.status])
        print("Objective value:", PLP.value(self.model.objective))
        for k, e in enumerate(self.edges):
            if self.x[e].varValue is not None and self.x[e].varValue > 0:
                print(f"Edge {e} is included in the solution with cost {round(self.cost[k], 2)}")
                print(f"This corresponds to the group {self.nodes[e[0] + 1 : e[1] + 1 ]}\n")


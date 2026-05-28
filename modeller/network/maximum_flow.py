import pulp as PLP
from modeller.network.minimum_cost_flow import min_cost_flow

class maximum_flow(min_cost_flow):
    """
    This class implements the maximum flow problem. It follows from Uge 7 Afsnit 5.3 Netværksmodeller
    the maximum flow can be implementated as a minimum flow problem where we have b[i] = 0 for all nodes
    and add an edge from end to start with a negative cost and no upper bound. Then we add the edge capacity constraints.
    """
    def __init__(self, nodes, edges, capacity):
        self.edges = edges
        cost = {}
        for e in edges:
            cost[e] = 0
        supply = [0] * len(nodes)
        end_to_start_edge = (nodes[-1], nodes[0])
        edges = edges + [end_to_start_edge]
        cost[end_to_start_edge] = -1
        very_large_number = 10**6
        capacity[end_to_start_edge] = very_large_number


        super().__init__(nodes, edges, cost, supply, capacity=capacity)

    def solve_and_print(self):
        self.construct_constraints()
        self.model.solve()

        print("Status:", PLP.LpStatus[self.model.status])
        print("Objective value:", -PLP.value(self.model.objective))
        for e in self.edges:
            if self.x[e].varValue is not None and self.x[e].varValue > 0 and e != (self.nodes[-1], self.nodes[0]):
                print(f"Edge {e} is included in the solution with flow {round(self.x[e].varValue, 2)}")

# Example usage:
if __name__ =="__main__":

    nodes = list(range(0,7))
    # (from, to, cost)
    edges_and_capacity = [(0,1,8), (0,2,6), (1,2,1), (2,1,2), (1,3,5), (2,3,9),(1,4,2), (2,5,3), (3,5,4), (3,4,1),
                       (4,3,5), (4,6,4), (5,6,7)]
    edges = []
    capacity = {}
    for t in edges_and_capacity:
        e = (t[0],t[1])
        edges.append(e)
        capacity[e] = t[2]


    MF = maximum_flow(nodes, edges, capacity)
    MF.solve_and_print()
import pulp as PLP

class critical_path_problem:
    """
    This class defines the critical path problem. The implementation follows from uge 7 Afsnit 5.3 Netværksmodeller
    slide 42.

    Input:
    Nodes - list of integers
    Edges - list of integers
    times - dict of time associated with each edge

    """

    def __init__(self,nodes,edges, times):
        self.nodes = nodes
        self.edges = edges
        self.times = times


        #Model, decision variable and objective
        self.model = PLP.LpProblem("critical_path_problem", sense=PLP.LpMinimize)

        self.z = PLP.LpVariable("z", lowBound=0, cat=PLP.LpContinuous)
        self.t = PLP.LpVariable.dicts("t", range(len(self.nodes)), lowBound=0, cat=PLP.LpContinuous)

        self.model += self.z, "Objective"

    def construct_constraints(self):
        for i,j in self.edges:
            # Ending j must be greater than start i + time for activity i to j
            self.model += self.t[j] >= self.t[i] + self.times[(i,j)]
        for j in self.nodes:
            # decision variable t must be less than or equal to z for all nodes
            self.model += self.t[j] <= self.z

    def solve_and_print(self):
        self.construct_constraints()
        self.model.solve()

        print("Status:", PLP.LpStatus[self.model.status])
        print("Objective value:", PLP.value(self.model.objective))

        for j in self.nodes:
            print(f"Node {j} has time {round(self.t[j].varValue, 2)}")


# Example usage:
nodes = list(range(7))

# (i,j,cost)
edges_and_cost = [(0,1,4), (0,2,12), (0,3,7), (1,3,2), (2,5,5), (3,4,10), (4,2,0), (4,5,3), (5,6,4)]
edges = []
cost = {}
for i, j , c in edges_and_cost:
    e = (i,j)
    edges.append(e)
    cost[e] = c
CPP = critical_path_problem(nodes,edges,cost)
CPP.solve_and_print()
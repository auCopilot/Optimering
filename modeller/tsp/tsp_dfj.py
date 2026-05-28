import pulp as PLP
import itertools
import numpy as np

class tsp_dfj:
    """ This implementation of the symmetric TSP DFJ problem follows from
    the slipes in uge 10, TSP-formuleringer (pdf), slides 7 - 10"""

    def __init__(self, n, cost_matrix = None, x_coords = None, y_coords = None):
        self.n = n
        self.cost_matrix = cost_matrix

        if x_coords is not None and y_coords is not None and cost_matrix is None:
            self.cost_matrix = self.cost_from_coordinates(x_coords, y_coords)

        # ILP problem
        self.model = PLP.LpProblem(name = "SymmetricTSP_DFJ", sense = PLP.LpMinimize)
        # Define arcs,
        self.arcs = [(i,j) for i in range(n) for j in range(n)]
        # Definte subsets
        self.S = self.define_subsets()

        #### Variable definition ####
        # Binary variable indicating whether arc (i,j) is used in the solution
        self.x = PLP.LpVariable.dicts("x", self.arcs, lowBound=0, upBound=1, cat=PLP.LpBinary)

        #### Obejctive function ####
        self.model += PLP.lpSum(self.cost_matrix[i][j] * self.x[(i, j)] for i, j in self.arcs), "Objective"


    def define_constraints(self):

        ### CONSTRAINTS ###
        # Outlow
        for i in range(self.n):
            self.model += PLP.lpSum(self.x[(i, j)] for j in range(self.n)) == 1, f"Outflow{i}"


        # Inflow
        for j in range(self.n):
            self.model += PLP.lpSum(self.x[(i, j)] for i in range(self.n)) == 1, f"Inflow{j}"

        # Subtour elimination, DFJ uses subsets and we restrict the solution such that
        # There does not exist a S subset of {0, 1, 2, ..., n - 1 } such there is a closed
        # loops in the solution in the vertices contained in S
        for k, s in enumerate(self.S):
            self.model += PLP.lpSum(self.x[(i, j)] for i in s for j in s if i < j) <= len(
                s) - 1, f"SubtourElimination{k}"
        self.constraints = "Added"

    def cost_from_coordinates(self, x_cords, y_cords):
        # Computes L2 distance between points, this can serve as a cost.
        n = len(x_cords)
        cost_matrix = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                if i == j:
                    # Set diagonal to very large number
                    very_large_number = 10 ** 6
                    cost_matrix[i][j] = very_large_number
                else:
                    diff_x = x_cords[i] - x_cords[j]
                    diff_y = y_cords[i] - y_cords[j]
                    dist = np.sqrt(diff_x ** 2 + diff_y ** 2)
                    cost_matrix[i][j] = dist
        return cost_matrix

    def define_subsets(self):
        S = []
        for cardinality in range(2, self.n - 2 + 1):
            # Finds all combinations of the cardinality
            subset = itertools.combinations(list(range(self.n)), cardinality)
            # Return the set
            subset = set(subset)
            # Add the subset to S
            S = S + list(subset)
        return S

    def solve_and_print(self, one_indexed = True, quiet = True):
        ### SOLVE ###
        if self.constraints is None:
            raise Exception("You must define the constraints before solving, call define_constraints() method")

        self.model.solve(PLP.PULP_CBC_CMD(msg = 0 if quiet else 1))
        print("Status:", PLP.LpStatus[self.model.status])
        print("Objective value:", PLP.value(self.model.objective))
        for arc in self.arcs:
            if self.x[arc].varValue > 0.5:
                print(f"Arc ({arc[0] + (1 if one_indexed else 0)}, {arc[1] + (1 if one_indexed else 0)}) is in the"
                      f" solution with cost {round(self.cost_matrix[arc[0]][arc[1]],2)}")

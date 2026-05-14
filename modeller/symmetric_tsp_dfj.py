import pulp as PLP

import numpy as np

import itertools
class symmetric_tsp_dfj:
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
        self.arcs = [(i,j) for i in range(n) for j in range(n) if i < j]
        # Definte subsets
        self.S = self.define_subsets()
        #### Variable definition ####

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
        for cardinality in range(3, self.n - 3):
            # Finds all combinations of the cardinality
            subset = itertools.combinations(list(range(self.n)), cardinality)
            # Return the set
            subset = set(subset)
            # Add the subset to S
            S = S + list(subset)
        return S

    def solve_and_print(self, one_indexed = True, quiet = True):
        ### CONSTRAINTS ###
        # Binary variable indicating whether arc (i,j) is used in the solution
        self.x = PLP.LpVariable.dicts("x", self.arcs, lowBound=0, upBound=1, cat=PLP.LpBinary)

        #### Obejctive function ####
        self.model += PLP.lpSum(self.cost_matrix[i][j] * self.x[(i, j)] for i, j in self.arcs), "Objective"

        ### Valence contraint, makes sure that each point it connected to two other points
        for j in range(self.n):
            self.model += PLP.lpSum(self.x[(i, j)] for i in range(j)) + \
                          PLP.lpSum(self.x[(j, i)] for i in range(j + 1, self.n)) \
                          == 2, f"valence{j}"

        ### Subtour elimination, DFJ uses subsets and we restrict the solution such that
        # There does not exist a S subset of {0, 1, 2, ..., n - 1 } such there is a closed
        # loops in the solution in the vertices contained in S
        for k, s in enumerate(self.S):
            self.model += PLP.lpSum(self.x[(i, j)] for i in s for j in s if i < j) <= len(
                s) - 1, f"SubtourElimination{k}"

        ### SOLVE ###

        self.model.solve(PLP.PULP_CBC_CMD(msg = 0 if quiet else 1))
        print("Status:", PLP.LpStatus[self.model.status])
        print("Objective value:", PLP.value(self.model.objective))
        for arc in self.arcs:
            if self.x[arc].varValue > 0.5:
                print(f"Arc ({arc[0] + (1 if one_indexed else 0)}, {arc[1] + (1 if one_indexed else 0)}) is in the"
                      f" solution with cost {round(self.cost_matrix[arc[0]][arc[1]],2)}")

x_coords = "2.0 2.5 2.8 1.0 1.5 2.0 1.5 7.0 7.3 7.9 8.2 7.6".split(" ")
x_coords = [float(v) for v in x_coords]
y_coords = "3.0 3.5 2.7 8.0 8.5 8.0 7.5 5.0 5.4 5.6 5.0 4.5".split(" ")
y_coords = [float(v) for v in y_coords]
n = len(x_coords)

STSP = symmetric_tsp_dfj(n, x_coords=x_coords, y_coords=y_coords)
STSP.S = []
STSP.solve_and_print(quiet = False)

STSPrelaxed = symmetric_tsp_dfj(n, x_coords=x_coords, y_coords=y_coords)
STSPrelaxed.S = [(range(3)), range(3, 7), range(7, 12)]
STSPrelaxed.solve_and_print(quiet = False)

for name, constraint in STSPrelaxed.model.constraints.items():
    if "Subtour" in name:
        print(name, " : ", constraint)


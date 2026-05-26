import math

import pulp as PLP
import numpy as np

class multiple_tsp:
    """
    This class implements multiple TSP algorithm, thus if we set m, the number of travellers, to m = 1
    and the maximum point we can visit, L, to the number of points in the problem, we will have a standard TSP problem.
    The algorithm is based on the slides from "uge 16 VRP-MTZ"

    Depot value is the first vertex in the problem, thus i = 0 or j = 0

    Note this generalizes to the standard MTZ ATSP from Uge 10, TSP-Formuleringer if we set m = 1 and L = n - 1,

    """
    def __init__(self, m, n, L, cost_matrix, x_coords = None, y_coords = None):
        # Number of verticies
        self.n = n
        # Number of travellers
        self.m = m
        # Maximum number of verticies a traveller can visit
        self.L = L

        self.cost_matrix = cost_matrix

        # If no alternative cost matrix is given, compute the L2-distance cost.
        if x_coords is not None and y_coords is not None and cost_matrix is None:
            self.cost_matrix = self.cost_from_coordinates(x_coords, y_coords)

        # ILP problem
        self.model = PLP.LpProblem(name = "MultipleTSP", sense = PLP.LpMinimize)
        # Define arcs,
        self.arcs = [(i,j) for i in range(n) for j in range(n) if i != j]

        #### Variable definition ####

        # Binary variable indicating whether arc (i,j) is used in the solution
        self.x = PLP.LpVariable.dicts("x", self.arcs, lowBound=0, upBound=1, cat = PLP.LpBinary)

        # Indicator variable that indentifies the i'th vertex position in the traversal of the rute
        self.u = PLP.LpVariable.dicts("u", range(n), lowBound = 0)

        #### Obejctive function ####
        self.model += PLP.lpSum(self.cost_matrix[i][j] * self.x[(i,j)] for i,j in self.arcs), "Objective"

        #### Constraints ####

        # We must have m routes leaving the depot (vertex 0)
        self.model += PLP.lpSum(self.x[(0, j)] for j in range(1, self.n)) == m, "LeavingDepot"

        # We must have m routes returning to the depot (vertex 0)
        self.model += PLP.lpSum(self.x[(i, 0)] for i in range(1, self.n)) == m, "EnteringDepot"

        # Outflow is 1 for all vertex
        for i in range(1, self.n):
            self.model += PLP.lpSum(self.x[(i,j)] for j in range(self.n) if (i,j) in self.arcs) == 1, f"Outflow{i}"

        # Inflow is 1 for all vertex
        for j in range(1, self.n):
            self.model += PLP.lpSum(self.x[(i,j)] for i in range(self.n) if (i,j) in self.arcs) == 1, f"Inflow{j}"

        # Subtour elimination and maximum number of verticies a traveller can visit
        for i, j in self.arcs:
            if i != 0 and j != 0:
                if i != j: # Only for arcs between customers
                    self.model += self.u[i] - self.u[j] + self.L * self.x[(i,j)] <= self.L - 1, f"SubtourElimination_{i}_{j}"


    def cost_from_coordinates(self, x_cords, y_cords):
        # Computes L2 distance between points, this can serve as a cost.
        n = len(x_cords)
        cost_matrix = np.zeros((n,n))
        for i in range(n):
            for j in range(n):
                if i == j:
                    # Set diagonal to very large number
                    very_large_number = 10**6
                    cost_matrix[i][j] = very_large_number
                else:
                    diff_x = x_cords[i] - x_cords[j]
                    diff_y = y_cords[i] - y_cords[j]
                    dist = np.sqrt(diff_x**2 + diff_y**2)
                    cost_matrix[i][j] = dist
        return cost_matrix

    def solve_and_print(self, one_indexed = True, msg = False):
        self.model.solve(PLP.PULP_CBC_CMD(msg=msg))
        print("Status:", PLP.LpStatus[self.model.status])
        eps = 0.5
        for i, j in sorted(
                self.arcs,
                key=lambda arc: self.u[arc[0]].varValue if self.u[arc[0]] else 1 # Sort according to the u value
        ):
            if self.x[(i, j)].varValue > 0 + eps:
                # Track positioning
                u_step = int((self.u[i].varValue if self.u[i].varValue is not None else -1) + (1 if one_indexed else 0))
                # Bool to check if depot
                dep_or_vertex = f"vertex_{j + (1 if one_indexed else 0)}" if j != 0 else "Depot"
                print(
                    f"Arc ({i + (1 if one_indexed else 0)}, {j + (1 if one_indexed else 0)})"
                    f" is used in the solution with cost {round(self.cost_matrix[i][j], 2)},"
                    f" {dep_or_vertex} is visited as the "
                    f"{u_step}"
                    f" th vertex in the route\n"
                )
        print("Total cost:", PLP.value(self.model.objective))












# Test
if __name__ == "__main__":
    XCoor = [2, 3, 5, 4, 2, 3, 6, 17, 15, 15, 15, 11, 14, 17, 10]
    YCoor = [2, 1, 2, 4, 5, 7, 6, 4, 8, 3, 5, 7, 10, 9, 8]

    n = len(XCoor) # Number of vertices
    m = 1  # Number of travelers
    L = len(XCoor) - 1 # Max vertex visits
    test_mtsp = multiple_tsp(m, n, L, None, XCoor, YCoor)
    test_mtsp.solve_and_print(one_indexed = True)
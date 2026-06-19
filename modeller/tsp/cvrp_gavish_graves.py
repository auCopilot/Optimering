import numpy as np
import pulp as PLP

class cvrp_gavish_graves:
    """
    This implementation follows from uge 13 VRP-MTZ, and defines the Capacitated Vehicle Routing Problem (CVRP) using
    the MTZ formulation.

    Punkt 1 repræsenterer et depot, og hvert af de øvrige punkter repræsenterer en kunde
    I Til hver kant (i, j) ∈ A er tilknyttet en omkostning cij
    I Der er endvidere oplyst et antal vogne m, som alle er placeret i depotet
    I Vognene er identiske og har hver en lastekapacitet Q
    I For hver kunde i = 2, . . . , n er oplyst en efterspørgsel qi , som skal leveres fra depotet til kunden
    I Problemet g˚ar ud p˚a at bestemme m ruter, som har minimal samlet omkostning, under flg.
    begrænsninger:
    I Hver rute starter og slutter i depotet
    I Hver kunde bliver besøgt netop ´en gang, hvor hele den efterspurgte mængde leveres
    I Den samlede mængde p˚a hver rute m˚a ikke overstige vognkapaciteten

    """

    def __init__(self, m, n, demand, vehicle_capacity, cost_matrix, x_coords=None, y_coords=None):
        # Number of verticies
        self.n = n
        # Number of travellers
        self.m = m
        # Demand for each vertex, q_i.
        self.demand = demand
        # Maximum, identical vehicle capacity
        self.vehicle_capacity = vehicle_capacity


        self.cost_matrix = cost_matrix

        # If no alternative cost matrix is given, compute the L2-distance cost.
        if x_coords is not None and y_coords is not None and cost_matrix is None:
            self.cost_matrix = self.cost_from_coordinates(x_coords, y_coords)

        # ILP problem
        self.model = PLP.LpProblem(name="MultipleTSP", sense=PLP.LpMinimize)
        # Define arcs,
        self.arcs = [(i, j) for i in range(n) for j in range(n) if i != j]

        #### Variable definition ####

        # Binary variable indicating whether arc (i,j) is used in the solution
        self.x = PLP.LpVariable.dicts("x", self.arcs, lowBound=0, upBound=1, cat=PLP.LpBinary)
        self.f = PLP.LpVariable.dicts("f", self.arcs, lowBound=0, cat = PLP.LpContinuous)
        # Indicator variable that indentifies the i'th vertex position in the traversal of the rute
        self.u = PLP.LpVariable.dicts("u", range(n), lowBound=0)

        #### Obejctive function ####
        self.model += PLP.lpSum(self.cost_matrix[i][j] * self.x[(i, j)] for i, j in self.arcs), "Objective"

    def define_constraints(self):
        #### Constraints ####

        # We must have m routes leaving the depot (vertex 0)
        self.model += PLP.lpSum(self.x[(0, j)] for j in range(1, self.n)) == self.m, "LeavingDepot"

        # We must have m routes returning to the depot (vertex 0)
        self.model += PLP.lpSum(self.x[(i, 0)] for i in range(1, self.n)) == self.m, "EnteringDepot"

        # Outflow is 1 for all vertex
        for i in range(1, self.n):
            self.model += PLP.lpSum(self.x[(i, j)] for j in range(self.n) if (i, j) in self.arcs) == 1, f"Outflow{i}"

        # Inflow is 1 for all vertex
        for j in range(1, self.n):
            self.model += PLP.lpSum(self.x[(i, j)] for i in range(self.n) if (i, j) in self.arcs) == 1, f"Inflow{j}"
        # Amount out = Amount in + demand
        for i in range(1, self.n):
            self.model += (PLP.lpSum(self.f[(i,j)] - self.f[(j,i)]
                                    for j in range(self.n)
                                    if (((i, j) in self.arcs) or ((j, i) in self.arcs)))
                                    - self.demand[i] == 0, f"InOutDemand{i}")
        # Bounds for f variables
        for arc in self.arcs:
            self.model += self.f[arc] >= 0, f"LowBoundf{arc}"
            self.model += self.f[arc] <= self.vehicle_capacity * self.x[arc], f"HighBoundf{arc}"

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

    def solve_and_print(self, one_indexed = True, msg = False):
        self.model.solve(PLP.PULP_CBC_CMD(msg=msg))
        if self.constraints != "Added":
            raise Exception("You must define the constraints before solving, call define_constraints() method")
        print("Status:", PLP.LpStatus[self.model.status])
        eps = 0.5
        for i, j in sorted(
                self.arcs,
                key=lambda arc: self.u[arc[0]].varValue if self.u[arc[0]] else 1 # Sort according to the u value
        ):
            if self.x[(i, j)].varValue > 0 + eps:
                # Track positioning
                f_step = int((self.f[(i, j)].varValue
                              if self.f[(i, j)].varValue is not None else -1)
                             + ( 1 if one_indexed else 0))
                # Bool to check if depot
                dep_or_vertex = f"vertex_{j + (1 if one_indexed else 0)}" if j != 0 else "Depot"
                print(
                    f"Arc ({i + (1 if one_indexed else 0)}, {j + (1 if one_indexed else 0)})"
                    f" is used in the solution with cost {round(self.cost_matrix[i][j], 2)},"
                    f" {dep_or_vertex} is visited as the "
                    f"{f_step}"
                    f" th vertex in the route\n"
                )
        print("Total cost:", PLP.value(self.model.objective))



if __name__ == "__main__":
    XCoor = [2, 3, 5, 4, 2, 3, 6, 17, 15, 15, 15, 11, 14, 17, 10]
    YCoor = [2, 1, 2, 4, 5, 7, 6, 4, 8, 3, 5, 7, 10, 9, 8]
    Demand = [0, 1, 1, 2, 1, 1, 1, 2, 3, 4, 1, 3, 3, 1, 4]
    n = len(XCoor)

    m = 3  # Antal ruter
    Q = 10  # Vognkapacitet
    CVRP = cvrp_gavish_graves(m, n, demand = Demand, vehicle_capacity = Q, cost_matrix= None, x_coords= XCoor, y_coords= YCoor)
    CVRP.define_constraints()
    CVRP.solve_and_print(one_indexed = True, msg= True)
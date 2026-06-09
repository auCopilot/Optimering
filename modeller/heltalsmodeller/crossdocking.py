import numpy as np
import pulp as PLP

class Crossdocking():
    """
    The following implementation of CDAP follows from uge 18 Crossdocking. Note that there may exist many
    optimal solution for the same problem and the we have to add linearization of the variables like in a QAP
    to formulate this as an LP.
    :Input:
    inbound_trucks - range of inbound trucks
    outbound_trucks - range of outbound trucks
    inbound_doors - range of inbound doors
    outbound_doors - range of outbound doors
    inbound_doors_cap - list of capacities for each inbound door
    outbound_doors_cap - list of capacities for each outbound door
    distance_matrix - 2D matrix of distances between inbound and outbound doors
    volume_flow_matrix - 2D matrix of volumes between inbound trucks and outbound trucks
    """

    def __init__(self,
                 inbound_trucks,
                 outbound_trucks,
                 inbound_doors,
                 outbound_doors,
                 inbound_doors_cap,
                 outbound_doors_cap,
                 distance_matrix,
                 volume_flow_matrix):
        # Parameters
        # Ranges
        self.M = inbound_trucks
        self.N = outbound_trucks
        self.I = inbound_doors
        self.J = outbound_doors

        # Lists
        self.S = inbound_doors_cap
        self.R = outbound_doors_cap

        #Matrices
        self.d = distance_matrix
        self.w = volume_flow_matrix

        self.constraints = "NOT ADDED"

        self.total_inbound = [sum([self.w[m][n] for n in self.N]) for m in self.M]
        self.total_outbound = [sum([self.w[m][n] for m in self.M]) for n in self.N]

        # Model and variables
        self.model = PLP.LpProblem("Crossdocking", PLP.LpMinimize)
        self.x = PLP.LpVariable.dicts("x", indices= (self.M, self.I), cat=PLP.LpBinary)
        self.y = PLP.LpVariable.dicts("y", indices= (self.N, self.J), cat=PLP.LpBinary)

        # Linearization of product
        self.t = [(m,i,n,j) for m in self.M
                            for n in self.N
                            for j in self.J
                            for i in self.I]

        self.prod_var = PLP.LpVariable.dicts("prod_var", indices = self.t, cat = PLP.LpBinary)


        # Objective
        self.model += PLP.lpSum(self.d[i][j] * self.w[m][n] * self.prod_var[(m, i, n ,j)]
                                for m, i, n ,j in self.t)

        # Relation between x, y, and XYVar variables:
        for m,i,n,j in self.t:
            self.model += self.prod_var[(m,i,n,j)] <= self.x[m][i]
            self.model += self.prod_var[(m,i,n,j)] <= self.y[n][j]
            self.model += self.prod_var[(m,i,n,j)] >= self.x[m][i] + self.y[n][j] - 1



    def construct_constraints(self):
        """
        Construct the constraints (1a), (1b), (2a) and (2b).
        (1c) and (2c) are implied in variable definition
        """

        # Cap. constraint for inbound doors
        for i in self.I:
            self.model += (PLP.lpSum(self.total_inbound[m]*self.x[m][i] for m in self.M) <= self.S[i],
            f"Cap_Inbound{i}")
        # Cap. One inbound truck for each inbound door
        for m in self.M:
            self.model += (PLP.lpSum(self.x[m][i] for i in self.I) == 1,
            f"One_Inbound_to_One_Door{m}")

        # Cap. constraint for outbound doors
        for j in self.J:
            self.model += (PLP.lpSum(self.total_outbound[n]*self.y[n][j] for n in self.N) <= self.R[j],
            f"Cap_Outbound{j}")
        # Cap. One outbound truck for each outbound door
        for n in self.N:
            self.model += (PLP.lpSum(self.y[n][j] for j in self.J) == 1,
            f"One_Outbound_to_One_Door{n}")
        self.constraints = "ADDED"

    def solve_and_print(self, quiet = True, one_indexed = True):

        idx = 1 if one_indexed else 0

        if self.constraints != "ADDED":
            raise ValueError("The constraints is not ADDED")

        self.model.solve(PLP.PULP_CBC_CMD(msg = 0 if quiet else 1))

        print("Status:", PLP.LpStatus[self.model.status])
        print("Objective value:", PLP.value(self.model.objective))


        #Inbound solution
        for m in self.M:
            for i in self.I:
                if self.x[m][i].varValue > 0.5:
                    print(f"Inbound truck {m+idx} is assigned to inbound door {i+idx}")
        #Outbound solution
        for n in self.N:
            for j in self.J:
                if self.y[n][j].varValue > 0.5:
                    print(f"Outbound truck {n+idx} is assigned to outbound door {j+idx}")


if __name__ == "__main__":
    inbound_trucks = range(3)
    outbound_trucks = range(4)
    inbound_doors = range(3)
    outbound_doors = range(4)
    inbound_doors_cap = [8,8,8]
    outbound_doors_cap = [6,6,6,6]

    distance_matrix = [
        [2,2,6,10], # Distances from I1
        [6,2,2, 6], # -              I2
        [10,6,2, 2]] # -              I3

    volume_flow_matrix = [
        [2,0,2,1], # Flow from IT1
        [1,2,2,1], # -         IT2
        [1,1,0,3]] # -         IT3

    CDAP = Crossdocking(inbound_trucks, outbound_trucks,
                    inbound_doors, outbound_doors,
                    inbound_doors_cap, outbound_doors_cap,
                    distance_matrix, volume_flow_matrix)
    CDAP.construct_constraints()
    CDAP.solve_and_print(quiet = True)




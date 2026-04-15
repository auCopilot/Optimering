import numpy as np
import pulp as PLP

class QuadraticAssignmentProblem:

    def __init__(self, n, flow_matrix, distance_matrix, name = "QuadraticAssignmentProblem"):
        self.n = n
        self.flow_matrix = flow_matrix
        self.distance_matrix = distance_matrix
        self.name = name
        self.variable_range = range(self.n)
        # Constraint variables for linear formulation
        self.x = PLP.LpVariable.dicts("x",
                                      (self.variable_range,self.variable_range),
                                      cat = PLP.LpBinary)
        # k > i, incodes that the distances between pairs of locations and
        # flows are symmetric.
        self.y_tuple = [(i,j,k,l)
                        for i in self.variable_range
                        for j in self.variable_range
                        for k in self.variable_range
                        for l in self.variable_range if k > i]

        self.y = PLP.LpVariable.dicts("y",
                                      self.y_tuple,
                                      cat = PLP.LpBinary)

        self.model = PLP.LpProblem(name = self.name, sense = PLP.LpMinimize)
        self.model += PLP.lpSum(self.flow_matrix[y_tuple[0]][y_tuple[2]] *
                                self.distance_matrix[y_tuple[1]][y_tuple[3]]
                                * self.y[y_tuple] for y_tuple in self.y_tuple), "Objective"
        self.construct_constraints()

    def construct_constraints(self):
        # Each machine is assigned to exactly one location
        for i in self.variable_range:
            self.model += PLP.lpSum(self.x[i][j] for j in self.variable_range) == 1, f"Machine_{i}_constraint"
        # Each location is assigned to exactly one machine
        for j in self.variable_range:
            self.model += PLP.lpSum(self.x[i][j] for i in self.variable_range) == 1, f"Location_{j}_constraint"

        for t in self.y_tuple:
            self.model += self.y[t] <= self.x[t[0]][t[1]]
            self.model += self.y[t] <= self.x[t[2]][t[3]]
            self.model += self.y[t] >= self.x[t[0]][t[1]] + self.x[t[2]][t[
                3]] - 1


    def solve(self, quiet = True, postive_variables_only = True):

        # Solve quietly
        print()
        self.model.solve(PLP.PULP_CBC_CMD(msg = 0 if quiet else 1))
        # Print af loesningens status
        print("Status:", PLP.LpStatus[self.model.status])

        # Print of values of the decision variables, with option to only print positive variables

        if postive_variables_only:
            epsilon = 1e-5
            condition = lambda v: v.varValue > epsilon
        else:
            condition = None
        if condition is not None:
            for v in self.model.variables():
                if condition(v):
                    print(v.name, "=", v.varValue)
        else:
            for v in self.model.variables():
                print(v.name, "=", v.varValue)

        # Print af den optimale objektfunktionsvaerdi
        print("Value of Objective function. = ",
              PLP.value(self.model.objective))
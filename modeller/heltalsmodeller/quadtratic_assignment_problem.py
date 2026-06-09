import numpy as np
import pulp as PLP

class QuadraticAssignmentProblem:

    def __init__(self, machine_range, location_range, flow_matrix, distance_matrix, max_capacities = None, name = "QuadraticAssignmentProblem"):
        # Or factory range
        self.machine_range = machine_range
        self.location_range = location_range
        self.flow_matrix = flow_matrix
        self.distance_matrix = distance_matrix
        self.max_capacities = max_capacities
        self.name = name
        # Constraint variables for linear formulation
        self.x = PLP.LpVariable.dicts("x",
                                      (self.machine_range,self.location_range),
                                      cat = PLP.LpBinary)
        # k > i, incodes that the distances between pairs of locations and
        # flows are symmetric.
        self.y_tuples = [(i,j,k,l)
                        for i in self.machine_range
                        for j in self.location_range
                        for k in self.machine_range
                        for l in self.location_range if k > i]

    def construct_model(self):
        self.y = PLP.LpVariable.dicts("y",
                                      self.y_tuples,
                                      cat=PLP.LpBinary)

        self.model = PLP.LpProblem(name=self.name, sense=PLP.LpMinimize)
        self.model += PLP.lpSum(self.flow_matrix[t[0]][t[2]] *
                                self.distance_matrix[t[1]][t[3]]
                                * self.y[t] for t in self.y_tuples), "Objective"
        self.model_construction = True

    def construct_constraints(self):

        # More machines than locations, more than one machine must be assigned to some locations.
        if len(self.machine_range) > len(self.location_range):
            if self.max_capacities is None:
                raise ValueError("If the number of machines is greater than the number of locations, max_capacities must be provided.")
            # Each machine is assigned to exactly one location
            for i in self.machine_range:
                self.model += PLP.lpSum(self.x[i][j] for j in self.location_range) == 1, f"Machine_{i}_constraint"
            # Each machine is assign to at most max_capacities[j] locations
            for j in self.location_range:
                self.model += PLP.lpSum(self.x[i][j] for i in self.machine_range) <= self.max_capacities[j], f"Location_{j}_constraint"

        # More locations than machines, so we can accept less than one machine at location
        elif len(self.location_range) > len(self.machine_range):
            # Each machine is assigned to exactly one location
            for i in self.machine_range:
                self.model += PLP.lpSum(self.x[i][j] for j in self.location_range) == 1, f"Machine_{i}_constraint"
            # Each location is assigned to at most one machine
            for j in self.location_range:
                self.model += PLP.lpSum(self.x[i][j] for i in self.machine_range) <= 1, f"Location_{j}_constraint"

        # Standard one to one case
        else:
            # Each machine is assigned to exactly one location
            for i in self.machine_range:
                self.model += PLP.lpSum(self.x[i][j] for j in self.location_range) == 1, f"Machine_{i}_constraint"
            # Each location is assigned to exactly one machine
            for j in self.location_range:
                self.model += PLP.lpSum(self.x[i][j] for i in self.machine_range) == 1, f"Location_{j}_constraint"

        # Other usual constraints
        for t in self.y_tuples:
            self.model += self.y[t] <= self.x[t[0]][t[1]]
            self.model += self.y[t] <= self.x[t[2]][t[3]]
            self.model += self.y[t] >= self.x[t[0]][t[1]] + self.x[t[2]][t[3]] - 1
        self.constraints = "ADDED"



    def solve(self, quiet = True, postive_variables_only = True):
        if not self.model_construction:
            raise Exception("You must construct the model before solving.")
        if self.constraints != "ADDED":
            raise Exception("You must constrain the model before solving.")
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
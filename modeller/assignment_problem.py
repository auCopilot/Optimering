import pulp as PLP
import numpy as np


class AssignmentProblem:

    """This implementation follows "Afsnit 5.3 Netværksmodeller" from week 7 """
    def __init__(self, n,
                 cost_matrix = None,
                 name = "AssignmentProblem",
               ):
        # Number of jobs/assignments
        self.n = n
        self.name = name
        self.cost_matrix = cost_matrix
        # Range of decision variable x
        self.variable_range = range(self.n)

        # decision variables
        self.x = PLP.LpVariable.dicts("x",
                                     (self.variable_range, self.variable_range),
                                     lowBound = 0 )

        if self.cost_matrix is None:
            raise ValueError("Cost matrix must be provided")
        else:
            # Define objective function
            self.model = PLP.LpProblem(name = self.name, sense =
            PLP.LpMinimize)
            self.model += PLP.lpSum(self.cost_matrix[i][j] * self.x[i][j]
                                   for i in self.variable_range
                                   for j in self.variable_range
                                   ), "Objective"
            # Construct constraints according to the definition of the
            # assignment problem, which states that each job is assigned to
            # exactly one worker, and each worker is assigned to exactly one job.
            self.construct_constraints()


    def construct_constraints(self):
        # Each job is assigned to exactly one worker
        for i in self.variable_range:
            self.model += PLP.lpSum(self.x[i][j] for j in self.variable_range) == 1, f"Job_{i}_constraint"
        # Each worker is assigned to exactly one job
        for j in self.variable_range:
            self.model += PLP.lpSum(self.x[i][j] for i in self.variable_range) == 1, f"Worker_{j}_constraint"
        # Positivity constraints are already defined by lowBound = 0 in variable definition
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




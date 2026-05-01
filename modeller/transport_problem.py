import numpy as np
import pulp as PLP

class TransportProblem:
    """Implementation follows Netværksmodeller from week 7"""
    def __init__(self, cost_matrix, capacities, demands):
        # VERY LARGE NUMBER
        self.M = 10**6
        self.cost_matrix = cost_matrix
        self.demands = demands
        self.capacities = capacities

        self.demand_surplus = False
        self.supply_surplus = False
        self.balanced = False


        # Check if problem is valid
        if sum(self.capacities) < sum(self.demands):
            print("DEMAND SURPLUS, ADD DUMMY SUPPLIER")
            self.difference = abs(sum(self.demands) - sum(self.capacities))
            self.demand_surplus = True

        elif sum(self.capacities) > sum(self.demands):
            self.difference = abs(sum(self.demands) - sum(self.capacities))
            self.supply_surplus = True
            print("CAPACITY SURPLUS, ADD DUMMY COSTUMER")
        else:
            print("SUPPLY MEETS DEMAND")
            self.balanced = True


        # m suppliers
        self.m = len(self.capacities)
        self.supplier_range = range(self.m)
        # n costumers
        self.n = len(self.demands)
        self.demands_range = range(self.n)
        self.name = "TransportProblem"

        if not self.balanced:
            self.add_dummy()

        # Model definition
        self.model = PLP.LpProblem( name = self.name, sense = PLP.LpMinimize)
        # Decision variables
        self.x = PLP.LpVariable.dicts( name = "x", indices= (self.supplier_range, self.demands_range), lowBound= 0)
        # Objective
        self.model += PLP.lpSum(self.cost_matrix[i][j] * self.x[i][j]
                                         for i in self.supplier_range
                                         for j in self.demands_range), "Objective"
        self.construct_constraints()



    def construct_constraints(self):
        # We must be able to supply
        for i in self.supplier_range:
            self.model += PLP.lpSum(self.x[i][j] for j in self.demands_range) <= self.capacities[i], f"Capacities{i}"
        # We must meet demand
        for j in self.demands_range:
            self.model += PLP.lpSum(self.x[i][j] for i in self.supplier_range) == self.demands[j], f"Demands{j}"
        # Non-negativity is enforced in variable definition

    def add_dummy(self):
        # Adds dummy according to surplus
        if self.demand_surplus:
            print(f"Demand surplus, adding dummy supplier with supply: {self.difference}")
            self.capacities.append(self.difference)
            self.m = len(self.capacities)
            self.supplier_range = range(self.m)
            self.dummy_index = len(self.capacities) - 1
            # Add zero cost row to matrix
            self.cost_matrix = np.vstack((self.cost_matrix, np.zeros(self.n)))

        if self.supply_surplus:
            print(f"Supply surplus, adding dummy customer with demand: {self.difference}")
            self.demands.append(self.difference)
            self.n = len(self.demands)
            self.demands_range = range(self.n)
            self.dummy_index = len(self.demands) - 1
            # Add zero cost row to matrix
            self.cost_matrix = np.hstack((self.cost_matrix, np.zeros((self.m, 1))))

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
            print("Solution gives the following positive variables:\n")
            for v in self.model.variables():
                if condition(v):
                    print(v.name, "=", v.varValue)
        else:
            print("Solution gives the following variables:\n")
            for v in self.model.variables():
                print(v.name, "=", v.varValue)

        # Print af den optimale objektfunktionsvaerdi
        print("Value of Objective function. = ",
              PLP.value(self.model.objective))

    def print_transport_details(self, epsilon=1e-5, one_indexed = False):
        """Prints the amount and cost details for all active transport routes."""
        print("\n--- Transport Route Details ---")
        if one_indexed:
            print("\n--- Transport Route Details (1-indexed) ---")
            idx = 1
        else:
            idx = 0
        self.model.solve(PLP.PULP_CBC_CMD(msg=0))
        # Make sure the model has been solved
        if self.model.status != PLP.LpStatusOptimal:
            print("Model has not been solved to optimality yet.")
            return

        total_calculated_cost = 0

        for i in self.supplier_range:
            for j in self.demands_range:
                amount = self.x[i][j].varValue

                unit_cost = self.cost_matrix[i][j]
                route_cost = amount * unit_cost
                total_calculated_cost += route_cost
                if not self.balanced:
                    if self.supply_surplus:
                        if j != self.dummy_index:
                            print(f"Supplier {i + idx} sends {amount} units to Customer {j + idx} "
                                  f"| Unit Cost: {unit_cost} | Route Cost: {route_cost}")
                        else:
                            print(f"Supplier {i + idx} sends {amount} units to Dummy Customer {j + idx} "
                                  f"| Unit Cost: {unit_cost} | Route Cost: {route_cost}")
                    if self.demand_surplus:
                        if i != self.dummy_index:
                            print(f"Supplier {i + idx} sends {amount} units to Customer {j + idx} "
                                  f"| Unit Cost: {unit_cost} | Route Cost: {route_cost}")
                        else:
                            print(f"Dummy Supplier {i + idx} sends {amount} units to Customer {j + idx} "
                                  f"| Unit Cost: {unit_cost} | Route Cost: {route_cost}")
                else:
                    print(f"Supplier {i + idx} sends {amount} units to Customer {j + idx} "
                          f"| Unit Cost: {unit_cost} | Route Cost: {route_cost}")

        print("-" * 31)
        # Model objective
        print(f"Model Objective Value: {PLP.value(self.model.objective)}")


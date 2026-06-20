# noinspection PyUnresolvedReferences
import pulp as PLP
"""
3-decision variable version.
"""
A = PLP.LpVariable(name="A",lowBound=0)
B = PLP.LpVariable(name="B",lowBound=0)
C = PLP.LpVariable(name="C",lowBound=0)

model = PLP.LpProblem(name="LP1", sense=PLP.LpMaximize)

# Define objective function
sales_price = 8*A + 16*B + 12*C

cost1 = 0.3*(3*B + 2*C)
cost2 = 0.7*(2*A + 5*B + 4*C)
cost3 = 0.4*(3*A + 1*B + 2*C)
cost4 = 0.8*(2*A + 4*B + 3*C)

total_cost = cost1 + cost2 + cost3 + cost4
profit = sales_price - total_cost
model += profit, "Objective"

# Add constraints
model += 3*B + 2*C <= 150, "R1"
model += 2*A + 5*B + 4*C <= 170, "R2"
model += 3*A + 1*B + 2*C <= 120, "R3"
model += 2*A + 4*B + 3*C <= 140, "R4"


def print_solution(Model):
    # Loesning af modellen vha. PuLP's valg af Solver
    Model.solve()
    # Print af loesningens status
    print("Status:", PLP.LpStatus[Model.status])
    # Print af hver variabel med navn og loesningsvaerdi
    for v in Model.variables():
        print(v.name, "=", v.varValue)
    # Print af den optimale objektfunktionsvaerdi
    print("Obj. = ", PLP.value(Model.objective))
print_solution(model)

"""
7 - decision variable version. Add costs1 to costs4 for resources 1 to 4.
"""
model = PLP.LpProblem(name="LP1", sense=PLP.LpMaximize)

A = PLP.LpVariable(name="A",lowBound=0)
B = PLP.LpVariable(name="B",lowBound=0)
C = PLP.LpVariable(name="C",lowBound=0)
costs1 = PLP.LpVariable(name="costs1", lowBound=0)
costs2 = PLP.LpVariable(name="costs2", lowBound=0)
costs3 = PLP.LpVariable(name="costs3", lowBound=0)
costs4 = PLP.LpVariable(name="costs4", lowBound=0)

model += 8*A + 16*B + 12*C - (costs1 + costs2 + costs3 + costs4), "Objective"
# Add explicit cost calculations
model += costs1 == 0.3*(3*B + 2*C), "Cost1"
model += costs2 == 0.7*(2*A + 5*B + 4*C) , "Cost2"
model += costs3 == 0.4*(3*A + 1*B + 2*C) , "Cost3"
model += costs4 == 0.8*(2*A + 4*B + 3*C) , "Cost4"
# Add cost constraints instead of resource constraints
model += costs1 <= 150*0.3, "R1"
model += costs2 <= 170*0.7, "R2"
model += costs3 <= 120*0.4, "R3"
model += costs4 <= 140*0.8, "R4"

print_solution(model)



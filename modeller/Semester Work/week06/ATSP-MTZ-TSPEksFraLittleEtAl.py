# ATSP eksemplet med n=6 fra Little et al.'s artikel
# Her formuleres problemet som et Mixed Integer Linear Programming problem 
# vha. MTZ Subtour Elimination Constraints

# Importer PuLP-funktioner
import pulp as PLP

# Minimeringsproblem
Model = PLP.LpProblem("ATSP-MTZ",PLP.LpMinimize)

M = 999
Costs = [[0],
        [0, M,27,43,16,30,26],
        [0, 7, M,16, 1,30,25],
        [0,20,13, M,35, 5, 0],
        [0,21,16,25, M,18,18],
        [0,12,46,27,48, M, 5],
        [0,23, 5, 5, 9, 5, M]]

PunktRange = range(1,7) # 1..6
UIndexRange = range(2,7) # 2..6

# Heltallige beslutningsvariable x(i,j)
x = PLP.LpVariable.dicts("x",(PunktRange,PunktRange),0,1,PLP.LpInteger) # x(1,1) .. x(6,6)

# Kontinuerte beslutningsvariable u(i)
u = PLP.LpVariable.dicts("u",UIndexRange,1,5,PLP.LpContinuous) # u(2)..u(6) hvor 1 <= u(i) <= 5 for i=2,...,6

# Objektfunktion
Model += PLP.lpSum([Costs[i][j] * x[i][j] for i in PunktRange for j in PunktRange]),"Objektfunktion"

# Outflow:
for i in PunktRange:
    Model += PLP.lpSum([x[i][j] for j in PunktRange]) == 1,"Outflow%s"%i

# Inflow:
for j in PunktRange:
    Model += PLP.lpSum([x[i][j] for i in PunktRange]) == 1,"Inflow%s"%j

for i in UIndexRange:
    for j in UIndexRange:
        if i != j:
            navn = '_MTZ_{0}_{1}'.format(i,j)
            Model += u[i] - u[j] + 5 * x[i][j] <= 4,navn

# Model.writeLP("ATSP-MTZ.lp")

Model.solve(PLP.PULP_CBC_CMD(msg=False))

# Print af løsningens status
print("Status:", PLP.LpStatus[Model.status])

# Print af hver variabel med navn og løsningsværdi
for v in Model.variables():
    if v.varValue > 0.01:
        print(v.name, "=", v.varValue)

# Print af den optimale objektfunktionsværdi
print("Obj. = ", PLP.value(Model.objective))

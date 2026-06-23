# Eksempel på ATSPTW
# Her benyttes datamaterialet for 11 punkter som angivet i Excel-filen "ATSPTW-Eksempel.xlsx".
# Model 1

import math
# Importer PuLP-funktioner
import pulp as PLP

# Minimeringsproblem
Model = PLP.LpProblem("ATSPTW",PLP.LpMinimize)

BigM = 999

#Index =  1  2  3  4  5  6  7  8  9 10 11
XCoor=[0,47,30,77,92,43,55,27,99,87,83,50]
YCoor=[0,31,34,39,26,56,85,14,45,12,24,50]

#Index =     1   2   3   4   5   6   7   8   9  10   11
TWStart=[0, 50,100, 40,150,  0,100,  0, 30,100,200,   0]
TWSlut= [0,300,400,200,300, 20,200,400, 70,300,250,BigM]

def dist(i: int, j: int) -> float:
    xdiff = XCoor[i] - XCoor[j]
    ydiff = YCoor[i] - YCoor[j]
    return math.sqrt(xdiff*xdiff + ydiff*ydiff)

PunktRange = range(1,12) # 1..11

Arcs = [(i,j) for i in PunktRange for j in PunktRange if i != j and TWStart[i] + dist(i,j) <= TWSlut[j]]
# Betingelsen TWStart[i] + dist(i,j) <= TWSlut[j] eliminerer visse variable, bl.a. er der efter denne eliminering
# kun kanten (11,5) til punkt 5, som dermed bliver det første punkt på ruten i enhver brugbar løsning
# print(Arcs)

XVar = PLP.LpVariable.dicts("x",Arcs,0,1,PLP.LpInteger)
TVar = PLP.LpVariable.dicts("t",PunktRange,0,None,PLP.LpContinuous)

Model += PLP.lpSum([XVar[a]*dist(a[0],a[1]) for a in Arcs]), "Obj"

# Outflow:
for i in PunktRange:
    Model += PLP.lpSum(XVar[a] for a in Arcs if a[0] == i) == 1,"Outflow%s"%i

# Inflow:
for j in PunktRange:
    Model += PLP.lpSum(XVar[a] for a in Arcs if a[1] == j) == 1,"Inflow%s"%j

# MTZ:
for a in Arcs:
    if a[1] <= 10:
        Model += TVar[a[0]] + dist(a[0],a[1]) - BigM * (1-XVar[a]) <= TVar[a[1]]

for t in TVar:
    TVar[t].bounds(TWStart[t],TWSlut[t]) # Nedre og øvre grænse for hver t-variabel

# print(Model)

Model.solve(PLP.PULP_CBC_CMD(msg=False))

# Print af løsningens status
print("Status:", PLP.LpStatus[Model.status])

# Print af hver positiv variabel med navn og løsningsværdi
for v in Model.variables():
    if v.varValue > 0.01:
        print(v.name, "=", v.varValue)

# Print af den optimale objektfunktionsværdi
print("Obj. = ", PLP.value(Model.objective))

# Optimalløsning:
# Obj. = 332.868
# Rute = (11,5,8,6,3,4,9,10,1,7,2,11)

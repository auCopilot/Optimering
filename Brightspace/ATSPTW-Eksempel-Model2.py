# Eksempel på ATSPTW
# Her benyttes datamaterialet for 11 punkter som angivet i Excel-filen "ATSPTW-Eksempel.xlsx".
# Model 2

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

Model += PLP.lpSum([XVar[a]*dist(a[0],a[1]) for a in Arcs]), "Obj"

# Outflow:
for i in PunktRange:
    Model += PLP.lpSum(XVar[a] for a in Arcs if a[0] == i) == 1,"Outflow%s"%i

# Inflow:
for j in PunktRange:
    Model += PLP.lpSum(XVar[a] for a in Arcs if a[1] == j) == 1,"Inflow%s"%j

# print(Model)

# Herefter tilføjes iterativt uligheder til eliminering af subture og ikke-brugbare stier,
# indtil den resulterende heltalsløsning er brugbar og dermed optimal

# 1. løsning:
# Obj. = 222.037
# Subture: (1,7,2,1) (3,8,3) (4,9,10,4) (5,6,11,5)


        
# Tilføjelse af DFJ SECs:
S1 = [1,2,7]
S2 = [3,8]
S3 = [4,9,10]
S4 = [5,6,11]

Model += PLP.lpSum(XVar[a] for a in Arcs if a[0] in S1 and a[1] in S1) <= len(S1)-1
Model += PLP.lpSum(XVar[a] for a in Arcs if a[0] in S2 and a[1] in S2) <= len(S2)-1
Model += PLP.lpSum(XVar[a] for a in Arcs if a[0] in S3 and a[1] in S3) <= len(S3)-1
Model += PLP.lpSum(XVar[a] for a in Arcs if a[0] in S4 and a[1] in S4) <= len(S4)-1

#print(Model)

# 2. løsning:
# Obj. = 243.076
# Subture: (1,11,5,6,1) (2,7,2) (3,8,4,3) (9,10,9)

# Tilføjelse af DFJ SECs:
S5 = [1,5,6,11]
S6 = [2,7]
S7 = [3,4,8]
S8 = [9,10]

Model += PLP.lpSum(XVar[a] for a in Arcs if a[0] in S5 and a[1] in S5) <= len(S5)-1
Model += PLP.lpSum(XVar[a] for a in Arcs if a[0] in S6 and a[1] in S6) <= len(S6)-1
Model += PLP.lpSum(XVar[a] for a in Arcs if a[0] in S7 and a[1] in S7) <= len(S7)-1
Model += PLP.lpSum(XVar[a] for a in Arcs if a[0] in S8 and a[1] in S8) <= len(S8)-1

# 3. løsning:
# Obj. = 256.823
# Subture: (1,11,5,6,2,7,1) (3,8,4,10,9,3)

# Her kunne tilføjes en DFJ SEC for den ene af de to subture 
# (når der kun er to subture, er det tilstrækkeligt at tilføje een begrænsning for at eliminere begge subture)

# For illustrationens skyld vises her i stedet en ulighed til eliminering af en ikke-brugbar sti
# Stien (9,3,8) er en del af løsningen men er ikke brugbar
# Stien elimineres med flg. ulighed:

Model += XVar[(9,3)] + XVar[(3,8)] <= 1

# 4. løsning:
# Obj. = 259.679
# Subture: (1,11,5,6,2,7,1) (3,8,10,9,4,3)

# ... osv. For at løse modellen til optimalitet fortsættes processen iterativt, 
# indtil løsningen er brugbar og dermed optimal.
# Processen er dog ikke ført videre her

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


# Eksempel vedr. ordreplukning i et varehus

# Importer PuLP-funktioner
import pulp as PLP

# Minimeringsproblem
Model = PLP.LpProblem("CTSP",PLP.LpMinimize)

Afstand =  [[0],
			[0,0,14,15,18,19,20,22,30,36,34,36,39,32],
			[0,14,0,17,14,13,28,24,36,26,34,38,41,18],
			[0,15,17,0,9,10,17,13,25,27,25,27,30,23],
			[0,18,14,9,0,1,20,16,28,22,28,30,33,14],
			[0,19,13,10,1,0,21,17,29,21,29,31,34,13],
			[0,20,28,17,20,21,0,4,16,26,24,26,29,22],
			[0,22,24,13,16,17,4,0,20,22,20,22,25,18],
			[0,30,36,25,28,29,16,20,0,16,14,16,19,24],
			[0,36,26,27,22,21,26,22,16,0,12,18,19,8],
			[0,34,34,25,28,29,24,20,14,12,0,10,13,16],
			[0,36,38,27,30,31,26,22,16,18,10,0,9,26],
			[0,39,41,30,33,34,29,25,19,19,13,9,0,23],
			[0,32,18,23,14,13,22,18,24,8,16,26,23,0]]

PunktRange = range(1,14) # 1..13

Edges = [(i,j) for i in range(1,13) for j in range(i+1,14)]
#print("Edges:\n",Edges)

#for e in Edges:
#    print("Edge:",e[0],e[1])

XVar = PLP.LpVariable.dicts("x",Edges,0,1,PLP.LpInteger)

#print("XVar:\n",XVar)

Model += PLP.lpSum([XVar[e]*Afstand[e[0]][e[1]] for e in Edges]), "Obj"

# Valens = 2: Alle punkter skal besøges
for i in PunktRange:
    Model += PLP.lpSum(XVar[e] for e in Edges if i in e) == 2, "Degree_" + str(i)

# Tilføjelse af begrænsninger for klyngeinddelt problem:
KlyngeA = [1,7,10,11]
KlyngeB = [2,4,6]
KlyngeC = [3,5,8]
KlyngeD = [9,12]

Model += PLP.lpSum(XVar[e] for e in Edges if e[0] in KlyngeA and e[1] in KlyngeA) == len(KlyngeA)-1 # Lighedstegn i begrænsning
Model += PLP.lpSum(XVar[e] for e in Edges if e[0] in KlyngeB and e[1] in KlyngeB) == len(KlyngeB)-1 # Lighedstegn i begrænsning
Model += PLP.lpSum(XVar[e] for e in Edges if e[0] in KlyngeC and e[1] in KlyngeC) == len(KlyngeC)-1 # Lighedstegn i begrænsning
Model += PLP.lpSum(XVar[e] for e in Edges if e[0] in KlyngeD and e[1] in KlyngeD) == len(KlyngeD)-1 # Lighedstegn i begrænsning

# Løsningen til ovenstående formulering indeholder ingen subture og er dermed optimal. 
# Generelt skal dog om nødvendigt tilføjes begrænsninger til eliminering af subture.

# Obj. = 200
# Optimal CTSP løsning:
# SD-5-3-8-6-4-2-1-7-10-11-12-9-SD
# = SD-KlyngeC-KlyngeB-KlyngeA-KlyngeD-SD

# Model.writeLP("Varehus-CTSP.lp")

Model.solve(PLP.PULP_CBC_CMD(msg=False))

# Print af løsningens status
print("Status:", PLP.LpStatus[Model.status])

# Print af hver positiv variabel med navn og løsningsværdi
for v in Model.variables():
    if v.varValue > 0.01:
        print(v.name, "=", v.varValue)

# Print af den optimale objektfunktionsværdi
print("Obj. = ", PLP.value(Model.objective))

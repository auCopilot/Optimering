# Beregning af reduktioner og den reducerede matrix i Little m.fl.'s algoritme
# ATSP eksemplet med n=6 fra Little et al.'s artikel

import numpy as NP

M = 999
C = NP.array([[M, M, M, M, M, M, M],
              [M, M,27,43,16,30,26],
              [M, 7, M,16, 1,30,25],
              [M,20,13, M,35, 5, 0],
              [M,21,16,25, M,18,18],
              [M,12,46,27,48, M, 5],
              [M,23, 5, 5, 9, 5, M]])


print("Oprindelig matrix:")
print(C)

n = 5
PunktRange = range(1,n+1) # 1..6

# F.eks. delproblem P5 i branch-and-bound træet:
# ArcsFixedIn = [(1,4),(2,1),(5,6)]
# ArcsFixedOut = [(3,5)]

ArcsFixedIn = [(1,4)] #Her angives de kanter, som via
# branching er
# tvunget
# med i
                # løsningen
ArcsFixedOut = [] #Her angives de kanter, som via branching ikke må indgå i løsningen

print("\nFixedIn: ",ArcsFixedIn)
print("FixedOut: ",ArcsFixedOut)

# Kanter, som skal indgå i løsning:
# Next[i] angiver en evt. tvunget efterfølger til punkt i, og 0 hvis der 
# ikke er en tvungen efterfølger
# Prev[i] angiver en evt. tvunget forgænger til punkt i, og 0 hvis der 
# ikke er en tvungen forgænger

Next = [0 for i in range(0,n+1)]
Prev = [0 for i in range(0,n+1)]

for a in ArcsFixedIn:
    Next[a[0]] = a[1]
    Prev[a[1]] = a[0]
print("Next =",Next)
print("Prev =",Prev)

# For hver tvungen kant (a[0],a[1]) forbydes alle andre kanter til a[1] og 
# alle andre kanter fra a[0]:

for a in ArcsFixedIn:
    for i in PunktRange:
        if i != a[0]:
            C[i][a[1]] = M
    for j in PunktRange:
        if j != a[1]:
            C[a[0]][j] = M

# Identificer stier bestående af tvungne kanter. For hver sti forbydes
# kanten fra sidste punkt til første punkt på stien, idet kanten ellers 
# ville danne en subtur sammen med den fundne sti:

for Pkt in PunktRange:
    if Next[Pkt] > 0 and Prev[Pkt] == 0: # En tvunget sti starter i Pkt
        Start = Pkt
        # print("Start = ",Start)
        i = Next[Start]
        # print(i)

        while Next[i] > 0:
            #print(i)
            i = Next[i]

        Slut = i
        #print("Slut = ",Slut)

        # En tvunget sti fra Start til Slut
        print("En tvunget sti fra",Start,"til",Slut,"=> C(",Slut,",",Start,") = M")
        C[Slut][Start] = M

# Kanter, som ikke må indgå i løsningen:
for a in ArcsFixedOut:
    C[a[0],a[1]] = M

print("\nMatrix inkl. M-værdier pga. branching:")
print(C)

# Reducer matrix

RedSum = 0 # Sum af reduktioner
# Reduktion i rækker:
for r in PunktRange:
    RMin = min(C[r])
    RedSum += RMin
    C[r] -= RMin
    # print(RMin,RedSum)

print("\nMatrix efter rækkereduktioner:")
print(C)

# Reduktion i kolonner:
for c in PunktRange:
    CMin = min(C[:,c])
    RedSum += CMin
    C[:,c] -= CMin
    # print(CMin,RedSum)

print("\nEndelig reduceret matrix efter række- og kolonnereduktioner:")
print(C)
print("\nSamlet reduktion = ",RedSum)

# Beregning af straffe
MaxStraf = 0
BedsteR = 0
BedsteC = 0

for r in PunktRange:
    for c in PunktRange:
        if C[r][c] == 0 and Next[r] == 0:
            # Beregn straf for branching på kanten (r,c)
            C[r][c] = M # Midlertidigt, for nemmere at kunne finde næstmindste i rækken og kolonnen
            Straf = min(C[r]) + min(C[:,c])
            C[r][c] = 0
            if Straf > MaxStraf:
                MaxStraf = Straf
                BedsteR = r
                BedsteC = c

print("\nBranching: R =",BedsteR,", C =",BedsteC,", Straf =",MaxStraf)


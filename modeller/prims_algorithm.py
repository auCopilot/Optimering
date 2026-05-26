
def prim(G, cost):

    """
    Implementation follows Uge 8 Mindste Udspændende træer.

    Input:
     Non directional Graph G(N,E), list of lists
     Dictionary cost with e in E as key.
    """
    N = G[0]
    E = G[1]

    V = set()
    V.update([N[0]])
    E_T = set()

    while len(E_T) < len(N) - 1:
        # Some high initial cost
        c = 999
        min_e = (None, None)
        for e in E:
            # Find delta(V)
            if e[0] in V and e[1] not in V:
                if cost[e] < c:
                    # Minimal cost in delta(V)
                    c = cost[e]
                    min_e = e
        # Update sets
        E_T.update([min_e])
        if min_e[1] is not None:
            V.update([min_e[1]])
    return N, E_T

G = (list(range(1,8)), [(1, 2), (1, 4), (2, 3), (3, 4), (4, 7), (3, 5), (5,6), (6,7), (7, 3)])
cost = {(1, 2) : 4,
        (1, 4) : 5,
        (2, 3) : 1,
        (3, 4) : 3,
        (4, 7) : 8,
        (3, 5) : 7,
        (5, 6) : 2,
        (6, 7) : 6,
        (7, 3) : 9}

N, E_T = prim(G, cost)
p = 0
for e in E_T:
    p += cost[e]
    print(f"Edge used {e} with price {cost[e]}")

print("Total cost:", p)


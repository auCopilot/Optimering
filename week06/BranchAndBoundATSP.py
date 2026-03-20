import numpy as np


c = np.array([[ 9999,27,43,16,30,26],
              [ 7, 9999,16, 1,30,25],
              [20,13, 9999,35, 5, 0],
              [21,16,25, 9999,18,18],
              [12,46,27,48, 9999, 5],
              [23, 5, 5, 9, 5, 9999]]).astype(float)


c = np.array([
    [9999, 12, 10, 19, 8, 11],
    [7, 9999, 6, 15, 9, 12],
    [8, 9, 9999, 7, 14, 10],
    [14, 6, 12, 9999, 11, 13],
    [10, 8, 9, 6, 9999, 7],
    [11, 13, 5, 8, 6, 9999]
]).astype(float)

def branch_and_bound_atsp(cost, included_edges, excluded_edges, lower_bound,
                          depth=0, best_lower_bound=[np.inf], p=[0]):
    """Branch and bound algorithm for the Asymmetric Traveling Salesman Problem
    Input:
    - cost: 2D numpy array representing the cost matrix of the ATSP instance

    - included_edges: list of edges (i,j) that are forced to be included in
    the solution

    - excluded_edges: list of edges (i,j) that are forced to be excluded from
    the solution

    - lower_bound: the current lower bound on the cost of the solution for
    this branch, starting at 0 for the root node

    - depth: the current depth in the branch-and-bound tree, starting at 0

    - best_lower_bound: a mutable object (list) that holds the best known
    lower, muteability allows us to update it inside the recursive function.
     Initially set to infinity, and updated whenever we find a complete tour
     with a better cost.

     - p: a mutable object (list) that holds the problem number for
      printing purposes, starting at 0 and incremented for
        each call to the function.
    """


    M = np.inf
    if included_edges is None:

        included_edges = []
        excluded_edges = []
        np.fill_diagonal(cost, M)

    m,n = cost.shape

    def reduce_cost_matrix(cost):
        """Vectorized cost matrix reduction for ATSP.
         Returns the reduced cost matrix and the sum of reductions."""
        # Sum of reductions
        cost = cost.copy() # Avoid modifying original cost matrix
        red_sum = 0
        for i in range(m):
            row_min = np.min(cost[i])
            if row_min < np.inf:
                red_sum += row_min
                cost[i] -= row_min

        for j in range(n):
            col_min = np.min(cost[:,j])
            if col_min < np.inf:
                red_sum += col_min
                cost[:,j] -= col_min
        return cost, red_sum

    def exclude(cost, forced_edges):
        """Set cost[i][j] to infinity (or a very large number) to exclude edge (i,j) from the solution."""
        c = cost.copy()  # Avoid modifying original cost matrix
        for edge in forced_edges:
            i,j = edge
            c[i][j] = M
        return c

    def include(cost, forced_edges):
        """Include edge (i,j) in the solution by setting all other edges from i and to j to infinity.
        Inspired from Jens' implementation in week06/ATSP-LittleEtAl-Reduktion.py."""
        c = cost.copy()
        for edge in forced_edges:
            for i in range(m):
                if i != edge[0]:
                    c[i][edge[1]] = M
            for j in range(n):
                if j != edge[1]:
                    c[edge[0]][j] = M


        Next = [-1] * n
        Prev = [-1] * n

        # Build Next/Prev from forced_edges
        for (a, b) in forced_edges:
            Next[a] = b
            Prev[b] = a
        for pkt in range(n):
            if Next[pkt] > -1 and Prev[pkt] == -1:
                start = pkt
                i = Next[pkt]
                while Next[i] > -1:
                    i = Next[i]
                slut = i
                c[slut][start] = M
        return c

    def branching(cost):
        """ Find the next branching edge (i,j) with cost 0 in the reduced
         cost matrix and create two branches, such that the cost of excluding
         edge (i,j) is as high as possible."""

        max_price = 0
        for i in range(cost.shape[0]):
            for j in range(cost.shape[1]):
                if cost[i][j] == 0 and (i,j) not in included_edges:
                    tmp_cost = cost.copy()
                    # Change cost[i][j] such that this is not the minimum cost edge
                    tmp_cost[i][j] = M
                    # anymore, i.e. the cost of excluding this edge is high
                    # Found a zero-cost edge (i,j) to branch on
                    price = np.min(tmp_cost[i]) + np.min(tmp_cost[:,j])

                    if price > max_price:
                        max_price = price
                        best_edge = (i,j)


        return best_edge



    # If the lower bound is already worse than the best known solution, prune this branch


    # Step 1: Reduce the cost matrix and calculate the lower bound
    print("############################################")
    print(f"Problem{p[0]}")
    p[0] += 1
    reduced_cost, reduction_sum = reduce_cost_matrix(cost)


    # If we have a complete tour depth == n - 1, we can update the best known
    # solution if this tour is better than the best known solution.
    # We use a mutable object (list) for best_lower_bound to allow updating it
    # inside the recursive function.

    # Step 2: Branching on the edge with the highest price (cost of exclusion)
    branch = branching(reduced_cost)

    print("Branching on edge:", branch)
    print("included edges:", included_edges)
    print("excluded edges:", excluded_edges)
    print("BEST LOWER BOUND:", best_lower_bound[0])
    print()

    if reduction_sum < np.inf:
        lower_bound += reduction_sum
    else:
        # Invalid solution due to infinite reduction, prune this branch
        return
    print("Lower bound after reduction:", lower_bound)

    # Check if we can prune this branch
    if lower_bound >= best_lower_bound[0]:
        print("Pruning branch at depth", depth, "with lower bound",
              lower_bound)
        print("included edges:", included_edges)
        print("excluded edges:", excluded_edges)
        print("BEST LOWER BOUND:", best_lower_bound[0])
        print("############################################")
        print()
        return
    # Step 3: Create two branches - one including the edge and one excluding the edge

    included_edges = included_edges + [branch]
    included_cost = include(reduced_cost, included_edges)

    if depth == n - 1:
        if lower_bound < best_lower_bound[0]:
            print("Complete tour found with cost:", lower_bound)
            print("Depth:", depth)

            best_lower_bound[0] = lower_bound
            print("Branching on edge:", branch)
            print("included edges:", included_edges)
            print("excluded edges:", excluded_edges)
            print("BEST LOWER BOUND:", best_lower_bound[0])
            print("############################################")
            return


    # Step 4: Recursively solve, start by solving the branch that includes the edge

    branch_and_bound_atsp(included_cost,
                           included_edges,
                           excluded_edges,
                           lower_bound,
                           depth + 1,
                           best_lower_bound,
                        p)

    # After DFS on right branch, we backtrack and explore the left branch that excludes the edge
    if included_edges:
        excluded_edges = excluded_edges + [included_edges.pop()]

    excluded_cost = exclude(reduced_cost, excluded_edges)

    branch_and_bound_atsp(excluded_cost,
                          included_edges,
                          excluded_edges,
                          lower_bound,
                          depth,
                          best_lower_bound,
                          p)











branch_and_bound_atsp(c,None, None, 0, depth=1, best_lower_bound=[np.inf],
                      p=[0])

import itertools



n = len(c)
best_cost = float('inf')
best_route = None

for perm in itertools.permutations(range(1, n)):
    route = (0,) + perm + (0,)
    total = sum(c[route[i]][route[i + 1]] for i in range(n))

    if total < best_cost:
        best_cost = total
        best_route = route

print(best_route, best_cost)
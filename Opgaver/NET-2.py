from modeller.network.clustering_from_shortest_path import clustering_from_shortest_path
#1)
group_sizes = [3,4]
# 0 U Nodes
nodes = range(23)
h = "0.0 10.3 11.1 11.2 11.9 12.1 12.2 13.4 15.2 16.1 16.7 17.1 17.2 17.5 18.4 19.5 20.1 22.1 23.7 25.8 26.4 27.1 28.2"
h = h.split(" ")
h = [float(i) for i in h]
# Possible edges are the ones where we jump within the possible groupsizes and the jump does not exceed the nodes.
edges = [(i, i+j) for i in nodes for j in group_sizes if i + j < len(nodes)]

def cost(edges):
    # Ordered handicap, so we can just compute the difference over the edges.
    return [h[j] - h[i + 1] for i, j in edges]

CFSP = clustering_from_shortest_path(nodes, edges, cost)
CFSP.construct_constraints()
CFSP.solve_and_print()

# 2) We can minimize the number of groupes made by adding a fixed penalty for making a group. If we make this
# penalty much larger than any cost from the difference in golf handicap, we minimize the groups

def cost(edges):
    # Ordered handicap, so we can just compute the difference over the edges.
    M = 1000
    return [h[j] - h[i+1] + M for i, j in edges]

CFSP = clustering_from_shortest_path(nodes, edges, cost)
CFSP.construct_constraints()
CFSP.solve_and_print()
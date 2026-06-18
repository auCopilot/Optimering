import numpy as np
from modeller.set_covering_problem import set_covering_problem
from itertools import product # Cartisian product

# Coordinates defines S
x = [3.6, 1.6, 6.5, 8.8, 0.4, 2.8, 6.3, 8.6, 1.0, 6.4, 5.7, 8.6, 2.8, 4.1, 8.7]
y = [2.1, 3.3, 8.5, 0.7, 8.3, 7.9, 1.2, 1.6, 0.9, 5.0, 7.1, 4.7, 4.2, 2.7, 7.8]
city_coordinates = list(zip(x,y))
city_range = range(len(x))

# Grid integer coordinates defines Families F 0 ... 9 X 0 ... 9 grid
p = (range(10))
possible_coordinates = list(product(p,p))


def adj_matrix(L):
    # Shape of |M| and |F|
    adj_matrix = np.zeros((len(city_coordinates), len(possible_coordinates)))

    # Fill adj-matrix according to L2 norm
    for i, c_coord in enumerate(city_coordinates):
        for j, p_coord in enumerate(possible_coordinates):
            np.array(p_coord)
            diff = np.array(c_coord) - np.array(p_coord)
            if np.linalg.norm(diff) <= L:
                adj_matrix[i][j] = 1
            else:
                adj_matrix[i][j] = 0
    return adj_matrix
# 1)
# Set is covered if distance is less than L
L = 3
adj_matrixL3 = adj_matrix(L)
# Cost is the samme for all possible locations
cost = [1] * len(possible_coordinates)
# Weights are equal for all cities
weights = [1] * len(city_coordinates)

set_cover_problem = set_covering_problem(adj_matrixL3, weights, cost, possible_coordinates)
set_cover_problem.construct_constraints()
set_cover_problem.solve_and_print()
set_cover_problem.plot_solution(city_coordinates,
                                subset_coordinates=possible_coordinates,
                                coverage_radius= L,
                                title=f"HELTAL-5: Selected Positions to Cover Cities, L = {L}")

# Set is covered if distance is less than L
L = 4
adj_matrixL4 = adj_matrix(L)
# Cost is the samme for all possible locations
cost = [1] * len(possible_coordinates)
# Weights are equal for all cities
weights = [1] * len(city_coordinates)

set_cover_problem = set_covering_problem(adj_matrixL4, weights, cost, possible_coordinates)
set_cover_problem.construct_constraints()
set_cover_problem.solve_and_print()
set_cover_problem.plot_solution(city_coordinates,
                                subset_coordinates=possible_coordinates,
                                coverage_radius= L,
                                title=f"HELTAL-5: Selected Positions to Cover Cities, L = {L}")

# Add weights to 5 first cities such that they are covered at least twice
L = 3
# Cost is the samme for all possible locations
cost = [1] * len(possible_coordinates)
# Weights are equal for all cities
weights = [2] * 5 + [1] * (len(city_coordinates) - 5)

set_cover_problem = set_covering_problem(adj_matrixL3, weights, cost, possible_coordinates)
set_cover_problem.construct_constraints()
set_cover_problem.solve_and_print()
set_cover_problem.plot_solution(city_coordinates,
                                subset_coordinates=possible_coordinates,
                                coverage_radius= L,
                                title=f"HELTAL-5: Selected Positions to Cover Cities, L = {L} And Weights on first 5 cities")
L = 4
# Cost is the samme for all possible locations
cost = [1] * len(possible_coordinates)
# Weights are equal for all cities
weights = [2] * 5 + [1] * (len(city_coordinates) - 5)

set_cover_problem = set_covering_problem(adj_matrixL4, weights, cost, possible_coordinates)
set_cover_problem.construct_constraints()
set_cover_problem.solve_and_print()
set_cover_problem.plot_solution(city_coordinates,
                                subset_coordinates=possible_coordinates,
                                coverage_radius= L,
                                title=f"HELTAL-5: Selected Positions to Cover Cities, L = {L} And Weights on first 5 cities")

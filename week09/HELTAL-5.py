
import pulp as PLP
import numpy as np
from itertools import product
from CustomFunctions import print_solution

x = [3.6, 1.6, 6.5, 8.8, 0.4, 2.8, 6.3, 8.6, 1.0, 6.4, 5.7, 8.6, 2.8, 4.1, 8.7]

y = [2.1, 3.3, 8.5, 0.7, 8.3, 7.9, 1.2, 1.6, 0.9, 5.0, 7.1, 4.7, 4.2, 2.7, 7.8]
city_coordinates = list(zip(x,y))
city_range = range(len(x))

p = (range(10))
L = 3

possible_coordinates = list(product(p,p))
print("Length pos", len(possible_coordinates))
pos_range = range(len(possible_coordinates))


def cost(j):
    return 1

def distance(city_coord, pos_cord, i, j):
    return ((city_coord[i][0] - pos_cord[j][0] ) ** 2
            + (city_coord[i][1] - pos_cord[j][1])**2) ** 0.5

def in_range(i, j, L):
    return distance(city_coordinates, possible_coordinates, i, j) <= L

a = np.zeros((len(city_range), len(pos_range)), dtype=int)

# Define the adjacency matrix of the graph, where a[i][j] = 1 if nodes i and
# j are connected, and 0 otherwise. This is later used to find subsets of nodes
# in which atleast one of the nodes must be in the subset.

for i in city_range:
    for j in pos_range:
        if in_range(i,j, L):
            a[i][j] = 1


model = PLP.LpProblem(name="HELTAL-5", sense=PLP.LpMinimize)

delta = PLP.LpVariable.dicts("delta", pos_range, cat=PLP.LpBinary)

# All costs are assumed to be equal, so we define the objective function as
model += PLP.lpSum(cost(j) * delta[j] for j in pos_range), "Objective"

# At least one subset constraint with option to add minium two positions in
# the cities 1-5
opg2 = True
for i in range(len(x)):
    if opg2 and i <= 4:
        model += (PLP.lpSum(a[i][j]*delta[j] for j in pos_range) >= 2,
                  (f"Subset "
                                                                     f"Constarint_{i}"))
    elif opg2 and i > 4:
        model += PLP.lpSum(a[i][j]*delta[j] for j in pos_range) >= 1, (f"Subset "
                                                                      f"Constarint_{i}")
    else:
        model += PLP.lpSum(a[i][j]*delta[j] for j in pos_range) >= 1, (f"Subset "
                                                                      f"Constarint_{i}")
print_solution(model)

# Retrive non-zero variables
selected_positions = [j for j in pos_range if delta[j].varValue > 0]
for s in selected_positions:
    print(f"Selected position: {possible_coordinates[s]} with cost {cost(s)}")

# Plot the cities and the selected positions
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(8, 8))
# Plot cities
plt.scatter(x, y, color='blue', label='Cities')
# Annotate cities with their indices
for i, (x_coord, y_coord) in enumerate(city_coordinates):
    plt.text(x_coord + 0.1, y_coord + 0.1, str(i + 1), fontsize=9,
             color='blue')

# Plot selected positions
selected_coords = [possible_coordinates[j] for j in selected_positions]
selected_x = [coord[0] for coord in selected_coords]
selected_y = [coord[1] for coord in selected_coords]
plt.scatter(selected_x, selected_y, color='red', label='Selected Positions')
circles = []
for idx, s in enumerate(selected_coords):
    circles.append(
        plt.Circle(
            s, L, color='red', fill=True, alpha=0.5,
            label='Coverage Area' if idx == 0 else None
        )
    )

for circle in circles:
    ax.add_patch(circle)
plt.title(f'HELTAL-5: Selected Positions to Cover Cities, L = {L}')
plt.xlabel('X Coordinate')
plt.ylabel('Y Coordinate')
plt.legend()
# Make plot square.
plt.axis('equal')
plt.grid()
plt.show()

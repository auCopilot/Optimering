import numpy as np
import matplotlib.pyplot as plt
import pulp as PLP

class set_covering_problem:
    """ This implementaion follows Set Covering, Packing, Partition from Uge 13, it is modified to be
    able to handle the weighted problem, by allowing weights != 1 for the constraints
    Input:
    adj_matrix: Adjacency matrix shape(m,n), that to some criteria defines if i = 1...m'th element is
    contained in the j = 1...n subset, thus adj_matrix[i][j] = 1 if i is in subset j, and 0 otherwise

    weights: A list of length m, where weights[i] is the weight of the i'th element, allowing
    requiring 1 or more subsets to cover the element, thus weights[i] = 1 means that the i'th element must be covered by
    at least one subset, weights[i] = 2 means that the i'th element must be covered by at least two subsets, and so on.

    costs: A list of length n, where costs[j] is the cost of including the j'th subset in the solution.

    F: the Famlily of possible subsets
    """
    def __init__(self, adj_matrix, weights, costs, F):
        self.adj_matrix = adj_matrix
        self.weights = weights
        self.costs = costs
        self.m , self.n = adj_matrix.shape
        self.F = F

        self.model = PLP.LpProblem(name="SetCoveringProblem", sense=PLP.LpMinimize)
        self.delta = PLP.LpVariable.dicts("delta", range(self.n), cat=PLP.LpBinary, lowBound=0, upBound=1)

        # Add objective
        self.model += PLP.lpSum(self.costs[j] * self.delta[j] for j in range(self.n)), "Objective"
        self.constraints = "NOT ADDED"


    def construct_constraints(self):
        for i in range(self.m):
            self.model += PLP.lpSum(self.adj_matrix[i][j]*self.delta[j]
                                    for j in range(self.n)) >= self.weights[i], f"Subset_Constraint_{i}"
        self.constraints = "ADDED"

    def solve_and_print(self, quiet = True):
        if self.constraints != "ADDED":
            raise ValueError("You must add the constraints before solving")
        eps = 0.01
        self.model.solve(PLP.PULP_CBC_CMD(msg=0 if quiet else 1))
        print("Status:", PLP.LpStatus[self.model.status])
        print("Objective value:", PLP.value(self.model.objective))
        for i in range(self.n):
            if self.delta[i].varValue is not None and self.delta[i].varValue > 0 + eps:
                print(f"Subset {self.F[i]} is included in the solution with cost {self.costs[i]}")

    ### PLOTTING CODE ###

    def get_selected_subset_indices(self, eps=1e-6):
        """Return indices of subsets selected in the solved model."""
        return [j for j in range(self.n) if self.delta[j].varValue is not None and self.delta[j].varValue > eps]

    def plot_solution(
        self,
        element_coordinates,
        subset_coordinates=None,
        selected_indices=None,
        coverage_radius=None,
        annotate_elements=True,
        annotate_subsets=False,
        show_all_subsets=False,
        figsize=(8, 8),
        title="Set Covering Solution",
        equal_axis=True,
    ):
        """
        Plot element coordinates and selected subset coordinates.

        Args:
            element_coordinates: Sequence of (x, y) coordinates for elements to cover (size m).
            subset_coordinates: Sequence of (x, y) coordinates for subsets (size n). Defaults to self.F.
            selected_indices: Optional explicit subset indices to plot as selected.
            coverage_radius: Optional radius for drawing coverage circles around selected subsets.
        """
        if subset_coordinates is None:
            subset_coordinates = self.F

        if len(element_coordinates) != self.m:
            raise ValueError(f"Expected {self.m} element coordinates, got {len(element_coordinates)}")
        if len(subset_coordinates) != self.n:
            raise ValueError(f"Expected {self.n} subset coordinates, got {len(subset_coordinates)}")

        if selected_indices is None:
            selected_indices = self.get_selected_subset_indices()
            if len(selected_indices) == 0:
                raise ValueError("No selected subsets found. Solve the model before plotting.")

        for idx in selected_indices:
            if idx < 0 or idx >= self.n:
                raise IndexError(f"Selected subset index {idx} is out of bounds for n={self.n}")

        element_x = [coord[0] for coord in element_coordinates]
        element_y = [coord[1] for coord in element_coordinates]
        selected_coords = [subset_coordinates[j] for j in selected_indices]
        selected_x = [coord[0] for coord in selected_coords]
        selected_y = [coord[1] for coord in selected_coords]

        fig, ax = plt.subplots(figsize=figsize)

        if coverage_radius is not None:
            if coverage_radius <= 0:
                raise ValueError("coverage_radius must be positive")
            for idx, coord in enumerate(selected_coords):
                circle = plt.Circle(
                    coord,
                    coverage_radius,
                    color="red",
                    fill=True,
                    alpha=0.4,
                    label="Coverage Area" if idx == 0 else None,
                )
                ax.add_patch(circle)

        plt.scatter(element_x, element_y, color="blue", label="Elements")

        if annotate_elements:
            for i, (x_coord, y_coord) in enumerate(element_coordinates):
                plt.text(x_coord + 0.1, y_coord + 0.1, str(i + 1), fontsize=9, color="blue")

        if show_all_subsets:
            all_subset_x = [coord[0] for coord in subset_coordinates]
            all_subset_y = [coord[1] for coord in subset_coordinates]
            plt.scatter(all_subset_x, all_subset_y, color="lightgray", marker="x", label="All Subsets")

        plt.scatter(selected_x, selected_y, color="green", label="Selected Subsets")

        if annotate_subsets:
            for idx, (x_coord, y_coord) in zip(selected_indices, selected_coords):
                plt.text(x_coord + 0.1, y_coord + 0.1, str(subset_coordinates[idx]), fontsize=9, color="red")



        plt.title(title)
        plt.xlabel("X Coordinate")
        plt.ylabel("Y Coordinate")
        plt.legend()
        if equal_axis:
            plt.axis("equal")
        plt.grid()
        plt.show()
        return fig, ax



# Example usage Heltal-5
if __name__ == "__main__":

    from itertools import product
    # Coordinates defines S
    x = [3.6, 1.6, 6.5, 8.8, 0.4, 2.8, 6.3, 8.6, 1.0, 6.4, 5.7, 8.6, 2.8, 4.1, 8.7]
    y = [2.1, 3.3, 8.5, 0.7, 8.3, 7.9, 1.2, 1.6, 0.9, 5.0, 7.1, 4.7, 4.2, 2.7, 7.8]
    city_coordinates = list(zip(x,y))
    city_range = range(len(x))

    # Grid integer coordinates defines Families F 0 ... 9 X 0 ... 9 grid
    p = (range(10))
    possible_coordinates = list(product(p,p))

    # Set is covered if distance is less than L
    L = 2
    # Shape of |M| and |F|
    adj_matrix = np.zeros((len(city_coordinates), len(possible_coordinates)))

    def dist(coord1, coord2):
        return ((coord1[0] - coord2[0]) ** 2 + (coord1[1] - coord2[1]) ** 2) ** 0.5

    # Fill adj-matrix
    for i, c_coord in enumerate(city_coordinates):
        for j, p_coord in enumerate(possible_coordinates):
            if dist(c_coord, p_coord) <= L:
                adj_matrix[i][j] = 1
            else:
                adj_matrix[i][j] = 0

    weights = [2,2,2,2,2] + [1] * 10
    costs = [1] * len(possible_coordinates)

    SCP = set_covering_problem(adj_matrix, weights, costs, possible_coordinates)
    SCP.construct_constraints()
    SCP.solve_and_print(quiet = True)

    SCP.plot_solution(
        element_coordinates=city_coordinates,
        subset_coordinates=possible_coordinates,
        coverage_radius=L,
        annotate_elements=True,
        title=f"HELTAL-5: Selected Positions to Cover Cities, L = {L}",
    )

import pulp as PLP
import numpy as np
import matplotlib.pyplot as plt

def construct_constraints(model,
                          x,
                          variable_names,
                          coef_matrix,
                          rhs,
                          equality_types):

    """Construct constraints for a LP model.
    Inputs:
        model: PuLP LpProblem instance
        x: dictionary of PuLP LpVariable instances
        variable_names: list of variable names corresponding to x
        coef_matrix: list of lists, where each inner list contains coefficients
                     for the variables in a constraint.
        rhs: list of right-hand side values for each constraint.
        equality_types: list of strings indicating the type of each constraint
                        ("<=", ">=", "==").

    """
    # Determine number of constraints from length of rhs
    n_constraints = len(rhs)
    n_variables = len(variable_names)
    # Define constraints according to their types.
    for i in range(n_constraints):
        constraint_expr = PLP.lpSum(coef_matrix[i][j] * x[variable_names[j]]
                                    for j in range(n_variables))
        if equality_types[i] == "<=":
            model += constraint_expr <= rhs[i], f"Constraint_{i+1}"
        elif equality_types[i] == ">=":
            model += constraint_expr >= rhs[i], f"Constraint_{i+1}"
        elif equality_types[i] == "==":
            model += constraint_expr == rhs[i], f"Constraint_{i+1}"

    print("Constraints constructed.")


class LPFeasibleRegionPlotter:
    def __init__(self, coef_matrix, rhs, equality_types, x1_bounds=(0, 20), x2_bounds=(0, 20)):
        """
        Initialize the plotter with problem data.

        Args:
            coef_matrix: List of lists [[a1, b1], [a2, b2], ...] for constraints a*x1 + b*x2
            rhs: List of right-hand side values [c1, c2, ...]
            equality_types: List or tuple of strings ["<=", ">=", "=="]
            x1_bounds: Tuple (min, max) for x-axis
            x2_bounds: Tuple (min, max) for y-axis
        """
        self.coef_matrix = np.array(coef_matrix)
        self.rhs = np.array(rhs)
        self.equality_types = equality_types
        self.x1_bounds = x1_bounds
        self.x2_bounds = x2_bounds

    def plot(self, objective_coeffs=None, optimal_value=None):
        """
        Plot the feasible region and optionally the optimal solution line.
        """
        # Create grid
        d = np.linspace(self.x1_bounds[0], self.x1_bounds[1], 300)
        x1_grid, x2_grid = np.meshgrid(d, d)

        # Start with all points being feasible
        feasible_mask = np.ones_like(x1_grid, dtype=bool)

        plt.figure(figsize=(8, 8))

        # Use a colormap to get distinct colors
        cmap = plt.get_cmap("tab10")

        # 1. Calculate feasible region mask and plot constraint lines
        for i in range(len(self.rhs)):
            a, b = self.coef_matrix[i]
            c = self.rhs[i]
            eq_type = self.equality_types[i]
            color = cmap(i % 10) # Cycle through 10 distinct colors

            # Update feasible mask (using numerical tolerance)
            lhs_val = a * x1_grid + b * x2_grid
            if eq_type == "<=" or eq_type == "<":
                feasible_mask &= (lhs_val <= c + 1e-9)
            elif eq_type == ">=" or eq_type == ">":
                feasible_mask &= (lhs_val >= c - 1e-9)
            elif eq_type == "==" or eq_type == "=":
                feasible_mask &= (np.abs(lhs_val - c) <= 1e-1) # Thicker band for visual equality

            # Plot line a*x1 + b*x2 = c
            # Avoid division by zero for vertical lines
            if abs(b) > 1e-6:
                x2_line = (c - a * d) / b
                # Remove x1 from labels if a is zero.
                if abs(a) < 1e-6:
                    plt.plot(d, x2_line, color=color, linewidth=2,
                             label=f'{b}$x_{2}$ {eq_type} {c}')
                else:
                    plt.plot(d, x2_line, color=color, linewidth=2,
                             label=f'{a}$x_{1}$ + {b}$x_{2}$ {eq_type} {c}')
            else:
                plt.axvline(x=c/a, color=color, linewidth=2,
                            label=f'{a}$x_{1}$ {eq_type} {c}')

        # 1.5 Calculate and plot intersections
        labels = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        label_idx = 0
        points_plotted = []

        # Add pure axis boundaries to find intercepts with axes if needed,
        # but here we focus on finding intersections between explicit constraints.
        # We iterate over all unique pairs of constraints
        num_constraints = len(self.coef_matrix)

        for i in range(num_constraints):
            for j in range(i + 1, num_constraints):
                # Solving system:
                # a1*x1 + b1*x2 = c1
                # a2*x1 + b2*x2 = c2
                A = np.array([self.coef_matrix[i], self.coef_matrix[j]])
                B = np.array([self.rhs[i], self.rhs[j]])

                # Check if lines are parallel (det = 0)
                det = np.linalg.det(A)
                if abs(det) < 1e-10:
                    continue

                intersection = np.linalg.solve(A, B)
                x, y = intersection

                # Check if point is within plot bounds
                if (self.x1_bounds[0] <= x <= self.x1_bounds[1]) and \
                   (self.x2_bounds[0] <= y <= self.x2_bounds[1]):

                    # Avoid plotting duplicate points close to each other
                    is_duplicate = False
                    for px, py in points_plotted:
                        if np.hypot(x-px, y-py) < 0.2:
                            is_duplicate = True
                            break

                    if not is_duplicate:
                        plt.plot(x, y, 'ko', markersize=5) # Black dot
                        lbl = labels[label_idx % len(labels)]
                        # Add numeric suffix if we run out of letters
                        if label_idx >= len(labels):
                            lbl += str(label_idx // len(labels))

                        plt.annotate(lbl, (x, y), xytext=(5, 5), textcoords='offset points', fontweight='bold')
                        points_plotted.append((x, y))
                        label_idx += 1

        # 2. Plot feasible region (Green)
        plt.imshow(feasible_mask.astype(int),
                   extent=(self.x1_bounds[0], self.x1_bounds[1], self.x1_bounds[0], self.x1_bounds[1]),
                   origin="lower", cmap="Greens", alpha=0.3)

        # 3. Plot optimal objective line if provided
        if objective_coeffs and optimal_value is not None:
            c1, c2 = objective_coeffs
            # c1*x1 + c2*x2 = optimal_value => x2 = (optimal_value - c1*x1) / c2
            if abs(c2) > 1e-6:
                x2_opt = (optimal_value - c1 * d) / c2
                plt.plot(d, x2_opt, 'r--', linewidth=2, label=f'Optimal Z = {optimal_value}')
            else:
                plt.axvline(x=optimal_value/c1, color='r', linestyle='--', linewidth=2, label=f'Optimal Z = {optimal_value}')

        # Formatting
        plt.xlim(self.x1_bounds)
        plt.ylim(self.x2_bounds)
        plt.xlabel('$x_{1}$')
        plt.ylabel('$x_{2}$')
        plt.grid(True, which='both', linestyle='--', alpha=0.7)
        plt.title('Feasible Region (Green area)')
        plt.legend(loc='best', bbox_to_anchor=(1.05, 1))
        plt.tight_layout()
        plt.show()


def print_solution(Model, condition = None):
    # Loesning af modellen vha. PuLP's valg af Solver
    Model.solve()
    # Print af loesningens status
    print("Status:", PLP.LpStatus[Model.status])
    # Print af hver variabel med navn og loesningsvaerdi
    if condition is not None:
        for v in Model.variables():
            if condition(v):
                print(v.name, "=", v.varValue)
    else:
        for v in Model.variables():
            print(v.name, "=", v.varValue)

    # Print af den optimale objektfunktionsvaerdi
    print("Obj. = ", PLP.value(Model.objective))

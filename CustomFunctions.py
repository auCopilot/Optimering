import pulp as PLP
import numpy as np
import matplotlib.pyplot as plt

def construct_constraints(model,
                          x,
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
    variable_names = list(x.keys())
    n_variables = len(variable_names)
    # Define constraints according to their types

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
    def __init__(
        self,
        coef_matrix,
        rhs,
        equality_types,
        x1_bounds=(0, 20),
        x2_bounds=(0, 20),
        grid_points=400,
        tol=1e-9,
    ):
        """
        Plot feasible regions for 2-variable LP constraints.

        Args:
            coef_matrix: Iterable of [a, b] for each constraint a*x1 + b*x2 (shape: n x 2)
            rhs: Iterable of right-hand side values c (length: n)
            equality_types: Iterable of constraint types: "<=", "<", ">=", ">", "==", "="
            x1_bounds: (min, max) for x1 axis
            x2_bounds: (min, max) for x2 axis
            grid_points: Resolution for feasible-region raster
            tol: Numerical tolerance
        """
        self.coef_matrix = np.asarray(coef_matrix, dtype=float)
        self.rhs = np.asarray(rhs, dtype=float)
        self.equality_types = list(equality_types)
        self.x1_bounds = tuple(x1_bounds)
        self.x2_bounds = tuple(x2_bounds)
        self.grid_points = int(grid_points)
        self.tol = float(tol)

        self._validate_inputs()

    def _validate_inputs(self):
        if self.coef_matrix.ndim != 2 or self.coef_matrix.shape[1] != 2:
            raise ValueError("coef_matrix must have shape (n_constraints, 2).")

        n = self.coef_matrix.shape[0]
        if len(self.rhs) != n or len(self.equality_types) != n:
            raise ValueError(
                "Lengths must match: len(coef_matrix) == len(rhs) == len(equality_types)."
            )

        valid_eq = {"<=", "<", ">=", ">", "==", "="}
        bad = [e for e in self.equality_types if e not in valid_eq]
        if bad:
            raise ValueError(f"Invalid equality_types found: {bad}. Allowed: {sorted(valid_eq)}")

        if self.x1_bounds[0] >= self.x1_bounds[1]:
            raise ValueError("x1_bounds must satisfy min < max.")
        if self.x2_bounds[0] >= self.x2_bounds[1]:
            raise ValueError("x2_bounds must satisfy min < max.")
        if self.grid_points < 50:
            raise ValueError("grid_points should be at least 50 for decent visualization.")

    @staticmethod
    def _format_constraint_label(a, b, eq_type, c):
        def fmt_num(v):
            if abs(v - round(v)) < 1e-12:
                return str(int(round(v)))
            return f"{v:.3g}"

        parts = []
        if abs(a) > 1e-12:
            parts.append(f"{fmt_num(a)}$x_1$")
        if abs(b) > 1e-12:
            sign = "+" if b >= 0 and parts else ""
            parts.append(f"{sign}{fmt_num(b)}$x_2$")
        if not parts:
            lhs = "0"
        else:
            lhs = " ".join(parts)

        return f"{lhs} {eq_type} {fmt_num(c)}"

    def _constraint_line(self, a, b, c, x_vals):
        """
        Returns x2 values for line a*x1 + b*x2 = c if non-vertical.
        For vertical lines, caller should use x = c/a.
        """
        return (c - a * x_vals) / b

    def plot(
        self,
        objective_coeffs=None,
        optimal_value=None,
        show_constraints=True,
        show_feasible_region=True,
        show_objective=True,
        show_equality_bands=False,
        equality_band_tol=None,
        ax=None,
        title="Feasible Region",
        legend=True,
    ):
        """
        Create the LP feasible region plot and return (fig, ax) for post-editing.

        Args:
            objective_coeffs: (c1, c2) for objective c1*x1 + c2*x2
            optimal_value: scalar Z value to plot objective level set c1*x1 + c2*x2 = Z
            show_constraints: draw constraint boundaries
            show_feasible_region: shade feasible region
            show_objective: draw objective level-set line if objective data provided
            show_equality_bands: if True, equality constraints also affect mask via thin tolerance band
            equality_band_tol: tolerance for equality in mask (default derived from grid spacing)
            ax: optional Matplotlib axis to draw on
            title: plot title
            legend: whether to show legend

        Returns:
            (fig, ax): Matplotlib figure and axis for further editing.
        """
        # Prepare axis
        if ax is None:
            fig, ax = plt.subplots(figsize=(8, 8))
        else:
            fig = ax.figure

        x_vals = np.linspace(self.x1_bounds[0], self.x1_bounds[1], self.grid_points)
        y_vals = np.linspace(self.x2_bounds[0], self.x2_bounds[1], self.grid_points)
        x1_grid, x2_grid = np.meshgrid(x_vals, y_vals)

        feasible_mask = np.ones_like(x1_grid, dtype=bool)

        # Tolerance band for equality mask if requested
        dx = (self.x1_bounds[1] - self.x1_bounds[0]) / max(self.grid_points - 1, 1)
        dy = (self.x2_bounds[1] - self.x2_bounds[0]) / max(self.grid_points - 1, 1)
        eq_tol = equality_band_tol if equality_band_tol is not None else max(dx, dy) * 1.25

        cmap = plt.get_cmap("tab10")
        used_labels = set()

        for i, (coef, c, eq_type) in enumerate(zip(self.coef_matrix, self.rhs, self.equality_types)):
            a, b = coef
            lhs = a * x1_grid + b * x2_grid

            # Feasible mask update
            if eq_type in ("<=", "<"):
                feasible_mask &= lhs <= c + self.tol
            elif eq_type in (">=", ">"):
                feasible_mask &= lhs >= c - self.tol
            elif eq_type in ("==", "="):
                # Usually equalities define boundaries (not areas).
                # Optional banding can be enabled for visualization.
                if show_equality_bands:
                    feasible_mask &= np.abs(lhs - c) <= eq_tol

            # Plot constraint boundary
            if show_constraints:
                color = cmap(i % 10)
                label = self._format_constraint_label(a, b, eq_type, c)
                label = label if label not in used_labels else None
                if label:
                    used_labels.add(label)

                # Degenerate: 0*x1 + 0*x2 = c
                if abs(a) <= self.tol and abs(b) <= self.tol:
                    # Skip plotting, but keep logical impact already handled
                    continue

                if abs(b) > self.tol:
                    y_line = self._constraint_line(a, b, c, x_vals)
                    ax.plot(x_vals, y_line, color=color, linewidth=2, label=label)
                else:
                    # Vertical line: x = c / a
                    x_const = c / a
                    ax.axvline(x=x_const, color=color, linewidth=2, label=label)

        # Plot feasible region mask
        if show_feasible_region:
            ax.imshow(
                feasible_mask.astype(float),
                extent=(
                    self.x1_bounds[0],
                    self.x1_bounds[1],
                    self.x2_bounds[0],  # correct y-min
                    self.x2_bounds[1],  # correct y-max
                ),
                origin="lower",
                cmap="Greens",
                alpha=0.30,
                interpolation="nearest",
                aspect="auto",
                zorder=0,
            )

        # Objective level set line
        if (
            show_objective
            and objective_coeffs is not None
            and optimal_value is not None
        ):
            c1, c2 = map(float, objective_coeffs)

            if abs(c1) <= self.tol and abs(c2) <= self.tol:
                pass  # Degenerate objective; nothing to draw
            elif abs(c2) > self.tol:
                y_obj = (float(optimal_value) - c1 * x_vals) / c2
                ax.plot(
                    x_vals,
                    y_obj,
                    "r--",
                    linewidth=2,
                    label=f"Objective level: Z = {optimal_value}",
                )
            else:
                x_obj = float(optimal_value) / c1
                ax.axvline(
                    x=x_obj,
                    color="r",
                    linestyle="--",
                    linewidth=2,
                    label=f"Objective level: Z = {optimal_value}",
                )

        # Styling
        ax.set_xlim(self.x1_bounds)
        ax.set_ylim(self.x2_bounds)
        ax.set_xlabel("$x_1$")
        ax.set_ylabel("$x_2$")
        ax.set_title(title)
        ax.grid(True, linestyle="--", alpha=0.6)

        if legend:
            ax.legend(loc="best", fontsize=9)

        fig.tight_layout()
        return fig, ax


# -------------------------------
# Example usage
# -------------------------------
if __name__ == "__main__":
    # Example LP:
    #  x1 + x2 <= 8
    #  x1 <= 6
    #  x2 <= 5
    #  x1 >= 0
    #  x2 >= 0
    A = [
        [1, 1],
        [1, 0],
        [0, 1],
        [1, 0],
        [0, 1],
    ]
    b = [8, 6, 5, 0, 0]
    eq = ["<=", "<=", "<=", ">=", ">="]

    plotter = LPFeasibleRegionPlotter(
        coef_matrix=A,
        rhs=b,
        equality_types=eq,
        x1_bounds=(0, 10),
        x2_bounds=(0, 10),
        grid_points=500,
    )

    fig, ax = plotter.plot(
        objective_coeffs=(3, 2),
        optimal_value=18,
        title="LP Feasible Region (Editable Figure)",
        legend=True,
    )

    # You can edit afterwards:
    ax.set_facecolor("#f8f8f8")
    ax.set_title("Customized Title")
    # fig.savefig("feasible_region.png", dpi=200)

def print_solution(Model, condition = None):
    # Loesning af modellen vha. PuLP's valg af Solver
    # Solve quietly
    print()
    Model.solve(PLP.PULP_CBC_CMD(msg = 0))
    # Model.solve()
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

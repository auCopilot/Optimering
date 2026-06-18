from operator import eq

import numpy as np

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
        self.coef_matrix = np.asarray(coef_matrix, dtype=float) if coef_matrix is not None else None
        self.rhs = np.asarray(rhs, dtype=float) if rhs is not None else None
        self.equality_types = list(equality_types) if equality_types is not None else None
        self.x1_bounds = tuple(x1_bounds)
        self.x2_bounds = tuple(x2_bounds)
        self.grid_points = int(grid_points)
        self.tol = float(tol)
        self.objective_coeffs = None
        self.objective_value = None




    def constraints_from_model(self, model):
        import pulp as PLP
        constraints = list(model.constraints.values())
        variables = model.variables()

        def format_sense(x):
            if x == 0:
                return "=="
            elif x == -1:
                return "<="
            elif x == 1:
                return ">="
            else:
                raise ValueError(f"Unknown constraint sense: {x}")

        coef_matrix = []
        rhs = []
        equality_types = []

        for constraint in constraints:
            rhs.append(-constraint.constant)
            equality_types.append(format_sense(constraint.sense))

            coef_matrix.append([
                constraint.expr.get(v, 0)
                for v in variables
            ])

        self.coef_matrix = np.array(coef_matrix)
        self.rhs = rhs
        self.equality_types = equality_types
        self.objective_coeffs = [model.objective.get(v, 0) for v in variables]
        model.solve()
        self.objective_value = PLP.value(model.objective)

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
        show = True
    ):
        import matplotlib.pyplot as plt
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
        self._validate_inputs()
        # Prepare axis
        if ax is None:
            fig, ax = plt.subplots(figsize=(8, 8))
        else:
            fig = ax.figure
        if objective_coeffs is None and self.objective_coeffs is not None:
            objective_coeffs = self.objective_coeffs
        if optimal_value is None and self.objective_value is not None:
            optimal_value = self.objective_value

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
        ax.set_xticks(range(int(self.x1_bounds[0]), int(self.x1_bounds[1]) + 1))
        ax.set_yticks(range(int(self.x2_bounds[0]), int(self.x2_bounds[1]) + 1))
        ax.grid(True)
        ax.set_xlim(self.x1_bounds)
        ax.set_ylim(self.x2_bounds)
        ax.set_xlabel("$x_1$")
        ax.set_ylabel("$x_2$")
        ax.set_title(title)
        ax.grid(True, linestyle="--", alpha=0.6)

        if legend:
            ax.legend(loc="best", fontsize=9)

        fig.tight_layout()
        if show:
            plt.show()
        return fig, ax
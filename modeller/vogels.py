def vogels_table(costs, supply, demand, active_rows=None, active_cols=None):
    """
    Create a Vogel Approximation tableau.

    Parameters
    ----------
    costs : list[list] or np.ndarray
        Cost matrix.
    supply : list
        Current remaining supply.
    demand : list
        Current remaining demand.
    active_rows : list[bool], optional
        Rows still active in the algorithm.
    active_cols : list[bool], optional
        Columns still active in the algorithm.

    Returns
    -------
    df : pd.DataFrame
    row_penalties : list
    col_penalties : list
    max_penalty : tuple
        ('row', i, penalty) or ('col', j, penalty)

In Vogel’s Approximation Method, an edge is selected iteratively and then assigned as much flow as possible.

The edge is chosen as the least-cost edge in a row or column for which the difference between the cheapest and the second-cheapest cost in that row or column is maximal.

The value (flow) assigned to the edge is the maximum possible amount, determined by the supplier’s remaining capacity and the customer’s remaining demand (i.e., the minimum of the two).

Since in each iteration either a remaining supply or a remaining demand is reduced to zero, there can be at most n+m−1 iterations in a balanced transportation problem.

According to the pseudocode, however, there are no further choices to make once only a single supplier or a single customer remains. This situation occurs after at most n+m−3 iterations.

    """
    import numpy as np
    import pandas as pd
    costs = np.array(costs)

    n, m = costs.shape

    if active_rows is None:
        active_rows = [True] * n

    if active_cols is None:
        active_cols = [True] * m

    def penalty(values):
        values = sorted(values)
        if len(values) >= 2:
            return values[1] - values[0]
        elif len(values) == 1:
            return values[0]
        return 0

    # Row penalties
    row_penalties = []
    for i in range(n):
        if not active_rows[i]:
            row_penalties.append(None)
            continue

        vals = [costs[i, j]
                for j in range(m)
                if active_cols[j]]

        row_penalties.append(penalty(vals))

    # Column penalties
    col_penalties = []
    for j in range(m):
        if not active_cols[j]:
            col_penalties.append(None)
            continue

        vals = [costs[i, j]
                for i in range(n)
                if active_rows[i]]

        col_penalties.append(penalty(vals))

    # Largest saving
    candidates = []

    for i, p in enumerate(row_penalties):
        if p is not None:
            candidates.append(("row", i, p))

    for j, p in enumerate(col_penalties):
        if p is not None:
            candidates.append(("col", j, p))

    max_penalty = max(candidates, key=lambda x: x[2])

    # Build table
    row_names = [f"Supply {i+1}" for i in range(n)]
    col_names = [f"Demand {j+1}" for j in range(m)]

    data = []

    for i in range(n):

        if active_rows[i]:
            row = [costs[i, j] if active_cols[j] else np.nan
                   for j in range(m)]
            row_supply = supply[i]
            row_penalty = row_penalties[i]
        else:
            row = [np.nan] * m
            row_supply = np.nan
            row_penalty = np.nan

        row.append(row_supply)
        row.append(row_penalty)

        data.append(row)


    columns = col_names + ["Supply", "delta"]

    df = pd.DataFrame(data,
                      index=row_names,
                      columns=columns)

    df.loc["Demand"] = [
                           demand[j] if active_cols[j] else np.nan
                           for j in range(m)
                       ] + ["", ""]

    df.loc["delta"] = [
                      col_penalties[j] if active_cols[j] else np.nan
                      for j in range(m)
                  ] + ["", ""]

    return df, row_penalties, col_penalties, max_penalty

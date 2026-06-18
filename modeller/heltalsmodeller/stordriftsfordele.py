
import pulp as PLP

def stordriftsfordele(model, new_objective, price_intervals, costs_of_interval):
    """

    :param model: ILP model from a class wrapper
    :param price_intervals: Should start at [0, a, b, M] where M is a very large number, i.e price remains the same.
    :param costs_of_interval: [0, c, d, e] Should contain zero for proper indexing
    :return: ILP model where stordriftsfordele is implemented by including the piecewise linear function as an
    constraint and objective.
    NOTE YOU HAVE TO ADD A CONSTRAINT ON THE SUPPLIER / COSTUMER IN QUESTION AFTER THIS FUNCTION IS CALLED.
    EXAMPLE FROM opg 1 Eks 2022:

    demands = [225, 125, 150, 325, 175]
    capacities = [400, 200, 300 , 100]
    cost_matrix = np.array([[3,6,6,7,7],
                            [2,9,4,9,4],
                            [8,8,3,1,7],
                            [5,4,8,5,2]])

    tpLarge = TransportProblem(cost_matrix, capacities, demands)
    from modeller.heltalsmodeller.stordriftsfordele import stordriftsfordele
    # price intervals:return: ILP model where stordriftsfordele is implemented by including the piecewise linear function as an
    #     constraint and objective
    price_intervals = [0, 100, 150, 225]
    # costs
    costs_of_interval = [0, 4, 3, 2]
    # Update objective to exclude the prices from factory 1 to costumer 1, since we will add this in the stordriftsfordele function
    new_obj =  PLP.lpSum(cost_matrix[i][j]*tpLarge.x[i][j] for i in tpLarge.supplier_range for j in tpLarge.demands_range  if i > 0 or j > 0)

    tpLarge, x_large = stordriftsfordele(tpLarge, new_obj, price_intervals, costs_of_interval)
    # Restrict factory 1 to send to costumer 1 by the amount given by the stordriftsfordele function
    tpLarge.model += tpLarge.x[0][0] == x_large
    """


    n = len(price_intervals)

    f_range = range(1, n)
    # fracton of demand that is sent on each line segment is introduced as a variable
    f = PLP.LpVariable.dict("f", f_range, cat=PLP.LpContinuous, lowBound=0, upBound=1)

    x_large = PLP.lpSum(f[j] * (price_intervals[j] - price_intervals[j - 1]) for j in f_range)
    # Slope, times interval length
    c = [0] + [(costs_of_interval[j]) * (price_intervals[j] - price_intervals[j-1])
                    for j in f_range]
    C = PLP.LpVariable("C", 0, None, PLP.LpContinuous)

    # Introduce the pricing to the objective
    model.model.objective = new_objective + C

    # We introduce delta variables to indicate if we are sending on line segment j
    delta_stor = PLP.LpVariable.dict("delta_stor", range(1, n + 1), cat=PLP.LpBinary)
    for j in f_range:
        # Indicates that the fraction is used
        model.model += f[j] <= delta_stor[j]
    for j in f_range[1:]:
        # Indicates that previous fraction must be used before we can use the next
        model.model += f[j - 1] >= delta_stor[j]

    # Add new cost constraint
    model.model += PLP.lpSum(c[j] * f[j] for j in f_range) == C

    return model, x_large
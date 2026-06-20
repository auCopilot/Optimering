import pulp as PLP

def knap_sack(weights, values, capacity, kp_type ="0-1"):
    """Knapsack problem formulation.

    Note, as subproblem in the cutting stock problem, we have the input
    correspondance:

    weights -> lengths of pieces
    values -> dual values from master problem
    capacity -> stock length """


    model = PLP.LpProblem(name="Knapsack", sense=PLP.LpMaximize)
    n = len(weights)
    if kp_type == "0-1":
        x = PLP.LpVariable.dicts("x",
                             range(n),
                             lowBound = 0,
                             upBound = 1,
                             cat = PLP.LpInteger)
    elif kp_type == "bounded":
        # Prompt user for integer upper bound, keep prompting until valid input is provided
        while    True:
            try:
                upper_bound = int(input("Enter an integer upper bound for the"
                                        " number of copies of"
                                        " each item (must be >= 1): "))
                if upper_bound < 1:
                    print("Please enter an integer greater than or equal to 1.")
                    continue
                break
            except ValueError:
                print("Invalid input. Please enter an integer.")

        x = PLP.LpVariable.dicts("x",
                                 range(n),
                                 lowBound = 0,
                                 upBound = upper_bound,
                                 cat = PLP.LpInteger)
    elif kp_type == "unbounded":

        x = PLP.LpVariable.dicts("x",
                             range(n),
                             lowBound = 0,
                             upBound = None,
                             cat = PLP.LpInteger)
    else:
        raise ValueError("Invalid knapsack type. Must be '0-1', 'bounded', or 'unbounded'.")


    model += PLP.lpSum(values[i] * x[i] for i in range(n)), "Objective"
    model += PLP.lpSum(weights[i] * x[i] for i in range(n)) <= capacity, "CapacityConstraint"
    return model, n
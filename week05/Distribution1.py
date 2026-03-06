import pulp as PLP
import numpy as np

"""This is a transshipment problem, we have two suppliers, 6 customers, 
and four distribution centers (DC). We wish to reformulate this as a standard 
transportation problem - to do so we must transform the distribution centers into
suppliers and customers, such that each new suppliers has full capacity and 
full demand and such that there is no cost of sending from a DC-customer to a 
DC-supplier """

""" Problem input """
# Let index 0,1 denote Liverpool and Brighton respectively
suppliers = ["Liverpool", "Brighton"]
supply = [150000, 200000]  # tons
distributors = ["Newcastle", "Birmingham", "London", "Exeter"]
throughput = [70000, 50000, 100000, 40000]
demand = [50000, 10000, 40000, 35000, 60000, 20000]
customers = [f"C{i + 1}" for i in range(len(demand))]

M = 1e99
distributor_costs = np.array([[0.5, M],
                              [0.5, 0.3],
                              [1.0, 0.5],
                              [0.2, 0.2]])
costs = np.array([
    [1.0, 2.0, M, 1.0, M, M],
    [M, M, 1.5, 0.5, 1.5, M],
    [1.5, M, 0.5, 0.5, 2.0, 0.2],
    [2.0, M, 1.5, 1.0, M, 1.5],
    [M, M, M, 0.5, 0.5, 0.5],
    [1.0, M, 1.0, M, 1.5, 1.5]
])


def define_transport_problem(costs, distributor_costs,
                             suppliers, supply,
                             customers, demand,
                             distributors=[], throughput=[]):
    """Redefine transshipment problem with distributors as both suppliers and
    customers.
    Inputs:
    costs: 2D numpy array of costs from suppliers to customers
    distributor_costs: 2D numpy array of costs from suppliers to distributors
    suppliers: list of supplier names
    supply: list of supply amounts for each supplier
    customers: list of customer names
    demand: list of demand amounts for each customer
    distributors: list of distributor names (optional)
    throughput: list of throughput amounts for each distributor (optional)

    Outputs generalized transportation problem"""


    if distributors == [] or throughput == []:
        print("Transportation problem without distributors")

    n_customer = len(customers)
    n_supplier = len(supply)
    n_distributor = len(throughput)

    # Assign distributors as both suppliers and customers, with supply and demand equal to throughput
    suppliers = suppliers + distributors
    customers = customers + distributors
    supply = supply + throughput
    demand = demand + throughput
    # Check if supply and demand are balanced, if not add dummy supplier or customer
    ss = sum(supply)
    sd = sum(demand)
    diff = ss - sd

    if diff == 0:
        print("Balanced supply and demand, no dummy needed.")

    elif diff > 0:
        print("Supply surplus, adding dummy customer")
        print("Supply surplus: ", diff)
        demand.append(diff)
        customers.append("SupplySurplusDummy")
        n_customer += 1

    elif diff < 0:
        print("Demand surplus, adding dummy supplier.")
        print("Demand surplus: ", -diff)
        supply.append(-diff)
        suppliers.append("DemandSurplusDummy")
        n_supplier += 1

    # Update ranges of suppliers and customers
    c_range = range(len(customers))
    s_range = range(len(suppliers))

    n, m = costs.shape
    k, l = distributor_costs.shape
    # Define new cost matrix with distributors as both suppliers and customers
    i = 0
    for row in distributor_costs:

        # Shipping from distributor to distributor is free,
        # If it is the same distributor.otherwise it is M.
        d = np.repeat(M, m - l)
        x = np.append(row, d)
        # Allow shipping from distributor to itself at zero cost, but not to other distributors.
        x[i + l] = 0
        costs = np.append(costs, [x], axis = 0)
        i += 1

    print(costs)
    # Modify cost matrix according to the surplus of supply or demand, if any.
    if diff > 0:
        # Add zero cost row to dummy costumer
        x = np.append(np.zeros(l), np.repeat(M,m - l))
        costs = np.vstack([costs, x])
    if diff < 0:
        # Add zero cost column to dummy supplier
        costs = np.hstack([costs, np.zeros((n + k, 1))])

    print("Defining Transportation problem with:")
    print(
        f"{n_supplier} suppliers, {n_distributor} distributors, {n_customer} customers")
    print("The suppliers are:", suppliers)
    print("The customers are:", customers)
    print("The distributors are:", distributors)
    return costs, suppliers, supply, customers, demand, s_range, c_range


costs, suppliers, supply, customers, demand, s_range, c_range = define_transport_problem(
    costs, distributor_costs,
    suppliers, supply,
    customers, demand,
    distributors, throughput)

# Cost minimization problem
model = PLP.LpProblem(name = "Distribution1", sense = PLP.LpMinimize)

# Decision variable x: How much to send from supplier s and distributor d to customer c
# customer supplier distributor connections
sd = PLP.LpVariable.dicts("Ship_To_From", (customers, suppliers), lowBound = 0)

# Objective function
cost_from_suppliers_to_customers = \
    PLP.lpSum(costs[i][j] * sd[customers[i]][suppliers[j]]
              for i in c_range
              for j in s_range)

model += (cost_from_suppliers_to_customers, "Objective")

# Continuity
# model += (PLP.lpSum(s[sup] for sup in suppliers) -
#          PLP.lpSum(c[cus] for cus in customers) == 0, "Continuity")
# We must ship from factories
for i in s_range:
    model += (PLP.lpSum(sd[customers[j]][suppliers[i]] for j in c_range) <=
              supply[i],
              f"Supply From Supplier {suppliers[i]} ")

for j in c_range:
    model += (PLP.lpSum(sd[customers[j]][suppliers[i]] for i in s_range) ==
              demand[j], f"Demand From Customer {customers[j]}")

from CustomFunctions import print_solution

print_solution(model, condition = lambda x: abs(x.varValue) >= 0.1)

# Print af dual information
print("Duale priser:")
for name, c in list(model.constraints.items()):
     print(name,":",c.pi)

""" We now add preferences to the model, such that customers prefer to receive
 from certain suppliers / distributors.
Keep in mind that even though the book says that costs are all set to zero, 
this is just really misleading. We still need to keep the costs in the 
model, so it will try and minimize the cost as a secondary objective, but we
will add a penalty term to the objective function, such that the model will
try to avoid sending from non-preferred suppliers / distributors."""
# Add preference for customers to receive from given supplier / distributor
preferences  = [("C1", "Liverpool"),
                ("C2", "Newcastle"),
                ("C3",),
                ("C4",),
                ("C5", "Birmingham"),
                ("C6", "Exeter", "London")
                ]
def indicator_function(customer, supplier, preferences):
    # Indicator function that returns 0 if the supplier is preferred by the customer, and 1 otherwise
    for pref in preferences:
        if customer == pref[0] and supplier in pref[1:]:
            return 0
    return 1

# Define distinct Penalty term
P = 1000  # Large penalty for non-preferred suppliers
preference_penalty = PLP.lpSum(
    sd[c][s] * indicator_function(c, s, preferences) * P
    for s in suppliers for c in customers
)

model.setObjective(cost_from_suppliers_to_customers + preference_penalty)

print_solution(model, condition = lambda x: abs(x.varValue) >= 0.1)

# Calculate the real financial price of the solution,
# by summing up the costs of the paths taken in the solution,
# without the preference penalty.
price = 0
for c in customers:
    for s in suppliers:
        # Use global cost matrix lookup
        idx_c = customers.index(c)
        idx_s = suppliers.index(s)
        path_cost = costs[idx_c][idx_s]

        flow = sd[c][s].varValue
        if flow and flow > 0:
            price += path_cost * flow
            # Optional: Check if preference was met
            was_preferred = (indicator_function(c, s, preferences) == 0)
            print(
                f"{c} <- {s} : {flow} (Cost: {path_cost}, Preferred: {was_preferred})")

print("Total Real Financial Price: ", price)
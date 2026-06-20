import numpy as np
import pulp as PLP

# Maximization problem
model = PLP.LpProblem(name="FoodManufacture1", sense=PLP.LpMaximize)

# Weight and volume constraint values
max_section_weight = [300, 450, 250]
max_section_volume = [2200, 2800, 1600]
max_supply = [1000, 800, 1250, 650] # ton
profits = [1400, 1800, 1600, 1250] # profit / ton
volumes_ton = [5, 7, 6, 4]
fraction_weight = [0.3, 0.45, 0.25]


# Indcies of variables
commodity_range = list(range(4))
section_range = list(range(3))

# Define commodity variables to track total aomout of commodities.
commodity = PLP.LpVariable.dicts("commodity", commodity_range, lowBound= 0)

# Define section commodity variables to track the amount of each commodity in each section.
# We need double indexings since each supplier can supply the different
# coomodities to different sections. Tracks Tons in each section, for each commodity.
section_commodity = PLP.LpVariable.dicts("section_commodity", (section_range, commodity_range), lowBound=0)

# Additional variables to track the total weight and volume of each section.
section_volume = PLP.LpVariable.dicts("section_volume", section_range, lowBound=0)

# Variable to track the total weight of the commodities.
total_weight = PLP.LpVariable("total_weight", lowBound=0)



# Define upper bounds on supply
for c in commodity:
    commodity[c].bounds(0, max_supply[c])
# Define upper bounds on volume
for s in section_range:
    section_volume[s].bounds(0, max_section_volume[s])

# Objective is to maximize profits
model += PLP.lpSum(profits[i]*commodity[i] for i in commodity_range), "Profit"

# Add the total to output
model += total_weight == PLP.lpSum(commodity[i] for i in commodity_range)

# Define weight distribution constraint
for s in section_range:
    # Fraction constraint
    model += (PLP.lpSum(section_commodity[s][i] for i in commodity_range) ==
              total_weight*fraction_weight[s],
              f"FractionConstraint{s}")
    # Defines the sectional volumes. Bounds are defined by the max_section_volume variable.
    model += (section_volume[s] ==
              PLP.lpSum(volumes_ton[i] * section_commodity[s][i]
                        for i in commodity_range),
              f"VolumeConstraint{s}")
    # Weight constraint, such that the sum of commodities in each section
    # cannot exceed the max weight of the section.
    model += (PLP.lpSum(section_commodity[s][i] for i in commodity_range) <=
              max_section_weight[s], f"WeightConstraint{s}")


# Continuity, make sure that the sum of commodities in each section equals to total amount.
# If not added, the model cannot determine how to distribute the commodities across sections
for i in commodity_range:
    model += commodity[i] == PLP.lpSum(section_commodity[s][i] for s in section_range)



from CustomFunctions import print_solution
print_solution(model)




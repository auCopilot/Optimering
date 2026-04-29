import pulp as PLP
import numpy as np

############################## Spm. 1) #######################################

"""
I denne opgave ønsker vi at placere gates således at det vægtede flow
minimeres. Da der ingen interaktion er mellem flyene kan dette modelleres som
et normal assignment problem.
"""
gates = "A B C D E".split()
distances = [150, 200, 250, 400, 500]
flows = [60, 50, 20 , 90, 40]
n = 5
cost_matrix = np.zeros((n,n))

for i in range(n):
    for j in range(n):
        cost_matrix[i][j] = distances[j] * flows[i]
print("Cost matrix:", cost_matrix)

from modeller.assignment_problem import AssignmentProblem
variable_dict = dict((i,gates[j]) for i in range(n) for j in range(n))
assignment_problem = AssignmentProblem(n,
                                       cost_matrix = cost_matrix,
                                       name ="GateAssignment")

# Rename according to gate names.
for i in assignment_problem.variable_range:
    for j in assignment_problem.variable_range:
        assignment_problem.x[i][j].name = f"x_{i}_{gates[j]}"
assignment_problem.solve()

################################ Spm. 2) ######################################

"""
Vi betragter nu en situation hvor kun kigger på inter-transit flow,
og ønsker at minimere det vægtede flow mellem gates. Dette er et QAP problem.
"""
from modeller.quadtratic_assignment_problem import QuadraticAssignmentProblem

distances = np.array([[0, 150, 200, 250, 400, 500],
                      [150, 0, 50, 100, 250, 350],
                      [200, 50, 0, 50, 300, 400],
                      [250, 100, 50, 0, 250, 350],
                      [400, 250, 300, 250, 0, 300],
                      [500, 350, 400, 350, 300, 0]])

flows = np.zeros((6, 6))

# upper triangle values
flows[0, 1:] = [60, 50, 20, 90, 40]
flows[1, 2:] = [10, 15, 2, 12]
flows[2, 3:] = [3, 20, 35]
flows[3, 4:] = [8, 11]
flows[4, 5:] = [9]

# make symmetric
flows = flows + flows.T

# Check symmetry
if all(distances[i][j] == distances[j][i] for i in range(n) for j in range(n)):
    print("Symmetric")
else:
    raise ValueError("Non-symmetric Matrix")

distances_no_gate = distances[1:,1:]
flows_no_gate = flows[1:,1:]



QAD_no_gate = QuadraticAssignmentProblem(n = n,
                                 flow_matrix = flows_no_gate,
                                 distance_matrix = distances_no_gate)


# Rename according to gate names.
for i in QAD_no_gate.variable_range:
    for j in QAD_no_gate.variable_range:
        QAD_no_gate.x[i][j].name = f"x_{i}_{gates[j]}"

QAD_no_gate.solve()

##################################### Spm. 3) ################################
"""
We now also consider the traffic from the planes to the gates. This constitutes
a mixed AP-QAP problem, where we edit the obejctive in the QAP, such that
the linear AP is also considered.
"""
# Standard QAD
QAD = QuadraticAssignmentProblem(n = n,
                                 flow_matrix = flows_no_gate,
                                 distance_matrix= distances_no_gate)
# Update the obejctive
QAD.model.objective = QAD.model.objective + PLP.lpSum(QAD.x[i][j]*
                                                      cost_matrix[i][j]
                                                      for i in range(n)
                                                      for j in range(n))


# Rename according to gate names.
for i in QAD.variable_range:
    for j in QAD.variable_range:
        QAD.x[i][j].name = f"x_{i+1}_{gates[j]}"
print("QAP-AP")
QAD.solve()

print("QAP with dummy plane, forced to index 0")
n = n + 1
QAD = QuadraticAssignmentProblem(n = n,
                                 flow_matrix = flows,
                                 distance_matrix = distances)
# Zeroth index is a dummy plane. We must make the location of this plane fixed.
# Dummy plane is fixed to first gate, so we add the constraint that x[0][0] = 1
QAD.model += QAD.x[0][0] == 1, "DummyPlaneConstraint"
# Rename according to gate names.
gates = ["IU"] + gates
for i in QAD.variable_range:
    for j in QAD.variable_range:
        QAD.x[i][j].name = f"x_{i}_{gates[j]}"
QAD.solve()


from modeller.heltalsmodeller.quadtratic_assignment_problem import QuadraticAssignmentProblem
import numpy as np
import pulp as PLP
# We have n = 5 factories and only 3 location, however, we can still solve the problem by letting locations have more
# than one factory.
m = 5  # (A, B, C, D, E)
M = 10**6
flow_matrix = np.zeros((5,5))
flow_matrix[0,1:] = [0.0, 1.0, 1.5, 0.0]
flow_matrix[1,2:] = [1.4, 1.2, 0.0]
flow_matrix[2,3:] = [0.0, 2.0]
flow_matrix[3,4:] = [0.7]

flow_matrix = (flow_matrix + flow_matrix.T) * 1000
print(flow_matrix)

dist_matrix = np.zeros((3,3))
dist_matrix[0,:] = [5, 14, 13]
dist_matrix[1,1:] = [5, 9]
dist_matrix[2,2:] = [10]
dist_matrix[:,0] = dist_matrix[0,:]
dist_matrix[:,1] = dist_matrix[1,:]
print(dist_matrix)
n = 3
factory_range = range(m)
location_range = range(n)

QAP = QuadraticAssignmentProblem(factory_range, location_range, flow_matrix, dist_matrix, max_capacities= [3] * n)
QAP.construct_model()
# Relocation savings
S = np.array([[10,15,10,20,5], # Bristol
              [10,20,15,15,15],# Brighton
              [0, 0, 0, 0, 0]]).T * 1000 # London
# Modify objective
QAP.model.objective = QAP.model.objective - PLP.lpSum(QAP.x[i][j]*S[i][j] for i in factory_range for j in location_range)
QAP.construct_constraints()

QAP.solve(quiet=False)

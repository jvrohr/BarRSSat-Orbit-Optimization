#!/bin/python3

import os, sys
from simulation import *

opt = Optimize()

# print(simulation.ObjectiveFunction([6900, 78, 45]))
opt.Optimize([6920, 45, 180], ((6871, 6971), (10, 80), (0, 360)))

# result = []
# for a in range(6871, 6971, 5):
#     aux1 = []
#     for i in range(30, 89, 5):
#         aux2 = []
#         for raan in range(0, 360, 10):
#             aux2.append(simulation.ObjectiveFunction([a, i, raan]))
#         aux1.append(aux2)
#     result.append(aux1)
# print(result)
#!/bin/python3

import os, sys
from simulation import *

# Get the directory of the currently executing script
currentDir = os.path.dirname(os.path.abspath(sys.argv[0]))

configurationDict = {
    "SMA": 7000.0, # varia
    "ECC": 0.0, 
    "INC": 78.0, # varia
    "RAAN": 45.0, # varia
    "AOP": 90.0, # fixo
    "DragArea": 0.01, 
    "SRPArea": 0.01, 
    "Cd": 2.0, 
    "DryMass": 3.3, 
    "Cr": 1.75,
    "ContactLocatorFilename": f"'BarRSSatOUTPUT.txt'",
    "ElapsedDays": 7
}

simulation = Simulate(currentDir + "/BarRSSat.script", configurationDict)

# print(simulation.ObjectiveFunction([6900, 78, 45]))
simulation.Optimize([6900, 78, 45], ((6871, 6971), (1, 80), (0, 360)))
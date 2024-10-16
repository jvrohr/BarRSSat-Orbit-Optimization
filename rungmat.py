#!/bin/python3

from typing import *
from load_gmat import *
import os, sys
from datetime import datetime

# Get the directory of the currently executing script
currentDir = os.path.dirname(os.path.abspath(sys.argv[0]))
GMATPATH = new_path = os.path.join(currentDir, 'GMAT', 'R2022a')

class Simulate:
    def __init__(self, sourceScriptPath, configurationDict):
        self.sourceScriptPath = sourceScriptPath
        self.resultScriptPath = sourceScriptPath.replace(".script", "test.script")
        self.configurationDict =  configurationDict

        self.ReplaceWordsInScript()

    def ReplaceWordsInScript(self):
        with open(self.sourceScriptPath, 'r') as file:
            content = file.read()

        for key, value in self.configurationDict.items():
            content = content.replace("$" + key + "$", str(value))

        with open(self.resultScriptPath, 'w') as file:
            file.write(content)

    def RunScript(self):
        gmat.LoadScript(self.resultScriptPath)
        if gmat.RunScript():
            print("[INFO] Script run OK")
            gmat.Clear()
        else:
            print("[INFO] Script run NOT OK")
        os.remove(self.resultScriptPath)

    def ConvertDatetime(self, stringDate):
        return datetime.strptime(stringDate, "%d %b %Y %H:%M:%S.%f")

    def CalculateMin(self, runDict):
        minDurationDict = {}
        for groundStation in runDict.keys():
            minAux = 10000000
            for value in runDict[groundStation].values():
                if value < minAux:
                    minAux = value
            minDurationDict[groundStation] = minAux
        
        return minDurationDict

x = sys.argv[1:]

configurationDict = {
    "SMA": x[0],
    "ECC": 0.0, 
    "INC": x[1],
    "RAAN": x[2],
    "AOP": 90.0,
    "DragArea": 0.01, 
    "SRPArea": 0.01, 
    "Cd": 2.0, 
    "DryMass": 3.3, 
    "Cr": 1.75,
    "ContactLocatorFilename": f"'BarRSSatOUTPUT.txt'",
    "ElapsedDays": 7
}

simulation = Simulate(currentDir + "/BarRSSat.script", configurationDict)
simulation.ReplaceWordsInScript()
simulation.RunScript()
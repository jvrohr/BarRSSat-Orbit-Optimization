#!/bin/python3

from typing import *
from load_gmat import *
import os
import sys
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np

# Get the directory of the currently executing script
currentDir = os.path.dirname(os.path.abspath(sys.argv[0]))
outputFilename = "BarRSSatOUTPUT.txt"

GMATPATH = new_path = os.path.join(currentDir, 'GMAT', 'R2022a')

class Simulate:
    def __init__(self, sourceScriptPath, configurationDict):
        self.sourceScriptPath = sourceScriptPath
        self.resultScriptPath = sourceScriptPath.replace(".script", "test.script")
        self.configurationDict =  configurationDict

        self.ReplaceWordsInScript()

    def SetConfiguration(self, configurationDict):
        self.configurationDict = configurationDict
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
        print(gmat.RunScript())
        os.remove(self.resultScriptPath)

# Function to process the text file
def ProcessFile(file_path):
    resultDict = {}
    
    with open(file_path, 'r') as file:
        data = file.read()

    reportSections = data.split("\n\n")
    # Cleaning number of events and top header
    reportSections = [elem for elem in reportSections if "Observer" in elem]
    for section in reportSections:
        lines = section.split("\n")
        lines = [line for line in lines if line != '']
        groundStationName = lines[0].split(" ")[1]
        lines = lines[2::]

        auxiliaryDict = {}
        for line in lines:
            values = line.split("    ")
            auxiliaryDict[values[0]] = float(values[2])

        resultDict[groundStationName] = auxiliaryDict

    return resultDict

def ConvertDatetime(stringDate):
    return datetime.strptime(stringDate, "%d %b %Y %H:%M:%S.%f")

def CalculateMin(runDict):
    # para cada groundstation pegar o mínimo valor
    minDurationDict = {}
    for groundStation in runDict.keys():
        minAux = 10000000
        for value in runDict[groundStation].values():
            if value < minAux:
                minAux = value
        minDurationDict[groundStation] = minAux
    
    return minDurationDict

def CalculateDictAverage(inputDict):
    return np.mean(list(inputDict.values()))

configurationDict = {
    "SMA": 7000.0, 
    "ECC": 0.05, 
    "INC": 78.0, 
    "RAAN": 45.0,
    "AOP": 90.0,
    "DragArea": 0.01, 
    "SRPArea": 0.01, 
    "Cd": 2.0, 
    "DryMass": 3.0, 
    "Cr": 1.75,
    "ContactLocatorFilename": f"'{outputFilename}'",
    "ElapsedDays": 1
}

scriptFilename = "BarRSSat.script"

simulation = Simulate(currentDir + "/" + scriptFilename, configurationDict)

simulation.RunScript()

contactDict = ProcessFile(GMATPATH + "/output/" + outputFilename)

print(CalculateDictAverage(CalculateMin(contactDict)))
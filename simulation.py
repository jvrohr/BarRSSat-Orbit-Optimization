from typing import *
from load_gmat import *
import os, sys
from datetime import datetime
import numpy as np
import scipy.optimize as opt

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
        else:
            print("[INFO] Script run NOT OK")
        os.remove(self.resultScriptPath)

    # Method to process the text file
    def ProcessFile(self, filePath):
        resultDict = {}
        
        with open(filePath, 'r') as file:
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

    def CalculateAverage(self, runDict):
        accumulation = []
        for groundStation in runDict.keys():
            accumulation.append(self.CalculateDictAverage(runDict[groundStation]))
        return np.mean(accumulation)

    def CalculateDictAverage(self, inputDict):
        return np.mean(list(inputDict.values()))
    
    def CleanFiles(self, path):
        # Check if the directory exists
        if os.path.exists(path):
            # Loop through all the files in the given directory
            for fileName in os.listdir(path):
                filePath = os.path.join(path, fileName)
                try:
                    # If it's a file, remove it
                    if os.path.isfile(filePath) or os.path.islink(filePath):
                        os.unlink(filePath)
                except Exception as e:
                    print(f"Failed to delete {filePath}. Reason: {e}")
        else:
            print("Directory does not exist")

    def PrintCurrentStatus(self, x, average):
        print(f"[INFO] a = {x[0]}, i = {x[1]}, RAAN = {x[2]}, average = {average}")
        
    def ObjectiveFunction(self, x):
        self.configurationDict["SMA"] = x[0]
        self.configurationDict["INC"] = x[1]
        self.configurationDict["RAAN"] = x[2]
        self.ReplaceWordsInScript()

        self.RunScript()
        self.contactDict = self.ProcessFile(GMATPATH + "/output/" + 
                                            self.configurationDict["ContactLocatorFilename"].
                                            replace("'", ""))
        self.CleanFiles(GMATPATH + "/output/")

        average = self.CalculateAverage(self.contactDict)
        self.PrintCurrentStatus(x, average)

        return -average

    def Optimize(self, initialValues: List[float], bounds: Tuple[Tuple[float]]):
        result = opt.minimize(self.ObjectiveFunction, initialValues, bounds=bounds, options={"disp":True})

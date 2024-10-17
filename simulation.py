from typing import *
from load_gmat import *
import os, sys
import numpy as np
import scipy.optimize as opt

# Get the directory of the currently executing script
currentDir = os.path.dirname(os.path.abspath(sys.argv[0]))
GMATPATH = new_path = os.path.join(currentDir, 'GMAT', 'R2022a')

class Optimize:
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
        print(f"[INFO] e = {x[0]}, w = {x[1]}, average = {average}")
        
    def ObjectiveFunction(self, x):
        os.system(f'./rungmat.py --ECC {x[0]} --AOP {x[1]}')

        self.contactDict = self.ProcessFile(GMATPATH + "/output/" + 
                                            "BarRSSatOUTPUT.txt")
        self.CleanFiles(GMATPATH + "/output/")

        average = self.CalculateAverage(self.contactDict)
        average = -average if not np.isnan(average) else 0
        self.PrintCurrentStatus(x, -average)

        return average

    def Optimize(self, initialValues: List[float], bounds: Tuple[Tuple[float]]):
        result = opt.differential_evolution(self.ObjectiveFunction, bounds=bounds, disp=True, popsize=10)

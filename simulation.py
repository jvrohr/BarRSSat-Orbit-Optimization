from typing import *
from load_gmat import *
import os, sys
import numpy as np
import scipy.optimize as opt
from datetime import datetime

## Arguments parsing
ElapsedDays = 7

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

    def RunGMAT(self, x):
        os.system(f'./rungmat.py --ECC {x[0]} --AOP {x[1]}')

        self.contactDict = self.ProcessFile(GMATPATH + "/output/" + 
                                            "BarRSSatOUTPUT.txt")
        self.CleanFiles(GMATPATH + "/output/")

    def ObjectiveFunction(self, x):
        ## Constraint gets ran first, so the contactDict gets set there and used here
        print("HERE")

        average = self.CalculateAverage(self.contactDict)
        average = -average if not np.isnan(average) else 0
        self.PrintCurrentStatus(x, -average)

        return average
    
    def ConvertDatetime(self, stringDate):
        return datetime.strptime(stringDate, "%d %b %Y %H:%M:%S.%f")

    def EverydayConstraint(self, x):
        self.RunGMAT(x)
        print(f"[INFO] e = {x[0]}, w = {x[1]}")

        for station in self.contactDict.keys():
            listDatetimeContacts = list(self.contactDict[station].keys())
            listDayContacts = [self.ConvertDatetime(strDate).day for strDate in listDatetimeContacts]
            numberDays = len(set(listDayContacts))
            if numberDays != ElapsedDays:
                print("[INFO] Contact NOT detected everyday")
                return ElapsedDays - numberDays
        print("[INFO] Contact detected everyday")
        return 0

    def Optimize(self, bounds: Tuple[Tuple[float]]):
        constraint = opt.NonlinearConstraint(self.EverydayConstraint, 0, 0, keep_feasible=True)
        result = opt.differential_evolution(self.ObjectiveFunction, bounds=bounds, constraints=[constraint], disp=True, polish=False, popsize=10)
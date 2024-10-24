from typing import *
import os, sys, json, arguments
import numpy as np
import scipy.optimize as opt
from datetime import datetime

## Argument parser
parser = arguments.CreateParser(description="Python Script to run optimization of the BarRSSat orbit.")
args = parser.parse_args()

# Get the directory of the currently executing script
currentDir = os.path.dirname(os.path.abspath(sys.argv[0]))
GMATPATH = os.path.join(currentDir, 'GMAT', 'R2022a')

class Optimize:
    def __init__(self, optimizationVariables, optimizationRanges):
        self.optimizationVariables = optimizationVariables
        self.optimizationRanges = optimizationRanges
        self.simulationResults = {}
    
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

    def CalculateDurationAverage(self, runDict):
        accumulation = []
        for groundStation in runDict.keys():
            listValues = list(runDict[groundStation].values())
            accumulation.append(np.mean(listValues))
        return np.mean(accumulation)

    def CalculateDailyAverage(self, runDict):
        totalResults = []
        for station in runDict.keys():
            listDayContacts = [self.ConvertDatetime(strDate).day for strDate in list(runDict[station].keys())]
            # get only unique values
            listDayContacts = list(set(listDayContacts))

            index = 0
            stationResult = [0]
            for contact in runDict[station].keys():
                ## if day in runDict is on the current index day, add to result in the right bin 
                if(self.ConvertDatetime(contact).day == listDayContacts[index]):
                    stationResult[index] = stationResult[index] + runDict[station][contact]
                else: ## otherwise append the new index relative to the new day
                    stationResult.append(0)
                    index = index + 1
            
            totalResults.append(np.mean(stationResult))
        return np.mean(totalResults)
    
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

    def PrintCurrentStatus(self, x):
        string = f"[INFO] "
        for i, var in enumerate(self.optimizationVariables):
            string = string + var + f" = {x[i]} "
        print(string)

    def RunGMAT(self, x):
        ## Running GMAT with terminal command
        cmdString = f'./rungmat.py'
        for i, var in enumerate(self.optimizationVariables):
            cmdString = cmdString + f" --{var} {x[i]}"
        ### add fixed options
        cmdString = cmdString + f"{' '.join(sys.argv[1:])}"
        os.system(cmdString)

        ## Get contact duration dictionary
        self.contactDict = self.ProcessFile(GMATPATH + "/output/" + 
                                            "BarRSSatOUTPUT.txt")
        self.CleanFiles(GMATPATH + "/output/")

        ## Calculate average and store result for combination of variables
        durationAverage = self.CalculateDurationAverage(self.contactDict)
        dailyAverage = self.CalculateDailyAverage(self.contactDict)
        self.simulationResults[str(x)] = {
            "durationAverage": durationAverage,
            "dailyAverage": dailyAverage
            }

    def ObjectiveFunction(self, x, *args):
        if not args:
            outputVariable = "dailyAverage"
        else:
            outputVariable = args[0]

        ## Constraint gets ran first, so the contactDict gets set there and used here
        print("[INFO] Objective Function")
        self.PrintCurrentStatus(x)
        try:
            output = self.simulationResults[str(x)][outputVariable]
        except:
            self.RunGMAT(x)

        print(f"[INFO] {outputVariable} = {output}")

        return -output if not np.isnan(output) else 0
    
    def ConvertDatetime(self, stringDate):
        return datetime.strptime(stringDate, "%d %b %Y %H:%M:%S.%f")

    def EverydayConstraint(self, x):
        print("[INFO] Running Constraint Function")
        self.PrintCurrentStatus(x)
        self.RunGMAT(x)

        for station in self.contactDict.keys():
            listDatetimeContacts = list(self.contactDict[station].keys())
            listDayContacts = [self.ConvertDatetime(strDate).day for strDate in listDatetimeContacts]
            numberDays = len(set(listDayContacts))
            
            if numberDays != args.ElapsedDays:
                print("[INFO] Contact NOT detected everyday")
                self.simulationResults[str(x)]["constraintMet"] = False
                return args.ElapsedDays - numberDays
        
        print("[INFO] Contact detected everyday")
        self.simulationResults[str(x)]["constraintMet"] = True

        return 0

    def Optimize(self):
        constraint = opt.NonlinearConstraint(self.EverydayConstraint, 0, 0)
        result = opt.differential_evolution(self.ObjectiveFunction, bounds=self.optimizationRanges, constraints=[constraint], disp=True, polish=False, popsize=10)
        if result.success:
            print("The converged solution is: " + str(result.x))
        
        ## Save the simulation results dictionary into a json file
        with open('simulationResultsDictionary.json', 'w') as file:
            json.dump(self.simulationResults, file)

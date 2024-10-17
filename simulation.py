from typing import *
from load_gmat import *
import os, sys, argparse
import numpy as np
import scipy.optimize as opt
from datetime import datetime

## Argument parser
parser = argparse.ArgumentParser(description="Python Script to run optimization of the BarRSSat orbit.")

parser.add_argument('--SMA', type=float, default=7000, help='Semi-major axis [km].')
parser.add_argument('--ECC', type=float, default=0.0, help='Excentricity [-].')
parser.add_argument('--INC', type=float, default=45.0, help='Inclination [degrees].')
parser.add_argument('--RAAN', type=float, default=0.0, help='Right Ascension of the Ascending Node [degrees].')
parser.add_argument('--AOP', type=float, default=0.0, help='Argument of Periapsis [degrees].')
parser.add_argument('--DragArea', type=float, default=0.01, help='Transversal area for drag model [m^2].')
parser.add_argument('--SRPArea', type=float, default=0.01, help='Transversal area for Solar Radiation Pressure model [m^2].')
parser.add_argument('--Cd', type=float, default=2.0, help='Drag coefficient [-].')
parser.add_argument('--DryMass', type=float, default=3.3, help='Dry mass [kg].')
parser.add_argument('--Cr', type=float, default=1.75, help='Reflectivity coefficient [-].')
parser.add_argument('--ElapsedDays', type=float, default=7, help='Number of days to conduct simulation [days].')

parser.add_argument('--sourceScript', type=str, default="BarRSSat.script", help='Source Script used to substitute orbital elements arguments in.')
parser.add_argument('--outputFilename', type=str, default="BarRSSatOUTPUT.txt", help='Name of the temporary output file name for the gmat contact locator report.')
parser.add_argument('--keepScript', action='store_true', help='Wether or not to keep the generated SCRIPT file after the run.')

args = parser.parse_args()

# Get the directory of the currently executing script
currentDir = os.path.dirname(os.path.abspath(sys.argv[0]))
GMATPATH = new_path = os.path.join(currentDir, 'GMAT', 'R2022a')

class Optimize:
    def __init__(self, optimizationVariables, optimizationRanges):
        self.optimizationVariables = optimizationVariables
        self.optimizationRanges =optimizationRanges
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
        os.system(cmdString)

        ## Get contact duration dictionary
        self.contactDict = self.ProcessFile(GMATPATH + "/output/" + 
                                            "BarRSSatOUTPUT.txt")
        self.CleanFiles(GMATPATH + "/output/")

        ## Calculate average and store result for combination of variables
        average = self.CalculateAverage(self.contactDict)
        self.simulationResults[str(x)] = {"average": average}

    def ObjectiveFunction(self, x):
        ## Constraint gets ran first, so the contactDict gets set there and used here
        print("[INFO] Objective Function")
        self.PrintCurrentStatus()
        try:
            average = self.simulationResults[str(x)]["average"]
        except:
            self.RunGMAT(x)

        print(f"[INFO] Average = {average}")
        average = -average if not np.isnan(average) else 0

        return average
    
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
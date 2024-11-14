#!/bin/python3.10

from typing import *
from load_gmat import *
import os, sys, arguments

## Argument parser
parser = arguments.CreateParser(description="Python Script to run GMAT orbit simulations varying orbital elements for the BarRSSat mission, by substitution of variables in a GMAT script file.")
args = parser.parse_args()

# Get the directory of the currently executing script
currentDir = os.path.dirname(os.path.abspath(sys.argv[0]))

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
        if not args.keepScript:
            os.remove(self.resultScriptPath)


configurationDict = {
    "SMA": args.SMA,
    "ECC": args.ECC,
    "INC": args.INC,
    "RAAN": args.RAAN,
    "AOP": args.AOP,
    "DragArea": args.DragArea, 
    "SRPArea": args.SRPArea, 
    "Cd": args.Cd, 
    "DryMass": args.DryMass, 
    "Cr": args.Cr,
    "ContactLocatorFilename": f"'{args.outputFilename}'",
    "ElapsedDays": args.ElapsedDays
}

simulation = Simulate(os.path.join(currentDir, args.sourceScript), configurationDict)
simulation.ReplaceWordsInScript()
simulation.RunScript()
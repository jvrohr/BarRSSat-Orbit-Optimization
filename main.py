#!/bin/python3

from typing import *
from load_gmat import *
import os
import sys

# Get the directory of the currently executing script
current_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

GMATPATH = new_path = os.path.join(current_dir, 'GMAT', 'R2022a')

class GmatFunctions:
    def __init__(self, dragArea, srpArea, cD, dryMass, cR):
        self.dragArea = dragArea
        self.srpArea = srpArea
        self.cD = cD
        self.dryMass = dryMass
        self.cR = cR

    def objectiveFunction(self, variables: List[float]):
        a, e, i, RAAN, w = variables

        self.SetupGmat(a, e, i, RAAN, w)
        reports = self.runGmat()

    def SetupGmat(self, a, e, i, RAAN, w):
        # Spacecraft configuration preliminaries
        earthorb = gmat.Construct("Spacecraft", "BarRSSat")

        # Date and Coordinate System
        earthorb.SetField("DateFormat", "UTCGregorian")
        earthorb.SetField("Epoch", "12 Oct 2026 12:00:00.000")
        earthorb.SetField("CoordinateSystem", "EarthMJ2000Eq")
        earthorb.SetField("DisplayStateType", "Keplerian")

        # Orbital Elements
        earthorb.SetField("SMA", a)
        earthorb.SetField("ECC", e)
        earthorb.SetField("INC", i)
        earthorb.SetField("RAAN", RAAN)
        earthorb.SetField("AOP", w)
        earthorb.SetField("TA", 0)

        # Spacecraft ballistic properties for the SRP and Drag models
        earthorb.SetField("SRPArea", self.srpArea)
        earthorb.SetField("Cr", self.cR)
        earthorb.SetField("DragArea", self.dragArea)
        earthorb.SetField("Cd", self.cD)
        earthorb.SetField("DryMass", self.dryMass)

        # Force model settings
        fm = gmat.Construct("ForceModel", "FM")
        fm.SetField("CentralBody", "Earth")
        # An 8x8 JGM-3 Gravity Model
        earthgrav = gmat.Construct("GravityField")
        earthgrav.SetField("BodyName","Earth")
        earthgrav.SetField("PotentialFile", GMATPATH + "/data/gravity/earth/JGM3.cof")
        earthgrav.SetField("Degree",8)
        earthgrav.SetField("Order",8)
        fm.AddForce(earthgrav)
        # The Point Masses
        moongrav = gmat.Construct("PointMassForce")
        moongrav.SetField("BodyName","Luna")
        sungrav = gmat.Construct("PointMassForce")
        sungrav.SetField("BodyName","Sun")
        # Drag using Jacchia-Roberts
        jrdrag = gmat.Construct("DragForce")
        jrdrag.SetField("AtmosphereModel","JacchiaRoberts")
        # Build and set the atmosphere for the model
        atmos = gmat.Construct("JacchiaRoberts")
        jrdrag.SetReference(atmos)
        # Add all of the forces into the ODEModel container
        fm.AddForce(moongrav)
        fm.AddForce(sungrav)
        fm.AddForce(jrdrag)

        # Connecting the spacecraft
        psm = gmat.PropagationStateManager()
        psm.SetObject(earthorb)
        psm.BuildState()
        fm.SetPropStateManager(psm)
        fm.SetState(psm.GetState())

        # Assemble all of the objects together
        gmat.Initialize()

        # Finish force model setup:
        ## Map spacecraft state into the model
        fm.BuildModelFromMap()
        ## Load physical parameters needed for the forces
        fm.UpdateInitialData()

        # # Now access state and get derivative data
        # pstate = earthorb.GetState().GetState()
        # print("State Vector: ", pstate)

        # fm.GetDerivatives(pstate)
        # dv = fm.GetDerivativeArray()
        # print("Derivative: ", dv)

        # vec = fm.GetDerivativesForSpacecraft(earthorb)
        # print("SCDerivative: ", vec)

funcs = GmatFunctions(0.01, 0.01, 2, 3, 1.75)
funcs.SetupGmat(7000, 0.05, 78, 45, 90)
gmat.ShowObjects()

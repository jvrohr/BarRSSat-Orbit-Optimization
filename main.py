#!/bin/python3

from typing import *
from load_gmat import *
import os
import sys
import matplotlib.pyplot as plt

# Get the directory of the currently executing script
current_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

GMATPATH = new_path = os.path.join(current_dir, 'GMAT', 'R2022a')

class GmatFunctions:
    def __init__(self, dragArea, srpArea, cD, dryMass, cR):
        # Create spacecraft
        self.spacecraft = self.SetupSpacecraft(dragArea, srpArea, cD, dryMass, cR)

        # Date and Coordinate System
        self.SetupCoordinates()

        # Force model settings
        self.forceModel = self.SetupForceModel()

        # Assemble all of the objects together
        gmat.Initialize()

        # Numerical Propagator
        self.SetupPropagator()

        ## Setup the spacecraft that is propagated
        self.pdPropagator.AddPropObject(self.spacecraft)
        ## Concludes configuration of the internal models, including force model
        self.pdPropagator.PrepareInternals()

        ## Refresh the 'gator and force model reference
        self.gator = self.pdPropagator.GetPropagator()
        self.forceModel = self.pdPropagator.GetODEModel()

    def SetupSpacecraft(self, dragArea, srpArea, cD, dryMass, cR):
        spacecraft = gmat.Construct("Spacecraft", "BarRSSat")
        # Spacecraft ballistic properties for the SRP and Drag models
        spacecraft.SetField("DragArea", dragArea)
        spacecraft.SetField("SRPArea", srpArea)
        spacecraft.SetField("Cd", cD)
        spacecraft.SetField("DryMass", dryMass)
        spacecraft.SetField("Cr", cR)

        return spacecraft

    def SetupPropagator(self):
        self.pdPropagator = gmat.Construct("Propagator","PDProp")

        ## Create and assign a numerical integrator for use in the propagation
        gator = gmat.Construct("PrinceDormand78")
        self.pdPropagator.SetReference(gator)
        self.pdPropagator.SetReference(self.forceModel)

        ## Set some of the fields for the integration
        self.pdPropagator.SetField("InitialStepSize", 30.0)
        self.pdPropagator.SetField("Accuracy", 1.0e-12)
        self.pdPropagator.SetField("MinStep", 1e-5)
        self.pdPropagator.SetField("MaxStep", 1e2)

        ## Update propagator
        self.UpdatePropagator()

    def UpdatePropagator(self):
        ## Setup the spacecraft that is propagated
        self.pdPropagator.AddPropObject(self.spacecraft)
        ## Concludes configuration of the internal models, including force model
        self.pdPropagator.PrepareInternals()

    def SetupCoordinates(self, date = "12 Oct 2026 12:00:00.000", dateFormat = "UTCGregorian",
                          coordinates = "EarthMJ2000Eq", variables = "Keplerian"):
        self.spacecraft.SetField("DateFormat", dateFormat)
        self.spacecraft.SetField("Epoch", date)
        self.spacecraft.SetField("CoordinateSystem", coordinates)
        self.spacecraft.SetField("DisplayStateType", variables)

    def SetupForceModel(self):
        # Force model settings
        forceModel = gmat.Construct("ForceModel", "FM")
        forceModel.SetField("CentralBody", "Earth")
        # An 8x8 JGM-3 Gravity Model
        earthGravity = gmat.Construct("GravityField")
        earthGravity.SetField("BodyName","Earth")
        earthGravity.SetField("PotentialFile", GMATPATH + "/data/gravity/earth/JGM3.cof")
        earthGravity.SetField("Degree", 8)
        earthGravity.SetField("Order", 8)
        forceModel.AddForce(earthGravity)
        # The Point Masses
        moonGravity = gmat.Construct("PointMassForce")
        moonGravity.SetField("BodyName", "Luna")
        sunGravity = gmat.Construct("PointMassForce")
        sunGravity.SetField("BodyName", "Sun")
        # Drag using Jacchia-Roberts
        jacchiaDrag = gmat.Construct("DragForce")
        jacchiaDrag.SetField("AtmosphereModel", "JacchiaRoberts")
        # Build and set the atmosphere for the model
        atmosphere = gmat.Construct("JacchiaRoberts")
        jacchiaDrag.SetReference(atmosphere)
        # Add all of the forces into the ODEModel container
        forceModel.AddForce(moonGravity)
        forceModel.AddForce(sunGravity)
        forceModel.AddForce(jacchiaDrag)

        return forceModel

    def objectiveFunction(self, variables: List[float]):
        a, e, i, RAAN, w = variables

        self.SetupGmat(a, e, i, RAAN, w)
        reports = self.runGmat()

    def SetupOrbitalElements(self, a, e, i, RAAN, w):
        # Orbital Elements
        self.spacecraft.SetField("SMA", a)
        self.spacecraft.SetField("ECC", e)
        self.spacecraft.SetField("INC", i)
        self.spacecraft.SetField("RAAN", RAAN)
        self.spacecraft.SetField("AOP", w)
        self.spacecraft.SetField("TA", 0)

        self.UpdatePropagator()

    def PrintPropagation(self):
        # Take a 60 second step, showing the state before and after, and start buffering
        # Buffers for the data
        time = []
        pos = []
        vel = []
        gatorstate = self.gator.GetState()
        t = 0.0
        r = []
        v = []
        for j in range(3):
            r.append(gatorstate[j])
            v.append(gatorstate[j+3])
        time.append(t)
        pos.append(r)
        vel.append(v)
        print("Starting state: ", t, r, v)
        
        # Take a step and buffer it
        self.gator.Step(60.0)
        gatorstate = self.gator.GetState()
        t = t + 60.0
        r = []
        v = []
        for j in range(3):
            r.append(gatorstate[j])
            v.append(gatorstate[j+3])
        time.append(t)
        pos.append(r)
        vel.append(v)
        print("Propped state: ", t, r, v)

    def PlotPropagation(self):
        time = []
        pos = []
        vel = []
        gatorstate = self.gator.GetState()
        t = 0.0
        r = []
        v = []
        for i in range(360):
            # Take a step and buffer it
            self.gator.Step(60.0)
            gatorstate = self.gator.GetState()
            t = t + 60.0
            r = []
            v = []
            for j in range(3):
                r.append(gatorstate[j])
                v.append(gatorstate[j+3])
            time.append(t)
            pos.append(r)
            vel.append(v)
        
        plt.rcParams['figure.figsize'] = (15, 5)
        plt.plot(time, pos)
        plt.show()
        plt.plot(time, vel)
        plt.show()

funcs = GmatFunctions(0.01, 0.01, 2, 3, 1.75)
funcs.SetupOrbitalElements(7000, 0.05, 78, 45, 90)
funcs.PlotPropagation()

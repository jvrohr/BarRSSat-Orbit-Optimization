#!/bin/python3

from load_gmat import *
import os, sys, re
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

currentDir = os.path.dirname(os.path.abspath(sys.argv[0]))
GMATPATH = os.path.join(currentDir, 'GMAT', 'R2022a')
outputDir = os.path.join(GMATPATH, 'output')

earthRadius = 6371

# scriptName = "BarRSSat_decay.script"
# gmat.LoadScript(os.path.join(currentDir, scriptName))
# gmat.RunScript()

def ProcessFile(filePath):
    elapsedSecs = []
    X = []
    Y = []
    Z = []
    
    with open(filePath, 'r') as file:
        data = file.read().split("\n")

    for line in data[1:]:
        line = re.split(r"\s+", line.strip())
        if len(line) > 1:
            elapsedSecs.append(float(line[0]))
            X.append(float(line[1]))
            Y.append(float(line[2]))
            Z.append(float(line[3]))

    return elapsedSecs, X, Y, Z

def CalculateR(X, Y, Z):
    return [np.sqrt(x**2 + y**2 + z**2) - earthRadius for x, y, z in zip(X, Y, Z)]

def PlotResults(secs, R):
    # Create 3D figure and axis
    fig = plt.figure(figsize=(10, 8))

    days = [s/(60*60*24) for s in secs]

    ## Linear decay trend
    x_reshaped = np.array(days).reshape(-1, 1)

    # Create and fit the model
    model = LinearRegression()
    model.fit(x_reshaped, R)

    # Get the linear relationship parameters
    slope = model.coef_[0]
    intercept = model.intercept_

    # Generate predictions
    y_pred = model.predict(x_reshaped)

    plt.plot(days, R, color="blue", linestyle="-", label="Radius")
    plt.plot(days, y_pred, label='Trend Line', color='red', linewidth=2)
    plt.plot(days[0], y_pred[0], color="k", marker="*", label=f"Initial Value ({y_pred[0]:.2f} km)")
    plt.plot(days[-1], y_pred[-1], color="k", marker="o", label=f"Final Value ({y_pred[-1]:.2f} km)")
    plt.xlabel("Elapsed Time [days]")
    plt.ylabel("Altitude of Satellite [km]")
    plt.title("BaRSat Orbit Decay Over an Year")
    plt.grid()
    plt.legend()

    plt.savefig('decay_plot.png')

    plt.show()

seconds, X, Y, Z = ProcessFile(os.path.join(outputDir, "ReportFile1.txt"))

PlotResults(seconds, CalculateR(X, Y, Z))
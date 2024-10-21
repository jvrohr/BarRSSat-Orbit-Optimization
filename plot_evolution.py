#!/bin/python3

import json, sys, os, ast
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm

currentDir = os.path.dirname(os.path.abspath(sys.argv[0]))

with open(os.path.join(currentDir, "simulationResultsDictionary.json"), 'r') as file:
    resultDict = json.load(file)

def PlotResults(dict, optPoint):
    keys = [ast.literal_eval(a.replace('\n', '').strip().replace(' ', ', ')) for a in list(dict.keys())]

    inc = [a[2] for a in keys]
    raan = [a[3] for a in keys]
    aop = [a[4] for a in keys]
    dailyAverage = [value["dailyAverage"] for value in list(dict.values())]

    # Create 3D figure and axis
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    # Plot scatter with color gradient
    scatter = ax.scatter(inc, raan, aop, c=dailyAverage, cmap=cm.plasma, alpha=1)

    # Add color bar to indicate the scale
    colorbar = fig.colorbar(scatter, ax=ax)
    colorbar.set_label('7-day Daily Contact Duration Averaged for all Stations [s]')

    # Set axis labels
    ax.set_title("Explored Points During Optimization")
    ax.set_xlabel('Inclination [°]')
    ax.set_ylabel('RAAN [°]')
    ax.set_zlabel('AOP [°]')

    plt.savefig('optimization_plot.png')

    # Show the plot
    plt.show()

optimizationPoint = [35.27, 313.47, 46.35]

PlotResults(resultDict, optimizationPoint)
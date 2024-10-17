#!/bin/python3

from simulation import *

opt = Optimize(["SMA", "ECC", "INC", "RAAN", "AOP"], ((6871, 6971), (0, 0.01), (0, 102), (0, 360), (0, 360)))

opt.Optimize()
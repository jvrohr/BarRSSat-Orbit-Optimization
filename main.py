#!/bin/python3.10

from optimization import *

opt = Optimize(["SMA", "ECC", "INC", "RAAN", "AOP"], ((6871, 6971), (0, 0.007), (0, 102), (0, 360), (0, 360)), 1.5)

opt.Optimize()

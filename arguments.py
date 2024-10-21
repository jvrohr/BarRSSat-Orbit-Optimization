import argparse

def CreateParser(description="Parser for orbit simulation"):
    parser = argparse.ArgumentParser(description=description)

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

    return parser
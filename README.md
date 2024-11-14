# BarRSSat-Orbit-Optimization
Orbit selection optimization algorithm for a nanosatellite mission for dams level data collection in the state of Rio Grande do Sul, Brazil

Requirements and limitations:
- Maximize exposure time to the data collection platforms (DCP) and ground station. Fortunately they are close together.
- Minimize cost of launch.
- Orbit parameters within launcher possible range.
- Minimize debris in Master
- Pass over the ground station at least once a day
- 12 months of minimum lifetime
- Re-enter the atmosphere after the mission lifetime

## Setting up the environment

If in Linux run the ```setupscript.sh``` in order to download GMAT and make the needed file configuration. 

If in Windows or some error occurred, please be pacient and consult the GMAT documentation (API User's Guide) for more information on how to install everything.

Basically the default GMAT folder should be placed in this repository root and two configurations in ```api_startup_file.txt``` and ```load_gmat.py``` are needed.

## Example call

Example of how to call the optimization function for mean contact duration time for the predefined groundstations. The function uses the ```rungmat.py``` file to run GMAT through the GMAT Python API. A template script (sourceScript) should be made beforehand by the user with the arguments that can be changed (SMA, ECC, etc). Note that the time of passege by the periapsis is not set a range because it does not affect the orbit contact duration for the long run.  

```
from optimization import *

opt = Optimize()

opt.Optimize(((6871, 6971), # SMA
        (0, 0.007),         # ECC 
        (0, 102),           # INC
        (0, 360),           # RAAN
        (0, 360)))          # AOP
```

## TO-DO

- Organize files in folders and make the paths work with these changes
- Add decay check in optimization
- Output final orbit
# vpower
Add virtual power to your trainer ride on the Tacx Blue Motion T2600. Record your speed during your workout on your Garmin and add virtual power with this Python program. 

## Usage
- First, obtain a TCX file corresponding with the .fit file from your Garmin.
- Download the file [vpower.py](https://github.com/cast42/vpower/blob/master/vpower.py) into the same directory of the .tcx file.
- Execute:
```
python vpower.py <file>.tcx
```
- A new file is created (or overwritten) called `vpower_<file>.tcx` that contains the calculated power values derived from the speed recorded by your Garmin.
- Upload the generated file `vpower_<file>.tcx` to Strava for analysis
- By default, it's assumed the lever is at position 5. If your lever was at another position during your workout, specify this as follows (assuming lever position was 6):
```
python vpower.py --lever=6 <file>.tcx
```

# fit2gpx

## Setup
The python library reauires Python 2.7. I created a conda environment to set this up:
```
conda create -n vpower environment.yml
```

## Usage
- Execute:
```
python fit2gpx.py <file>.fit
```
- A new file is created (or overwritten) called `<file>.gpx` that containt the ride in gpx format.


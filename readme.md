# Star Tracker // Astrophotography // Raspberry PI

Provides the ability to track any object in the sky, day or night. High precision allows for long exposures when capturing photographs.

## Stellarium integration

![alt text](https://avatars.githubusercontent.com/u/7320160?s=70)

Control your EQ mount directly from Stellarium using the telescope plugin


## REST API


#### Calibration

`by Object Name`

Calibrate by _many_ object names in the sky. Stars, DSO's, etc...

```
/api/calibrate/by_name/?name=polaris
```

`by Solar System Object`

Calibrate by objects in our solar system. Sun, Jupiter, Mars, etc...

```
/api/calibrate/solar_system_object/?name=jupiter
```

`by RA/DEC`

Calibrate directly with coordinates

```
/api/calibrate/?ra=00h45m42.223s&dec=37d56m33.427s
```


## Fully 3D-Printed, Equatorial Mount


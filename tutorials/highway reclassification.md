# OSM Highway


# 1. `OSMnx`

Refer to [`OSMnx`](https://osmnx.readthedocs.io/en/stable/) Package, in the built-in function [`osmnx
._overpass._get_osm_filter()`](https://github.com/gboeing/osmnx/blob/main/osmnx/_overpass.py), including six network types:

- all
- all_private
- drive
- drive_service
- bike
- walk

####  (1) **`network_type='all'`**

to download all ways, just filter out everything not currently in use or that is private-access only

```python
["highway"]
["area"!~"yes"]
["highway"!~"abandoned|construction|no|planned|platform|proposed|raceway|razed"]
["service"!~"private"]
```

####  (2) **`network_type='all_private'`**

 to download all ways, including private-access ones, just filter out everything not currently in use

```python
["highway"]
["area"!~"yes"]
["highway"!~"abandoned|construction|no|planned|platform|proposed|raceway|razed"]
```

####  (3) **`network_type='drive'`**

**driving:** filter out un-drivable roads, service roads, private ways, and anything specifying motor=no. also filter out any non-service roads that are tagged as providing certain services

```python
["highway"]
["area"!~"yes"]
["highway"!~"abandoned|bridleway|bus_guideway|construction|corridor|cycleway|elevator|escalator|footway|no|path|pedestrian|planned|platform|proposed|raceway|razed|service|steps|track"]
["motor_vehicle"!~"no"]
["motorcar"!~"no"]
["service"!~"alley|driveway|emergency_access|parking|parking_aisle|private"]
```

####  (4) **`network_type='drive_service'`**

**drive+service:** allow ways tagged 'service' but filter out certain types

```python
["highway"]
["area"!~"yes"]["highway"!~"abandoned|bridleway|bus_guideway|construction|corridor|cycleway|elevator|escalator|footway|no|path|pedestrian|planned|platform|proposed|raceway|razed|steps|track"]
["motor_vehicle"!~"no"]
["motorcar"!~"no"]'
["service"!~"emergency_access|parking|parking_aisle|private"]
```

####  (5) `network_type='bike'`

**biking:** filter out foot ways, motor ways, private ways, and anything specifying biking=no

```python
["highway"]
["area"!~"yes"]
["highway"!~"abandoned|bus_guideway|construction|corridor|elevator|escalator|footway|motor|no|planned|platform|proposed|raceway|razed|steps"]
["bicycle"!~"no"]
["service"!~"private"]
```

####  (6) `network_type='walk'`

**walking:** filter out cycle ways, motor ways, private ways, and anything specifying foot=no. allow service roads, permitting things like parking lot lanes, alleys, etc that you *can* walk on even if they're not exactly pleasant walks. some cycleways may allow pedestrians, but this filter ignores such cycleways.

```python
["highway"]
["area"!~"yes"]
["highway"!~"abandoned|bus_guideway|construction|cycleway|motor|no|planned|platform|proposed|raceway|razed"]'
["foot"!~"no"]
["service"!~"private"]'
```

# 2. `Pyrosm`

Refer to [`Pyrosm`](https://pyrosm.readthedocs.io/en/stable/) Package, in the built-in function [`pyrosm.config
.osm_filters.get_osm_filter()`](https://github.com/pyrosm/pyrosm/blob/master/pyrosm/config/osm_filters.py). 

Based on the developer's statement, this package uses the same filters with `OSMnx`'s.
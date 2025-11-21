# OSM Highway


# 1. `OSMnx`

Refer to [`OSMnx`](https://osmnx.readthedocs.io/en/stable/) Package, in the built-in function [`osmnx
._overpass._get_osm_filter()`](https://github.com/gboeing/osmnx/blob/main/osmnx/_overpass.py), including six network types:

- all
- all_public
- drive
- drive_service
- bike
- walk

####  (1) **`network_type='all'`**

to download all ways, including private-access ones, just filter out everything not currently in use

```css
["highway"]
["area"!~"yes"]
["highway"!~"abandoned|construction|no|planned|platform|proposed|raceway|razed|rest_area|services"]
```

```powershell
% filter by osmium tools
osmium tags-filter ^
    INPUT.osm.pbf ^
    w/highway ^
    w/area!=yes ^
    w/highway!=abandoned,construction,no,planned,platform,proposed,raceway,razed,rest_area,services ^
    -o OUTPUT.osm
```

####  (2) **`network_type='all_public'`**

all public ways, just filter out everything not currently in use or that is private-access only

```css
["highway"]
["area"!~"yes"]
["access"!~"private"]
["highway"!~"abandoned|construction|no|planned|platform|proposed|raceway|razed|rest_area|services"]
["service"!~"private"]
```

```powershell
% filter by osmium tools
osmium tags-filter ^
    INPUT.osm.pbf ^
    w/highway ^
    w/area!=yes ^
    w/access!=private ^
    w/highway!=abandoned,construction,no,planned,platform,proposed,raceway,razed,rest_area,services ^
    w/service!=private ^
    -o OUTPUT.osm
```

####  (3) **`network_type='drive'`**

**driving:** filter out un-drivable roads, service roads, private ways, and anything tagged motor=no. also filter out any non-service roads that are tagged as providing certain services

```CSS
["highway"]
["area"!~"yes"]
["access"!~"private"]
["highway"!~"abandoned|bridleway|bus_guideway|construction|corridor|cycleway|elevator|escalator|footway|no|path|pedestrian|planned|platform|proposed|raceway|razed|rest_area|service|services|steps|track"]
["motor_vehicle"!~"no"]
["motorcar"!~"no"]
["service"!~"alley|driveway|emergency_access|parking|parking_aisle|private"]
```

```powershell
% filter by osmium tools
osmium tags-filter ^
    INPUT.osm.pbf ^
    w/highway ^
    w/area!=yes ^
    w/access!=private ^
    w/highway!=abandoned,bridleway,bus_guideway,construction,corridor,cycleway,elevator,escalator,footway,no,path,pedestrian,planned,platform,proposed,raceway,razed,rest_area,service,services,steps,track ^
    w/motor_vehicle!=no ^
    w/motorcar!=no ^
    w/service!=alley,driveway,emergency_access,parking,parking_aisle,private ^
    -o OUTPUT.osm
```

####  (4) **`network_type='drive_service'`**

**drive+service:** allow ways tagged 'service' but filter out certain types

```CSS
["highway"]
["area"!~"yes"]
["access"!~"private"]
["highway"!~"abandoned|bridleway|bus_guideway|construction|corridor|cycleway|elevator|escalator|footway|no|path|pedestrian|planned|platform|proposed|raceway|razed|rest_area|services|steps|track"]
["motor_vehicle"!~"no"]
["motorcar"!~"no"]
["service"!~"emergency_access|parking|parking_aisle|private"]
```

```powershell
% filter by osmium tools
osmium tags-filter ^
    INPUT.osm.pbf ^
    w/highway ^
    w/area!=yes ^
    w/access!=private ^
    w/highway!=abandoned,bridleway,bus_guideway,construction,corridor,cycleway,elevator,escalator,footway,no,path,pedestrian,planned,platform,proposed,raceway,razed,rest_area,services,steps,track ^
    w/motor_vehicle!=no ^
    w/motorcar!=no ^
    w/service!=emergency_access,parking,parking_aisle,private ^
    -o OUTPUT.osm
```

####  (5) `network_type='bike'`

**biking:** filter out foot ways, motor ways, private ways, and anything specifying biking=no

```css
["highway"]
["area"!~"yes"]
["access"!~"private"]
["highway"!~"abandoned|bus_guideway|construction|corridor|elevator|escalator|footway|motor|no|planned|platform|proposed|raceway|razed|rest_area|services|steps"]
["bicycle"!~"no"]
["service"!~"private"]
```

```powershell
osmium tags-filter ^
    INPUT.osm.pbf ^
    w/highway ^
    w/area!=yes ^
    w/access!=private ^
    w/highway!=abandoned,bus_guideway,construction,corridor,elevator,escalator,footway,motor,no,planned,platform,proposed,raceway,razed,rest_area,services,steps ^
    w/bicycle!=no ^
    w/service!=private ^
    -o bike.osm
```

####  (6) `network_type='walk'`

**walking:** filter out cycle ways, motor ways, private ways, and anything specifying foot=no. allow service roads, permitting things like parking lot lanes, alleys, etc that you *can* walk on even if they're not exactly pleasant walks. some cycleways may allow pedestrians, but this filter ignores such cycleways.

```css
["highway"]
["area"!~"yes"]
["access"!~"private"]
["highway"!~"abandoned|bus_guideway|construction|cycleway|motor|no|planned|platform|proposed|raceway|razed|rest_area|services"]
["foot"!~"no"]
["service"!~"private"]
["sidewalk"!~"separate"]
["sidewalk:both"!~"separate"]
["sidewalk:left"!~"separate"]
["sidewalk:right"!~"separate"]
```

```powershell
% filter by osmium tools
osmium tags-filter ^
    INPUT.osm.pbf ^
    w/highway ^
    w/area!=yes ^
    w/access!=private ^
    w/highway!=abandoned,bus_guideway,construction,cycleway,motor,no,planned,platform,proposed,raceway,razed,rest_area,services ^
    w/foot!=no ^
    w/service!=private ^
    w/sidewalk!=separate ^
    w/sidewalk:both!=separate ^
    w/sidewalk:left!=separate ^
    w/sidewalk:right!=separate ^
    -o OUTPUT.osm
```

# 2. `Pyrosm`

Refer to [`Pyrosm`](https://pyrosm.readthedocs.io/en/stable/) Package, in the built-in function [`pyrosm.config
.osm_filters.get_osm_filter()`](https://github.com/pyrosm/pyrosm/blob/master/pyrosm/config/osm_filters.py). 

Based on the developer's statement, this package uses the same filters with `OSMnx`'s.
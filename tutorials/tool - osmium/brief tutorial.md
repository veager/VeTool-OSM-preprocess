# Osmium Tool

Core resources:

- [Homepage](https://osmcode.org/osmium-tool/)

- [Github](https://github.com/osmcode/osmium-tool)

- [Document](https://docs.osmcode.org/osmium/latest/)

# 1. Installation

A convenient way using `osmium` tool is to install the `osmium` package in Python environment.

- Python Environment

pip install
```bash
pip install osmium
```

or by conda
```bash
conda install osmium-tool
conda install -c conda-forge osmium-tool
```

After successful installation, the osmium executable (on Windows `osmium.exe`) is located in your Python environment's `Library/bin` directory. For example:

```bash
%PYTHON_ENV%\Library\bin\osmium.exe
```

# 2. Usage

## 2.1 OSM file formats



## 2.2 Geographic extraction

#### (1) Core commands

Use `osmium extract` to clip an OSM file to a boundary defined by a bounding box or polygon. Detailed documentation can be found at [site](https://osmcode.org/osmium-tool/manual.html#creating-geographic-extracts).

```bash
osmium extract --config CONFIG-FILE [OPTIONS] INPUT.osm.pbf
osmium extract --bbox LEFT,BOTTOM,RIGHT,TOP [OPTIONS] INPUT.osm.pbf
osmium extract --polygon POLYGON-FILE [OPTIONS] INPUT.osm.pbf

% print help document
osmium extract --help
osmium extract -h
```

#### (2) Examples and arguments

```bash
osmium extract ^
  --polygon "boundary-wgs84.poly" ^
  --output "extracted.osm.pbf" ^
  --strategy complete_ways ^
  "original.osm.pbf"

% or
osmium extract ^
  -p "boundary-wgs84.poly" ^
  -o "extracted.osm.pbf" ^
  -s complete_ways ^
  "original.osm.pbf"
  
 % or ouput to OSM XML format
osmium extract ^
  -p "boundary-wgs84.poly" ^
  -o "extracted.osm" ^
  -s complete_ways ^
  "original.osm.pbf"
```

- **Arguments**

- `--polygon` or `-p`: Specify a `.poly` file in WGS84.

    - A typical `.poly` file format is explained in the [Osmosis/Polygon Filter File Format](https://wiki.openstreetmap.org/wiki/Osmosis/Polygon_Filter_File_Format).

    - A function to convert a shapefile (`.shp`) to a `.poly` file is provided in the `shapefile_to_poly.py` script.

- `--bbox` or `-b`: Provide coordinates as `min_lon,min_lat,max_lon,max_lat`.

- `--strategy` or `-s`: Specify the strategy for extracting data. The default is `simple`.

    - `--strategy simple`: Only include *nodes* and *ways* that are fully inside the polygon.

    - `--strategy complete_ways`: Include all nodes and ways that intersect with the polygon, even if they are not fully inside.

    - `--strategy smart`: A combination of both strategies, including all nodes and ways that intersect with the polygon, but only including relations that are fully referenced.


**A brief comparison of the three strategies `--strategy`:**

| Feature                | simple                                                                     | complete_ways                                                                                                                   | smart                                                                                                                                                                                   |
|------------------------|----------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Nodes Included**         | Only nodes whose coordinates lie inside the region                         | All nodes inside the region **plus** all nodes used by ways that intersect                                                      | Same as **complete_ways**                                                                                                                                                               |
| **Ways Included**          | Any way with ≥ 1 node inside (may be missing exterior nodes)               | All ways with ≥ 1 node inside (always fully referenced if they were in the input)                                                | Same as **complete_ways**                                                                                                                                                               |
| **Relations Included**     | Any relation that contains an included node or way (but may be incomplete) | Any relation that contains an included node or way, plus all parent relations (relations not reference-complete)                  | Same as **complete_ways**, **plus** any multipolygon relation and all its members when ≥ 1 member node lies inside                                                                      |
| **Reference Completeness** | Ways: no<br>Relations: no                                                  | Ways: yes<br>Relations: no                                                                                                       | Ways: yes<br>Relations: only for configured types                                                                                                                                       |
| **Input Reads**            | 1                                                                          | 2                                                                                                                                | 3                                                                                                                                                                                       |
| **History Support**        | No                                                                         | Yes (with `--with-history`)                                                                                                      | No                                                                                                                                                                                      |
| **Notes**                  | Works with STDIN/STDOUT                                                    | Requires two passes; use `--with-history` to include full version history of matching objects                                    | Default for relations tagged `type=multipolygon`; configurable via `-S types...`. <br> E.g., `-S types=any` for all relation types, `-S types=multipolygon,route` for particular types. |


## 2.3 Tags filtering

#### (1) Core commands

Use `osmium tags-filter` to include or exclude OSM objects based on their tags. See the full documentation here [site](https://osmcode.org/osmium-tool/manual.html#filtering-by-tags).

```bash
osmium tags-filter [OPTIONS] INPUT.osm.pbf TAG_FILTERS
```

- **Arguments**

  - `INPUT.osm.pbf`: the source OSM file
  
  - `TAG_FILTERS`: one or more filters, in the form `<element>/<key>=<value>` or `<element>/<key>!=<value>`

  - `<element>` is `n` (node), `w` (way), or `r` (relation)
  
  - `<key>` is the tag key, and `<value>` is the tag value. Use `*` as a wildcard for values

#### (2) Examples and arguments

```bash
% Extract all ways with highway tags
osmium tags-filter INPUT.osm.pbf w/highway -o OUTPUT.osm.pbf
osmium tags-filter INPUT.osm.pbf w/highway -o OUTPUT.osm
```

Filtering syntax of `TAG_FILTERS`

```bash
% Extract only motorway, trunk, and primary highways
w/highway=motorway,trunk,primary

% Exclude multipolygon and route relations
r/type!=multipolygon,route

% Extract nodes or ways whose "name" contains "school" (case-sensitive)
n/name=*school w/name=*School
```

Extract *driving* network (refer to `OSMnx`)

```
["highway"]
["area"!~"yes"]
["highway"!~"abandoned|bridleway|bus_guideway|construction|corridor|cycleway|elevator|escalator|footway|no|path|pedestrian|planned|platform|proposed|raceway|razed|service|steps|track"]
["motor_vehicle"!~"no"]
["motorcar"!~"no"]
["service"!~"alley|driveway|emergency_access|parking|parking_aisle|private"]
```

```bash
osmium tags-filter ^
  INPUT.osm.pbf ^
  w/highway ^
  w/area!=yes ^
  w/highway!=abandoned,bridleway,bus_guideway,construction,corridor,cycleway,elevator,escalator,footway,no,path,pedestrian,planned,platform,proposed,raceway,razed,service,steps,track ^
  w/motor_vehicle!=no ^
  w/motorcar!=no ^
  w/service!=alley,driveway,emergency_access,parking,parking_aisle,private ^
  -o OUTPUT.osm.pbf
```

## 2.4 Filtering OSM data by time

#### (1) Download historical OSM file

Historical OSM file (.osh.pdf) can be downloaded through OpenStreetMap internal server at [site](https://osm-internal.download.geofabrik.de//index.html)

- [OpenStreetMap Data Extracts](https://download.geofabrik.de/) -> "Extracts with full metadata"

#### (2) Commands

Use osmium time-filter to extract objects valid at a given timestamp (or time range) from a history file (.osh.pbf).

```bash
osmium time-filter [OPTIONS] OSM-HISTORY-FILE [TIME]
osmium time-filter [OPTIONS] OSM-HISTORY-FILE FROM-TIME TO-TIME
```

The apply-changes and extract commands have an option `--with-history` that makes them work with history files.

- **Arguments**

- If omit `TIME`, the current timestamp is assumed.

- `TIME`, `FROM-TIME` and `TO-TIME` Timestamps must be in ISO 8601, e.g. `YYYY-MM-DDThh:mm:ssZ`, `2015-01-01T00:00:00Z`.

Copy all objects that were valid at the given `TIME` or in the time period between `FROM-TIME` (inclusive) and `TO-TIME` (not inclusive) from the input file into the output file. If no time is given, the current time is used.

#### (3) Examples


```bash
osmium time-filter ^ 
    -o "OUTPUT.osh.pbf" ^ 
    "INPUT.osh.pbf" ^
    2016-12-31T00:00:00Z

osmium extract ^
    -p "boundary\new-york-city-boundary-wgs84.poly" ^
    -o "nyc_2019-12-31.osm.pbf" ^
    -s complete_ways ^
    "us-northeast_2019-12-31.osm.pbf" 
```

A full example to extract OSM data with a specific boundary for each year using loop in powershell:

```bash
activate py310geo
cd "C:\Open street map\OSM US NYC\osm"

for %y in (2018, 2019, 2020, 2021, 2022) do (
    
    ECHO "Extracting temporal OSM data for year %y"    
    osmium time-filter ^
        -o "extract\us-northeast_%y-07-01.osm.pbf" ^
        "original\us-northeast-internal-2024-10-10.osh.pbf" ^
        %y-07-01T00:00:00Z
    
    ECHO "Extracting OSM data within the boundary"
    osmium extract ^
        -p "boundary.poly" ^
        -o "extract\nyc_%y-07-01.osm.pbf" ^
        -s complete_ways ^
        "extract\us-northeast_%y-07-01.osm.pbf"
)
```
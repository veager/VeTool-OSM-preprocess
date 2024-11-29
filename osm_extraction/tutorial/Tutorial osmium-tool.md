# Osmium Tool

- [Homepage](https://osmcode.org/osmium-tool/), [Github](https://github.com/osmcode/osmium-tool)

- [Document](https://docs.osmcode.org/osmium/latest/)

# 1. Installation

- Python Environment

pip install
```bash
pip install osmium
```
or by conda
```bash
conda install osmium-tool
```


After successful installation, the excutable application `osmium.exe` can be found in the following path

```bash
%PYTHON_ENV%\Library\bin\osmium.exe
```

# 2. Usage

## 2.X Extract region 

Extract OSM data by a given region boundary

```bash
osmium extract --config CONFIG-FILE [OPTIONS] OSM-FILE
osmium extract --bbox LEFT,BOTTOM,RIGHT,TOP [OPTIONS] OSM-FILE
osmium extract --polygon POLYGON-FILE [OPTIONS] OSM-FILE
```

- Example

```bash
osmium extract ^
  -p "boundary-wgs84.poly" ^
  -o "aoi.osm.pbf" ^
  -s complete_ways ^
  "all.osm.pbf"
```

## 2.X Time filter

filter OSM data by time from a history file (`.osh.pbf`)

```bash
osmium time-filter [OPTIONS] OSM-HISTORY-FILE [TIME]
osmium time-filter [OPTIONS] OSM-HISTORY-FILE FROM-TIME TO-TIME
```
Copy all objects that were valid at the given `TIME` or in the time period between `FROM-TIME` (inclusive) and `TO-TIME` (not inclusive) from the input file into the output file. If no time is given, the current time is used.

- Example

```bash
osmium time-filter -o output.osh.pbf input.osh.pbf 2016-01-02T00:00:00Z
```
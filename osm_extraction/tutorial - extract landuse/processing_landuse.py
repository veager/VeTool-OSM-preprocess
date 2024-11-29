import pandas as pd



def extract_osm_landuse(data, landuse_col=None):
    '''
    Extract land use data from OSM tags and map them into EULUC 2018 categories
     - Considering tags: 'landuse', 'amenity', 'leisure', 'natural'
     - Mapping rule: r'C:\zhouweifile\Github-Project\VeTool-Processing-POI-Landuse\OSM tags\tag_processing.xlsx'

    :param data:
    :return:
    '''

    # mapped tags
    osm_tag_category_path = r'C:\zhouweifile\Github-Project\VeTool-Processing-POI-Landuse\OSM tags\tag_processing.xlsx'
    print('OSM mapped tags:', osm_tag_category_path)

    # in piority order
    if landuse_col is None:
        landuse_col = ['landuse', 'amenity', 'leisure', 'natural']

    # map original tags to EULUC 2018 labels
    for col in landuse_col:
        osm_landuse_category = pd.read_excel(osm_tag_category_path, sheet_name=col) \
            [['Value', 'EULUC2018']].dropna() \
            .set_index('Value') \
            .squeeze() \
            .to_dict()

        data[col] = data[col].map(osm_landuse_category)

    # drop na
    data = data[landuse_col + ['geometry']] \
        .dropna(subset=landuse_col, how='all')

    return data
# ======================================================================================================================
def make_valid_polygon(geom):
    '''
    make valid polygon, if the input is 'GeometryCollection', it will be converted to 'MultiPolygon'

    :param geom:
    :return:
    '''
    from shapely.validation import make_valid
    from shapely.geometry import MultiPolygon

    if not geom.is_valid:
        geom = make_valid(geom)

    if geom.geom_type == 'GeometryCollection':
        geom = MultiPolygon([make_valid(p) for p in geom.geoms if p.geom_type in ['Polygon', 'MultiPolygon']])

    return geom
# ======================================================================================================================
def merge_landuse_type(data, landuse_cols):
    '''
    Assign landuse type to the boundary polygon

    :parameter
    ---
    data (geopandas.GeoDataFrame) :
    landuse_cols:
        column names indicating land use type, the order of the column names will be the priority of the land use type,

    :return:
    '''
    # select polygon
    data = data[(data.geometry.geom_type == 'Polygon') | (data.geometry.geom_type == 'MultiPolygon')]
    data = data[data.area > 0.]

    # total covered area
    covered_boundary = make_valid_polygon(data['geometry'].unary_union)

    landuse_all = []

    for col in landuse_cols:
        print(f'Processing the land use column \'{col}\'...')

        data_col = data[[col, 'geometry']].dropna() \
            .dissolve(by = col, as_index = False) \
            .explode(index_parts = False) \
            .assign(geometry = lambda x : x['geometry'].intersection(covered_boundary).make_valid()) \
            .rename(columns = {col : 'landuse'})

        # select polygon
        data_col = data_col[(data_col.geometry.geom_type == 'Polygon') | (data_col.geometry.geom_type == 'MultiPolygon')]
        data_col = data_col[data_col.area > 0.]

        landuse_all.append(data_col)

        # assigned region in this loop
        assigned_area = make_valid_polygon(data_col['geometry'].unary_union)
        # print(assigned_area.area, assigned_area.geom_type)
        # update unassigned region
        covered_boundary = make_valid_polygon(covered_boundary.difference(assigned_area))
        if covered_boundary.area < 1e-8: break

    landuse_all = pd.concat(landuse_all, axis=0, ignore_index=True) \
        .dissolve(by = 'landuse', as_index = False) \
        .explode(index_parts = False) \
        .assign(geometry = lambda x : x['geometry'].make_valid())

    landuse_all = landuse_all[(landuse_all.geometry.geom_type == 'Polygon') | (landuse_all.geometry.geom_type == 'MultiPolygon')]
    landuse_all = landuse_all[landuse_all.area > 0.]

    return landuse_all
# ======================================================================================================================
#%%

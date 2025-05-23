import pandas as pd
import geopandas as gpd

def read_road_hierarchy(path=None):
    
    if path is None:
        path = 'C:/zhouweifile/Transportation Data/OSM/tag_processing.xlsx' 
    
    hierarchy_mapper = pd.read_excel(path, sheet_name='highway', index_col=None, header=0) \
                            .query('Key == \'highway\'') \
                            .query('Hierarchy != \'Deleted\'')\
                            [['Value', 'Hierarchy']] \
                            .set_index('Value') \
                            .squeeze() \
                            .to_dict()  
    
    return hierarchy_mapper
# --------------------------------------------------------------------------
def preprocessed_road_network(path, drop_link=True, target_crs=None):

    data = gpd.read_file(path, encoding='gbk')
    
    if not (target_crs is None):
        data = data.to_crs(target_crs)
        
    if drop_link:
        for link_label in ['motorway_link', 'trunk_link', 'primary_link', 'secondary_link', 'tertiary_link']:
            data = data[data['highway'] != link_label]
    
    
    hierarchy_mapper = read_road_hierarchy(path=None)
    data['hierarchy'] = data['highway'].map(hierarchy_mapper)
    data = data[data['hierarchy'] != 'Deleted']
    data['geometry'] = data['geometry'].make_valid()
    
    return data
# ==========================================================



read_path = 'zip://road_network.zip!road_network.shp'
save_path = 'road_network_processed.shp'

data = preprocessed_road_network(read_path, target_crs=None)
data.to_file(save_path, encoding='utf-8')
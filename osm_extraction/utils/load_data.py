import pathlib
import pandas as pd

DATABASE_FOLDER = r'C:\Users\Wei Zhou\Documents\zhouwei file\Github-Project\VeTool-Code-Template\osm_extraction\tags'
DATABASE_FOLDER = pathlib.Path(DATABASE_FOLDER)

def load_osm_tag_category(tag_name):

    assert tag_name in ['amenity', 'shop', 'leisure'], f'Not supported tag name: {tag_name}'

    path = DATABASE_FOLDER / f'{tag_name}.xlsx'
    data = pd.read_excel(path, sheet_name=tag_name)

    return data
# ================================================================






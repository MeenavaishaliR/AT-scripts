from read_files import read_shp, read_geotiff, write_shp, read_kml, write_kml
import os
from geo import world2Pixel, Pixel2world
import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon


from utils import get_image_proj_transform


def split_tables(tables_dataframe, geo_matrix, table_type):
    # Initialise module dataframe
    modules_data_dict = []

    if table_type == 1:
        rows = 2
        columns = 20
    #elif table_type == 2:
    #    rows = 64
    #    columns = 1
    # elif table_type == 3:
    #     rows = 2
    #     columns = 15
    else:
        rows = 0
        columns = 0
        print("Table type {} is not supported yet".format(table_type))
        exit()
    # FOr each table
    tables_dataframe = pd.concat([tables_dataframe, tables_dataframe.bounds], axis=1)
    for table_index, table in tables_dataframe.iterrows():

        # Get boundaries,  Convert world to pixel. It has [bottom left, bottom right, top right, top left]
        table_top_left, table_bottom_right = [world2Pixel(geoTrans, boundary_pt[0], boundary_pt[1])
                                              for boundary_pt in [(table.minx, table.miny), (table.maxx, table.maxy)]]

        # Images are in third quadrant. So y_max is < ymin
        table_y_top = table_bottom_right[1]
        table_x_right = table_bottom_right[0]
        table_y_bottom = table_top_left[1]
        table_x_left = table_top_left[0]
        # TODO Document the logic better
        for row in range(rows):

            # Minus because of tiff image in third quadrant
            module_top_y = table_y_top - (row*(table_y_top - table_y_bottom)/rows)
            module_bottom_y = table_y_top - ((row+1)*(table_y_top - table_y_bottom)/rows)
            for col in range(columns):
                module_left_x = table_x_left + (col * (table_x_right - table_x_left) / columns)
                module_right_x = table_x_left + ((col + 1) * (table_x_right - table_x_left) / columns)
                module_index = (row+1, col+1)

                module_left_x_latlon, module_bottom_y_latlon = Pixel2world(geoTrans, module_left_x, module_bottom_y)
                module_right_x_latlon, module_top_y_latlon = Pixel2world(geoTrans, module_right_x, module_top_y)

                polygon_geom = Polygon(zip([module_left_x_latlon, module_right_x_latlon, module_right_x_latlon, module_left_x_latlon, module_left_x_latlon],
                                           [module_bottom_y_latlon, module_bottom_y_latlon, module_top_y_latlon, module_top_y_latlon, module_bottom_y_latlon],
                                           [0.0, 0.0, 0.0, 0.0, 0.0]))

                modules_data_dict.append({'geometry': polygon_geom, 'description': str(module_index), 'parent_table_type': table_type})
    modules_dataframe = gpd.GeoDataFrame(modules_data_dict)
    return modules_dataframe


if __name__ == '__main__':

    # set the paths
    tables_path = '/media/deepanshu/Seagate Expansion Drive/AERIAL_THERMOGRAPHY/Magnet-1/CAD/split/CAD'
    thermal_image_path = '/media/deepanshu/Seagate Expansion Drive/AERIAL_THERMOGRAPHY/Magnet-1/GIS_TO_AUTOMATION/Fullgreyscale/Fullgreyscale.tif'
    output_path = '/media/deepanshu/Seagate Expansion Drive/AERIAL_THERMOGRAPHY/Magnet-1/CAD/output'

    # Get the coordinates from the geoTiff
    thermal_image = read_geotiff(thermal_image_path)
    epsg, geoTrans = get_image_proj_transform(thermal_image)

    # Iterate for each type of table
    for table in os.listdir(tables_path):

        # Table type
        table_type = int(table[:-4])

        # Full path of table
        table_full_path = os.path.join(tables_path, table)

        # Read tables
        tables_dataframe = read_kml(table_full_path)
        # Convert to latlon
        tables_dataframe = tables_dataframe.to_crs('epsg:'+epsg)

        # Split tables to modules
        modules_dataframe = split_tables(tables_dataframe, geoTrans, table_type)
        modules_dataframe.crs = "epsg:"+epsg
        modules_dataframe = modules_dataframe.to_crs("epsg:4326")

        modules_dataframe_based_on_type_name = 'split_' + table.split('.')[0] + \
                                               '.' + table.split('.')[1]
        modules_dataframe_based_on_type_path = os.path.join(output_path, modules_dataframe_based_on_type_name)
        write_kml(modules_dataframe, modules_dataframe_based_on_type_path)

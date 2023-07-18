from utils import get_image_proj_transform
from read_files import read_shp, read_geotiff, write_shp, read_kml, write_kml
import geo
from collections import Counter
import pyproj
from shapely.ops import transform
import os

def get_image_stream(thermal_image):
    srcband = thermal_image.GetRasterBand(1)
    image_stream = srcband.ReadAsArray()
    return image_stream


def process_data(model_dataframe, defect_dataframe, thermal_image):

    # Convert to image stream
    image_stream = get_image_stream(thermal_image)

    # Get projection details
    img_proj, img_trans = get_image_proj_transform(thermal_image)

    # Transform data
    model_dataframe = model_dataframe.to_crs('epsg:'+img_proj)
    defect_dataframe = defect_dataframe.to_crs('epsg:'+img_proj)
    # defect_dataframe['min_temp'] = ''
    # defect_dataframe['max_temp'] = ''

    # FOr each defect
    for defect_index, defect in defect_dataframe.iterrows():
        temp = str(defect.Description)
        inv_no = temp.split("Inverter No: ")[1].split(" Table No: ")[0]
        tbno = temp.split("Table No: ")[1].split(" Defect: ")[0]
        defect_val = temp.split("Defect: ")[1].split(" Description: ")[0]
        descrip = temp.split("Description: ")[1]

        x = "Inverter No: "+ str(inv_no) + "\n\nTable No: "+str(tbno) +"\n\nDefect: "+str(defect_val) +"\n\nDescription: "+str(descrip)

        # print(x)
        # print("-----------------------")
        # print(defect_dataframe)
        # Get the containing polygon
        containing_poly = get_containing_polygon(defect.geometry, model_dataframe)

        # Get cropped themal file
        module_image_overlay = get_module_image_overlay(containing_poly, image_stream, img_trans)
        minimum_temp, maximum_temp, avg_temp = get_min_max(module_image_overlay)
        defect_dataframe.at[defect_index, 'Description'] = x + \
                                                           "\n\nModule No: " + containing_poly["Description"] +  \
                                                           "\n\nMinimum Temperature(°C): "+str(minimum_temp) + \
                                                           "\n\nMaximum Temperature(°C): " + str(maximum_temp) + \
                                                           "\n\nAverage Temperature(°C): " + str(avg_temp) + "\n\n"
    return defect_dataframe


def get_module_image_overlay(containing_poly, tifImg, geoTrans):

    coord_x_list, coord_y_list = containing_poly.geometry.exterior.coords.xy
    pixel_x_list, pixel_y_list = list(zip(*[geo.world2Pixel(geoTrans, x, y) for x, y in zip(coord_x_list, coord_y_list)]))
    crop_img = tifImg[min(pixel_y_list):max(pixel_y_list), min(pixel_x_list):max(pixel_x_list)]
    return crop_img


def get_min_max(path):
    path = path.astype('float16')
    f = list(path.flatten())

    cnt = Counter(f)
    lst = [k for k, v in cnt.items() if v > 2]
    # cnt = [i for i in cnt.keys()]
    minmum = float(min(lst))
    maximum = float(max(lst))
    average = sum(lst) / len(lst)
    return round(minmum, 2), round(maximum, 2), round(average, 2)


def transform_crs(geom, in_coord, out_coord):
    project = pyproj.Transformer.from_crs(pyproj.CRS('EPSG:'+in_coord), pyproj.CRS('EPSG:'+out_coord),
                                          always_xy=True).transform
    transformed_geom = transform(project, geom)
    return transformed_geom


def get_containing_polygon(defect, model_dataframe):
    for poly_index, poly in model_dataframe.iterrows():
        if poly.geometry.contains(defect):
            return poly



if __name__ == '__main__':

    # TODO Change the hardcode to a cli
    model_path = '/media/deepanshu/Seagate Expansion Drive/AERIAL_THERMOGRAPHY/Magnet-1/Defects/INV_MOD_CAD/'
    defect_path = '/media/deepanshu/Seagate Expansion Drive/AERIAL_THERMOGRAPHY/Magnet-1/Defects/INV_WISE_DEFECTS/'
    thermal_image_path = '/media/deepanshu/Seagate Expansion Drive/AERIAL_THERMOGRAPHY/Magnet-1/GIS_TO_AUTOMATION/Fullgreyscale/Fullgreyscale.tif'
    output_shape_file = '/media/deepanshu/Seagate Expansion Drive/AERIAL_THERMOGRAPHY/Magnet-1/Defects/INV_WISE_DEFECTS_with_modno/'

    for table in os.listdir(model_path):
        print(model_path + table)
        model_dataframe = read_kml(model_path + table)
        # print(model_dataframe)
        print(defect_path + table)
        defect_dataframe = read_kml(defect_path + table)
        thermal_image = read_geotiff(thermal_image_path)
        defect_dataframe = process_data(model_dataframe, defect_dataframe, thermal_image)
        modules_dataframe_based_on_type_path = os.path.join(output_shape_file, table)
        # print(modules_dataframe_based_on_type_path)
        write_kml(defect_dataframe, modules_dataframe_based_on_type_path)
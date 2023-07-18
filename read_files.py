import geopandas as gpd
from osgeo import gdal
import fiona

fiona.drvsupport.supported_drivers['LIBKML'] = 'rw'
fiona.drvsupport.supported_drivers['libkml'] = 'rw'
fiona.drvsupport.supported_drivers['KML'] = 'rw'
fiona.drvsupport.supported_drivers['kml'] = 'rw'


def read_shp(path):
    dataframe = gpd.read_file(path)
    return dataframe


def write_shp(dataframe, path):
    dataframe.to_file(driver='ESRI Shapefile', filename=path)


def read_kml(path):
    dataframe = gpd.read_file(path, driver='kml')
    return dataframe


def write_kml(dataframe, path):
    dataframe.to_file(driver='KML', filename=path)


def read_geotiff(path):
    image = gdal.Open(path)
    return image


from osgeo import osr


def get_image_proj_transform(image):
    proj = osr.SpatialReference(wkt=image.GetProjection())
    epsg = proj.GetAttrValue('AUTHORITY', 1)
    geoTrans = image.GetGeoTransform()
    return epsg, geoTrans
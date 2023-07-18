from datetime import datetime
start_time = datetime.now()

# ================================== Import Packages ======================================================
import cv2
import numpy as np
import re
from osgeo import gdal
from pykml import parser
import simplekml
from pyproj import Proj, transform
import gdal
from skimage.io import imread
import os
from matplotlib import pyplot as plt
cv2.useOptimized()
from pathlib import Path
import pandas as pd
from shapely.geometry import Point
import geo


CAD = '/media/deepanshu/Seagate Expansion Drive/AERIAL_THERMOGRAPHY/Magnet-1/CAD/Final_CAD.kml'

BOUND = '/media/deepanshu/Seagate Expansion Drive/AERIAL_THERMOGRAPHY/Magnet-1/GIS_TO_AUTOMATION/KML/Inverter_Boundary.kml'

out = '/media/deepanshu/Seagate Expansion Drive/AERIAL_THERMOGRAPHY/Magnet-1/Defects/INV_MOD_CAD'


def KMLgen(features,KML_name,des):

    kml = simplekml.Kml()
    i = 0
    for row in features:
        pol = kml.newpolygon(outerboundaryis=[(row[0][0], row[0][1]),
                                                              (row[1][0], row[1][1]),
                                                              (row[2][0], row[2][1]),
                                                              (row[3][0], row[3][1]),
                                                              (row[0][0], row[0][1])])
        pol.description = des[i]

        i+=1
    kml.save(KML_name)


coords , INVERTER = geo.polyRead(BOUND)
CAD_kml , des = geo.polyRead(CAD)


from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from shapely import geometry
from shapely.geometry import MultiPoint


for i in range(len(coords)):
    name = INVERTER[i].split("Inverter No: ")[1].split('</description>')[0]
    name = name.replace(' ', '')
    name = name.replace('\n', '')
    print(name)
    polys = []
    descript = []

    poly = geometry.Polygon([[float(p[0]), float(p[1])] for p in coords[i]])
    print(poly)
    for j in range(len(CAD_kml)):

        g = [(float(i[0]),float(i[1])) for i in CAD_kml[j]]

        points = MultiPoint(g)
        p = points.centroid
        print(p)
        if poly.contains(p):
            polys.append(CAD_kml[j])
            descript.append(des[j])

    kml_name = out+'/'+name+'.kml'
    if len(polys)> 0 :
        KMLgen(polys,kml_name ,descript)


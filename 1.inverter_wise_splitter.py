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



CAD = '/media/deepanshu/Seagate Expansion Drive/AERIAL_THERMOGRAPHY/Magnet-1/GIS_TO_AUTOMATION/KML/Thermal_Defects.kml'

BOUND = '/media/deepanshu/Seagate Expansion Drive/AERIAL_THERMOGRAPHY/Magnet-1/GIS_TO_AUTOMATION/KML/Inverter_Boundary.kml'

out = '/media/deepanshu/Seagate Expansion Drive/AERIAL_THERMOGRAPHY/Magnet-1/Defects/INV_WISE_DEFECTS'


def tupler(coords):
    coords_add=[]
    for i in coords:
        h =[]
        for j in i:
            h.append(tuple(j))
        h.append(tuple(i[0]))
        coords_add.append(h)

    coords_new =[]
    for i in coords_add:
        coords_new.append([tuple(j) for j in i])
    return coords_new

def KMLgen(features,KML_name,des):

    kml = simplekml.Kml()
    i = 0
    for row in features:
        pol = kml.newpoint(coords=[row])
        # pol = kml.newpolygon(outerboundaryis=row)
        pol.description = des[i]

        i+=1
    kml.save(KML_name)


def read_kml(kml_file, kml_type='CAD'):
    f = open(kml_file, "r")
    docs = parser.parse(f)
    try:
        doc = docs.getroot().Document.Folder

    except:
        try:
            doc = docs.getroot().Document
        except:

            return
    # ===================================== Load KML and append the Data in variable ============================

    coords = []
    des = []
    for place in doc.Placemark:
        x = str(place.Polygon.outerBoundaryIs.LinearRing.coordinates)

        v = re.findall("\d+\.\d+\d+\d+\d+\d+\d+", x)

        c = []
        for i in range(0, len(v) - 2, 2):
            c.append([float(v[i]), float(v[i + 1])])

        coords.append(c)

        if kml_type == 'CAD':

            INVERTER = str(place.description)
            # INVERTER = INVERTER.split(' ')
            # INVERTER = INVERTER[-1]
            des.append(INVERTER)
        else:
            INVERTER = str(place.description)
            INVERTER = INVERTER.split("Inverter No:")[1].split('</description>')[0]
            INVERTER = INVERTER.replace(' ', '')
            INVERTER = INVERTER.replace('\n', '')
            # INVERTER = INVERTER[-1]
            des.append(INVERTER)

    print('number of Coordinates Extracted from KML is',len(coords))

    return coords , des


def readkml(kml_file):

    f = open(kml_file, "r")
    docs = parser.parse(f)
    try:
        doc = docs.getroot().Document.Folder

    except:
        doc = docs.getroot().Document
    temp = []
    class_coords = []
    descript =[]
    coo = []
    for place in doc.Placemark:
        y= str(place.Point.coordinates)
        y=y.split(",")
        y = float(y[0]), (float(y[1]))
        x = str(place.description)
        class_coords.append(y)
        descript.append(x)

    return class_coords , descript

def list_to_tuple(list):
    k = []
    for g in list:
        k.append(tuple(g))
    return k

# ===================================== Load KML and append the Data in variable ============================


coords , INVERTER = read_kml(BOUND,'bound')

CAD_kml , des = readkml(CAD)


print('number of coordinates',len(coords))
print('number of INVERTERS is',len(INVERTER))

from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from shapely import geometry
from shapely.geometry import MultiPoint

for i in range(len(coords)):
    name = INVERTER[i]
    polys = []
    descript = []

    poly = geometry.Polygon([[p[0], p[1]] for p in coords[i]])

    for j in range(len(CAD_kml)):

        # points = MultiPoint(list_to_tuple(CAD_kml[j]))
        # p = points.centroid
        x = CAD_kml[j][0],CAD_kml[j][1]
        p = Point(CAD_kml[j])

        if poly.contains(p):
            polys.append(CAD_kml[j])
            descript.append(des[j])


    # polys = tupler(polys)
    kml_name = out+'/'+name+'.kml'
    if len(polys)> 0:
        KMLgen(polys,kml_name ,descript)



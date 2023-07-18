from datetime import datetime
start_time = datetime.now()
import rem

# ================================== Import Packages ======================================================
from pykml import parser
import simplekml
import cv2
import os
from natsort import natsorted


from pathlib import Path
cv2.useOptimized()

KML_PATH = "/media/deepanshu/Seagate Expansion Drive/AERIAL_THERMOGRAPHY/Magnet-1/CAD"
OUT_PUT_PATH = '/media/deepanshu/Seagate Expansion Drive/AERIAL_THERMOGRAPHY/Magnet-1/CAD/split'


def KMLgen(feature, name):
    # =============================================== Export As a KML ==================================================

    kml = simplekml.Kml()
    # print(feature)
    for i in range(len(feature)):
        # print(feature[i])
        pol = kml.newpolygon(outerboundaryis=feature[i])


    kml.save(name)

string = ['1']



def readkml(kml_file,string):

    f = open(kml_file, "r")
    docs = parser.parse(f)
    try:
        doc = docs.getroot().Document.Folder

    except:
        doc = docs.getroot().Document
    # print('number of features in KML is', len(doc.Placemark))
    coo = []
    for place in doc.Placemark:
        x = str(place.description)
        pan = x.split('STRING_ID:')[1].split('Defects:')[0]
        pan = pan.replace(' ', '')
        pan = pan.replace('\n', '')
        #print(pan)
        if pan == string:
            print(pan)
            x = str(place.Polygon.outerBoundaryIs.LinearRing.coordinates)
            v = re.findall("\d+\.\d+\d+\d+", x)
            c = []
            for i in range(0, len(v), 2):
                # print("i",i)
                c.append([float(v[i]), float(v[i + 1])])

            # c.append([float(v[0]), float(v[1])])
            coo.append(c)
    return coo

path =[]
for root, directories, filenames in os.walk(KML_PATH):
    for filename in filenames:
        path.append(os.path.join(root,filename))

path = list(natsorted(path))
print(path)

def split(path,string):
    for i in range(len(string)):

        v = Path(path).name
        file = v.replace(".", " ").split()[0]

        if not os.path.exists(OUT_PUT_PATH+'/'+str(file)):
            os.makedirs(OUT_PUT_PATH+'/' +str(file))
        data = readkml(path,string[i])

        KMLgen(data,OUT_PUT_PATH+'/'+str(file)+"/"+string[i]+".kml")

for i in range(len(path)):

    if not os.path.exists(OUT_PUT_PATH ):
        os.makedirs(OUT_PUT_PATH )

    split(path[i],string)

# -------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      tabea
#
# Created:     23/03/2020
# Copyright:   (c) tabea 2020
# Licence:     <your licence>
# -------------------------------------------------------------------------------

def main():
    pass


import os
import string
import re
import json
import time

# Libraries that need to be installed from 3rd parties
import numpy

# ... for Web scraping
import requests
import sys
import foursquare
import json
import csv
from itertools import chain
import pandas as pd

### what category do you want to fetch? Uncomment only the one that you need!

# category_name = "Food" ##Foursquare category Food
# category = '4d4b7105d754a06374d81259'

# category_name = "ArtsEntertainment" ##Foursquare category Nighlife Spot
# category = '4d4b7104d754a06370d81259'

# category_name = "Nightlife"  ##Foursquare category Nighlife Spot
# category = '4d4b7105d754a06376d81259'

# category_name = "College_Uni" ##Foursquare category College & University
# category = '4d4b7105d754a06372d81259'
#
category_name = "Outdoors_Recreation" ##Foursquare category Outdoors & Recreation
category = '4d4b7105d754a06377d81259'
#
# category_name = "ShopsServ" ##Foursquare category Shop and Services
# category = '4d4b7105d754a06378d81259'
# #
# category_name = "Profess_other"  ##Foursquare category Professional and other places
# category = '4d4b7105d754a06375d81259'


def coordinate_seq(coord, n):
    return [coord + (0.001 * n) for n in range(1, n + 1)]


## set here the coordinate box for which you want to fetch Foursquare data
## (in WG84, e.g. Google Maps corrdinates)

# Amsterdam coordinate box WG84
# 52.256203, 4.706479
# 52.471075, 5.077090

minlat = 52.250
minlon = 4.706
lat_extent = 300
lon_extent = 300
latitude_sequence = coordinate_seq(coord=minlat, n=lat_extent)
longitude_sequence = coordinate_seq(coord=minlon, n=lon_extent)

print(latitude_sequence[1])
print(longitude_sequence[1])

coordinatedict = []

i = 0
while i < (lat_extent - 1):
    x = 0
    coordinates = []
    while x < (lon_extent - 1):
        coordinates.append(str(latitude_sequence[i]) + ', ' + str(longitude_sequence[x]))
        x += 1
    coordinatedict.append(coordinates)
    i += 1

clientid_list = ['AGXJHQICGJPFIS213RVXIC4K1YYL2OVCIWIAMZYB1POBUR2A',
                 'DMOHFINUSZSKWFFIXAJQLBTYTIJKDC1TFUEIYWRTHXBOHLGT',
                 'YKCEGK2Y23DLC235QLD2TQC2KGVHVVLGSXKVERU5WDFY0HNS',
                 'AVAJ0TEQDREV003M15W15E1QRZHCD4XXFY310EFEVEOSPEFC',
                 '4QSBFBGZ12JS0B0JBYPG0VUEWPWUPM5BMFQGQPPM21QIBYXT',
                 'RV2KWDAL03AFC3TYMBHTXGRWTM0JA4YCAC4CZWDT500PGKOB',
                 '0K2JWOCMJBXC3VCV0WH1SD3BEC5HXM1P1SXV455BFXXEOL5B']
clientsecr_list = ['HQARUEPUG31GK5RUBE5L0T1L3G3QIALZZFJSVIPTQ2WQAEXO',
                   'F5MRESLTMXEGP4LW3XATD5T0CNK15HOLVUX1WNBCHSAW3SZL',
                   'IARXE4FXOMLKRSZKUOGZ2G2UQLGFKK42M2UJ0EPX1O5DEPG2',
                   'CH3DMZQK1VMFJAUF0KT3JJNOTDED55KPGES3J2O2OS2MOT5O',
                   'S2ZRSKGD3KHSSKAA0U1TAH1I0WL3LBU2MO0MGIZSEE23JANZ',
                   'YJP1BZODIUDPVVA0N1DW45PJRXZGQUOZ1MWAJ4UVNUZNJAFV',
                   'AV01NROCD1GVTFU3XCLFUJRITL1UH04KK3KQSAFCSV33SHZO']

client = foursquare.Foursquare(client_id=str(clientid_list[1]), client_secret=str(clientsecr_list[1]))
Foursquarevenues = client.venues.search(
    params={'sw': str(coordinatedict[0][0]), 'ne': str(coordinatedict[1][1]), 'intent': 'browse',
            'categoryId': str(category)})

print(Foursquarevenues)

Foursquarevenues_tot = []

j = 0
x = 0
s = (len(coordinatedict) - 1)
while j < s:
    while x <= (len(clientid_list) - 1) and j < s:
        h = j + 15
        while j < h and j < s:
            clientid = clientid_list[x]
            clientsecr = clientsecr_list[x]
            i = 0
            while i < (len(coordinatedict[j]) - 1):
                client = foursquare.Foursquare(client_id=str(clientid), client_secret=str(clientsecr))
                Foursquarevenues_2 = client.venues.search(
                    params={'sw': str(coordinatedict[j][i]), 'ne': str(coordinatedict[j + 1][i + 1]),
                            'intent': 'browse',
                            'limit': '50', 'categoryId': str(category)})
                Foursquarevenues_tot.append(Foursquarevenues_2.items())
                i += 1
            j += 1
        x += 1
        print("completed boxes: " + str(0) + "-" + str(j) + " of " + str(s))
    if j >= s:
        print("total completed")
    else:
        time.sleep(1001)
        x = 0


def writeJson(dictionary, outfile):
    with open(outfile, 'w') as fp:
        fp.seek(0)
        dict2 = list(chain.from_iterable(dictionary))
        json.dump(dict2, fp)
        fp.close()


def main():
    os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Data\Amsterdam\Foursquare")
    city = "Amsterdam"
    jsonfile1 = os.path.join(os.getcwd(), city + "_Foursquarevenues_" + category_name + '.json')
    writeJson(Foursquarevenues_tot, jsonfile1)


print(Foursquarevenues_tot)

if __name__ == '__main__':
    main()

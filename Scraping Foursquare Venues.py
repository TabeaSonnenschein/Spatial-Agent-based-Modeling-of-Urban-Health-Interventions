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


import numbers
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

import pandas as pd

##          'categoryId': '4d4b7105d754a06374d81259',       #Food
##          'categoryId': '4d4b7104d754a06370d81259',       #Arts & Entertainment
##          'categoryId': '4d4b7105d754a06372d81259',       #College & University
##          'categoryId': '4d4b7105d754a06373d81259',       #Event
##          'categoryId': '4d4b7105d754a06376d81259',       #Nighlife Spot
##          'categoryId': '4d4b7105d754a06377d81259',       #Outdoors & Recreation
##          categoryId= '4d4b7105d754a06375d81259',       #Professional and other places
##          categoryId= '4d4b7105d754a06378d81259',       #Shop and Services
##          categoryId= '4d4b7105d754a06379d81259',       #Travel & Transport
##          categoryId= '4e67e38e036454776db1fb3a',       #Residence

category = '4d4b7105d754a06374d81259'


####
##clientid = '4QSBFBGZ12JS0B0JBYPG0VUEWPWUPM5BMFQGQPPM21QIBYXT'
##clientsecr = 'S2ZRSKGD3KHSSKAA0U1TAH1I0WL3LBU2MO0MGIZSEE23JANZ'

##clientid = 'VD5JRI5HLXSD21ZJUALG0K4BJOAVJNBIUXUNJDSDHERAYSA0'
##clientsecr= 'J3SNUNCWZ4NCJU1YLP211M4K5ATSBEYRT12VFPNXC4RMYQ5Z'

##
##clientid ='RV2KWDAL03AFC3TYMBHTXGRWTM0JA4YCAC4CZWDT500PGKOB'
##clientsecr = '1DUD0P3YPUWDAXOTJUM5KZTUMMOXSRXIYHIXWKAB41Z2BFBU'

##clientid ='0K2JWOCMJBXC3VCV0WH1SD3BEC5HXM1P1SXV455BFXXEOL5B'
##clientsecr = 'AV01NROCD1GVTFU3XCLFUJRITL1UH04KK3KQSAFCSV33SHZO'

##clientid ='AGXJHQICGJPFIS213RVXIC4K1YYL2OVCIWIAMZYB1POBUR2A'
##clientsecr = 'HQARUEPUG31GK5RUBE5L0T1L3G3QIALZZFJSVIPTQ2WQAEXO'


def coordinate_seq(coord, n):
    return [coord + (0.001 * n) for n in range(1, n + 1)]

# Amsterdam coordinate box WG84
# 52.256203, 4.706479
# 52.471075, 5.077090

minlat = 52.250
minlon = 4.706
lat_extent = 300
lon_extent = 300
latitude_sequence = coordinate_seq( coord = minlat, n=lat_extent)
longitude_sequence = squarescoordinateslon( coord = minlon,n=lon_extent)

print(latitude_sequence[1])
print(longitude_sequence[1])

coordinatedict = []

i = 0
x = 0
while i < (lat_extent-1):
    coordinates = []
    while x < (lon_extent-1):
        coordinates.append(str(latitude_sequence[i]) + ', ' + str(longitude_sequence[x]))
        x += 1
    coordinatedict.append(coordinates)
    i += 1


print(coordinatedict)
print(len(coordinatedict))

clientid = 'DMOHFINUSZSKWFFIXAJQLBTYTIJKDC1TFUEIYWRTHXBOHLGT'
clientsecr = 'F5MRESLTMXEGP4LW3XATD5T0CNK15HOLVUX1WNBCHSAW3SZL'

client = foursquare.Foursquare(client_id=str(clientid), client_secret=str(clientsecr), version=str(date))
Foursquarevenues = client.venues.search(
    params={'sw': str(coordinatedict[0][0]), 'ne': str(coordinatedict[1][1]), 'intent': 'browse', 'categoryId': str(category)})

print(Foursquarevenues)


Foursquarevenues_tot = []

clientid_list = [ 'AGXJHQICGJPFIS213RVXIC4K1YYL2OVCIWIAMZYB1POBUR2A', 'DMOHFINUSZSKWFFIXAJQLBTYTIJKDC1TFUEIYWRTHXBOHLGT', 'YKCEGK2Y23DLC235QLD2TQC2KGVHVVLGSXKVERU5WDFY0HNS',
                  'AVAJ0TEQDREV003M15W15E1QRZHCD4XXFY310EFEVEOSPEFC','4QSBFBGZ12JS0B0JBYPG0VUEWPWUPM5BMFQGQPPM21QIBYXT', 'RV2KWDAL03AFC3TYMBHTXGRWTM0JA4YCAC4CZWDT500PGKOB', '0K2JWOCMJBXC3VCV0WH1SD3BEC5HXM1P1SXV455BFXXEOL5B']
clientsecr_list = [ 'HQARUEPUG31GK5RUBE5L0T1L3G3QIALZZFJSVIPTQ2WQAEXO','F5MRESLTMXEGP4LW3XATD5T0CNK15HOLVUX1WNBCHSAW3SZL','IARXE4FXOMLKRSZKUOGZ2G2UQLGFKK42M2UJ0EPX1O5DEPG2',
                    'CH3DMZQK1VMFJAUF0KT3JJNOTDED55KPGES3J2O2OS2MOT5O', 'S2ZRSKGD3KHSSKAA0U1TAH1I0WL3LBU2MO0MGIZSEE23JANZ', 'YJP1BZODIUDPVVA0N1DW45PJRXZGQUOZ1MWAJ4UVNUZNJAFV', 'AV01NROCD1GVTFU3XCLFUJRITL1UH04KK3KQSAFCSV33SHZO']
j = 0
x = 0
s = len(coordinatedict)
while j < s:
    while x <= len(clientid_list):
        h = j + 20
        while j < h:
           clientid = clientid_list[0]
           clientsecr = clientsecr_list[0]
           i = 0
           while i < (len(coordinatedict[j]) - 1):
                client = foursquare.Foursquare(client_id=str(clientid), client_secret=str(clientsecr))
                Foursquarevenues_2 = client.venues.search(
                     params={'sw': str(coordinatedict[j][i]), 'ne': str(coordinatedict[j+1][i + 1]), 'intent': 'browse',
                        'limit': '50', 'categoryId': str(category)})
                Foursquarevenues_tot.append(Foursquarevenues_2.items())
                i += 1
           j += 1
        x += 1
    print("completed diagonals: " + str(j) + "-" + str(h))
    if j >= s:
        print("total completed")
    else:
        time.sleep(1701)
        x = 0



def writeJson(dictionary, outfile):
    with open(outfile, 'w') as fp:
        fp.seek(0)
        json.dump(dictionary, fp)
        fp.close()


def main():
    os.chdir("C:\Dokumente\Utrecht\Master_these\Data\Foursquare")
    jsonfile1 = os.path.join(os.getcwd(), 'MilanFoursquaring_Food2' + date + '.json')
    writeJson(Foursquarevenues_tot, jsonfile1)


if __name__ == '__main__':
    main()

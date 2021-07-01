#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      tabea
#
# Created:     23/03/2020
# Copyright:   (c) tabea 2020
# Licence:     <your licence>
#-------------------------------------------------------------------------------

def main():
    pass


import numbers
import os
import string
import re
import json
import time

#Libraries that need to be installed from 3rd parties
import numpy

#... for Web scraping
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

date = '20190701'
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

#have scraped: 45.38, 45.66
#have scraped: 9.05, 9.33

#need: 9.52, 8.69 --> 830
#need: 45.31, 45.87 --> 560

##9.33 - 9.52 --> 190
## 8.69 - 9.05 --> 360

## 45.31 -45.48 --> 70
## 45.66 - 45.87 --> 200


#45.38 +490
#8.69 + 360

## 45.66 + 200
## 9.19+ 200

##45.45 + 280
##9.33 + 190

## 45.31 + 70
## 9.10 + 230

#52.256203, 4.706479
#52.471075, 5.077090
def squarescoordinateslat(n):
    return [52.250 + (0.001*n) for n in range(1, n + 1)]


latitude_sequence = squarescoordinateslat(n= 300)
print(latitude_sequence[1])

def squarescoordinateslon(n):
    return [4.70 + (0.001*n) for n in range(1, n + 1)]


longitude_sequence = squarescoordinateslon(n= 300)
print(longitude_sequence[1])


coordinates_1 = str(latitude_sequence[0]) + ', ' + str(longitude_sequence[0])
coordinates_2 = str(latitude_sequence[1]) + ', ' + str(longitude_sequence[1])

coordinates = [coordinates_1, coordinates_2]



i= 1
while i < 299:
    coordinates.append(str(latitude_sequence[i])+ ', ' + str(longitude_sequence[i]))
    i += 1


coordinates2_1 = str(latitude_sequence[0]) + ', ' + str(longitude_sequence[1])
coordinates2_2 = str(latitude_sequence[1]) + ', ' + str(longitude_sequence[2])

coordinates2 = [coordinates2_1, coordinates2_2]

e= 1
while e < 299:
    coordinates2.append(str(latitude_sequence[e])+ ', ' + str(longitude_sequence[e+1]))
    e += 1


coordinates3_1 = str(latitude_sequence[1]) + ', ' + str(longitude_sequence[0])
coordinates3_2 = str(latitude_sequence[2]) + ', ' + str(longitude_sequence[1])

coordinates3 = [coordinates3_1, coordinates3_2]

m= 2
while m < 499:
    coordinates3.append(str(latitude_sequence[m+1])+ ', ' + str(longitude_sequence[m]))
    m += 1


coordinatedict = [coordinates, coordinates2, coordinates3]


f= 1
while f < 498:
    coordinates_up_1 = (str(latitude_sequence[0]) + ', ' + str(longitude_sequence[f]))
    coordinates_up_2 = (str(latitude_sequence[1]) + ', ' + str(longitude_sequence[f+1]))
    coordinates_up = [coordinates_up_1, coordinates_up_2]
    m = 2
    while m < (498-f):
        coordinates_up.append(str(latitude_sequence[m])+ ', ' + str(longitude_sequence[m+f]))
        m+=1
    coordinatedict.append(coordinates_up)
    f+=1



f= 1
while f < 498:
    coordinates_down_1 = (str(latitude_sequence[f]) + ', ' + str(longitude_sequence[0]))
    coordinates_down_2 = (str(latitude_sequence[f+1]) + ', ' + str(longitude_sequence[1]))
    coordinates_down = [coordinates_down_1, coordinates_down_2]
    m = 2
    while m < (498-f):
        coordinates_down.append(str(latitude_sequence[m+f])+ ', ' + str(longitude_sequence[m]))
        m+=1
    coordinatedict.append(coordinates_down)
    f+=1



##print(coordinatedict)

print(len(coordinatedict))

clientid ='DMOHFINUSZSKWFFIXAJQLBTYTIJKDC1TFUEIYWRTHXBOHLGT'
clientsecr = 'F5MRESLTMXEGP4LW3XATD5T0CNK15HOLVUX1WNBCHSAW3SZL'

client = foursquare.Foursquare(client_id= str(clientid), client_secret= str(clientsecr), version = str(date))
Foursquarevenues = client.venues.search(params={'sw': str(coordinates[1]), 'ne': str(coordinates[2]), 'intent' : 'browse', 'categoryId': str(category)})

print(Foursquarevenues)

client = foursquare.Foursquare(client_id= str(clientid), client_secret= str(clientsecr), version = str(date))
Foursquarevenues_2 = client.venues.search(params={'sw': str(coordinates[2]), 'ne': str(coordinates[3]), 'intent' : 'browse', 'limit': '50', 'categoryId': str(category)})

Foursquarevenues_tot = [Foursquarevenues.items(), Foursquarevenues_2.items()]


r = 0
s = 210
while r< s:
    j= r
    h = j + 10
    while j< h:
        clientid ='AGXJHQICGJPFIS213RVXIC4K1YYL2OVCIWIAMZYB1POBUR2A'
        clientsecr = 'HQARUEPUG31GK5RUBE5L0T1L3G3QIALZZFJSVIPTQ2WQAEXO'
        i = 0
        while i < (len(coordinatedict[j])-1):
            client = foursquare.Foursquare(client_id= str(clientid), client_secret= str(clientsecr), version = str(date))
            Foursquarevenues_3 = client.venues.search(params={'sw': str(coordinatedict[j][i]), 'ne': str(coordinatedict[j][i+1]), 'intent' : 'browse', 'limit': '50', 'categoryId': str(category)})
            Foursquarevenues_tot.append(Foursquarevenues_3.items())
            i+=1
        j+= 1
    print("completed diagonals: " + str(r) +"-" + str(h))
    z= h + 10
    while h < z:
        clientid ='DMOHFINUSZSKWFFIXAJQLBTYTIJKDC1TFUEIYWRTHXBOHLGT'
        clientsecr = 'F5MRESLTMXEGP4LW3XATD5T0CNK15HOLVUX1WNBCHSAW3SZL'
        i = 0
        while i < (len(coordinatedict[h])-1):
            client = foursquare.Foursquare(client_id= str(clientid), client_secret= str(clientsecr), version = str(date))
            Foursquarevenues_3 = client.venues.search(params={'sw': str(coordinatedict[h][i]), 'ne': str(coordinatedict[h][i+1]), 'intent' : 'browse', 'limit': '50', 'categoryId': str(category)})
            Foursquarevenues_tot.append(Foursquarevenues_3.items())
            i+=1
        h+= 1
    print("completed diagonals: " + str(z-10) +"-" + str(z))
    q = z + 10
    while z < q:
        clientid ='YKCEGK2Y23DLC235QLD2TQC2KGVHVVLGSXKVERU5WDFY0HNS'
        clientsecr = 'IARXE4FXOMLKRSZKUOGZ2G2UQLGFKK42M2UJ0EPX1O5DEPG2'
        i = 0
        while i < (len(coordinatedict[z])-1):
            client = foursquare.Foursquare(client_id= str(clientid), client_secret= str(clientsecr), version = str(date))
            Foursquarevenues_3 = client.venues.search(params={'sw': str(coordinatedict[z][i]), 'ne': str(coordinatedict[z][i+1]), 'intent' : 'browse', 'limit': '50', 'categoryId': str(category)})
            Foursquarevenues_tot.append(Foursquarevenues_3.items())
            i+=1
        z+= 1
    print("completed diagonals: " + str(q-10) +"-" + str(q))
    h = q + 10
    while q < h:
        clientid ='AVAJ0TEQDREV003M15W15E1QRZHCD4XXFY310EFEVEOSPEFC'
        clientsecr = 'CH3DMZQK1VMFJAUF0KT3JJNOTDED55KPGES3J2O2OS2MOT5O'
        i = 0
        while i < (len(coordinatedict[q])-1):
            client = foursquare.Foursquare(client_id= str(clientid), client_secret= str(clientsecr), version = str(date))
            Foursquarevenues_3 = client.venues.search(params={'sw': str(coordinatedict[q][i]), 'ne': str(coordinatedict[q][i+1]), 'intent' : 'browse', 'limit': '50', 'categoryId': str(category)})
            Foursquarevenues_tot.append(Foursquarevenues_3.items())
            i+=1
        q+= 1
    print("completed diagonals: " + str(h-10) +"-" + str(h))
    k= h + 10
    while h< k:
        clientid = '4QSBFBGZ12JS0B0JBYPG0VUEWPWUPM5BMFQGQPPM21QIBYXT'
        clientsecr = 'S2ZRSKGD3KHSSKAA0U1TAH1I0WL3LBU2MO0MGIZSEE23JANZ'
        i = 0
        while i < (len(coordinatedict[h])-1):
            client = foursquare.Foursquare(client_id= str(clientid), client_secret= str(clientsecr), version = str(date))
            Foursquarevenues_3 = client.venues.search(params={'sw': str(coordinatedict[h][i]), 'ne': str(coordinatedict[h][i+1]), 'intent' : 'browse', 'limit': '50', 'categoryId': str(category)})
            Foursquarevenues_tot.append(Foursquarevenues_3.items())
            i+=1
        h+= 1
    print("completed diagonals: " + str(k-10) +"-" + str(k))
    z = k + 10
    while k < z:
        clientid ='RV2KWDAL03AFC3TYMBHTXGRWTM0JA4YCAC4CZWDT500PGKOB'
        clientsecr = 'YJP1BZODIUDPVVA0N1DW45PJRXZGQUOZ1MWAJ4UVNUZNJAFV'
        i = 0
        while i < (len(coordinatedict[k])-1):
            client = foursquare.Foursquare(client_id= str(clientid), client_secret= str(clientsecr), version = str(date))
            Foursquarevenues_3 = client.venues.search(params={'sw': str(coordinatedict[k][i]), 'ne': str(coordinatedict[k][i+1]), 'intent' : 'browse', 'limit': '50', 'categoryId': str(category)})
            Foursquarevenues_tot.append(Foursquarevenues_3.items())
            i+=1
        k+= 1
    print("completed diagonals: " + str(z-10) +"-" + str(z))
    q = z + 10
    while z < q:
        clientid ='0K2JWOCMJBXC3VCV0WH1SD3BEC5HXM1P1SXV455BFXXEOL5B'
        clientsecr = 'AV01NROCD1GVTFU3XCLFUJRITL1UH04KK3KQSAFCSV33SHZO'
        i = 0
        while i < (len(coordinatedict[z])-1):
            client = foursquare.Foursquare(client_id= str(clientid), client_secret= str(clientsecr), version = str(date))
            Foursquarevenues_3 = client.venues.search(params={'sw': str(coordinatedict[z][i]), 'ne': str(coordinatedict[z][i+1]), 'intent' : 'browse', 'limit': '50', 'categoryId': str(category)})
            Foursquarevenues_tot.append(Foursquarevenues_3.items())
            i+=1
        z+= 1
    print("completed diagonals: " + str(q-10) +"-" + str(q))
    if q >= s:
        print("total completed")
    else:
        time.sleep(1701)
    r = q

time.sleep(1701)

r = 210
s = 315
while r< s:
    j= r
    h = j + 15
    while j< h:
        clientid ='YKCEGK2Y23DLC235QLD2TQC2KGVHVVLGSXKVERU5WDFY0HNS'
        clientsecr = 'IARXE4FXOMLKRSZKUOGZ2G2UQLGFKK42M2UJ0EPX1O5DEPG2'
        i = 0
        while i < (len(coordinatedict[j])-1):
            client = foursquare.Foursquare(client_id= str(clientid), client_secret= str(clientsecr), version = str(date))
            Foursquarevenues_3 = client.venues.search(params={'sw': str(coordinatedict[j][i]), 'ne': str(coordinatedict[j][i+1]), 'intent' : 'browse', 'limit': '50', 'categoryId': str(category)})
            Foursquarevenues_tot.append(Foursquarevenues_3.items())
            i+=1
        j+= 1
    print("completed diagonals: " + str(r) +"-" + str(h))
    z= h + 15
    while h < z:
        clientid ='DMOHFINUSZSKWFFIXAJQLBTYTIJKDC1TFUEIYWRTHXBOHLGT'
        clientsecr = 'F5MRESLTMXEGP4LW3XATD5T0CNK15HOLVUX1WNBCHSAW3SZL'
        i = 0
        while i < (len(coordinatedict[h])-1):
            client = foursquare.Foursquare(client_id= str(clientid), client_secret= str(clientsecr), version = str(date))
            Foursquarevenues_3 = client.venues.search(params={'sw': str(coordinatedict[h][i]), 'ne': str(coordinatedict[h][i+1]), 'intent' : 'browse', 'limit': '50', 'categoryId': str(category)})
            Foursquarevenues_tot.append(Foursquarevenues_3.items())
            i+=1
        h+= 1
    print("completed diagonals: " + str(z-15) +"-" + str(z))
    q = z + 15
    while z < q:
        clientid ='AGXJHQICGJPFIS213RVXIC4K1YYL2OVCIWIAMZYB1POBUR2A'
        clientsecr = 'HQARUEPUG31GK5RUBE5L0T1L3G3QIALZZFJSVIPTQ2WQAEXO'
        i = 0
        while i < (len(coordinatedict[z])-1):
            client = foursquare.Foursquare(client_id= str(clientid), client_secret= str(clientsecr), version = str(date))
            Foursquarevenues_3 = client.venues.search(params={'sw': str(coordinatedict[z][i]), 'ne': str(coordinatedict[z][i+1]), 'intent' : 'browse', 'limit': '50', 'categoryId': str(category)})
            Foursquarevenues_tot.append(Foursquarevenues_3.items())
            i+=1
        z+= 1
    print("completed diagonals: " + str(q-15) +"-" + str(q))
    h = q + 15
    while q< h:
        clientid ='AVAJ0TEQDREV003M15W15E1QRZHCD4XXFY310EFEVEOSPEFC'
        clientsecr = 'CH3DMZQK1VMFJAUF0KT3JJNOTDED55KPGES3J2O2OS2MOT5O'
        i = 0
        while i < (len(coordinatedict[q])-1):
            client = foursquare.Foursquare(client_id= str(clientid), client_secret= str(clientsecr), version = str(date))
            Foursquarevenues_3 = client.venues.search(params={'sw': str(coordinatedict[q][i]), 'ne': str(coordinatedict[q][i+1]), 'intent' : 'browse', 'limit': '50', 'categoryId': str(category)})
            Foursquarevenues_tot.append(Foursquarevenues_3.items())
            i+=1
        q+= 1
    print("completed diagonals: " + str(h-15) +"-" + str(h))
    k= h + 15
    while h< k:
        clientid = '4QSBFBGZ12JS0B0JBYPG0VUEWPWUPM5BMFQGQPPM21QIBYXT'
        clientsecr = 'S2ZRSKGD3KHSSKAA0U1TAH1I0WL3LBU2MO0MGIZSEE23JANZ'
        i = 0
        while i < (len(coordinatedict[h])-1):
            client = foursquare.Foursquare(client_id= str(clientid), client_secret= str(clientsecr), version = str(date))
            Foursquarevenues_3 = client.venues.search(params={'sw': str(coordinatedict[h][i]), 'ne': str(coordinatedict[h][i+1]), 'intent' : 'browse', 'limit': '50', 'categoryId': str(category)})
            Foursquarevenues_tot.append(Foursquarevenues_3.items())
            i+=1
        h+= 1
    print("completed diagonals: " + str(k-15) +"-" + str(k))
    z = k + 15
    while k < z:
        clientid ='RV2KWDAL03AFC3TYMBHTXGRWTM0JA4YCAC4CZWDT500PGKOB'
        clientsecr = 'YJP1BZODIUDPVVA0N1DW45PJRXZGQUOZ1MWAJ4UVNUZNJAFV'
        i = 0
        while i < (len(coordinatedict[k])-1):
            client = foursquare.Foursquare(client_id= str(clientid), client_secret= str(clientsecr), version = str(date))
            Foursquarevenues_3 = client.venues.search(params={'sw': str(coordinatedict[k][i]), 'ne': str(coordinatedict[k][i+1]), 'intent' : 'browse', 'limit': '50', 'categoryId': str(category)})
            Foursquarevenues_tot.append(Foursquarevenues_3.items())
            i+=1
        k+= 1
    print("completed diagonals: " + str(z-15) +"-" + str(z))
    q = z + 15
    while z < q:
        clientid ='0K2JWOCMJBXC3VCV0WH1SD3BEC5HXM1P1SXV455BFXXEOL5B'
        clientsecr = 'AV01NROCD1GVTFU3XCLFUJRITL1UH04KK3KQSAFCSV33SHZO'
        i = 0
        while i < (len(coordinatedict[z])-1):
            client = foursquare.Foursquare(client_id= str(clientid), client_secret= str(clientsecr), version = str(date))
            Foursquarevenues_3 = client.venues.search(params={'sw': str(coordinatedict[z][i]), 'ne': str(coordinatedict[z][i+1]), 'intent' : 'browse', 'limit': '50', 'categoryId': str(category)})
            Foursquarevenues_tot.append(Foursquarevenues_3.items())
            i+=1
        z+= 1
    print("completed diagonals: " + str(q-15) +"-" + str(q))
    if q >= s:
        print("total completed")
    else:
        time.sleep(1801)
    r = q

time.sleep(1801)

r = 315
s = 445
while r< s:
    j= r
    h = j + 15
    while j< h:
        clientid ='YKCEGK2Y23DLC235QLD2TQC2KGVHVVLGSXKVERU5WDFY0HNS'
        clientsecr = 'IARXE4FXOMLKRSZKUOGZ2G2UQLGFKK42M2UJ0EPX1O5DEPG2'
        i = 0
        while i < (len(coordinatedict[j])-1):
            client = foursquare.Foursquare(client_id= str(clientid), client_secret= str(clientsecr), version = str(date))
            Foursquarevenues_3 = client.venues.search(params={'sw': str(coordinatedict[j][i]), 'ne': str(coordinatedict[j][i+1]), 'intent' : 'browse', 'limit': '50', 'categoryId': str(category)})
            Foursquarevenues_tot.append(Foursquarevenues_3.items())
            i+=1
        j+= 1
    print("completed diagonals: " + str(r) +"-" + str(h))
    z= h + 15
    while h < z:
        clientid ='DMOHFINUSZSKWFFIXAJQLBTYTIJKDC1TFUEIYWRTHXBOHLGT'
        clientsecr = 'F5MRESLTMXEGP4LW3XATD5T0CNK15HOLVUX1WNBCHSAW3SZL'
        i = 0
        while i < (len(coordinatedict[h])-1):
            client = foursquare.Foursquare(client_id= str(clientid), client_secret= str(clientsecr), version = str(date))
            Foursquarevenues_3 = client.venues.search(params={'sw': str(coordinatedict[h][i]), 'ne': str(coordinatedict[h][i+1]), 'intent' : 'browse', 'limit': '50', 'categoryId': str(category)})
            Foursquarevenues_tot.append(Foursquarevenues_3.items())
            i+=1
        h+= 1
    print("completed diagonals: " + str(z-15) +"-" + str(z))
    q = z + 20
    while z < q:
        clientid ='AGXJHQICGJPFIS213RVXIC4K1YYL2OVCIWIAMZYB1POBUR2A'
        clientsecr = 'HQARUEPUG31GK5RUBE5L0T1L3G3QIALZZFJSVIPTQ2WQAEXO'
        i = 0
        while i < (len(coordinatedict[z])-1):
            client = foursquare.Foursquare(client_id= str(clientid), client_secret= str(clientsecr), version = str(date))
            Foursquarevenues_3 = client.venues.search(params={'sw': str(coordinatedict[z][i]), 'ne': str(coordinatedict[z][i+1]), 'intent' : 'browse', 'limit': '50', 'categoryId': str(category)})
            Foursquarevenues_tot.append(Foursquarevenues_3.items())
            i+=1
        z+= 1
    print("completed diagonals: " + str(q-20) +"-" + str(q))
    h = q + 20
    while q < h:
        clientid ='AVAJ0TEQDREV003M15W15E1QRZHCD4XXFY310EFEVEOSPEFC'
        clientsecr = 'CH3DMZQK1VMFJAUF0KT3JJNOTDED55KPGES3J2O2OS2MOT5O'
        i = 0
        while i < (len(coordinatedict[q])-1):
            client = foursquare.Foursquare(client_id= str(clientid), client_secret= str(clientsecr), version = str(date))
            Foursquarevenues_3 = client.venues.search(params={'sw': str(coordinatedict[q][i]), 'ne': str(coordinatedict[q][i+1]), 'intent' : 'browse', 'limit': '50', 'categoryId': str(category)})
            Foursquarevenues_tot.append(Foursquarevenues_3.items())
            i+=1
        q+= 1
    print("completed diagonals: " + str(h-20) +"-" + str(h))
    k= h + 20
    while h< k:
        clientid = '4QSBFBGZ12JS0B0JBYPG0VUEWPWUPM5BMFQGQPPM21QIBYXT'
        clientsecr = 'S2ZRSKGD3KHSSKAA0U1TAH1I0WL3LBU2MO0MGIZSEE23JANZ'
        i = 0
        while i < (len(coordinatedict[h])-1):
            client = foursquare.Foursquare(client_id= str(clientid), client_secret= str(clientsecr), version = str(date))
            Foursquarevenues_3 = client.venues.search(params={'sw': str(coordinatedict[h][i]), 'ne': str(coordinatedict[h][i+1]), 'intent' : 'browse', 'limit': '50', 'categoryId': str(category)})
            Foursquarevenues_tot.append(Foursquarevenues_3.items())
            i+=1
        h+= 1
    print("completed diagonals: " + str(k-20) +"-" + str(k))
    z = k + 20
    while k < z:
        clientid ='RV2KWDAL03AFC3TYMBHTXGRWTM0JA4YCAC4CZWDT500PGKOB'
        clientsecr = 'YJP1BZODIUDPVVA0N1DW45PJRXZGQUOZ1MWAJ4UVNUZNJAFV'
        i = 0
        while i < (len(coordinatedict[k])-1):
            client = foursquare.Foursquare(client_id= str(clientid), client_secret= str(clientsecr), version = str(date))
            Foursquarevenues_3 = client.venues.search(params={'sw': str(coordinatedict[k][i]), 'ne': str(coordinatedict[k][i+1]), 'intent' : 'browse', 'limit': '50', 'categoryId': str(category)})
            Foursquarevenues_tot.append(Foursquarevenues_3.items())
            i+=1
        k+= 1
    print("completed diagonals: " + str(z-20) +"-" + str(z))
    q = z + 20
    while z < q:
        clientid ='0K2JWOCMJBXC3VCV0WH1SD3BEC5HXM1P1SXV455BFXXEOL5B'
        clientsecr = 'AV01NROCD1GVTFU3XCLFUJRITL1UH04KK3KQSAFCSV33SHZO'
        i = 0
        while i < (len(coordinatedict[z])-1):
            client = foursquare.Foursquare(client_id= str(clientid), client_secret= str(clientsecr), version = str(date))
            Foursquarevenues_3 = client.venues.search(params={'sw': str(coordinatedict[z][i]), 'ne': str(coordinatedict[z][i+1]), 'intent' : 'browse', 'limit': '50', 'categoryId': str(category)})
            Foursquarevenues_tot.append(Foursquarevenues_3.items())
            i+=1
        z+= 1
    print("completed diagonals: " + str(q-20) +"-" + str(q))
    if q >= s:
        print("total completed")
    else:
        time.sleep(1501)
    r = q

time.sleep(1801)

r = 445
s = 545
while r< s:
    j= r
    h = j + 25
    while j< h:
        clientid ='YKCEGK2Y23DLC235QLD2TQC2KGVHVVLGSXKVERU5WDFY0HNS'
        clientsecr = 'IARXE4FXOMLKRSZKUOGZ2G2UQLGFKK42M2UJ0EPX1O5DEPG2'
        i = 0
        while i < (len(coordinatedict[j])-1):
            client = foursquare.Foursquare(client_id= str(clientid), client_secret= str(clientsecr), version = str(date))
            Foursquarevenues_3 = client.venues.search(params={'sw': str(coordinatedict[j][i]), 'ne': str(coordinatedict[j][i+1]), 'intent' : 'browse', 'limit': '50', 'categoryId': str(category)})
            Foursquarevenues_tot.append(Foursquarevenues_3.items())
            i+=1
        j+= 1
    print("completed diagonals: " + str(r) +"-" + str(h))
    z= h + 25
    while h < z:
        clientid ='DMOHFINUSZSKWFFIXAJQLBTYTIJKDC1TFUEIYWRTHXBOHLGT'
        clientsecr = 'F5MRESLTMXEGP4LW3XATD5T0CNK15HOLVUX1WNBCHSAW3SZL'
        i = 0
        while i < (len(coordinatedict[h])-1):
            client = foursquare.Foursquare(client_id= str(clientid), client_secret= str(clientsecr), version = str(date))
            Foursquarevenues_3 = client.venues.search(params={'sw': str(coordinatedict[h][i]), 'ne': str(coordinatedict[h][i+1]), 'intent' : 'browse', 'limit': '50', 'categoryId': str(category)})
            Foursquarevenues_tot.append(Foursquarevenues_3.items())
            i+=1
        h+= 1
    print("completed diagonals: " + str(z-25) +"-" + str(z))
    q = z + 10
    while z < q:
        clientid ='AGXJHQICGJPFIS213RVXIC4K1YYL2OVCIWIAMZYB1POBUR2A'
        clientsecr = 'HQARUEPUG31GK5RUBE5L0T1L3G3QIALZZFJSVIPTQ2WQAEXO'
        i = 0
        while i < (len(coordinatedict[z])-1):
            client = foursquare.Foursquare(client_id= str(clientid), client_secret= str(clientsecr), version = str(date))
            Foursquarevenues_3 = client.venues.search(params={'sw': str(coordinatedict[z][i]), 'ne': str(coordinatedict[z][i+1]), 'intent' : 'browse', 'limit': '50', 'categoryId': str(category)})
            Foursquarevenues_tot.append(Foursquarevenues_3.items())
            i+=1
        z+= 1
    print("completed diagonals: " + str(q-10) +"-" + str(q))
    h = q + 10
    while q < h:
        clientid ='AVAJ0TEQDREV003M15W15E1QRZHCD4XXFY310EFEVEOSPEFC'
        clientsecr = 'CH3DMZQK1VMFJAUF0KT3JJNOTDED55KPGES3J2O2OS2MOT5O'
        i = 0
        while i < (len(coordinatedict[q])-1):
            client = foursquare.Foursquare(client_id= str(clientid), client_secret= str(clientsecr), version = str(date))
            Foursquarevenues_3 = client.venues.search(params={'sw': str(coordinatedict[q][i]), 'ne': str(coordinatedict[q][i+1]), 'intent' : 'browse', 'limit': '50', 'categoryId': str(category)})
            Foursquarevenues_tot.append(Foursquarevenues_3.items())
            i+=1
        q+= 1
    print("completed diagonals: " + str(h-10) +"-" + str(h))
    k= h + 10
    while h< k:
        clientid = '4QSBFBGZ12JS0B0JBYPG0VUEWPWUPM5BMFQGQPPM21QIBYXT'
        clientsecr = 'S2ZRSKGD3KHSSKAA0U1TAH1I0WL3LBU2MO0MGIZSEE23JANZ'
        i = 0
        while i < (len(coordinatedict[h])-1):
            client = foursquare.Foursquare(client_id= str(clientid), client_secret= str(clientsecr), version = str(date))
            Foursquarevenues_3 = client.venues.search(params={'sw': str(coordinatedict[h][i]), 'ne': str(coordinatedict[h][i+1]), 'intent' : 'browse', 'limit': '50', 'categoryId': str(category)})
            Foursquarevenues_tot.append(Foursquarevenues_3.items())
            i+=1
        h+= 1
    print("completed diagonals: " + str(k-10) +"-" + str(k))
    z = k + 10
    while k < z:
        clientid ='RV2KWDAL03AFC3TYMBHTXGRWTM0JA4YCAC4CZWDT500PGKOB'
        clientsecr = 'YJP1BZODIUDPVVA0N1DW45PJRXZGQUOZ1MWAJ4UVNUZNJAFV'
        i = 0
        while i < (len(coordinatedict[k])-1):
            client = foursquare.Foursquare(client_id= str(clientid), client_secret= str(clientsecr), version = str(date))
            Foursquarevenues_3 = client.venues.search(params={'sw': str(coordinatedict[k][i]), 'ne': str(coordinatedict[k][i+1]), 'intent' : 'browse', 'limit': '50', 'categoryId': str(category)})
            Foursquarevenues_tot.append(Foursquarevenues_3.items())
            i+=1
        k+= 1
    print("completed diagonals: " + str(z-10) +"-" + str(z))
    q = z + 10
    while z < q:
        clientid ='0K2JWOCMJBXC3VCV0WH1SD3BEC5HXM1P1SXV455BFXXEOL5B'
        clientsecr = 'AV01NROCD1GVTFU3XCLFUJRITL1UH04KK3KQSAFCSV33SHZO'
        i = 0
        while i < (len(coordinatedict[z])-1):
            client = foursquare.Foursquare(client_id= str(clientid), client_secret= str(clientsecr), version = str(date))
            Foursquarevenues_3 = client.venues.search(params={'sw': str(coordinatedict[z][i]), 'ne': str(coordinatedict[z][i+1]), 'intent' : 'browse', 'limit': '50', 'categoryId': str(category)})
            Foursquarevenues_tot.append(Foursquarevenues_3.items())
            i+=1
        z+= 1
    print("completed diagonals: " + str(q-10) +"-" + str(q))
    if q >= s:
        print("total completed")
    else:
        time.sleep(1501)
    r = q

time.sleep(1701)

r = 545
s = 755
while r< s:
    j= r
    h = j + 10
    while j< h:
        clientid ='AGXJHQICGJPFIS213RVXIC4K1YYL2OVCIWIAMZYB1POBUR2A'
        clientsecr = 'HQARUEPUG31GK5RUBE5L0T1L3G3QIALZZFJSVIPTQ2WQAEXO'
        i = 0
        while i < (len(coordinatedict[j])-1):
            client = foursquare.Foursquare(client_id= str(clientid), client_secret= str(clientsecr), version = str(date))
            Foursquarevenues_3 = client.venues.search(params={'sw': str(coordinatedict[j][i]), 'ne': str(coordinatedict[j][i+1]), 'intent' : 'browse', 'limit': '50', 'categoryId': str(category)})
            Foursquarevenues_tot.append(Foursquarevenues_3.items())
            i+=1
        j+= 1
    print("completed diagonals: " + str(r) +"-" + str(h))
    z= h + 10
    while h < z:
        clientid ='DMOHFINUSZSKWFFIXAJQLBTYTIJKDC1TFUEIYWRTHXBOHLGT'
        clientsecr = 'F5MRESLTMXEGP4LW3XATD5T0CNK15HOLVUX1WNBCHSAW3SZL'
        i = 0
        while i < (len(coordinatedict[h])-1):
            client = foursquare.Foursquare(client_id= str(clientid), client_secret= str(clientsecr), version = str(date))
            Foursquarevenues_3 = client.venues.search(params={'sw': str(coordinatedict[h][i]), 'ne': str(coordinatedict[h][i+1]), 'intent' : 'browse', 'limit': '50', 'categoryId': str(category)})
            Foursquarevenues_tot.append(Foursquarevenues_3.items())
            i+=1
        h+= 1
    print("completed diagonals: " + str(z-10) +"-" + str(z))
    q = z + 10
    while z < q:
        clientid ='YKCEGK2Y23DLC235QLD2TQC2KGVHVVLGSXKVERU5WDFY0HNS'
        clientsecr = 'IARXE4FXOMLKRSZKUOGZ2G2UQLGFKK42M2UJ0EPX1O5DEPG2'
        i = 0
        while i < (len(coordinatedict[z])-1):
            client = foursquare.Foursquare(client_id= str(clientid), client_secret= str(clientsecr), version = str(date))
            Foursquarevenues_3 = client.venues.search(params={'sw': str(coordinatedict[z][i]), 'ne': str(coordinatedict[z][i+1]), 'intent' : 'browse', 'limit': '50', 'categoryId': str(category)})
            Foursquarevenues_tot.append(Foursquarevenues_3.items())
            i+=1
        z+= 1
    print("completed diagonals: " + str(q-10) +"-" + str(q))
    h = q + 10
    while q < h:
        clientid ='AVAJ0TEQDREV003M15W15E1QRZHCD4XXFY310EFEVEOSPEFC'
        clientsecr = 'CH3DMZQK1VMFJAUF0KT3JJNOTDED55KPGES3J2O2OS2MOT5O'
        i = 0
        while i < (len(coordinatedict[q])-1):
            client = foursquare.Foursquare(client_id= str(clientid), client_secret= str(clientsecr), version = str(date))
            Foursquarevenues_3 = client.venues.search(params={'sw': str(coordinatedict[q][i]), 'ne': str(coordinatedict[q][i+1]), 'intent' : 'browse', 'limit': '50', 'categoryId': str(category)})
            Foursquarevenues_tot.append(Foursquarevenues_3.items())
            i+=1
        q+= 1
    print("completed diagonals: " + str(h-10) +"-" + str(h))
    k= h + 10
    while h< k:
        clientid = '4QSBFBGZ12JS0B0JBYPG0VUEWPWUPM5BMFQGQPPM21QIBYXT'
        clientsecr = 'S2ZRSKGD3KHSSKAA0U1TAH1I0WL3LBU2MO0MGIZSEE23JANZ'
        i = 0
        while i < (len(coordinatedict[h])-1):
            client = foursquare.Foursquare(client_id= str(clientid), client_secret= str(clientsecr), version = str(date))
            Foursquarevenues_3 = client.venues.search(params={'sw': str(coordinatedict[h][i]), 'ne': str(coordinatedict[h][i+1]), 'intent' : 'browse', 'limit': '50', 'categoryId': str(category)})
            Foursquarevenues_tot.append(Foursquarevenues_3.items())
            i+=1
        h+= 1
    print("completed diagonals: " + str(k-10) +"-" + str(k))
    z = k + 10
    while k < z:
        clientid ='RV2KWDAL03AFC3TYMBHTXGRWTM0JA4YCAC4CZWDT500PGKOB'
        clientsecr = 'YJP1BZODIUDPVVA0N1DW45PJRXZGQUOZ1MWAJ4UVNUZNJAFV'
        i = 0
        while i < (len(coordinatedict[k])-1):
            client = foursquare.Foursquare(client_id= str(clientid), client_secret= str(clientsecr), version = str(date))
            Foursquarevenues_3 = client.venues.search(params={'sw': str(coordinatedict[k][i]), 'ne': str(coordinatedict[k][i+1]), 'intent' : 'browse', 'limit': '50', 'categoryId': str(category)})
            Foursquarevenues_tot.append(Foursquarevenues_3.items())
            i+=1
        k+= 1
    print("completed diagonals: " + str(z-10) +"-" + str(z))
    q = z + 10
    while z < q:
        clientid ='0K2JWOCMJBXC3VCV0WH1SD3BEC5HXM1P1SXV455BFXXEOL5B'
        clientsecr = 'AV01NROCD1GVTFU3XCLFUJRITL1UH04KK3KQSAFCSV33SHZO'
        i = 0
        while i < (len(coordinatedict[z])-1):
            client = foursquare.Foursquare(client_id= str(clientid), client_secret= str(clientsecr), version = str(date))
            Foursquarevenues_3 = client.venues.search(params={'sw': str(coordinatedict[z][i]), 'ne': str(coordinatedict[z][i+1]), 'intent' : 'browse', 'limit': '50', 'categoryId': str(category)})
            Foursquarevenues_tot.append(Foursquarevenues_3.items())
            i+=1
        z+= 1
    print("completed diagonals: " + str(q-10) +"-" + str(q))
    if q >= s:
        print("total completed")
    else:
        time.sleep(1501)
    r = q

time.sleep(1701)

r = 755
s = 855
while r< s:
    j= r
    h = j + 10
    while j< h:
        clientid ='YKCEGK2Y23DLC235QLD2TQC2KGVHVVLGSXKVERU5WDFY0HNS'
        clientsecr = 'IARXE4FXOMLKRSZKUOGZ2G2UQLGFKK42M2UJ0EPX1O5DEPG2'
        i = 0
        while i < (len(coordinatedict[j])-1):
            client = foursquare.Foursquare(client_id= str(clientid), client_secret= str(clientsecr), version = str(date))
            Foursquarevenues_3 = client.venues.search(params={'sw': str(coordinatedict[j][i]), 'ne': str(coordinatedict[j][i+1]), 'intent' : 'browse', 'limit': '50', 'categoryId': str(category)})
            Foursquarevenues_tot.append(Foursquarevenues_3.items())
            i+=1
        j+= 1
    print("completed diagonals: " + str(r) +"-" + str(h))
    z= h + 15
    while h < z:
        clientid ='DMOHFINUSZSKWFFIXAJQLBTYTIJKDC1TFUEIYWRTHXBOHLGT'
        clientsecr = 'F5MRESLTMXEGP4LW3XATD5T0CNK15HOLVUX1WNBCHSAW3SZL'
        i = 0
        while i < (len(coordinatedict[h])-1):
            client = foursquare.Foursquare(client_id= str(clientid), client_secret= str(clientsecr), version = str(date))
            Foursquarevenues_3 = client.venues.search(params={'sw': str(coordinatedict[h][i]), 'ne': str(coordinatedict[h][i+1]), 'intent' : 'browse', 'limit': '50', 'categoryId': str(category)})
            Foursquarevenues_tot.append(Foursquarevenues_3.items())
            i+=1
        h+= 1
    print("completed diagonals: " + str(z-15) +"-" + str(z))
    q = z + 15
    while z < q:
        clientid ='AGXJHQICGJPFIS213RVXIC4K1YYL2OVCIWIAMZYB1POBUR2A'
        clientsecr = 'HQARUEPUG31GK5RUBE5L0T1L3G3QIALZZFJSVIPTQ2WQAEXO'
        i = 0
        while i < (len(coordinatedict[z])-1):
            client = foursquare.Foursquare(client_id= str(clientid), client_secret= str(clientsecr), version = str(date))
            Foursquarevenues_3 = client.venues.search(params={'sw': str(coordinatedict[z][i]), 'ne': str(coordinatedict[z][i+1]), 'intent' : 'browse', 'limit': '50', 'categoryId': str(category)})
            Foursquarevenues_tot.append(Foursquarevenues_3.items())
            i+=1
        z+= 1
    print("completed diagonals: " + str(q-15) +"-" + str(q))
    h = q + 15
    while q< h:
        clientid ='AVAJ0TEQDREV003M15W15E1QRZHCD4XXFY310EFEVEOSPEFC'
        clientsecr = 'CH3DMZQK1VMFJAUF0KT3JJNOTDED55KPGES3J2O2OS2MOT5O'
        i = 0
        while i < (len(coordinatedict[q])-1):
            client = foursquare.Foursquare(client_id= str(clientid), client_secret= str(clientsecr), version = str(date))
            Foursquarevenues_3 = client.venues.search(params={'sw': str(coordinatedict[q][i]), 'ne': str(coordinatedict[q][i+1]), 'intent' : 'browse', 'limit': '50', 'categoryId': str(category)})
            Foursquarevenues_tot.append(Foursquarevenues_3.items())
            i+=1
        q+= 1
    print("completed diagonals: " + str(h-15) +"-" + str(h))
    k= h + 15
    while h< k:
        clientid = '4QSBFBGZ12JS0B0JBYPG0VUEWPWUPM5BMFQGQPPM21QIBYXT'
        clientsecr = 'S2ZRSKGD3KHSSKAA0U1TAH1I0WL3LBU2MO0MGIZSEE23JANZ'
        i = 0
        while i < (len(coordinatedict[h])-1):
            client = foursquare.Foursquare(client_id= str(clientid), client_secret= str(clientsecr), version = str(date))
            Foursquarevenues_3 = client.venues.search(params={'sw': str(coordinatedict[h][i]), 'ne': str(coordinatedict[h][i+1]), 'intent' : 'browse', 'limit': '50', 'categoryId': str(category)})
            Foursquarevenues_tot.append(Foursquarevenues_3.items())
            i+=1
        h+= 1
    print("completed diagonals: " + str(k-15) +"-" + str(k))
    z = k + 15
    while k < z:
        clientid ='RV2KWDAL03AFC3TYMBHTXGRWTM0JA4YCAC4CZWDT500PGKOB'
        clientsecr = 'YJP1BZODIUDPVVA0N1DW45PJRXZGQUOZ1MWAJ4UVNUZNJAFV'
        i = 0
        while i < (len(coordinatedict[k])-1):
            client = foursquare.Foursquare(client_id= str(clientid), client_secret= str(clientsecr), version = str(date))
            Foursquarevenues_3 = client.venues.search(params={'sw': str(coordinatedict[k][i]), 'ne': str(coordinatedict[k][i+1]), 'intent' : 'browse', 'limit': '50', 'categoryId': str(category)})
            Foursquarevenues_tot.append(Foursquarevenues_3.items())
            i+=1
        k+= 1
    print("completed diagonals: " + str(z-15) +"-" + str(z))
    q = z + 15
    while z < q:
        clientid ='0K2JWOCMJBXC3VCV0WH1SD3BEC5HXM1P1SXV455BFXXEOL5B'
        clientsecr = 'AV01NROCD1GVTFU3XCLFUJRITL1UH04KK3KQSAFCSV33SHZO'
        i = 0
        while i < (len(coordinatedict[z])-1):
            client = foursquare.Foursquare(client_id= str(clientid), client_secret= str(clientsecr), version = str(date))
            Foursquarevenues_3 = client.venues.search(params={'sw': str(coordinatedict[z][i]), 'ne': str(coordinatedict[z][i+1]), 'intent' : 'browse', 'limit': '50', 'categoryId': str(category)})
            Foursquarevenues_tot.append(Foursquarevenues_3.items())
            i+=1
        z+= 1
    print("completed diagonals: " + str(q-15) +"-" + str(q))
    if q >= s:
        print("total completed")
    else:
        time.sleep(1801)
    r = q

time.sleep(1801)

r = 855
s = 997
while r< s:
    j= r
    h = j + 20
    while j< h:
        clientid ='YKCEGK2Y23DLC235QLD2TQC2KGVHVVLGSXKVERU5WDFY0HNS'
        clientsecr = 'IARXE4FXOMLKRSZKUOGZ2G2UQLGFKK42M2UJ0EPX1O5DEPG2'
        i = 0
        while i < (len(coordinatedict[j])-1):
            client = foursquare.Foursquare(client_id= str(clientid), client_secret= str(clientsecr), version = str(date))
            Foursquarevenues_3 = client.venues.search(params={'sw': str(coordinatedict[j][i]), 'ne': str(coordinatedict[j][i+1]), 'intent' : 'browse', 'limit': '50', 'categoryId': str(category)})
            Foursquarevenues_tot.append(Foursquarevenues_3.items())
            i+=1
        j+= 1
    print("completed diagonals: " + str(r) +"-" + str(h))
    z= h + 20
    while h < z:
        clientid ='DMOHFINUSZSKWFFIXAJQLBTYTIJKDC1TFUEIYWRTHXBOHLGT'
        clientsecr = 'F5MRESLTMXEGP4LW3XATD5T0CNK15HOLVUX1WNBCHSAW3SZL'
        i = 0
        while i < (len(coordinatedict[h])-1):
            client = foursquare.Foursquare(client_id= str(clientid), client_secret= str(clientsecr), version = str(date))
            Foursquarevenues_3 = client.venues.search(params={'sw': str(coordinatedict[h][i]), 'ne': str(coordinatedict[h][i+1]), 'intent' : 'browse', 'limit': '50', 'categoryId': str(category)})
            Foursquarevenues_tot.append(Foursquarevenues_3.items())
            i+=1
        h+= 1
    print("completed diagonals: " + str(z-20) +"-" + str(z))
    q = z + 20
    while z < q:
        clientid ='AGXJHQICGJPFIS213RVXIC4K1YYL2OVCIWIAMZYB1POBUR2A'
        clientsecr = 'HQARUEPUG31GK5RUBE5L0T1L3G3QIALZZFJSVIPTQ2WQAEXO'
        i = 0
        while i < (len(coordinatedict[z])-1):
            client = foursquare.Foursquare(client_id= str(clientid), client_secret= str(clientsecr), version = str(date))
            Foursquarevenues_3 = client.venues.search(params={'sw': str(coordinatedict[z][i]), 'ne': str(coordinatedict[z][i+1]), 'intent' : 'browse', 'limit': '50', 'categoryId': str(category)})
            Foursquarevenues_tot.append(Foursquarevenues_3.items())
            i+=1
        z+= 1
    print("completed diagonals: " + str(q-20) +"-" + str(q))
    h = q + 20
    while q < h:
        clientid ='AVAJ0TEQDREV003M15W15E1QRZHCD4XXFY310EFEVEOSPEFC'
        clientsecr = 'CH3DMZQK1VMFJAUF0KT3JJNOTDED55KPGES3J2O2OS2MOT5O'
        i = 0
        while i < (len(coordinatedict[q])-1):
            client = foursquare.Foursquare(client_id= str(clientid), client_secret= str(clientsecr), version = str(date))
            Foursquarevenues_3 = client.venues.search(params={'sw': str(coordinatedict[q][i]), 'ne': str(coordinatedict[q][i+1]), 'intent' : 'browse', 'limit': '50', 'categoryId': str(category)})
            Foursquarevenues_tot.append(Foursquarevenues_3.items())
            i+=1
        q+= 1
    print("completed diagonals: " + str(h-20) +"-" + str(h))
    k= h + 20
    while h< k:
        clientid = '4QSBFBGZ12JS0B0JBYPG0VUEWPWUPM5BMFQGQPPM21QIBYXT'
        clientsecr = 'S2ZRSKGD3KHSSKAA0U1TAH1I0WL3LBU2MO0MGIZSEE23JANZ'
        i = 0
        while i < (len(coordinatedict[h])-1):
            client = foursquare.Foursquare(client_id= str(clientid), client_secret= str(clientsecr), version = str(date))
            Foursquarevenues_3 = client.venues.search(params={'sw': str(coordinatedict[h][i]), 'ne': str(coordinatedict[h][i+1]), 'intent' : 'browse', 'limit': '50', 'categoryId': str(category)})
            Foursquarevenues_tot.append(Foursquarevenues_3.items())
            i+=1
        h+= 1
    print("completed diagonals: " + str(k-20) +"-" + str(k))
    z = k + 20
    while k < z:
        clientid ='RV2KWDAL03AFC3TYMBHTXGRWTM0JA4YCAC4CZWDT500PGKOB'
        clientsecr = 'YJP1BZODIUDPVVA0N1DW45PJRXZGQUOZ1MWAJ4UVNUZNJAFV'
        i = 0
        while i < (len(coordinatedict[k])-1):
            client = foursquare.Foursquare(client_id= str(clientid), client_secret= str(clientsecr), version = str(date))
            Foursquarevenues_3 = client.venues.search(params={'sw': str(coordinatedict[k][i]), 'ne': str(coordinatedict[k][i+1]), 'intent' : 'browse', 'limit': '50', 'categoryId': str(category)})
            Foursquarevenues_tot.append(Foursquarevenues_3.items())
            i+=1
        k+= 1
    print("completed diagonals: " + str(z-20) +"-" + str(z))
    q = z + 22
    while z < q:
        clientid ='0K2JWOCMJBXC3VCV0WH1SD3BEC5HXM1P1SXV455BFXXEOL5B'
        clientsecr = 'AV01NROCD1GVTFU3XCLFUJRITL1UH04KK3KQSAFCSV33SHZO'
        i = 0
        while i < (len(coordinatedict[z])-1):
            client = foursquare.Foursquare(client_id= str(clientid), client_secret= str(clientsecr), version = str(date))
            Foursquarevenues_3 = client.venues.search(params={'sw': str(coordinatedict[z][i]), 'ne': str(coordinatedict[z][i+1]), 'intent' : 'browse', 'limit': '50', 'categoryId': str(category)})
            Foursquarevenues_tot.append(Foursquarevenues_3.items())
            i+=1
        z+= 1
    print("completed diagonals: " + str(q-22) +"-" + str(q))
    if z >= s:
        print("total completed")
    else:
        time.sleep(1501)
    r = z



def writeJson(dictionary, outfile):
     with open(outfile, 'w') as fp:
        fp.seek(0)
        json.dump(dictionary, fp)
        fp.close()


def main():
    os.chdir("C:\Dokumente\Utrecht\Master_these\Data\Foursquare")
    jsonfile1 = os.path.join(os.getcwd(),'MilanFoursquaring_Food2' + date + '.json')
    writeJson(Foursquarevenues_tot, jsonfile1)


if __name__ == '__main__':
    main()
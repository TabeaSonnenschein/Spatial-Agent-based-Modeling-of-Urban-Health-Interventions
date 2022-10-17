import numpy
import time
import os

import numpy as np
import pandas as pd
from itertools import chain
import geopandas as gpd
import shapely.geometry
from shapely.geometry import Point, LineString, Polygon
from io import StringIO
pd.options.mode.chained_assignment = None  # default='warn'
import multiprocessing as mp
# print("Number of processors: ", mp.cpu_count())
# pool = mp.Pool(mp.cpu_count())

#
# os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Data\Amsterdam\Administrative Units")
# PC6 = os.path.join(os.getcwd(), ("PC6_small.csv"))
# PC6 = pd.read_csv(PC6)
# PC6 = PC6.drop_duplicates()
# print(PC6.head())
# PC6.to_csv("PC6_small.csv", index=False)
#
# os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Data\Amsterdam\ODIN\2018")
# ODIN = os.path.join(os.getcwd(), ("ODIN2018_origPC6_destPC4.csv"))
# ODIN = pd.read_csv(ODIN)
# ODIN = ODIN.drop_duplicates()
# print(len(ODIN.index))
# print(ODIN.head())
#
# os.chdir(r"D:")
#
# ODIN_ext = pd.merge(ODIN, PC6, on= "dest_postcode", how="left")
# print(len(ODIN_ext.index))
# ODIN_ext.to_csv("ODIN2018_Studyarea_PC6.csv", index=False)
#
def multiprocessSpatialJoin(lines, polygons):
    gdf_LeftJoin = gpd.sjoin(
        lines,
        polygons,
        how="left")
    return pd.DataFrame(gdf_LeftJoin)

if __name__ == '__main__':

    print("loading data")
    os.chdir(r"D:")
    PC6_data = os.path.join(os.getcwd(), ("PC6_env_behav_determ.csv"))
    PC6_data = pd.read_csv(PC6_data)

    PC6_shape = os.path.join(os.getcwd(), ("PC6_polygon_behav_determ.shp"))
    PC6_shape = gpd.read_file(PC6_shape)

    ODIN_ext = os.path.join(os.getcwd(), ("ODIN2018_Studyarea_PC6.csv"))
    ODIN_ext = pd.read_csv(ODIN_ext)
    print(len(ODIN_ext.index))


    # ODIN_ext = os.path.join(os.getcwd(), ("ODIN2018_Studyarea_PC6_sample.csv"))
    # ODIN_ext = pd.read_csv(ODIN_ext)


    print("preparing data")


    #variables that have to be joined with the trip origin PC6
    orig_variables = ["DistCBD", "pubTraDns", "coords.x1","coords.x2"]
    orig_vardata = PC6_data[list(chain.from_iterable([["PC6"], orig_variables]))]
    orig_vardata = orig_vardata.add_suffix('.orig')

    #variables that have to be averaged over the trip route
    route_variables = ["popDns", "retaiDns" , "greenCovr", "pubTraDns", "RdIntrsDns", "TrafAccid", "AccidPedes", "NrTrees", "MeanTraffV",
                        "SumTraffVo", "HighwLen", "PedStrWidt", "PedStrLen", "LenBikRout","retailDiv", "MaxSpeed", "MinSpeed", "MeanSpeed", "NrStrLight",
                        "CrimeIncid", "MaxNoisDay", "MxNoisNigh", "OpenSpace", "PNonWester", "PWelfarDep"]

    route_variables_later = [i + ".route" for i in route_variables]

    #variables that have to be joined with the trip destination PC6
    dest_variables = ["NrParkSpac","coords.x1","coords.x2"]
    dest_vardata = PC6_data[list(chain.from_iterable([["PC6"], dest_variables]))]
    dest_vardata= dest_vardata.add_suffix('.dest')

    print("merging data")


    print("Number of Rows:", len(ODIN_ext.index))
    print(divmod(len(ODIN_ext.index), 1000000))


    # for i in range(1, (len(ODIN_ext.index) // 1000000)):
    #     print("Merging Mod Number:", i, time.time())
    #     if i < (len(ODIN_ext.index) // 1000000):
    #         ODIN_orig = pd.merge(ODIN_ext[(1000000*(i-1)):(1000000*i)], orig_vardata, left_on="orig_PC6", right_on="PC6.orig" , how="left")
    #     else:
    #         ODIN_orig = pd.merge(ODIN_ext[(1000000*i):], orig_vardata, left_on="orig_PC6", right_on="PC6.orig" , how="left")
    #     ODIN_orig_dest = pd.merge(ODIN_orig, dest_vardata, left_on="dest_PC6", right_on="PC6.dest" , how="left")
    #     del ODIN_orig
    #     ODIN_orig_dest[list(chain.from_iterable([route_variables_later, ["trip_distance"]]))] = "NaN"
    #     orig_dest_line = gpd.GeoDataFrame(data={"ID": list(range(0, 1000000))}, geometry=gpd.GeoSeries.from_wkt(
    #             ["LINESTRING(" + str(ODIN_orig_dest["coords.x1.orig"].iloc[x]) + " " +
    #              str(ODIN_orig_dest["coords.x2.orig"].iloc[x]) + ", " +
    #              str(ODIN_orig_dest["coords.x1.dest"].iloc[x]) + " " +
    #              str(ODIN_orig_dest["coords.x2.dest"].iloc[x]) + ")" for x in
    #              range(0, 500000)]), crs='epsg:28992')
    #     print("We are spatial at "+ str(time.time()))
    #     ODIN_orig_dest["trip_distance"] = list(orig_dest_line.length)
    #     print("spatial join")
    #     route_stats = pd.concat([multiprocessSpatialJoin(orig_dest_line.iloc[((x - 1) * 25000):(x * 25000)], PC6_shape) for x in range(1, 20)])
    #     print(route_stats.head())
    #     # p = mp.Pool(6)  # 6=number of cores used
    #     # route_stats = [p.apply(multiprocessSpatialJoin, args=(orig_dest_line.iloc[((x - 1) * 25000):(x * 25000)], PC6_shape)) for x in range(1, 20)]
    #     # p.close()
    #     # p.join()
    #     route_stats = route_stats[list(chain.from_iterable([["ID"], route_variables]))]
    #     print("polygon join at " + str(time.time()))
    #     ODIN_orig_dest[route_variables_later] = route_stats.groupby("ID").mean()
    #     print("saving data")
    #     ODIN_orig_dest.to_csv(("ODIN2018_Studyarea_PC6_data1_" +str(i)+ ".csv"), index=False)
    #     del ODIN_orig_dest
    #
    #



    for i in range(167, 168):
        print("Merging Mod Number:", i)
        if i < (len(ODIN_ext.index) // 1000000):
            ODIN_orig = pd.merge(ODIN_ext[(1000000*(i-1)):(1000000*i)], orig_vardata, left_on="orig_PC6", right_on="PC6.orig" , how="left")
        else:
            ODIN_orig = pd.merge(ODIN_ext[(1000000*i):], orig_vardata, left_on="orig_PC6", right_on="PC6.orig" , how="left")
        ODIN_orig_dest = pd.merge(ODIN_orig, dest_vardata, left_on="dest_PC6", right_on="PC6.dest" , how="left")
        del ODIN_orig
        ODIN_orig_dest[list(chain.from_iterable([route_variables_later, ["trip_distance"]]))] = "NaN"
        for count in range(1, 101):
            print("range window: " + str(count) + " at " +str(time.time()))
            orig_dest_line = gpd.GeoDataFrame(data={"ID": list(range(0, 10000))}, geometry=gpd.GeoSeries.from_wkt(
                ["LINESTRING(" + str(ODIN_orig_dest["coords.x1.orig"].iloc[x]) + " " +
                 str(ODIN_orig_dest["coords.x2.orig"].iloc[x]) + ", " +
                 str(ODIN_orig_dest["coords.x1.dest"].iloc[x]) + " " +
                 str(ODIN_orig_dest["coords.x2.dest"].iloc[x]) + ")" for x in
                 range(((count - 1) * 10000), (count * 10000))]), crs='epsg:28992')
            print("We are spatial at "+ str(time.time()))
            ODIN_orig_dest["trip_distance"].iloc[(count - 1) * 10000:count * 10000] = list(orig_dest_line.length)
            route_stats = pd.DataFrame(orig_dest_line.sjoin(PC6_shape, how="left"))[
                list(chain.from_iterable([["ID"], route_variables]))]
            # print("polygon join at " + str(time.time()))
            route_stats = pd.DataFrame(route_stats.groupby("ID").mean())
            for indx, value in enumerate(route_variables_later):
                ODIN_orig_dest[value].iloc[((count - 1) * 10000):(count * 10000)] = route_stats[route_variables[indx]]
            # print(ODIN_orig_dest[route_variables_later].iloc[((count - 1) * 10000):(count * 10000)])
        print("saving data")
        ODIN_orig_dest.to_csv(("ODIN2018_Studyarea_PC6_data1_" +str(i)+ ".csv"), index=False)
        del ODIN_orig_dest

    #
    # ODIN_orig = pd.merge(ODIN_ext, orig_vardata, left_on="orig_PC6", right_on="PC6.orig" , how="left")
    # ODIN_orig_dest = pd.merge(ODIN_orig, dest_vardata, left_on="dest_PC6", right_on="PC6.dest" , how="left")
    # del ODIN_orig
    # ODIN_orig_dest[list(chain.from_iterable([route_variables_later, ["trip_distance"]]))] = "NaN"
    # for count in range(1, 300):
    #     print("row " + str(count))
    #     # "GEOMETRYCOLLECTION(" + ("LINESTRING("+ODIN_orig_dest["coords.x1.orig"].iloc[x]+" "+
    #     #                       ODIN_orig_dest["coords.x2.orig"].iloc[x]+", "+
    #     #                       ODIN_orig_dest["coords.x1.dest"].iloc[x]+" "+
    #     #                       ODIN_orig_dest["coords.x2.dest"].iloc[x] + ")" for x in range(((count - 1) * 1000), (count * 1000))) + ")"
    #     orig_dest_line = gpd.GeoDataFrame(data={"ID": list(range(0, 1000))}, geometry=gpd.GeoSeries.from_wkt(["LINESTRING(" + str(ODIN_orig_dest["coords.x1.orig"].iloc[x]) + " " +
    #                              str(ODIN_orig_dest["coords.x2.orig"].iloc[x]) + ", " +
    #                              str(ODIN_orig_dest["coords.x1.dest"].iloc[x]) + " " +
    #                              str(ODIN_orig_dest["coords.x2.dest"].iloc[x]) + ")" for x in
    #                              range(((count - 1) * 1000), (count * 1000))]), crs='epsg:28992')
    #     # orig_dest_line = gpd.GeoDataFrame(data={"ID": list(range(0, 1000))}, geometry=[
    #     #     LineString([(ODIN_orig_dest[["coords.x1.orig", "coords.x2.orig"]].iloc[x]),
    #     #                 (ODIN_orig_dest[["coords.x1.dest", "coords.x2.dest"]].iloc[x])]) for x in
    #     #     range(((count - 1) * 1000), (count * 1000))], crs='epsg:28992')
    #     print("we are spatial")
    #     ODIN_orig_dest["trip_distance"].iloc[(count - 1) * 1000:count * 1000] = list(orig_dest_line.length)
    #     route_stats = pd.DataFrame(orig_dest_line.sjoin(PC6_shape, how="left"))[list(chain.from_iterable([["ID"], route_variables]))]
    #     ODIN_orig_dest[route_variables_later] = route_stats.groupby("ID").mean()
    #     print(ODIN_orig_dest[route_variables_later])
    # print("saving data")
    # ODIN_orig_dest.to_csv(("ODIN2018_Studyarea_PC6_data.csv"), index=False)
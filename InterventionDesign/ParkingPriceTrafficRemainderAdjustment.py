
import pandas as pd
import os
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt


spatial_extract = gpd.read_file("D:/PhD EXPANSE/Data/Amsterdam/Built Environment/Transport Infrastructure/parking/parkingprices_prepostintervention.shp")
AirPollGrid = gpd.read_feather("D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/"+f"SpatialData/AirPollgrid50m.feather")
AirPollGrid = AirPollGrid.loc[~AirPollGrid["TrV7_8"].isnull()]
ringhighway = gpd.read_file(r"D:\PhD EXPANSE\Data\Amsterdam\Built Environment\Transport Infrastructure\cars\RingwegHighway.shp")

print(AirPollGrid.columns)
# do inner spatial join of spatial_extract and AirPollGrid
AirPollGridjoin = gpd.sjoin(AirPollGrid, spatial_extract, how="inner", predicate= "intersects")
print(AirPollGrid.head())
ringids = gpd.sjoin(AirPollGrid, ringhighway, how="inner", predicate= "intersects")

gridIDsinextract = AirPollGridjoin["int_id"].unique()
gridIDsinextract= [id for id in gridIDsinextract if id not in ringids["int_id"].unique()]

AirPollGridjoin = AirPollGridjoin.loc[AirPollGrid["int_id"].isin(gridIDsinextract)]
AirPollGridjoin.plot(column="TrV7_8", legend=True)
plt.show()

TraffRemainder =  pd.read_csv(r"D:\PhD EXPANSE\Data\Amsterdam\ABMRessources\ABMData\TrafficRemainder\AirPollGrid_HourlyTraffRemainder_21750.csv")
print(TraffRemainder.loc[TraffRemainder["int_id"].isin(gridIDsinextract)].head())
columnsTraff = [col for col in TraffRemainder.columns if col != "int_id"]
for column in columnsTraff:
    TraffRemainder.loc[TraffRemainder["int_id"].isin(gridIDsinextract), column] = TraffRemainder.loc[TraffRemainder["int_id"].isin(gridIDsinextract), column] * 0.971

print(TraffRemainder.loc[TraffRemainder["int_id"].isin(gridIDsinextract)].head())


TraffRemainder.to_csv(r"D:\PhD EXPANSE\Data\Amsterdam\ABMRessources\ABMData\TrafficRemainder\AirPollGrid_HourlyTraffRemainder_21750_PrkPriceInterv.csv", index=False)
import pandas as pd
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt

path_data = "C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/"

EnvBehavDeterms = gpd.read_feather(path_data+"FeatherDataABM/EnvBehavDeterminants.feather")

Interventions = ["SpeedInterv", "PedStrWidth", "AmenityDnsExistingAmenityPlaces", 
                 "AmenityDnsDivExistingAmenityPlaces", "LenBikRout", "PedStrWidthCenter", "PedStrWidthOutskirt",
                 "ParkSpace", "ParkPrice", "HighwLen", "PedStrLen", "RdIntrsDnsIncr", "RdIntrsDnsDcr",
                 "GreenCovr", "NrTrees"]
Variables = ["MeanSpeed", "PedStrWidt", "retaiDns","retailDiv", "LenBikRout", "PedStrWidt", "PedStrWidt", 
             "NrParkSpac", "PrkPricPre", "HighwLen", "PedStrLen", "RdIntrsDns", "RdIntrsDns", "greenCovr", "NrTrees"]

Interventions = ["PedStrLenCenter", "PedStrLenOutskirt"]
Variables = ["PedStrLen", "PedStrLen"]


for count,interv in enumerate(Interventions):
    EnvBehavDetermsInterv = gpd.read_feather(path_data+f"FeatherDataABM/EnvBehavDeterminants{interv}.feather")
    EnvBehavDeterms[Variables[count]] = EnvBehavDeterms[Variables[count]].fillna(0)
    EnvBehavDetermsInterv[Variables[count]] = EnvBehavDetermsInterv[Variables[count]].fillna(0)
    vmin = min(EnvBehavDeterms[Variables[count]])  # Minimum value for color scaling
    vmax = max(EnvBehavDeterms[Variables[count]])  # Maximum value for color scaling
    if max(EnvBehavDetermsInterv[Variables[count]]) > vmax:
        vmax = max(EnvBehavDetermsInterv[Variables[count]])
    cmap = 'viridis'  # Choose a colormap for the color scaling
    EnvBehavDeterms.plot(Variables[count], antialiased=False, legend = True, vmin=vmin, vmax=vmax, cmap=cmap) 
    plt.title("Status Quo")
    plt.savefig(path_data + f'ModelRuns/InterventionPlots/{interv}_StatusQuo_{Variables[count]}.png', dpi=300)
    plt.close()
    EnvBehavDetermsInterv.plot(Variables[count], antialiased=False, legend = True, vmin=vmin, vmax=vmax, cmap=cmap)  
    plt.title("Intervention Scenario")
    plt.savefig(path_data + f'ModelRuns/InterventionPlots/{interv}_Interv_{Variables[count]}.png', dpi = 300)
    plt.close()

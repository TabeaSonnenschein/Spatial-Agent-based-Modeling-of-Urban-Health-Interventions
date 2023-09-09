import pandas as pd
import numpy as np
import geopandas as gpd

path_data = "C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/"

EnvBehavDeterms = gpd.read_feather(path_data+"FeatherDataABM/EnvBehavDeterminants.feather")

#### max 30km speed limit: MaxSpeed
# EnvBehavDeterms.loc[EnvBehavDeterms["MaxSpeed"] > 30, "MaxSpeed"] = 30
# EnvBehavDeterms.loc[EnvBehavDeterms["MeanSpeed"] > 30, "MeanSpeed"] = 30
# EnvBehavDeterms.loc[EnvBehavDeterms["MinSpeed"] > 30, "MinSpeed"] = 30

# EnvBehavDeterms.to_feather(path_data+"FeatherDataABM/EnvBehavDeterminantsSpeedInterv.feather")


#### increasing greenCovr

# EnvBehavDeterms.loc[EnvBehavDeterms["greenCovr"].between(0.01,0.3), "greenCovr"] = 0.3
# EnvBehavDeterms.to_feather(path_data+"FeatherDataABM/EnvBehavDeterminantsGreenCovr.feather")

#### increasing NrTrees
# EnvBehavDeterms.loc[EnvBehavDeterms["NrTrees"].between(1,300), "NrTrees"] = 300
# EnvBehavDeterms.to_feather(path_data+"FeatherDataABM/EnvBehavDeterminantsNrTrees.feather")

#### increase retailDiv #amenitydiversity
# EnvBehavDeterms.loc[EnvBehavDeterms["retaiDns"].between(1,60), "retaiDns"] = 60
# EnvBehavDeterms.to_feather(path_data+"FeatherDataABM/EnvBehavDeterminantsAmenityDnsExistingAmenityPlaces.feather")

# EnvBehavDeterms.loc[EnvBehavDeterms["retailDiv"].between(0.1,4), "retailDiv"] = 4
# EnvBehavDeterms.to_feather(path_data+"FeatherDataABM/EnvBehavDeterminantsAmenityDnsDivExistingAmenityPlaces.feather")


#### increase PedStrWidt
# EnvBehavDeterms.loc[EnvBehavDeterms["PedStrWidt"].between(0.5, 5), "PedStrWidt"] = 5
# EnvBehavDeterms.to_feather(path_data+"FeatherDataABM/EnvBehavDeterminantsPedStrWidth.feather")
# print(EnvBehavDeterms["DistCBD"])
# print(((EnvBehavDeterms["PedStrWidt"].between(0.5, 5)) & (EnvBehavDeterms["DistCBD"] >= 3000)).value_counts())
# EnvBehavDeterms.loc[((EnvBehavDeterms["PedStrWidt"].between(0.5, 5)) & (EnvBehavDeterms["DistCBD"] < 3000)), "PedStrWidt"] = 5
# EnvBehavDeterms.to_feather(path_data+"FeatherDataABM/EnvBehavDeterminantsPedStrWidthCenter.feather")

# EnvBehavDeterms.loc[((EnvBehavDeterms["PedStrWidt"].between(0.5, 5)) & (EnvBehavDeterms["DistCBD"] >= 3000)), "PedStrWidt"] = 5
# EnvBehavDeterms.to_feather(path_data+"FeatherDataABM/EnvBehavDeterminantsPedStrWidthOutskirt.feather")

#### reducing NrParkSpac
# EnvBehavDeterms.loc[EnvBehavDeterms["NrParkSpac"]>100, "NrParkSpac"] = 100
# EnvBehavDeterms.to_feather(path_data+"FeatherDataABM/EnvBehavDeterminantsParkSpace.feather")


#### increasing PrkPricPre
# EnvBehavDeterms["PrkPricPre"] = EnvBehavDeterms["PrkPricPos"]
# EnvBehavDeterms.to_feather(path_data+"FeatherDataABM/EnvBehavDeterminantsParkPrice.feather")

#### increasing LenBikRout
# EnvBehavDeterms.loc[EnvBehavDeterms["LenBikRout"]< 350, "LenBikRout"] = 350
# EnvBehavDeterms.to_feather(path_data+"FeatherDataABM/EnvBehavDeterminantsLenBikRout.feather")

#### decrease HighwLen
# EnvBehavDeterms.loc[EnvBehavDeterms["HighwLen"]> 0, "HighwLen"] = 0
# EnvBehavDeterms.to_feather(path_data+"FeatherDataABM/EnvBehavDeterminantsHighwLen.feather")

#### increase PedStrLen
# EnvBehavDeterms.loc[EnvBehavDeterms["PedStrLen"].between(1,2000), "PedStrLen"] = 2000
# EnvBehavDeterms.to_feather(path_data+"FeatherDataABM/EnvBehavDeterminantsPedStrLen.feather")

# EnvBehavDeterms.loc[((EnvBehavDeterms["PedStrLen"].between(1,2000))& (EnvBehavDeterms["DistCBD"] >= 4000)), "PedStrLen"] = 2000
# EnvBehavDeterms.to_feather(path_data+"FeatherDataABM/EnvBehavDeterminantsPedStrLenOutskirt.feather")

EnvBehavDeterms.loc[((EnvBehavDeterms["PedStrLen"].between(1,2000))& (EnvBehavDeterms["DistCBD"] < 4000)), "PedStrLen"] = 2000
EnvBehavDeterms.to_feather(path_data+"FeatherDataABM/EnvBehavDeterminantsPedStrLenCenter.feather")

#### Increase RdIntrsDns
# EnvBehavDeterms.loc[EnvBehavDeterms["RdIntrsDns"].between(1, 28), "RdIntrsDns"] = 28
# EnvBehavDeterms.to_feather(path_data+"FeatherDataABM/EnvBehavDeterminantsRdIntrsDnsIncr.feather")

#### Decrease RdIntrsDns
# EnvBehavDeterms.loc[EnvBehavDeterms["RdIntrsDns"]> 28, "RdIntrsDns"] = 28
# EnvBehavDeterms.to_feather(path_data+"FeatherDataABM/EnvBehavDeterminantsRdIntrsDnsDcr.feather")
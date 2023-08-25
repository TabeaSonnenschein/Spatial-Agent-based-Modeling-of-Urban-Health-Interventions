import pandas as pd
import numpy as np
import geopandas as gpd

path_data = "C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/"

EnvBehavDeterms = gpd.read_feather(path_data+"FeatherDataABM/EnvBehavDeterminants.feather")

# # max 30km speed limit: MaxSpeed
# EnvBehavDeterms.loc[EnvBehavDeterms["MaxSpeed"] > 30, "MaxSpeed"] = 30
# EnvBehavDeterms.loc[EnvBehavDeterms["MeanSpeed"] > 30, "MeanSpeed"] = 30
# EnvBehavDeterms.loc[EnvBehavDeterms["MinSpeed"] > 30, "MinSpeed"] = 30

# EnvBehavDeterms.to_feather(path_data+"FeatherDataABM/EnvBehavDeterminantsSpeedInterv.feather")


# increasing greenCovr

# increase retailDiv #amenitydiversity

# increase PedStrWidt
EnvBehavDeterms.loc[EnvBehavDeterms["PedStrWidt"].between(0.5, 5), "PedStrWidt"] = 5
EnvBehavDeterms.to_feather(path_data+"FeatherDataABM/EnvBehavDeterminantsPedStrWidth.feather")



# reducing NrParkSpac

# increasing PrkPricPre
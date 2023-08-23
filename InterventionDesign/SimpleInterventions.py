import pandas as pd
import numpy as np
import geopandas as gpd

path_data = "C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/"

EnvBehavDeterms = gpd.read_feather(path_data+"FeatherDataABM/EnvBehavDeterminants.feather")

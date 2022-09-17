import netCDF4
import pandas as pd
import xarray as xr
import os
import numpy as np

# os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Data\Amsterdam\Weather")
# metereo_nc_file = 'KIS___OPER_P___OBS_____L2.nc'
# nc = xr.open_dataset(metereo_nc_file, engine= 'netcdf4')
#
# RH_df = nc.RH.to_dataframe().to_csv('RH.csv')
# RH_df = pd.read_csv(os.path.join(os.getcwd(), "RH.csv"))
# print(RH_df.columns)
# RH_df = RH_df.iloc[list(np.where(RH_df['time'] > "2018-12-30")[0])]
# print(RH_df)
# RH_df.to_csv('RH.csv', index_label=False)
# stations = RH_df[['station', 'lat', 'lon']].drop_duplicates()
# RH_df = RH_df.iloc[list(np.where(RH_df['station'] == 240)[0])]
# RH_df.to_csv('Rain_Amsterdam.csv', index_label=False)
#
#
# TG_df = nc.TG.to_dataframe().to_csv('TG.csv')
# TG_df = pd.read_csv(os.path.join(os.getcwd(), "TG.csv"))
# print(TG_df.columns)
# TG_df = TG_df.iloc[list(np.where(TG_df['time'] > "2018-12-30")[0])]
# print(TG_df)
# TG_df.to_csv('TG.csv', index_label=False)
# TG_df = TG_df.iloc[list(np.where(TG_df['station'] == 240)[0])]
# TG_df.to_csv('Temperature_Amsterdam.csv', index_label=False)
#
#
# FHVEC_df = nc.FHVEC.to_dataframe().to_csv('FHVEC.csv')
# FHVEC_df = pd.read_csv(os.path.join(os.getcwd(), "FHVEC.csv"))
# print(FHVEC_df.columns)
# FHVEC_df = FHVEC_df.iloc[list(np.where(FHVEC_df['time'] > "2018-12-30")[0])]
# print(FHVEC_df)
# FHVEC_df.to_csv('FHVEC.csv', index_label=False)
# FHVEC_df = FHVEC_df.iloc[list(np.where(FHVEC_df['station'] == 240)[0])]
# FHVEC_df.to_csv('Windspeed_Amsterdam.csv', index_label=False)
#
#
# DDVEC_df = nc.DDVEC.to_dataframe().to_csv('DDVEC.csv')
# DDVEC_df = pd.read_csv(os.path.join(os.getcwd(), "DDVEC.csv"))
# print(DDVEC_df.columns)
# DDVEC_df = DDVEC_df.iloc[list(np.where(DDVEC_df['time'] > "2018-12-30")[0])]
# print(DDVEC_df)
# DDVEC_df.to_csv('DDVEC.csv', index_label=False)
# DDVEC_df = DDVEC_df.iloc[list(np.where(DDVEC_df['station'] == 240)[0])]
# DDVEC_df.to_csv('Winddirection_Amsterdam.csv', index_label=False)

# stations.to_csv("Stations.csv", index_label=False)

#	EPSG4326
# station 240 is Amsterdam

#######################
### RD1-5 datasets ####
#######################

# os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Data\Amsterdam\Weather\Rd1_5\Extracts")
# listOfFiles = os.listdir(path='C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Weather/Rd1_5/Downloads')
#
# for file in listOfFiles:
#     nc = xr.open_dataset('C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Weather/Rd1_5/Downloads/'+file, engine= 'netcdf4')
#     df = nc.to_dataframe().to_csv(str(file) + "Precipitation.csv")
#

############################################
### RADNL_CLIM____MFBSNL21_01H datasets ####
############################################

os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Data\Amsterdam\Weather\RADNL_CLIM____MFBSNL21_01H_20190101T000000_20200101T000000_netCDF4_0002\2019\extracts\02")
listOfFiles = os.listdir(path='C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Weather/RADNL_CLIM____MFBSNL21_01H_20190101T000000_20200101T000000_netCDF4_0002/2019/downloads/02')

for file in listOfFiles:
    filename = str(file).replace(".nc", "")
    nc = xr.open_dataset('C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Weather/RADNL_CLIM____MFBSNL21_01H_20190101T000000_20200101T000000_netCDF4_0002/2019/downloads/02/'+file, engine= 'netcdf4')
    print(nc["image1_image_data"])
    df = nc["image1_image_data"].to_dataframe()
    # .to_csv(str(filename) + "Precipitation.csv")


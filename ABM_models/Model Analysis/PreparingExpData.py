import pandas as pd
import os
####################################################
nb_agents = 21750  #87000 = 10%, 43500 = 5%, 21750 = 2.5%, 8700 = 1%
path_data = "C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/"
# path_data ="/Users/tsonnens/Documents/Exposure Intervention"
# modelrun = "SpeedInterv"
# modelrun = "StatusQuo"
# modelrun = "PedStrWidth"
# modelrun = "RetaiDnsDiv"
modelrun = "LenBikRout"
# modelrun = "PedStrWidthOutskirt"
# modelrun = "PedStrWidthCenter"
# modelrun = "AmenityDnsExistingAmenityPlaces"
# modelrun  = "AmenityDnsDivExistingAmenityPlaces"
# modelrun = "PedStrLen"
# modelrun ="PedStrWidthOutskirt"
# modelrun ="PedStrWidthCenter"
# modelrun = "PedStrLenCenter"
# modelrun = "PedStrLenOutskirt"

# read exposure data
os.chdir(path_data + 'ModelRuns/AgentExposure/' + modelrun)
# os.chdir(path_data)
listOfFiles = os.listdir(path=os.getcwd())
print(listOfFiles)

# read the exposure data for each hour and merge them into one
for hour in range(24):
    exposure_df = pd.read_csv(f"AgentExposure_A{nb_agents}_M1_H{hour}_{modelrun}.csv")
    exposure_df = exposure_df.rename(columns={"NO2": f"NO2_{hour}", "MET": f"MET_{hour}"})
    if hour == 0:
        exposure_df_all = exposure_df
    else:
        exposure_df_all = pd.merge(exposure_df, exposure_df_all, on="agent", how="left")

exposure_df_all = exposure_df_all.rename(columns={"agent": "agent_ID"})
exposure_df_all.to_csv(f"AgentExposure_A{nb_agents}_M1_{modelrun}_hourAsColumns.csv", index=False)

# read the exposure data for each hour and merge them into one whereby the hour is a row 
for hour in range(24):
    exposure_df = pd.read_csv(f"AgentExposure_A{nb_agents}_M1_H{hour}_{modelrun}.csv")
    exposure_df["hour"] = hour
    if hour == 0:
        exposure_df_all = exposure_df
    else:
        exposure_df_all = pd.concat( [exposure_df_all,exposure_df], axis=0)
        
exposure_df_all = exposure_df_all.rename(columns={"agent": "agent_ID"})
exposure_df_all.to_csv(f"AgentExposure_A{nb_agents}_M1_{modelrun}_hourAsRows.csv", index=False)


print("Reading the  Agent data")
# read agent_df
agent_df = pd.read_csv(path_data + f"Population/Amsterdam_population_subset{nb_agents}.csv")

print("Merging the data")
# merge exposure data with agent_df
exposure_df = pd.merge(agent_df, exposure_df_all, on="agent_ID", how="right")
exposure_df.to_csv(f"AgentExposure_A{nb_agents}_M1_{modelrun}_hourAsRowsMerged.csv", index=False)


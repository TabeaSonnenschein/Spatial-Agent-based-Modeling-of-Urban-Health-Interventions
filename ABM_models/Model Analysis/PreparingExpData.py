import pandas as pd
import os
####################################################
nb_agents = 43500
# path_data = "C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/"
path_data ="/Users/tsonnens/Documents/Exposure Intervention"
modelrun = "SpeedInterv"
# read exposure data
# os.chdir(path_data + 'ModelRuns/AgentExposure/')
os.chdir(path_data)
listOfFiles = os.listdir(path=path_data)
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
agent_df = pd.read_csv("Amsterdam_population_subset.csv")

print("Merging the data")
# merge exposure data with agent_df
exposure_df = pd.merge(agent_df, exposure_df_all, on="agent_ID", how="right")
exposure_df.to_csv(f"AgentExposure_A{nb_agents}_M1_{modelrun}_hourAsRowsMerged.csv", index=False)


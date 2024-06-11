import pandas as pd
import os
##########################################
nb_agents = 21750  #87000 = 10%, 43500 = 5%, 21750 = 2.5%, 8700 = 1%
path_data = "D:\PhD EXPANSE\Data\Amsterdam\ABMRessources\ABMData\ModelRuns"
os.chdir(path_data)

# scenario = "SpeedInterv"
scenario = "StatusQuo"
# scenario = "PedStrWidth"
# scenario = "RetaiDnsDiv"
# scenario = "LenBikRout"
# scenario = "PedStrWidthOutskirt"
# scenario = "PedStrWidthCenter"
# scenario = "AmenityDnsExistingAmenityPlaces"
# scenario  = "AmenityDnsDivExistingAmenityPlaces"
# scenario = "StatusQuoAllVars"
# scenario = "PedStrLen"
# scenario ="PedStrWidthOutskirt"
# scenario ="PedStrWidthCenter"
# scenario = "PedStrLenCenter"
# scenario = "PedStrLenOutskirt"
# scenario = "PrkPriceInterv"

# identify model run for scenario
experimentoverview = pd.read_csv("D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/ExperimentOverview.csv")
modelruns = experimentoverview.loc[experimentoverview["Experiment"] == scenario, "Model Run"].values
# bestStatusQuo = 481658
modelruns = [708658, 481658]
# modelruns = [381609]

days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
for modelrun in modelruns:
    # read exposure data
    os.chdir(path_data+f"/{scenario}/{nb_agents}Agents/AgentExposure/{modelrun}")
    listOfFiles = os.listdir(path=os.getcwd())
    print(listOfFiles)
    for count, file in enumerate(listOfFiles):
        exposure_df = pd.read_csv(file)
        filesplit = file.split("_")
        print(filesplit)
        datetimesuffix = filesplit[3] + "_" + filesplit[4] + "_" + filesplit[5]
        exposure_df = exposure_df.rename(columns={"NO2": f"NO2_{datetimesuffix}", "MET": f"MET_{datetimesuffix}"})
        if count == 0:
            exposure_df_horizon = exposure_df
            exposure_df["day"] = filesplit[4][1:]
            exposure_df["month"] = filesplit[3][1:]
            exposure_df["hour"] = filesplit[5][1:]
            exposure_df_vertical = exposure_df
        else:
            exposure_df_horizon = pd.merge(exposure_df, exposure_df_horizon, on="agent", how="left")
            exposure_df["day"] = filesplit[4][1:]
            exposure_df["month"] = filesplit[3][1:]
            exposure_df["hour"] = filesplit[5][1:]
            exposure_df_vertical = pd.concat([exposure_df_vertical, exposure_df], axis=0)
    exposure_df_horizon = exposure_df_horizon.rename(columns={"agent": "agent_ID"})
    exposure_df_vertical = exposure_df_vertical.rename(columns={"agent": "agent_ID"})
    if not os.path.exists(path_data+f"/{scenario}/{nb_agents}Agents/AgentExposure/{modelrun}/ExposureViz"):
        # Create the directory
        os.mkdir(path_data+f"/{scenario}/{nb_agents}Agents/AgentExposure/{modelrun}/ExposureViz")
    os.chdir(path_data+f"/{scenario}/{nb_agents}Agents/AgentExposure/{modelrun}/ExposureViz")
    exposure_df_horizon.to_csv(f"Exposure_A{nb_agents}_{modelrun}_horizonAsColumns.csv", index=False)
    exposure_df_vertical.to_csv(f"Exposure_A{nb_agents}_{modelrun}_verticalAsRows.csv", index=False)



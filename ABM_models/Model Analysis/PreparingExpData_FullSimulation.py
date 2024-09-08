import pandas as pd
import os
##########################################
nb_agents = 21750  #87000 = 10%, 43500 = 5%, 21750 = 2.5%, 8700 = 1%
path_data = "D:\PhD EXPANSE\Data\Amsterdam\ABMRessources\ABMData\ModelRuns"
os.chdir(path_data)

# scenario = "StatusQuo"
# scenario = "PrkPriceInterv"
# scenario = "15mCity"
scenario = "15mCityWithDestination"
# scenario = "NoEmissionZone2025"
# scenario = "NoEmissionZone2030"


# identify model run for scenario
experimentoverview = pd.read_csv("D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/ExperimentOverview.csv")
modelruns = experimentoverview.loc[experimentoverview["Experiment"] == scenario, "Model Run"].values
# modelruns = [modelrun for modelrun in modelruns if not(modelrun in [669169,509190])]
# print(modelruns)
# bestStatusQuo = 481658
# modelruns = [708658, 481658]
# modelruns = [819838]
# modelruns = [ 912787, 493519, 989597]
modelruns = [ 989597]


days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
for modelrun in modelruns:
    # read exposure data
    os.chdir(path_data+f"/{scenario}/{nb_agents}Agents/AgentExposure/{modelrun}")
    listOfFiles = os.listdir(path=os.getcwd())
    if "ExposureViz" in listOfFiles:
        listOfFiles.remove("ExposureViz")
    print(listOfFiles)
    for count, file in enumerate(listOfFiles):
        exposure_df = pd.read_csv(file)
        filesplit = file.split("_")
        print(filesplit)
        if count == 0:
            exposure_df["day"] = filesplit[4][1:]
            exposure_df["month"] = filesplit[3][1:]
            exposure_df["hour"] = filesplit[5][1:]
            exposure_df_vertical = exposure_df
        else:
            exposure_df["day"] = filesplit[4][1:]
            exposure_df["month"] = filesplit[3][1:]
            exposure_df["hour"] = filesplit[5][1:]
            exposure_df_vertical = pd.concat([exposure_df_vertical, exposure_df], axis=0)
    exposure_df_vertical = exposure_df_vertical.rename(columns={"agent": "agent_ID"})
    if not os.path.exists(path_data+f"/{scenario}/{nb_agents}Agents/AgentExposure/{modelrun}/ExposureViz"):
        # Create the directory
        os.mkdir(path_data+f"/{scenario}/{nb_agents}Agents/AgentExposure/{modelrun}/ExposureViz")
    os.chdir(path_data+f"/{scenario}/{nb_agents}Agents/AgentExposure/{modelrun}/ExposureViz")
    exposure_df_vertical.to_csv(f"Exposure_A{nb_agents}_{modelrun}_verticalAsRows.csv", index=False)



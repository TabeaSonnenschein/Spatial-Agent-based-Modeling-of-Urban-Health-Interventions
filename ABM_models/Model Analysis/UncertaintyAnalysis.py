import numpy as np
import pandas as pd
import os
import geopandas as gpd

####  Calculate uncertainty in Monte Carlo simulation
# let the same population sample run 5 times
# difference between population samples
# difference between population sample size

def calculate_uncertainty(runs):
    """
    Calculate standard deviation for each run and then return the mean of the standard deviation
    """
    meanval = np.mean(runs)  # Mean of each sample
    std_devs = np.std(runs)  # Standard deviation for each sample
    mean_uncertainty = np.mean(std_devs)  # Mean of uncertainties (std deviations) across all samples
    uncertainty_percentage = mean_uncertainty/meanval
    return meanval, mean_uncertainty, uncertainty_percentage


#################################################################
### Population sample uncertainty
#################################################################
nb_agents = 21750  #87000 = 10%, 43500 = 5%, 21750 = 2.5%, 8700 = 1%
scenario = "StatusQuo"
path_data = "D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/ModelRuns"
experimentoverview = pd.read_csv("D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/ExperimentOverview.csv")
modelruns = experimentoverview.loc[(experimentoverview["Experiment"] == scenario)& (experimentoverview["Number of Agents"] == f"{nb_agents}Agents"), "Model Run"].values

AirPollGrid = gpd.read_feather("D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/"+f"SpatialData/AirPollgrid50m.feather")
cityextent = gpd.read_feather("D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/"+f"SpatialData/NoEmissionZone2030.feather")
city_Intids = gpd.sjoin(AirPollGrid,cityextent, how="inner", predicate='intersects')["int_id"].values


personalNO2,personalNO2wFilter, personalMET, walk, bike, drive, transit, traffic, NO2 = [], [], [], [], [], [], [], [], []
outcomevarnames = ["Personal NO2 Exposure","Personal NO2 Exposure w. I/O Filter", "Transport MET", "Walk Trips per hour", "Bike Trips per hour", "Drive Trips per hour", "Transit Trips per hour", "Traffic Volume", "NO2 (µg/m3)"]

for run in modelruns:
    exposure_df = pd.read_csv(path_data+f"/{scenario}/{nb_agents}Agents/AgentExposure/{run}/ExposureViz/Exposure_A{nb_agents}_{run}_aggregate.csv")
    exposurestats = exposure_df.loc[exposure_df["timeunit"] == "total", ["NO2", "NO2wFilter", "MET"]].values
    personalNO2.append(exposurestats[0][0])
    personalNO2wFilter.append(exposurestats[0][1])
    personalMET.append(exposurestats[0][2])
    modalsplit_df = pd.read_csv(path_data+f"/{scenario}/{nb_agents}Agents/ModalSplit/ModalSplitLog{nb_agents}_{scenario}_{run}.csv")
    walk.append(np.mean(modalsplit_df["walk"].values))
    bike.append(np.mean(modalsplit_df["bike"].values))
    drive.append(np.mean(modalsplit_df["drive"].values))
    transit.append(np.mean(modalsplit_df["transit"].values))
    NO2_df = pd.read_csv(path_data+f"/{scenario}/{nb_agents}Agents/NO2/NO2Viz/NO2Means_{scenario}_{run}.csv")
    NO2.append(np.mean(NO2_df.loc[NO2_df["int_id"].isin(city_Intids), "mean_prNO2"].values))
    Traff_df = pd.read_csv(path_data+f"/{scenario}/{nb_agents}Agents/Traffic/TraffViz/TraffMeans_{scenario}_{run}.csv")
    traffic.append(np.mean(Traff_df.loc[(Traff_df["int_id"].isin(city_Intids)) & (Traff_df["mean_prTraff"] != 0), "mean_prTraff"].values))

outcomevars = [personalNO2,personalNO2wFilter, personalMET, walk, bike, drive, transit, traffic, NO2]

for count, outcomevar in enumerate(outcomevars):
    meanval, mean_uncertainty, uncertainty_percentage = calculate_uncertainty(outcomevar)
    print(f"Uncertainty in {outcomevarnames[count]} is {uncertainty_percentage}")
    outcomevars[count].extend([meanval, mean_uncertainty, uncertainty_percentage])
    
# Save the uncertainties
# pd.DataFrame({"outcomevarnames": outcomevarnames, "uncertainty": outcomevars[-1]}).to_csv("D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData" + f"/PopSampleUncertainty_{scenario}_{nb_agents}.csv", index=False)
# save it with each modelrun result
modelruns = modelruns.tolist()
modelruns.extend(["meanval", "mean_uncertainty", "uncertainty_percentage"])
pd.DataFrame({"modelruns": modelruns, 
              # loop through the outcomevarnames and the outcomevar list of lists
                **{outcomevarnames[count]: outcomevars[count] for count in range(len(outcomevarnames))}
              }).to_csv("D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData" + f"/PopSampleUncertainty_{scenario}_{nb_agents}.csv", index=False)


#############################################################
### behavior sampling uncertainty: Modal Choice, Behavior Choice
#############################################################



###########################################################
### Pop size uncertainty
###########################################################


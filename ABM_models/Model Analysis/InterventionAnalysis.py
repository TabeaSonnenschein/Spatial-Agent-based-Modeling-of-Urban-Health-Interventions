import os
import pandas as pd
import  numpy as np
import matplotlib.pyplot as plt

nb_agents = 21750  #87000 = 10%, 43500 = 5%, 21750 = 2.5%, 8700 = 1%
path_data = "D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData"
os.chdir(path_data)
crs = "epsg:28992"

scenario = "StatusQuo"
# scenario = "PrkPriceInterv"
# scenario = "15mCity"
scenario = "15mCityWithDestination"
# scenario = "NoEmissionZone2025"

interanalysissuffix = "_parkingprice_interventionextent_trackintersect"
maketable = True
vizintervention = True

experimentoverview = pd.read_csv("ExperimentOverview.csv")
experimentoverview = experimentoverview.loc[experimentoverview["fullrun"] == True]
popsamples = experimentoverview["Population Sample"].unique()
popsamples = [x for x in popsamples if str(x) != 'nan']	
popsamples.sort()
print(popsamples)
poprange = range(0,10)

if maketable:
    IntervRunDict = {}
    for popsample in popsamples:
        experiments = experimentoverview.loc[experimentoverview["Population Sample"] == popsample, ["Experiment","Model Run"]]
        print(experiments)
        try:
            experimentdict = {"StatusQuo": experiments.loc[experiments["Experiment"] == "StatusQuo","Model Run"].values[0],
                            scenario: experiments.loc[experiments["Experiment"] == scenario,"Model Run"].values[0]}
            IntervRunDict[popsample] = experimentdict
        except:
            pass
        
    print(IntervRunDict)

    # write the IntervRunDict to a file
    with open(f"IntervRunDict_{scenario}.txt", "w") as file:
        file.write(str(IntervRunDict))

#     columns = ["nr_travelers", "nr_trips", "bike", "drive", "transit", "walk", "mean_duration"]
#     experiment, modelruns, popsample = [], [], []
#     meanbiketrips, meancartrips, meantransittrips, meanwalktrips, meannrtrips, meannrtravelers, meanduration = [], [], [], [], [], [], []
#     for run in poprange:
#         experimentdict = IntervRunDict[run]
#         print(experimentdict)

#         for key in experimentdict.keys():
#             modelrun = experimentdict[key]
#             dataloc = path_data+f"/ModelRuns/{key}/{nb_agents}Agents/Tracks/TrackViz"
#             experiment.append(key)
#             modelruns.append(modelrun)
#             popsample.append(run)
#             try:
#                 modalsplit = pd.read_csv(f"{dataloc}/ModalSplit_{key}_{modelrun}{interanalysissuffix}.csv")
#                 modalsplitmeans = modalsplit[columns].mean(axis=0)
#                 meanbiketrips.append(modalsplitmeans["bike"])
#                 meancartrips.append(modalsplitmeans["drive"])
#                 meantransittrips.append(modalsplitmeans["transit"])
#                 meanwalktrips.append(modalsplitmeans["walk"])
#                 meannrtrips.append(modalsplitmeans["nr_trips"])
#                 meannrtravelers.append(modalsplitmeans["nr_travelers"])
#                 meanduration.append(modalsplitmeans["mean_duration"])
#             except:
#                 meanbiketrips.append(None)
#                 meancartrips.append(None)
#                 meantransittrips.append(None)
#                 meanwalktrips.append(None)
#                 meannrtrips.append(None)
#                 meannrtravelers.append(None)
#                 meanduration.append(None)
#                 pass

#     modalsplitmeans_df = pd.DataFrame({"Experiment": experiment,
#                                         "Model Run": modelruns,
#                                         "Population Sample": popsample,
#                                         "Mean Bike Trips": meanbiketrips,
#                                         "Mean Car Trips": meancartrips,
#                                         "Mean Transit Trips": meantransittrips,
#                                         "Mean Walk Trips": meanwalktrips,
#                                         "Mean Nr Trips": meannrtrips,
#                                         "Mean Nr Travelers": meannrtravelers,
#                                         "Mean Duration": meanduration
#                                         })


#     modalsplitmeans_df["Bike Percentage"] = modalsplitmeans_df["Mean Bike Trips"]/modalsplitmeans_df["Mean Nr Trips"]
#     modalsplitmeans_df["Car Percentage"] = modalsplitmeans_df["Mean Car Trips"]/modalsplitmeans_df["Mean Nr Trips"]
#     modalsplitmeans_df["Transit Percentage"] = modalsplitmeans_df["Mean Transit Trips"]/modalsplitmeans_df["Mean Nr Trips"]
#     modalsplitmeans_df["Walk Percentage"] = modalsplitmeans_df["Mean Walk Trips"]/modalsplitmeans_df["Mean Nr Trips"]

#     columns = ["Mean Bike Trips", "Mean Car Trips", "Mean Transit Trips", "Mean Walk Trips", "Mean Nr Trips", 
#             "Mean Nr Travelers", "Mean Duration", "Bike Percentage", "Car Percentage", "Transit Percentage", "Walk Percentage"]
#     # calculating the difference between intervention and status quo per population sample

#     for experiment in ["StatusQuo", scenario]:
#         experimentrow = modalsplitmeans_df.loc[(modalsplitmeans_df["Experiment"] == experiment),columns]
#         experimentmeans = experimentrow.mean(axis=0)
#         experimentstd = experimentrow.std(axis=0)
#         newrows = pd.DataFrame({"Experiment": [experiment, experiment],
#                                 "Model Run": ["Mean", "Std"],
#                                 "Population Sample": ["Mean", "Std"],
#                                 "Mean Bike Trips": [experimentmeans.iloc[0], experimentstd.iloc[0]],
#                                 "Mean Car Trips": [experimentmeans.iloc[1], experimentstd.iloc[1]],
#                                 "Mean Transit Trips": [experimentmeans.iloc[2], experimentstd.iloc[2]],
#                                 "Mean Walk Trips": [experimentmeans.iloc[3], experimentstd.iloc[3]],
#                                 "Mean Nr Trips": [experimentmeans.iloc[4], experimentstd.iloc[4]],
#                                 "Mean Nr Travelers": [experimentmeans.iloc[5], experimentstd.iloc[5]],
#                                 "Mean Duration": [experimentmeans.iloc[6], experimentstd.iloc[6]],
#                                 "Bike Percentage": [experimentmeans.iloc[7], experimentstd.iloc[7]],
#                                 "Car Percentage": [experimentmeans.iloc[8], experimentstd.iloc[8]],
#                                 "Transit Percentage": [experimentmeans.iloc[9], experimentstd.iloc[9]],
#                                 "Walk Percentage": [experimentmeans.iloc[10], experimentstd.iloc[10]] 
#                                 })
#         modalsplitmeans_df= pd.concat([modalsplitmeans_df, newrows], ignore_index=True)


#     for run in poprange:
#         experimentdict = IntervRunDict[run]
#         # add a rpw to modalsplitmeans_df with the difference between the intervention and status quo
#         statusquorow = modalsplitmeans_df.loc[(modalsplitmeans_df["Experiment"] == "StatusQuo") & (modalsplitmeans_df["Population Sample"] == run)]
#         interventionrow = modalsplitmeans_df.loc[(modalsplitmeans_df["Experiment"] == scenario) & (modalsplitmeans_df["Population Sample"] == run)]
#         statusquorow = statusquorow[columns].values[0]
#         interventionrow = interventionrow[columns].values[0]
#         difference = [interventionrow[i] - statusquorow[i] for i in range(len(statusquorow))]
#         percentagechange = [difference[i]/statusquorow[i] for i in range(len(statusquorow))]
#         newrows =  pd.DataFrame({"Experiment": [f"{scenario} - StatusQuo", f"{scenario} - StatusQuo"],
#                                                             "Model Run": ["Difference", "Percentage Change"],
#                                                             "Population Sample": [run, run],
#                                                             "Mean Bike Trips": [difference[0], percentagechange[0]],
#                                                             "Mean Car Trips": [difference[1], percentagechange[1]],
#                                                             "Mean Transit Trips": [difference[2], percentagechange[2]],
#                                                             "Mean Walk Trips": [difference[3], percentagechange[3]],
#                                                             "Mean Nr Trips": [difference[4], percentagechange[4]],
#                                                             "Mean Nr Travelers": [difference[5], percentagechange[5]],
#                                                             "Mean Duration": [difference[6], percentagechange[6]],
#                                                             "Bike Percentage": [difference[7], percentagechange[7]],
#                                                             "Car Percentage": [difference[8], percentagechange[8]],
#                                                             "Transit Percentage": [difference[9], percentagechange[9]],
#                                                             "Walk Percentage": [difference[10], percentagechange[10]]
#                                                             })

#         modalsplitmeans_df= pd.concat([modalsplitmeans_df, newrows], ignore_index=True)

#     statusquomeans = modalsplitmeans_df.loc[(modalsplitmeans_df["Experiment"] == "StatusQuo")& (modalsplitmeans_df["Population Sample"] == "Mean"),columns].values[0]
#     interventionmeans = modalsplitmeans_df.loc[(modalsplitmeans_df["Experiment"] == scenario)& (modalsplitmeans_df["Population Sample"] == "Mean"),columns].values[0]
#     difference = [interventionmeans[i] - statusquomeans[i] for i in range(len(statusquomeans))]
#     percentagechange = [difference[i]/statusquomeans[i] for i in range(len(statusquomeans))]
#     percentagechangestd = modalsplitmeans_df.loc[(modalsplitmeans_df["Model Run"] == "Percentage Change")& (modalsplitmeans_df["Population Sample"] != "Mean"),columns].std(axis=0).values

#     newrows =  pd.DataFrame({"Experiment": [f"{scenario} - StatusQuo", f"{scenario} - StatusQuo", f"{scenario} - StatusQuo"],
#                                             "Model Run": ["Difference", "Percentage Change", "Percentage Change Std"],
#                                             "Population Sample": ["Mean", "Mean", "Std"],
#                                             "Mean Bike Trips": [difference[0], percentagechange[0], percentagechangestd[0]],
#                                             "Mean Car Trips": [difference[1], percentagechange[1], percentagechangestd[1]],
#                                             "Mean Transit Trips": [difference[2], percentagechange[2], percentagechangestd[2]],
#                                             "Mean Walk Trips": [difference[3], percentagechange[3], percentagechangestd[3]],
#                                             "Mean Nr Trips": [difference[4], percentagechange[4], percentagechangestd[4]],
#                                             "Mean Nr Travelers": [difference[5], percentagechange[5], percentagechangestd[5]],
#                                             "Mean Duration": [difference[6], percentagechange[6], percentagechangestd[6]],
#                                             "Bike Percentage": [difference[7], percentagechange[7], percentagechangestd[7]],
#                                             "Car Percentage": [difference[8], percentagechange[8], percentagechangestd[8]],
#                                             "Transit Percentage": [difference[9], percentagechange[9], percentagechangestd[9]],
#                                             "Walk Percentage": [difference[10], percentagechange[10], percentagechangestd[10]]
#                                             })

#     modalsplitmeans_df= pd.concat([modalsplitmeans_df, newrows], ignore_index=True)

#     modalsplitmeans_df.to_csv(f"ModalSplitMeans_{scenario}{interanalysissuffix}.csv", index=False)

# if vizintervention:
#     modalsplitmeans_df = pd.read_csv(f"ModalSplitMeans_{scenario}{interanalysissuffix}.csv")
#     columns = ["Mean Bike Trips", "Mean Car Trips", "Mean Transit Trips", "Mean Walk Trips", "Mean Nr Trips", 
#             "Mean Nr Travelers", "Mean Duration", "Bike Percentage", "Car Percentage", "Transit Percentage", "Walk Percentage"]

#     percentagechangerows = modalsplitmeans_df.loc[(modalsplitmeans_df["Model Run"] == "Percentage Change") & (modalsplitmeans_df["Population Sample"] != "Mean"),columns[0:4]]
#     percentagechangerows = percentagechangerows * 100
#     # creating a violin plot of the percentage change in the number of trips per mode
#     fig, ax = plt.subplots()
#     violin = ax.violinplot([percentagechangerows[col].values for col in columns[0:4]], showmeans=True)
#     violin["bodies"][0].set_facecolor("blue")
#     violin["bodies"][1].set_facecolor("red")
#     violin["bodies"][2].set_facecolor("green")
#     violin["bodies"][3].set_facecolor("purple")
#     ax.set_xticks(range(1,5))
#     ax.set_xticklabels(["Bike", "Car", "Transit", "Walk"])
#     ax.set_yticks(np.arange(-3,3,0.5))
#     ax.set_ylabel("Percentage Change (%)")
#     plt.savefig(f"PercentageChangeTrips_{scenario}{interanalysissuffix}.png", dpi=600, bbox_inches="tight")
import matplotlib.pyplot as plt
import pandas as pd
import os
import seaborn as sns
import geopandas as gpd
from pycirclize import Circos
import numpy as np
from matplotlib.lines import Line2D
import contextily as cx
from matplotlib_scalebar.scalebar import ScaleBar
from shapely.geometry.point import Point
from itertools import chain
####################################################

nb_agents = 21750  #87000 = 10%, 43500 = 5%, 21750 = 2.5%, 8700 = 1%
path_data = "D:\PhD EXPANSE\Data\Amsterdam\ABMRessources\ABMData\ModelRuns"
# path_data = "F:\ModelRunsOLDOLD"
os.chdir(path_data)
# experimentoverview = pd.read_csv("D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/ExperimentOverviewOLD.csv")
experimentoverview = pd.read_csv("D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/ExperimentOverview.csv")


scenarios = list(experimentoverview['Experiment'].unique())
scenarios.remove("PrkPriceIntervWithoutRemainderAdjust")
print(scenarios)

nontranspMEThweek2019 = pd.read_csv("D:\PhD EXPANSE\Data\Amsterdam\Physical Activity Data\Amsterdam_agents_nontranspmargMEThweek2019.csv")
nontranspMEThweek2019.index = nontranspMEThweek2019["agent_ID"]
nontranspMEThweek2019["transpmargMEThwk"] = nontranspMEThweek2019["totaltransportMEThwkmean"]
nontranspMEThweek2019["nontranspmargMEThwk"].fillna(0, inplace=True)
nontranspMEThweek2019["transpmargMEThwk"].fillna(0, inplace=True)

# plt.hist(nontranspMEThweek2019.loc[nontranspMEThweek2019["nontranspmargMEThwk"].notna(),"nontranspmargMEThwk"], bins=50, range=(0, 80), color = "teal", density=True)  
# # plt.title("CBS Non-transport marginal MET hours per week 2019")
# plt.xlabel("non-transport marginal MET hours per week\n(microdata extrapolation to synthetic population)")
# plt.ylabel("Density")
# plt.savefig(r"D:\PhD EXPANSE\Data\Amsterdam\Physical Activity Data\NontranspmargMEThweek2019.png", dpi = 600, bbox_inches = "tight")
# # plt.show()
# plt.close()

# plt.hist(nontranspMEThweek2019.loc[nontranspMEThweek2019["transpmargMEThwk"].notna(),"transpmargMEThwk"], bins=50, range=(0, 100), color = "teal", density=True)  
# # plt.title("CBS Transport marginal MET hours per week 2019")
# plt.xlabel("transport marginal MET hours per week\n(microdata extrapolation to synthetic population)")
# plt.ylabel("Density")
# plt.savefig(r"D:\PhD EXPANSE\Data\Amsterdam\Physical Activity Data\CBSTranspmargMEThweek2019.png", dpi = 600, bbox_inches = "tight")
# # plt.show()
# plt.close()


# populationsamples = []
# for i in range(10):
#     pop = pd.read_csv(f"D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/Population/Amsterdam_population_subset{nb_agents}_{i}.csv")
#     pop["nontranspmargMEThwk"]  = nontranspMEThweek2019.loc[pop["agent_ID"], "nontranspmargMEThwk"]
#     pop["transpmargMEThwk"]  = nontranspMEThweek2019.loc[pop["agent_ID"], "transpmargMEThwk"]
#     populationsamples.append(pop)

# exposure = "NO2"
# exposure = "MET"

# for scenario in scenarios:
#     print(scenario)
#     modelruns = experimentoverview.loc[(experimentoverview["Experiment"] == scenario)& (experimentoverview["Number of Agents"] == f"{nb_agents}Agents"), "Model Run"].values
#     popsamples = [experimentoverview.loc[experimentoverview["Model Run"]== modelrun, "Population Sample"].values[0] for modelrun in modelruns]
#     popsamples = [int(pop.replace("ElectricCarOwnership", "")) for pop in popsamples]

#     for i, modelrun in enumerate(modelruns):
#         print(modelrun, popsamples[i])
#         exposure = pd.read_csv(f"{scenario}/{nb_agents}Agents/AgentExposure/{modelrun}/ExposureViz/Exposure_A{nb_agents}_{modelrun}_verticalAsRows.csv")
#         uniqueAgentIDs = populationsamples[popsamples[i]]["agent_ID"].unique()
#         NO2_means = exposure.groupby("agent_ID")["NO2"].mean()
#         NO2wFiltermeans = exposure.groupby("agent_ID")["NO2wFilter"].mean()
#         NO2 = NO2_means.reindex(uniqueAgentIDs).tolist()
#         NO2wFilter = NO2wFiltermeans.reindex(uniqueAgentIDs).tolist()
#         populationsamples[popsamples[i]][f"NO2_{scenario}"] = NO2
#         populationsamples[popsamples[i]][f"NO2wFilter_{scenario}"] = NO2wFilter
#         exposure = pd.read_csv(f"{scenario}/{nb_agents}Agents/UpdatedExposure/{modelrun}/ExposureViz/MarginalMET_A{nb_agents}_{modelrun}_verticalAsRows.csv")
#         METweekly = exposure.groupby(["agent_ID", "month"])["METtot"].sum()
#         METweekly = METweekly.groupby("agent_ID").mean()
#         METh = METweekly.reindex(uniqueAgentIDs).tolist()
#         populationsamples[popsamples[i]][f"transportMEThwk_{scenario}"] = METh

# for i, pop in enumerate(populationsamples):
#     pop.to_csv(f"D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/Population/Exposure/Amsterdam_population_subset{nb_agents}_{i}_exposure.csv", index=False)


StatQdf = pd.DataFrame()
transportMEThwk, totMETwk = [], [] 
NO2wfilter, NO2personal = [], []
populationsamples = []
for i in range(10):
    pop = pd.read_csv(f"D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/Population/Exposure/Amsterdam_population_subset{nb_agents}_{i}_exposure.csv")
    for scenario in scenarios:
        pop["nontranspmargMEThwk"]  = nontranspMEThweek2019["nontranspmargMEThwk"].loc[pop["agent_ID"]].values
        pop["transpmargMEThwk"]  = nontranspMEThweek2019["transpmargMEThwk"].loc[pop["agent_ID"]].values
        pop[f"totalMEThwk_{scenario}"] = pop[f"transportMEThwk_{scenario}"].values + pop["nontranspmargMEThwk"].values
        if scenario == "StatusQuo":
            transportMEThwk.extend(pop[f"transportMEThwk_{scenario}"])
            totMETwk.extend(pop[f"totalMEThwk_{scenario}"])
            NO2wfilter.extend(pop[f"NO2wFilter_{scenario}"])
            NO2personal.extend(pop[f"NO2_{scenario}"])
            StatQdf = pd.concat([StatQdf, pop[["agent_ID", "age", "sex", "totalMEThwk_StatusQuo", "transportMEThwk_StatusQuo", "nontranspmargMEThwk", "transpmargMEThwk"]]], axis=0)
    pop.to_csv(f"D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/Population/Exposure/Amsterdam_population_subset{nb_agents}_{i}_exposure.csv", index=False)


# plt.hist(transportMEThwk, bins=50, range=(0, 100), color = "teal", density=True)  
# # plt.title("ABM Transport marginal MET hours per week")
# plt.xlabel("transport marginal MET hours per week\n(ABM Status Quo estimate)")
# plt.ylabel("Density")
# plt.savefig(r"D:\PhD EXPANSE\Data\Amsterdam\Physical Activity Data\ABMtranspmargMEThweek.png", dpi = 600, bbox_inches = "tight")
# # plt.show()
# plt.close()

# plt.hist(totMETwk, bins=50, range=(0, 120), color = "teal", density=True)  
# # plt.title("ABM total marginal MET hours per week")
# plt.xlabel("total marginal MET hours per week\n(sum of ABM transport METh and microdata non-transport METh)")
# plt.ylabel("Density")
# plt.savefig(r"D:\PhD EXPANSE\Data\Amsterdam\Physical Activity Data\ABMtotmargMEThweek.png", dpi = 600, bbox_inches = "tight")
# # plt.show()
# plt.close()

# plt.hist(NO2personal, bins=50, range=(0, 50), color = "teal", density=True)
# # plt.title("ABM NO2 with filter")
# plt.xlabel("Personal NO2\n(ABM Status Quo estimate)")
# plt.ylabel("Density")
# plt.savefig(r"D:\PhD EXPANSE\Written Paper\04- Case study 1 - Transport Interventions\figures\ABMNO2hist.png", dpi = 600, bbox_inches = "tight")
# plt.close()

# plt.hist(NO2wfilter, bins=50, range=(0, 50), color = "teal", density=True)
# # plt.title("ABM NO2 with filter")
# plt.xlabel("Personal NO2 with O/I filter \n(ABM Status Quo estimate)")
# plt.ylabel("Density")
# plt.savefig(r"D:\PhD EXPANSE\Written Paper\04- Case study 1 - Transport Interventions\figures\ABMNO2wfilterhist.png", dpi = 600, bbox_inches = "tight")
# plt.close()




# StatQdf["age_group10"] = pd.cut(StatQdf["age"], bins = range(0, 110, 10), labels = ["aged0to10", "aged10to20", "aged20to30", "aged30to40", "aged40to50", "aged50to60", "aged60to70", "aged70to80", "aged80to90", "aged90to100"])


# strat = [["age_group10", "sex"], ["age_group10"], ["sex"]]

# for stratification in strat:
#     stratdistrmean = StatQdf[stratification+["totalMEThwk_StatusQuo", "transportMEThwk_StatusQuo", "nontranspmargMEThwk", "transpmargMEThwk"]].groupby(stratification).mean()
#     stratdistrmean.columns = ["totalMEThwk_mean", "transportMEThwk_mean", "nontranspmargMEThwk_mean", "transpmargMEThwk_mean"]
#     stratdistrQ10 = StatQdf[stratification+["totalMEThwk_StatusQuo", "transportMEThwk_StatusQuo", "nontranspmargMEThwk", "transpmargMEThwk"]].groupby(stratification).quantile(0.1)
#     stratdistrQ10.columns = ["totalMEThwk_Q10", "transportMEThwk_Q10", "nontranspmargMEThwk_Q10", "transpmargMEThwk_Q10"]
#     stratdistrQ25 = StatQdf[stratification+["totalMEThwk_StatusQuo", "transportMEThwk_StatusQuo", "nontranspmargMEThwk", "transpmargMEThwk"]].groupby(stratification).quantile(0.25)
#     stratdistrQ25.columns = ["totalMEThwk_Q25", "transportMEThwk_Q25", "nontranspmargMEThwk_Q25", "transpmargMEThwk_Q25"]
#     stratdistrQ75 = StatQdf[stratification+["totalMEThwk_StatusQuo", "transportMEThwk_StatusQuo", "nontranspmargMEThwk", "transpmargMEThwk"]].groupby(stratification).quantile(0.75)
#     stratdistrQ75.columns = ["totalMEThwk_Q75", "transportMEThwk_Q75", "nontranspmargMEThwk_Q75", "transpmargMEThwk_Q75"]
#     stratdistrQ90 = StatQdf[stratification+["totalMEThwk_StatusQuo", "transportMEThwk_StatusQuo", "nontranspmargMEThwk", "transpmargMEThwk"]].groupby(stratification).quantile(0.90)
#     stratdistrQ90.columns = ["totalMEThwk_Q90", "transportMEThwk_Q90","nontranspmargMEThwk_Q90", "transpmargMEThwk_Q90"]

#     # merge the dataframes based on age_group and sex columns
#     stratdistr = pd.concat([stratdistrmean, stratdistrQ10, stratdistrQ25, stratdistrQ75, stratdistrQ90], axis=1)

#     totalcolumns = stratdistr.columns
#     totMETcols = [col for col in totalcolumns if "total" in col]
#     transportMETcols = [col for col in totalcolumns if "transport" in col]
#     nontranspMETcols = [col for col in totalcolumns if "nontransp" in col]
#     transCBScols = [col for col in totalcolumns if "transpmarg" in col and "nontransp" not in col]

#     stratstring = "_".join(stratification)
#     stratdistr[totMETcols+ transportMETcols+nontranspMETcols + transCBScols].to_csv(fr"D:\PhD EXPANSE\Data\Amsterdam\Physical Activity Data\ABM_METhstratdistr{stratstring}.csv")

#     stratdistr = pd.read_csv(fr"D:\PhD EXPANSE\Data\Amsterdam\Physical Activity Data\ABM_METhstratdistr{stratstring}.csv")
#     totalcolumns = stratdistr.columns
#     transportMETcols = [col for col in totalcolumns if "transport" in col]
#     nontranspMETcols = [col for col in totalcolumns if "nontransp" in col]
#     transCBScols = [col for col in totalcolumns if "transpmarg" in col and "nontransp" not in col]

#     print(stratdistr)

#     stratdistr2 = stratdistr[stratification+transportMETcols].iloc[2:].copy()
#     stratdistr3 = stratdistr[stratification+transCBScols].iloc[2:].copy()

#     melted= pd.melt(stratdistr2, id_vars=stratification, var_name='Statistic', value_name='ABMValue')
#     melted2= pd.melt(stratdistr3, id_vars=stratification, var_name='Statistic', value_name='CBSValue')

#     melted["CBSValue"] = melted2["CBSValue"]
#     melted["Statistic"] = melted["Statistic"].str.replace("transportMEThwk_", "")

#     print("processing", stratification)

#     print(melted["ABMValue"].corr(melted["CBSValue"]))

#     # print RMSE #normalized NRMSE
#     RMSE = np.sqrt(np.mean((melted["ABMValue"] - melted["CBSValue"])**2))
#     print(RMSE)
#     # normalized RMSE
#     NRMSE = RMSE/np.mean(melted["CBSValue"])
#     print(NRMSE)

#     melted["tot_correlation"] = melted["ABMValue"].corr(melted["CBSValue"])
#     melted["tot_RMSE"] = RMSE
#     melted["tot_NRMSE"] = NRMSE

#     melted[["group_corr", "group_RMSE", "group_NRMSE"]] = None

#     for summary in ["mean", "Q10", "Q25", "Q75", "Q90"]:
#         melted_summary = melted.loc[melted["Statistic"].str.contains(summary)]
#         corr = melted_summary["ABMValue"].corr(melted_summary["CBSValue"])
#         RMSE = np.sqrt(np.mean((melted_summary["ABMValue"] - melted_summary["CBSValue"])**2))
#         NRMSE = RMSE/np.mean(melted_summary["CBSValue"])
#         melted.loc[melted["Statistic"].str.contains(summary),["group_corr", "group_RMSE", "group_NRMSE"]] = corr, RMSE, NRMSE

#     melted.to_csv(fr"D:\PhD EXPANSE\Data\Amsterdam\Physical Activity Data\ABM_METhstratdistrTransport{stratstring}.csv", index=False)



# CBSdata = pd.read_csv(r"D:\PhD EXPANSE\Data\Amsterdam\Physical Activity Data\241121_0500_9234_stratMEThweek\9234_stratMEThweek\2019\MarginalMETIND2019_aggrdata_age10ysteps_transportMET.csv")

# StatQdf["age_groups_10y_steps"] = pd.cut(StatQdf["age"], bins = [0,15,20,30,40,50,60,70,80,110], labels = ["aged0to15", "aged15to20", "aged20to30", "aged30to40", "aged40to50", "aged50to60", "aged60to70", "aged70to80", "aged80to100"])
# stratdistrmean = StatQdf[["age_groups_10y_steps","transportMEThwk_StatusQuo"]].groupby("age_groups_10y_steps").mean()
# CBSdata["ABMValue"] = stratdistrmean["transportMEThwk_StatusQuo"].values

# corr = CBSdata["ABMValue"].corr(CBSdata["Transport Marginal MET"])
# RMSE = np.sqrt(np.mean((CBSdata["ABMValue"] - CBSdata["Transport Marginal MET"])**2))
# NRMSE = RMSE/np.mean(CBSdata["Transport Marginal MET"])

# CBSdata["tot_correlation"] = corr
# CBSdata["tot_RMSE"] = RMSE
# CBSdata["tot_NRMSE"] = NRMSE

# CBSdata.to_csv(r"D:\PhD EXPANSE\Data\Amsterdam\Physical Activity Data\ABM_METhstratdistrTransportage_groups_10y_steps.csv", index=False)



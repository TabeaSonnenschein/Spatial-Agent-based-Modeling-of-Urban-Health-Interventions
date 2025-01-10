import pandas as pd
import os
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
import pyarrow.feather as feather
from sklearn_pmml_model.ensemble import PMMLForestClassifier
from shapely.geometry import LineString, Point, Polygon, GeometryCollection
from sklearn import tree
from collections import Counter

# ####################################################
# ### Adding Electric Car Ownership
# ####################################################

# datapath = r"D:\PhD EXPANSE\Written Paper\04- Case study 1 - Transport Interventions\interventiondocs\mileuzonen\electric carownership"

# # ## growth rate of electric car adoption
# # data_growth = pd.read_csv(datapath+"/table_07c0c935-23ca-4390-8bf0-74f1fbd373ac.csv")
# # cols = data_growth.columns
# # data_growth = data_growth.rename(columns={cols[0]: "year"})
# # data_growth[cols[1]] = data_growth[cols[1]].str.replace(",", ".").astype(float)
# # data_growth[cols[3]] = data_growth[cols[3]].str.replace(",", ".").astype(float)
# # data_growth["total"] = data_growth[[cols[1], cols[3]]].sum(axis=1)
# # data_growth = data_growth[["year", "total", cols[1], cols[3]]]
# # data_growth["growthrate"] = data_growth["total"].pct_change()
# # print(data_growth)
# # data_growth.to_csv(datapath+"/electric_car_adoption_growth.csv", index=False)
# # mean_annual_growth = data_growth["growthrate"].mean()
# # print("Mean annual growth rate: ", mean_annual_growth)

# # ## conditional propensities
# # ## sex, age
# # # data_sexage = pd.read_csv(datapath+"/table_55706BFB8D7048C9A72E59F9C378ED8E.csv")
# # # print(data_sexage)
# # data_sexage2= pd.read_csv(datapath+"/table_779c6fff-ed77-494f-9a9a-8a1b01a10b18.csv")
# # # rename columns to year, male, female
# # data_sexage2.columns = ["age", "male", "female"]
# # # melt dataset to long format
# # print(data_sexage2)
# # male = data_sexage2[["age", "male"]]
# # male["sex"] = "male"
# # male.columns = ["age", "propensity", "sex"]
# # female = data_sexage2[["age", "female"]]
# # female["sex"] = "female"
# # female.columns = ["age", "propensity", "sex"]
# # data_sexage = pd.concat([male, female])
# # data_sexage["propensity"] = data_sexage["propensity"].str.replace(",", ".").astype(float)
# # data_sexage[["age", "sex", "propensity"]].to_csv(datapath+"/electric_car_adoption_sexage.csv", index=False)


# # # ## hh income, hh type
# # data_incomehht = pd.read_csv(datapath+"/table_D92008E0E1DB4CD69B9695E2C618A38F.csv")
# # data_incomehht.iloc[:,5] = data_incomehht.iloc[:,5].str.replace(",", ".").astype(float)
# # data_income = data_incomehht.iloc[0:5, [1, 5]]
# # data_income.columns = ["income", "propensity"]
# # data_hht = data_incomehht.iloc[11:17, [1, 5]]
# # data_hht.columns = ["hh_type", "propensity"]
# # print(data_income)
# # print(data_hht)
# # data_income.to_csv(datapath+"/electric_car_adoption_income.csv", index=False)
# # data_hht.to_csv(datapath+"/electric_car_adoption_hhtype.csv", index=False)

# # ### regional likelihood
# # data_region = pd.read_csv(datapath+"/table_42dd4172-bcd6-445b-bc04-7f76591c8589.csv")
# # data_region = data_region.loc[data_region["Gemeentenaam"] == "Amsterdam"]
# # data_region.columns = ["region", "propensity"]
# # data_region["propensity"] = data_region["propensity"].str.replace(",", ".").astype(float)
# # data_region.to_csv(datapath+"/electric_car_adoption_region.csv", index=False)

# # # ## car ownership
# # # ### adjust for fraction of car owners
# # Agent_df = pd.read_csv(r"D:\PhD EXPANSE\Data\Amsterdam\ABMRessources\ABMData\Population\Agent_pop_clean.csv")
# # print(Agent_df.columns)
# # carownershipfraction = Agent_df["car_access"].mean()
# # print("Car ownership fraction: ", carownershipfraction)

# # # ## taking mean propensity across attribute combinations
# # data_sexage = pd.read_csv(datapath+"/electric_car_adoption_sexage.csv")
# # print(data_sexage)

# # data_income = pd.read_csv(datapath+"/electric_car_adoption_income.csv")
# # print(data_income)
# # total_propensity = data_income["propensity"].iloc[0]
# # data_income = data_income.iloc[1:]

# # data_hht = pd.read_csv(datapath+"/electric_car_adoption_hhtype.csv")
# # print(data_hht)

# # data_region= pd.read_csv(datapath+"/electric_car_adoption_region.csv")
# # print(data_region)
# # Regionaladjuster = data_region["propensity"].iloc[0]/total_propensity
# # print("Regional adjuster: ", Regionaladjuster)

# # # repeat data_sexage for each income and hht
# # allpropensity = pd.concat([data_sexage]*len(data_income)*len(data_hht), ignore_index=True)
# # # rename propensity to propensitysexage
# # allpropensity.rename(columns={"propensity": "propensitysexage"}, inplace=True)
# # allpropensity["income"] = list(np.repeat(data_income["income"].values, len(data_sexage)))*len(data_hht)
# # allpropensity["propensityincome"] = list(np.repeat(data_income["propensity"].values, len(data_sexage)))*len(data_hht)
# # allpropensity["hh_type"] = list(np.repeat(data_hht["hh_type"].values, len(data_sexage)*len(data_income)))                                                                  
# # allpropensity["propensityhht"] = list(np.repeat(data_hht["propensity"].values, len(data_sexage)*len(data_income)))
# # allpropensity = allpropensity[["age", "sex", "income", "hh_type", "propensitysexage", "propensityincome", "propensityhht"]] 
# # allpropensity["Regionaladjuster"] = Regionaladjuster
# # allpropensity["propensity"] = allpropensity[["propensitysexage","propensityincome","propensityhht"]].mean(axis=1)
# # allpropensity["propensity"] = allpropensity["propensity"]*Regionaladjuster
# # print(allpropensity)
# # allpropensity.to_csv(datapath+"/electric_car_adoption_allpropensityAmsterdam2020.csv", index=False)


# # ## calculate propensity for car owners to have electric cars
# # carownerfactor = 1/carownershipfraction
# # print("Car owner factor: ", carownerfactor)
# # allpropensity["carownerfactor"] = carownerfactor
# # allpropensity["propensity"] = allpropensity["propensity"]*carownerfactor
# # allpropensity.to_csv(datapath+"/electric_car_adoption_allpropensityAmsterdam2020_carowners.csv", index=False)


# # ##### values from 2020
# # data_growth = pd.read_csv(datapath+"/electric_car_adoption_growth.csv")
# # mean_annual_growth = data_growth["growthrate"].mean()
# # print("Mean annual growth rate: ", mean_annual_growth)
# # years = np.arange(2021, 2031)
# # print(years)

# # for year in years:
# #     allpropensity[f"propensity_{year}"] = allpropensity["propensity"]*(1+mean_annual_growth)**(year-2020)
# #     print((1+mean_annual_growth)**(year-2020))
# #     allpropensity.loc[allpropensity[f"propensity_{year}"]>100, f"propensity_{year}"] = 100 

# # allpropensity.to_csv(datapath+"/electric_car_adoption_allpropensityAmsterdam2020_2030.csv", index=False)

# allpropensity = pd.read_csv(datapath+"/electric_car_adoption_allpropensityAmsterdam2020_2030.csv")
# print(allpropensity.head(20))
# # ## adding electric car ownership to the agents
# Agent_df = pd.read_csv(r"D:\PhD EXPANSE\Data\Amsterdam\ABMRessources\ABMData\Population\Agent_pop_clean.csv")
# origcols = Agent_df.columns
# print(Agent_df.columns)
# relevant_cols = ["age", "sex", "hh_single", "HH_size", "havechild", "Nrchildren", "incomeclass_int", "car_access"]
# # reclasssify age
# Agent_df["agegroup"] = pd.cut(Agent_df["age"], bins=[0, 18, 30, 40, 50, 60, 70, 110], labels=["0-18", "18 tot 30 jaar", "30 tot 40 jaar", "40 tot 50 jaar", "50 tot 60 jaar", "60 tot 70 jaar", "70 jaar of ouder"])
# print(Agent_df["agegroup"].value_counts())

# # reclassify income
# Agent_df["incomequarter"] = pd.cut(Agent_df["incomeclass_int"], bins=[0, 4, 6, 8, 11], labels=["1e 25%-groep", 
#                                                                                         "2e 25%-groep", 
#                                                                                         "3e 25%-groep", 
#                                                                                         "4e 25%-groep"])
# print(Agent_df["incomequarter"].value_counts())

# # sex
# print(Agent_df["sex"].value_counts())


# ## hhtype
# Agent_df["Nr_adults"] = Agent_df["HH_size"] - Agent_df["Nrchildren"]
# Agent_df["hh_type"] = ""
# Agent_df.loc[Agent_df["hh_single"]==1, "hh_type"] = "Eenpersoons- huishouden"
# Agent_df.loc[(Agent_df["HH_size"]==2) & (Agent_df["havechild"] == 0), "hh_type"] = "Paar zonder kinderen zonder anderen"
# Agent_df.loc[(Agent_df["HH_size"]>2) & (Agent_df["havechild"] == 1), "hh_type"] = "Paar met kinderen zonder anderen"
# Agent_df.loc[(Agent_df["HH_size"]>=2) & (Agent_df["havechild"] == 1) & (Agent_df["Nr_adults"]==1), "hh_type"] = "Eenoudergezin zonder anderen"
# Agent_df.loc[(Agent_df["HH_size"]>=2) & (Agent_df["Nr_adults"]>2), "hh_type"] = "Overige meerpersoons-huishouden"
# print(Agent_df["hh_type"].value_counts())

# print(Agent_df.head(20))
# originalorder = Agent_df["agent_ID"]

# allpropensity_clean = allpropensity[["age", "sex", "income", "hh_type", "propensity", "propensity_2025",  "propensity_2030"]]
# allpropensity_clean.columns = ["agegroup", "sex", "incomequarter", "hh_type", "propensity_2020", "propensity_2025",  "propensity_2030"]
# allpropensity_clean["car_access"] = 1

# Agent_df_extended = pd.merge(Agent_df, allpropensity_clean, on=["agegroup", "sex", "incomequarter", "hh_type", "car_access"], how="left")

# Agent_df_extended["ramdomnumber"] = np.random.uniform(0, 100, len(Agent_df_extended))

# Agent_df_extended["EV_access2021"] = 0
# Agent_df_extended["EV_access2025"] = 0
# Agent_df_extended["EV_access2030"] = 0
# Agent_df_extended.loc[Agent_df_extended["ramdomnumber"] <= Agent_df_extended["propensity_2020"], "EV_access2020"] = 1
# Agent_df_extended.loc[Agent_df_extended["ramdomnumber"] <= Agent_df_extended["propensity_2025"], "EV_access2025"] = 1
# Agent_df_extended.loc[Agent_df_extended["ramdomnumber"] <= Agent_df_extended["propensity_2030"], "EV_access2030"] = 1
# print(Agent_df_extended.head(20))

# Agent_df_extended.to_csv(datapath+"/Agent_pop_ElectricCarOwnership_full.csv", index=False)

# Agent_df_clean = Agent_df_extended[list(origcols)+["EV_access2020", "EV_access2025", "EV_access2030"]]
# Agent_df_clean.to_csv(datapath+"/Agent_pop_ElectricCarOwnership.csv", index=False)

# ###################################################
# ### save the altered subset data #################
# ###################################################
# path_data = "D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/Population/"
# # set directory to path_data
# os.chdir(path_data)
# fulldata = pd.read_csv("Agent_pop_cleanElectricCarOwnership.csv")
# subsets = range(10)

# for subset in subsets:
#     subsetdf = pd.read_csv(f"Amsterdam_population_subset21750_{subset}.csv")
#     print(subsetdf.head())
#     subsetdf = pd.merge(subsetdf, fulldata[["agent_ID", "EV_access2020", "EV_access2025", "EV_access2030"]], on="agent_ID", how="left")
#     print(subsetdf.head())
#     subsetdf.to_csv(f"Amsterdam_population_subset21750_{subset}ElectricCarOwnership.csv", index=False)


# ##############################################
# ## project commercial EV share
# ##############################################

# datapath = r"D:\PhD EXPANSE\Written Paper\04- Case study 1 - Transport Interventions\interventiondocs\mileuzonen\electric carownership"

# ## growth rate of electric car adoption
# data_growth = pd.read_csv(datapath+"/table_07c0c935-23ca-4390-8bf0-74f1fbd373ac.csv")
# cols = data_growth.columns
# print(data_growth)
# print(cols)
# data_growth = data_growth.rename(columns={cols[0]: "year"})
# data_growth[cols[2]] = data_growth[cols[2]].str.replace(",", ".").astype(float)
# data_growth[cols[4]] = data_growth[cols[4]].str.replace(",", ".").astype(float)
# data_growth["total"] = data_growth[[cols[2], cols[4]]].sum(axis=1)
# data_growth = data_growth[["year", "total", cols[2], cols[4]]]
# data_growth["growthrate"] = data_growth["total"].pct_change()
# print(data_growth)
# data_growth.to_csv(datapath+"/commercialelectric_car_adoption_growth.csv", index=False)
# mean_annual_growth = data_growth["growthrate"].mean()
# print("Mean annual growth rate: ", mean_annual_growth)

# ## percentage of commercial vehicles
# data_commercial = pd.read_csv(datapath+"/table_191317b3-7194-4ba3-b31e-c154dbcfab26.csv")
# print(data_commercial)
# cols = data_commercial.columns
# data_commercial[cols[1]] = data_commercial[cols[1]].str.replace(",", "").astype(int)
# data_commercial[cols[2]] = data_commercial[cols[2]].str.replace(",", "").astype(int)
# totalEV = data_commercial[cols[1]].sum()
# totalNonEV = data_commercial[cols[2]].sum()
# total = totalEV + totalNonEV
# percentagEV = totalEV/total
# print("Percentage of EVs 2022: ", percentagEV)


# Years = np.arange(2022, 2031)
# percentagEVs = [percentagEV]
# for year in Years[1:]:
#     evs = percentagEV*(1+mean_annual_growth)**(year-2022)
#     percentagEVs.append(evs)
    
# print(percentagEVs)
# percentagEVs = [val if val < 1  else 1 for val in percentagEVs]
# pd.DataFrame({"year": Years, "percentageEV": percentagEVs}).to_csv(datapath+"/commercialelectric_car_adoption_percentageEV.csv", index=False)


# ####################################################
# ## altering baseline traffic in zones
# ####################################################

# NoEmissionZone = gpd.read_file(r"D:\PhD EXPANSE\Written Paper\04- Case study 1 - Transport Interventions\figures\Intervention Designs\mileuzonen\Uitstootvrijgebied2025.shp")

# TrafficRemainder = pd.read_csv(r"D:\PhD EXPANSE\Data\Amsterdam\ABMRessources\ABMData\TrafficRemainder\AirPollGrid_HourlyTraffRemainder_21750.csv")
# Grid = gpd.read_file(r"D:\PhD EXPANSE\Data\Amsterdam\ABMRessources\ABMData\AirPollutionModelData\AirPollDeterm_grid50m.shp")
# print(Grid.columns)

# # make the int_id column to int
# Grid["int_id"] = Grid["int_id"].astype(int)

# # polygons that lie within the NoEmissionZone
# Grid["zone"] = ""
# for i, zone in enumerate(NoEmissionZone["geometry"]):
#     Grid.loc[Grid["geometry"].within(zone), "zone"] = 1
    
# IntIDs = Grid.loc[Grid["zone"]==1, "int_id"].unique()
# print(TrafficRemainder.head(20))
# print(Grid.head(20))
# print(IntIDs)
# print(len(IntIDs))

# Ringroad = gpd.read_file(r"D:\PhD EXPANSE\Data\Amsterdam\Built Environment\Transport Infrastructure\cars\RingwegHighway.shp")
# print(Ringroad.columns)
# Ringroad["ringroad"] = 1
# # find grid cells intersecting with ringroad

# ringcells = gpd.sjoin(Grid, Ringroad[["geometry", "ringroad"]], how="inner", predicate="intersects")
# ringcells = ringcells["int_id"]
# print("Ringcells", len(ringcells))

# IntIds = [intid for intid in IntIDs if not(intid in ringcells)]
# print("New IntIds", len(IntIds))

# TraffCols = TrafficRemainder.columns[1:]

# Gridplot = pd.merge(Grid, TrafficRemainder, on="int_id", how="left")
# Gridplot.plot(column="TraffVrest8", legend=True)
# plt.savefig(r"D:\PhD EXPANSE\Written Paper\04- Case study 1 - Transport Interventions\figures\Intervention Designs\mileuzonen\BeforeNoEmissionZone2025_TraffRemainder8_21750.png", dpi = 600, bbox_inches = 'tight')

# TrafficRemainder.loc[TrafficRemainder["int_id"].isin(IntIDs), TraffCols] = 0.0

# ## read commercial EV share
# data_commercial = pd.read_csv(r"D:\PhD EXPANSE\Written Paper\04- Case study 1 - Transport Interventions\figures\Intervention Designs\mileuzonen\electric carownership"+"/commercialelectric_car_adoption_percentageEV.csv")
# commericalEVshare = data_commercial.loc[data_commercial["year"]== 2025, "percentageEV"].values[0]
# print(commericalEVshare)

# TrafficRemainder[TraffCols] = TrafficRemainder[TraffCols]*(1-commericalEVshare)

# TrafficRemainder.to_csv(r"D:\PhD EXPANSE\Data\Amsterdam\ABMRessources\ABMData\TrafficRemainder\AirPollGrid_HourlyTraffRemainder_21750_NoEmissionZone2025.csv", index=False)


# # join the Grid and Traffic Remainder and plot the traffic remainder
# Grid = pd.merge(Grid, TrafficRemainder, on="int_id", how="left")
# Grid.plot(column="TraffVrest8", legend=True)
# plt.savefig(r"D:\PhD EXPANSE\Written Paper\04- Case study 1 - Transport Interventions\figures\Intervention Designs\mileuzonen\NoEmissionZone2025_TraffRemainder8_21750.png", dpi = 600, bbox_inches = 'tight')
# plt.show()



##########################################
### calculate percentage of electric car access
##########################################

# # read Agent_pop_ElectricCarOwnership.csv
# Agent_df = pd.read_csv(r"D:\PhD EXPANSE\Data\Amsterdam\ABMRessources\ABMData\Population\Agent_pop_cleanElectricCarOwnership.csv")

# nr_agents = len(Agent_df)
# nr_agents_EV2025 = Agent_df["EV_access2025"].sum()
# nr_agents_car_access = Agent_df["car_access"].sum()
# nr_agents_EV2030 = Agent_df["EV_access2030"].sum()

# print("Nr of agents: ", nr_agents)
# print("Nr of agents with EV access 2025: ", nr_agents_EV2025)
# print("Nr of agents with car access: ", nr_agents_car_access)
# print("Nr of agents with EV access 2030: ", nr_agents_EV2030)

# print("Percentage of EV from all vehicles: ", nr_agents_EV2025/nr_agents_car_access)
# print("Percentage of population with EV access: ", nr_agents_EV2025/nr_agents)
# print("Percentage of population with non-EV access: ", (nr_agents_car_access-nr_agents_EV2025)/nr_agents)
# print("Percentage car access of the total population 2020: ", nr_agents_car_access/nr_agents)
# print("Percentage reduction in nr of vehicles 2030: ", (nr_agents_car_access-nr_agents_EV2030)/nr_agents_car_access)
# print("Percentage of population with EV access 2030: ", nr_agents_EV2030/nr_agents)




# ########################################
# ### save NoEmissionZone as feather file
# ######################################## 
# NoEmissionZone = gpd.read_file(r"D:\PhD EXPANSE\Written Paper\04- Case study 1 - Transport Interventions\interventiondocs\mileuzonen\Uitstootvrijgebied2025.shp")
# NoEmissionZone.to_feather(r"D:\PhD EXPANSE\Data\Amsterdam\ABMRessources\ABMData\SpatialData\NoEmissionZone2025.feather")

# NoEmissionZone = gpd.read_file(r"D:\PhD EXPANSE\Written Paper\04- Case study 1 - Transport Interventions\interventiondocs\mileuzonen\UitstootvrijAmsterdam2030.shp")
# NoEmissionZone.to_feather(r"D:\PhD EXPANSE\Data\Amsterdam\ABMRessources\ABMData\SpatialData\NoEmissionZone2030.feather")

# #################################################
# ### check behavioral model for implementing NoEmissionZone
# #################################################
# def add_suffix(lst,  suffix): 
#     return  list(map(lambda x: x + suffix, lst))

# path_data = "D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/"
# crs = "epsg:28992"

# # read spatial data
# EnvBehavDeterms = gpd.read_feather(path_data+f"SpatialData/EnvBehavDeterminants.feather")
# Residences = gpd.read_feather(path_data+"SpatialData/Residences.feather")

# # Read the Mode of Transport Choice Model
# print("Reading Mode of Transport Choice Model")
# routevariables = ["RdIntrsDns", "retaiDns","greenCovr", "popDns", "TrafAccid", "NrTrees", "MeanTraffV", "HighwLen", "AccidPedes",
#                     "PedStrWidt", "PedStrLen", "LenBikRout", "DistCBD", "retailDiv", "MeanSpeed", "MaxSpeed", "NrStrLight", "CrimeIncid",
#                     "MaxNoisDay", "OpenSpace", "PNonWester", "PWelfarDep", "SumTraffVo", "pubTraDns", "MxNoisNigh", "MinSpeed", "PrkPricPre" ]
# personalvariables = ["sex_male", "age", "car_access", "Western", "Non_Western", "Dutch", 'income','employed',
#                             'edu_3_levels','HH_size', 'Nrchildren', 'student', 'driving_habit','biking_habit','transit_habit']
# tripvariables = ["trip_distance", "purpose_commute", 'purpose_leisure','purpose_groceries_shopping',
#                             'purpose_education', 'purpose_bring_person']
# weathervariables = ['Temperature', 'Rain', 'Windspeed','Winddirection' ]
# originvariables = ["pubTraDns", "DistCBD"]
# destinvariables = ["pubTraDns", "DistCBD", "NrParkSpac", "PrkPricPre"]

# routevariables_suff = add_suffix(routevariables, ".route")
# originvariables_suff = add_suffix(originvariables, ".orig")
# destinvariables_suff = add_suffix(destinvariables, ".dest")
# colvars = routevariables_suff + originvariables_suff + destinvariables_suff + personalvariables + tripvariables + weathervariables

# ModalChoiceModel = PMMLForestClassifier(pmml=path_data+f"ModalChoiceModel/RandomForest.pmml")
# ModalChoiceModel.splitter = "random"
# OrderPredVars = []
# with open(path_data+f"ModalChoiceModel/RFfeatures.txt", 'r') as file:
#     for line in file.readlines():
#         OrderPredVars.append(line.strip())
# # print(OrderPredVars)

##########################
# NrDecisiontrees = len(ModalChoiceModel.estimators_)
# print(NrDecisiontrees)
# for x in range(NrDecisiontrees):
#     fig, axes = plt.subplots(nrows = 1,ncols = 1,figsize = (25,6), dpi=1000)
#     tree.plot_tree(ModalChoiceModel.estimators_[x],
#                    feature_names = OrderPredVars, 
#                    class_names=["1","2","3","4"])
#     fig.savefig("D:/PhD EXPANSE/Written Paper/04- Case study 1 - Transport Interventions/interventiondocs/mileuzonen/ModalChoiceModel/trees/"+f"rf_individualtree{x}.png",dpi = 600)
#     plt.close(fig)

# ############################
# output_file_path = "D:/PhD EXPANSE/Written Paper/04- Case study 1 - Transport Interventions/interventiondocs/mileuzonen/ModalChoiceModel/" + "class_2_paths.txt"
# with open(output_file_path, 'w') as output_file:
#     for i, tree in enumerate(ModalChoiceModel.estimators_):
#         output_file.write(f"Tree {i+1}:\n")
#         # Get the tree structure
#         tree_structure = tree.tree_
        
#         # Access node attributes
#         children_left = tree_structure.children_left
#         children_right = tree_structure.children_right
#         feature = tree_structure.feature
#         threshold = tree_structure.threshold
#         values = tree_structure.value
        
#         # Recursive function to traverse the tree and find paths to "class 2" leaves
#         def find_class_2_paths(node_id, path_conditions):
#             # Check if this is a leaf node
#             if children_left[node_id] == children_right[node_id]:
#                 # Get the predicted class for this leaf node
#                 predicted_class = values[node_id].argmax(axis=1)
                
#                 # Check if the prediction is "class 2"
#                 if predicted_class == 2:
#                     # Print the path conditions leading to this leaf node
#                     output_file.write(f"  Leaf Node {node_id} predicts 'class 2'\n")
#                     output_file.write(f"    Path conditions:\n")
#                     for condition in path_conditions:
#                         feature_idx, split_value, direction = condition
#                         feature_name = OrderPredVars[feature_idx]
#                         direction_symbol = "<=" if direction == "left" else ">"
#                         output_file.write(f"      {feature_name} {direction_symbol} {split_value}\n")

#             else:
#                 # If not a leaf, recurse on children
#                 # Traverse left child
#                 if children_left[node_id] != -1:
#                     left_condition = (feature[node_id], threshold[node_id], "left")
#                     find_class_2_paths(children_left[node_id], path_conditions + [left_condition])
                
#                 # Traverse right child
#                 if children_right[node_id] != -1:
#                     right_condition = (feature[node_id], threshold[node_id], "right")
#                     find_class_2_paths(children_right[node_id], path_conditions + [right_condition])

#         # Start DFS from the root node
#         find_class_2_paths(0, [])
        
# #####################################################
# ### Find Key split points
# #####################################################
# ## key split points
# # Tree 1: SumTraffVo.route > 20866.185546875
# # Tree 2: MeanSpeed.route <= 34.46701431274414


# TreePaths = {}

# with open("D:/PhD EXPANSE/Written Paper/04- Case study 1 - Transport Interventions/interventiondocs/mileuzonen/ModalChoiceModel/class_2_paths.txt", 'r') as file:
#     for line in file.readlines():
#         if "Tree " in line:
#             tree = line.split()[1]
#             TreePaths[tree] = []
#         elif "Leaf" in line:
#             leaf = line.split()[2]
#             TreePaths[tree].append({"leaf": leaf, "conditions": []})
#         elif not("Path conditions:" in line):
#             TreePaths[tree][-1]["conditions"].append(line.strip())

# print(TreePaths)

# # Function to find common conditions
# def find_common_conditions(subleafs):
#     if not subleafs:
#         return []
#     # Start with conditions from the first path
#     common_conditions = set(subleafs[0]["conditions"])
#     # Intersect with conditions from other paths
#     for subleaf in subleafs[1:]:
#         common_conditions.intersection_update(subleaf["conditions"])
#     return list(common_conditions)

# def find_two_most_common_conditions(subleafs):
#     if not subleafs:
#         return []
#     # Flatten all conditions into a single list
#     all_conditions = [condition for subleaf in subleafs for condition in subleaf["conditions"]]
#     # Count the frequency of each condition
#     condition_counts = Counter(all_conditions)
#     # Find the two most common conditions
#     most_common_conditions = condition_counts.most_common(2)
#     return [condition for condition, count in most_common_conditions]

# commonconditionsfile = "D:/PhD EXPANSE/Written Paper/04- Case study 1 - Transport Interventions/interventiondocs/mileuzonen/ModalChoiceModel/common_conditions.txt"
# with open(commonconditionsfile, 'w') as output_file:
#     # Iterate over each tree and find common conditions
#     for tree in TreePaths:
#         output_file.write(f"Tree {tree}")
#         subleafs = TreePaths[tree]
        
#         # Find common conditions for this tree
#         common_conditions = find_common_conditions(subleafs)
        
#         # Print common conditions
#         if common_conditions:
#             output_file.write("\nCommon conditions across leaf nodes predicting 'class 2':")
#             for condition in common_conditions:
#                 output_file.write(f"\n  {condition}")
#         else:
#             # Find the two most common conditions if no single common condition exists
#             two_most_common_conditions = find_two_most_common_conditions(subleafs)
#             if two_most_common_conditions:
#                 output_file.write("\nTwo most common conditions across leaf nodes:")
#                 for condition in two_most_common_conditions:
#                     output_file.write(f"\n  {condition}")
#             else:
#                 output_file.write("\nNo conditions found.")
#         output_file.write("\n")


# CommonConditions = {}
# with open("D:/PhD EXPANSE/Written Paper/04- Case study 1 - Transport Interventions/interventiondocs/mileuzonen/ModalChoiceModel/common_conditions.txt", 'r') as file:
#     for line in file.readlines():
#         if "Tree " in line:
#             tree = line.split()[1]
#             CommonConditions[tree] = []
#         elif "Common conditions across leaf" in line:
#             CommonConditions[tree].append({"type": "common condition across all", "conditions": []})
#         elif "Two most common conditions" in line:
#             CommonConditions[tree].append({"type": "two most common conditions", "conditions": []})
#         else:
#             CommonConditions[tree][-1]["conditions"].append(line.strip())

# print(CommonConditions)

# ## find the most common conditions across all trees
# CommonConditionsAll = []
# for tree in CommonConditions:
#     for condition in CommonConditions[tree]:
#         CommonConditionsAll += condition["conditions"]

# condition_counts = Counter(CommonConditionsAll)

# print(condition_counts.most_common())
# condition_counts_df= pd.DataFrame(condition_counts.most_common(), columns=["condition", "count"])
# condition_counts_df["variable"] = condition_counts_df["condition"].apply(lambda x: x.split()[0])
# condition_counts_df.to_csv("D:/PhD EXPANSE/Written Paper/04- Case study 1 - Transport Interventions/interventiondocs/mileuzonen/ModalChoiceModel/common_conditions_all.csv", index=False)
# print(CommonConditions)
# condition_counts_df.groupby("variable")["count"].sum().sort_values(ascending=False).to_csv("D:/PhD EXPANSE/Written Paper/04- Case study 1 - Transport Interventions/interventiondocs/mileuzonen/ModalChoiceModel/common_conditions_all_sum.csv")


# ## find the most common conditions across all trees
# CommonConditionsAll = []
# for tree in CommonConditions:
#     for condition in CommonConditions[tree]:
#         if condition["type"] == "common condition across all":
#             CommonConditionsAll += condition["conditions"]

# condition_counts = Counter(CommonConditionsAll)

# print(condition_counts.most_common())
# condition_counts_df= pd.DataFrame(condition_counts.most_common(), columns=["condition", "count"])
# condition_counts_df["variable"] = condition_counts_df["condition"].apply(lambda x: x.split()[0])
# condition_counts_df.to_csv("D:/PhD EXPANSE/Written Paper/04- Case study 1 - Transport Interventions/interventiondocs/mileuzonen/ModalChoiceModel/common_conditions_deterministic.csv", index=False)
# condition_counts_df.groupby("variable")["count"].sum().sort_values(ascending=False).to_csv("D:/PhD EXPANSE/Written Paper/04- Case study 1 - Transport Interventions/interventiondocs/mileuzonen/ModalChoiceModel/common_conditions_deterministic_sum.csv")



# ################################################################
# ######## Running experiments
# ################################################################


# ### agents
# Agent_df = pd.read_csv(path_data+f"Population/Agent_pop_clean.csv")
# Agent_df["student"] = 0
# Agent_df.loc[Agent_df["current_education"] == "high", "student"] = 1

# ### weather data
# monthly_weather_df = pd.read_csv(path_data+"Weather/monthlyWeather2019TempDiff.csv") 
# months = pd.Series([1,4,7,10])

# def run_modeprediction_prob(samplesize, Agent_df, EnvBehavDeterms):
#     predictedmodes = []
#     for i in range(samplesize):
#         pos = Residences["geometry"].sample(1).values[0].coords[0]
#         destination_activity = Residences["geometry"].sample(1).values[0].coords[0]
#         WeatherVars = list(monthly_weather_df[["Temperature","Rain","Windspeed","Winddirection"]].loc[monthly_weather_df["month"]== months.sample(1).values[0]].values[0])
#         vector = list(Agent_df.sample(1).values[0])
#         # vector = list(Agent_df.loc[i].values)
#         IndModalPreds = [vector[i] for i in [19,2,13,20,21,22,17,11,12,23,24,25,15,14,16]] # "sex_male", "age", "car_access", 
#                                                                     # "Western", "Non_Western", "Dutch", 'income','employed',
#                                                                     #'edu_3_levels','HH_size', 'Nrchildren', 'student', 'driving_habit','biking_habit',
#                                                                     #'transit_habit']
#         route_eucl_line = LineString([Point(tuple(pos)), Point(tuple(destination_activity))])
#         trip_distance = route_eucl_line.length
#         random = pd.Series(range(10)).sample(1).values[0]
#         TripVars = [0,0,0,0,0]  #"purpose_commute", 'purpose_leisure','purpose_groceries_shopping','purpose_education', 'purpose_bring_person'
#         if random < 4:
#             TripVars[random] = 1
#         RouteVars = gpd.GeoDataFrame(data = {'id': ['1'], 'geometry': [route_eucl_line]}, geometry="geometry", crs=crs).sjoin(EnvBehavDeterms, how="left")[routevariables].mean(axis=0).values
#         OrigVars = gpd.GeoDataFrame(data = {'id': ['1'], 'geometry': [Point(tuple(pos))]}, geometry="geometry", crs=crs).sjoin(EnvBehavDeterms, how="left")[originvariables].values[0]
#         DestVars = gpd.GeoDataFrame(data = {'id': ['1'], 'geometry': [Point(tuple(destination_activity))]}, geometry="geometry",crs=crs).sjoin(EnvBehavDeterms, how="left")[destinvariables].values[0]
#         pred_df = pd.DataFrame(np.concatenate((RouteVars, OrigVars, DestVars, IndModalPreds, [trip_distance],TripVars, WeatherVars), axis=None).reshape(1, -1), 
#                                         columns=colvars).fillna(0)
#         modechoice = ModalChoiceModel.predict_proba(pred_df[OrderPredVars])
#         modechoice[0][1] = 0
#         # check which mode has the highest probability
#         modechoice = np.argmax(modechoice) + 1
#         modechoice = ["bike", "drive", "transit", "walk"][modechoice-1]
#         predictedmodes.append(modechoice)
#     return predictedmodes

# def run_modeprediction(samplesize, Agent_df, EnvBehavDeterms):
#     predictedmodes = []
#     for i in range(samplesize):
#         pos = Residences["geometry"].sample(1).values[0].coords[0]
#         destination_activity = Residences["geometry"].sample(1).values[0].coords[0]
#         WeatherVars = list(monthly_weather_df[["Temperature","Rain","Windspeed","Winddirection"]].loc[monthly_weather_df["month"]== months.sample(1).values[0]].values[0])
#         vector = list(Agent_df.sample(1).values[0])
#         # vector = list(Agent_df.loc[i].values)
#         IndModalPreds = [vector[i] for i in [19,2,13,20,21,22,17,11,12,23,24,25,15,14,16]] # "sex_male", "age", "car_access", 
#                                                                     # "Western", "Non_Western", "Dutch", 'income','employed',
#                                                                     #'edu_3_levels','HH_size', 'Nrchildren', 'student', 'driving_habit','biking_habit',
#                                                                     #'transit_habit']
#         route_eucl_line = LineString([Point(tuple(pos)), Point(tuple(destination_activity))])
#         trip_distance = route_eucl_line.length
#         random = pd.Series(range(10)).sample(1).values[0]
#         TripVars = [0,0,0,0,0]  #"purpose_commute", 'purpose_leisure','purpose_groceries_shopping','purpose_education', 'purpose_bring_person'
#         if random < 4:
#             TripVars[random] = 1
#         RouteVars = gpd.GeoDataFrame(data = {'id': ['1'], 'geometry': [route_eucl_line]}, geometry="geometry", crs=crs).sjoin(EnvBehavDeterms, how="left")[routevariables].mean(axis=0).values
#         OrigVars = gpd.GeoDataFrame(data = {'id': ['1'], 'geometry': [Point(tuple(pos))]}, geometry="geometry", crs=crs).sjoin(EnvBehavDeterms, how="left")[originvariables].values[0]
#         DestVars = gpd.GeoDataFrame(data = {'id': ['1'], 'geometry': [Point(tuple(destination_activity))]}, geometry="geometry",crs=crs).sjoin(EnvBehavDeterms, how="left")[destinvariables].values[0]
#         pred_df = pd.DataFrame(np.concatenate((RouteVars, OrigVars, DestVars, IndModalPreds, [trip_distance],TripVars, WeatherVars), axis=None).reshape(1, -1), 
#                                         columns=colvars).fillna(0)
#         modechoice = ModalChoiceModel.predict(pred_df[OrderPredVars])[0]
#         modechoice = ["bike", "drive", "transit", "walk"][modechoice-1]
#         predictedmodes.append(modechoice)
#     return predictedmodes


# predictedmodes = run_modeprediction_prob(100, Agent_df, EnvBehavDeterms)
# modes = pd.Series(predictedmodes).value_counts()


# #Status Quo
# Experimentpredictions = {}
# predictedmodes = run_modeprediction(500, Agent_df, EnvBehavDeterms)
# modes = pd.Series(predictedmodes).value_counts()
# Experimentpredictions["StatusQuo"] = modes
# Agent_orig = Agent_df.copy()
# EnvBehavDeterms_orig = EnvBehavDeterms.copy()

# #### Experiments
# Agentexperiments = ["car_access", "driving_habit", "biking_habit"] # set car access and driving_habit to 0 for all agents
# Experminentvals = [0, 0, 0]
# for count, experiment in enumerate(Agentexperiments):
#     Agent_df[experiment] = Experminentvals[count]
#     predictedmodes = run_modeprediction(500, Agent_df, EnvBehavDeterms)
#     modes = pd.Series(predictedmodes).value_counts()
#     Experimentpredictions[experiment] = modes
#     Agent_df = Agent_orig.copy()
    
# EnvBehavDetermExperiments = ["OpenSpace","SumTraffVo", "MeanTraffV", "HighwLen", "PWelfarDep", "MaxNoisDay", "RdIntrsDns", "MinSpeed"]
# EnvBehavDetermExperimentsvals = [0, 0, 0, 0, 0, 0, 50, 0]
# for count, experiment in enumerate(EnvBehavDetermExperiments):
#     EnvBehavDeterms[experiment] = EnvBehavDetermExperimentsvals[count]
#     predictedmodes = run_modeprediction(500, Agent_df, EnvBehavDeterms)
#     modes = pd.Series(predictedmodes).value_counts()
#     Experimentpredictions[experiment] = modes
#     EnvBehavDeterms = EnvBehavDeterms_orig.copy()
    
# # test all variables activated together
# for count, experiment in enumerate(Agentexperiments):
#     Agent_df[experiment] = Experminentvals[count]
# for count, experiment in enumerate(EnvBehavDetermExperiments):
#     EnvBehavDeterms[experiment] = EnvBehavDetermExperimentsvals[count]
# predictedmodes = run_modeprediction(500, Agent_df, EnvBehavDeterms)
# modes = pd.Series(predictedmodes).value_counts()
# Experimentpredictions["AllVars"] = modes

# print(Experimentpredictions)
# Experimentpredictions_df = pd.DataFrame(Experimentpredictions)
# Experimentpredictions_df.to_csv(r"D:\PhD EXPANSE\Written Paper\04- Case study 1 - Transport Interventions\interventiondocs\mileuzonen\ModalChoiceModel\ExperimentOverview.csv", index=True)

# ###########################################
# ### set Traffic to 0 and NO2 to baseline in results
# ############################################

# path_data = "D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/ModelRuns"

# if not os.path.exists(path_data+f"/NoEmissionZone2030/21750Agents/Traffic/TraffViz"):
#       # Create the directory
#       os.mkdir(path_data+f"/NoEmissionZone2030/21750Agents/Traffic/TraffViz")
      
# if not os.path.exists(path_data+f"/NoEmissionZone2030/21750Agents/NO2/NO2Viz"):
#       # Create the directory
#       os.mkdir(path_data+f"/NoEmissionZone2030/21750Agents/NO2/NO2Viz")
      
# Traffdest = path_data+f"/NoEmissionZone2030/21750Agents/Traffic/TraffViz"
# NO2dest = path_data+f"/NoEmissionZone2030/21750Agents/NO2/NO2Viz"

# # set emitting traffic to 0
# Traffic_df =  pd.read_csv(path_data+f"/StatusQuo/21750Agents/Traffic/TraffViz/TraffMeans_StatusQuo_MeanAcrossRuns.csv")
# columns = Traffic_df.columns
# Traffic_df[columns[1:]] = 0
# Traffic_df.to_csv(Traffdest+"/TraffMeans_NoEmissionZone2030_MeanAcrossRuns.csv", index=False)


# # read baseline NO2
# AirPollPred = pd.read_csv(f"D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/AirPollutionModelData/Pred_50mTrV_TrI_noTrA.csv")
# baselineNO2 = AirPollPred["baseline_NO2"]
# NO2_df =  pd.read_csv(path_data+f"/StatusQuo/21750Agents/NO2/NO2Viz/NO2Means_StatusQuo_MeanAcrossRuns.csv")
# columns = NO2_df.columns
# for col in columns[1:]:
#     NO2_df[col] = baselineNO2
# NO2_df.to_csv(NO2dest+"/NO2Means_NoEmissionZone2030_MeanAcrossRuns.csv", index=False)
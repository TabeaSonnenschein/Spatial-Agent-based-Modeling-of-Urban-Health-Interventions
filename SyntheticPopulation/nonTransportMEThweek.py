import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np
import random as rdm
from scipy.stats import expon


destinations = r"D:\PhD EXPANSE\Data\Amsterdam\Physical Activity Data"

year = 2019

datafolder = fr"D:\PhD EXPANSE\Data\Amsterdam\Physical Activity Data\241121_0500_9234_stratMEThweek\9234_stratMEThweek\{year}"
os.chdir(datafolder)

# totdistr = pd.read_csv(f"marginalMETIND_totaldistribution{year}.csv", sep=";")
# print(totdistr)

# Amsterdammer = pd.read_csv(f"MarginalMETIND{year}_aggrdata_Amsterdammer.csv", sep=";")
# age_sex_haschild = pd.read_csv(f"MarginalMETIND{year}_aggrdata_age_sex_haschild.csv", sep=";")
# age_sex_migrback = pd.read_csv(f"MarginalMETIND{year}_aggrdata_age_sex_migrback.csv", sep=";")
# age10ysteps = pd.read_csv(f"MarginalMETIND{year}_aggrdata_age10ysteps.csv", sep=";")
# edu_empl_income = pd.read_csv(f"MarginalMETIND{year}_aggrdata_edu_empl_income.csv", sep=";")
# haschild_bmi = pd.read_csv(f"MarginalMETIND{year}_aggrdata_haschild_bmi.csv", sep=";")
# hhsize_haschild = pd.read_csv(f"MarginalMETIND{year}_aggrdata_hhsize_haschild.csv", sep=";")
# income = pd.read_csv(f"MarginalMETIND{year}_aggrdata_income.csv", sep=";")
# migrback = pd.read_csv(f"MarginalMETIND{year}_aggrdata_migrback.csv", sep=";")
# sex = pd.read_csv(f"MarginalMETIND{year}_aggrdata_sex.csv", sep=";")
# sex_haschild = pd.read_csv(f"MarginalMETIND{year}_aggrdata_sex_haschild.csv", sep=";")
# urbanOrnot = pd.read_csv(f"MarginalMETIND{year}_aggrdata_urbanOrnot.csv", sep=";")

# # print(Amsterdammer.head())

# stratdfs = [age_sex_migrback, age_sex_haschild,edu_empl_income, 
#             hhsize_haschild]
# non0distr = [income,migrback,sex, sex_haschild]

# # print(Amsterdammer.columns.values)
# cols = Amsterdammer.columns.values[2:]
# print(cols)
# transportvars = ["margwwlmethwkmean", "margwwfmethwkmean", "margwanmethwkmean", "margfietmethwkmean"]
# totalMETh = 'totmargMEThwkmean'
# totalNontransportMETh = 'totnontranspmargMEThwkmean'
# totaltransportMETh = 'totaltransportMEThwkmean'
# transportvarsstd = [var.replace("mean", "std") for var in transportvars]
# transportvarstot = transportvars + transportvarsstd
# transportvarstotcompl = transportvarstot + [var.replace("mean", "pabove0") for var in transportvars]+ [var.replace("mean", "non0mean") for var in transportvars]

# nonstratcols = list(cols) +["count"]

# stratvars = []
# allvars = []
# for df in stratdfs:
#     dfcols = df.columns.values
#     localstrat = [col for col in dfcols if col not in nonstratcols]
#     stratvars.append(localstrat)
#     allvars.extend([True if all([col in dfcols for col in cols]) else False])
    
# print(stratvars)
# print(allvars)

# Amsterdammer["totaltransportMEThwkmean"] = Amsterdammer[transportvars].sum(axis=1)
# print(Amsterdammer[["Amsterdammer", "count",totalMETh, totalNontransportMETh, totaltransportMETh]].head())

# ['agegroups_6', 'sex', 'haschild'], ['agegroups_6', 'sex', 'migrationbackground']

# ['education_level', 'employed', 'incomequintile']
# ["bmi"]

# cleanstratdfs = []
# for count, stratvar in enumerate(stratvars):
#     if allvars[count]:
#         cleanstratdfs.append(stratdfs[count][stratvar+["count",totalNontransportMETh, 'totnontranspmargMEThwkstd', 'totnontranspmargMEThwkpabove0', 'totnontranspmargMEThwknon0mean']+transportvarstotcompl])
#     else:
#         cleanstratdfs.append(stratdfs[count][stratvar+["count",totalNontransportMETh, 'totnontranspmargMEThwkstd']+transportvarstot])
        


# age_sex_migrback_vals = cleanstratdfs[0][stratvars[0]]

# haschildvals = cleanstratdfs[1]['haschild'].drop_duplicates()
# # concat age_sex_migrback_vals for each haschild value
# finaldf = age_sex_migrback_vals.copy()
# finaldf["haschild"] = haschildvals[0]
# for haschild in haschildvals[1:]:
#     age_sex_migrback_vals["haschild"] = haschild
#     finaldf = pd.concat([finaldf, age_sex_migrback_vals])
# finaldf.reset_index(inplace=True, drop=True)
# print(finaldf)
    
# edu_empl_incomevals = edu_empl_income[stratvars[2]]
# finaldf[stratvars[2]] = edu_empl_incomevals.iloc[0].values
# finaltemp = finaldf.copy()
# for index in edu_empl_incomevals.index[1:]:
#     finaltemp[stratvars[2]] = edu_empl_incomevals.iloc[index].values
#     finaldf = pd.concat([finaldf, finaltemp])
# finaldf.reset_index(inplace=True, drop=True)
# print(finaldf)


# finaldf.to_csv(destinations+ f"/stratifiedMEThweek{year}sceleton.csv", index=False)


# finaldf[['totnontranspmargMEThwkmean', 'totnontranspmargMEThwkstd', 'totnontranspmargMEThwkpabove0', 'totnontranspmargMEThwknon0mean']] = None
# finaldf[transportvarstotcompl] = None
# finalstratdfvars = ['agegroups_6', 'sex', 'migrationbackground', 'haschild', 'education_level', 'employed', 'incomequintile']
# for row in finaldf.index:
#     # print(finaldf.loc[row, finalstratdfvars].values)
#     meanMETh = []
#     meanMEThstd = []
#     transmeanMETh = [[],[],[],[]]
#     transmeanMEThstd = [[],[],[],[]]
#     for cleanstratdf in cleanstratdfs:
#         availablestrats = [col for col in cleanstratdf.columns.values if col in finalstratdfvars]
#         # finding the row in cleanstratdf that matches the row in finaldf
#         rowindex = cleanstratdf.index[cleanstratdf[availablestrats].eq(finaldf.loc[row, availablestrats]).all(axis=1)]
#         # print(cleanstratdf.loc[rowindex])
#         if len(rowindex)>0:
#             meanMETh.append(cleanstratdf.loc[rowindex, 'totnontranspmargMEThwkmean'].values[0])
#             meanMEThstd.append(cleanstratdf.loc[rowindex, 'totnontranspmargMEThwkstd'].values[0])
#             for count, var in enumerate(transportvars):
#                 transmeanMETh[count].append(cleanstratdf.loc[rowindex, var].values[0])
#                 transmeanMEThstd[count].append(cleanstratdf.loc[rowindex, var.replace("mean", "std")].values[0])
            
#     finaldf.loc[row, 'totnontranspmargMEThwkmean'] = np.mean(meanMETh)
#     finaldf.loc[row, 'totnontranspmargMEThwkstd'] = np.mean(meanMEThstd)
#     for count, var in enumerate(transportvars):
#         finaldf.loc[row, var] = np.mean(transmeanMETh[count])
#     for count, var in enumerate(transportvarsstd):
#         finaldf.loc[row,var] = np.mean(transmeanMEThstd[count])
#     pabove0= []
#     non0mean = []
#     transpabove0 = [[],[],[],[]]
#     transmeanMETh = [[],[],[],[]]
#     for df in non0distr:
#         availablestrats = [col for col in df.columns.values if col in finalstratdfvars]
#         rowindex = df.index[df[availablestrats].eq(finaldf.loc[row, availablestrats]).all(axis=1)]
#         if len(rowindex)>0:
#             pabove0.append(df.loc[rowindex, 'totnontranspmargMEThwkpabove0'].values[0])
#             # non0mean.append(df.loc[rowindex, 'totnontranspmargMEThwknon0mean'].values[0])
#             for count, var in enumerate(transportvars):
#                 transpabove0[count].append(df.loc[rowindex, var.replace("mean", "pabove0")].values[0])
#     finaldf.loc[row, 'totnontranspmargMEThwkpabove0'] = np.mean(pabove0)
#     # finaldf.loc[row, 'totnontranspmargMEThwknon0mean'] = np.mean(non0mean)
#     for count, var in enumerate(transportvars):
#         finaldf.loc[row, var.replace("mean", "pabove0")] = np.mean(transpabove0[count])

# finaldf['totnontranspmargMEThwknon0mean'] = finaldf['totnontranspmargMEThwkmean'] * (1/finaldf['totnontranspmargMEThwkpabove0'])
# for var in transportvars:
#     finaldf[var.replace("mean", "non0mean")] = finaldf[var] * (1/finaldf[var.replace("mean", "pabove0")])
# finaldf.to_csv(destinations+ f"/stratifiedMEThweek{year}.csv", index=False)


# finaldf = pd.read_csv(destinations+ f"/stratifiedMEThweek{year}.csv")
# # rename haschild  to havechild
# finaldf.rename(columns={"haschild": "havechild", "education_level": "absolved_education"}, inplace=True)
# finalstratdfvars = ['agegroups_6', 'sex', 'migrationbackground', 'havechild', 'absolved_education', 'employed', 'incomequintile']
# transportvars = ["margwwlmethwkmean", "margwwfmethwkmean", "margwanmethwkmean", "margfietmethwkmean"]

# # substitute "employed" with 1 and unemployed with 0 in employed column
# finaldf["employed"] = finaldf["employed"].apply(lambda x: 1 if x == "employed" else 0)
 
# print(finaldf.head())
# agents = pd.read_csv("D:\PhD EXPANSE\Data\Amsterdam\ABMRessources\ABMData\Population\Agent_pop_clean.csv")
# agents["agegroups_6"] = pd.cut(agents["age"], bins=[0, 18, 25, 40, 60, 110], labels=["aged0to18", "aged18to25", "aged25to40", "aged40to60", "aged60to100"], right = False)
# agents["incomequintile"] = pd.cut(agents["incomeclass_int"], bins=[0, 3, 5, 7, 9, 11], labels=["1stQuintile", "2stQuintile", "3stQuintile", "4stQuintile", "5stQuintile"], right = False)
# print(agents.columns.values)

# print(agents[finalstratdfvars+ ["incomeclass_int","age"]].head(20))

# agents["nontranspmargMEThwk"] = None
# agents[[var.replace("mean", "") for var in transportvars]] = None

# distrsize = 10000
# # for row in [0,1,2,3]:
# for row in finaldf.index:
#     print(finaldf.loc[row, finalstratdfvars].values)
#     rowindex = agents.index[agents[finalstratdfvars].eq(finaldf.loc[row, finalstratdfvars]).all(axis=1)]
#     nragents = len(rowindex)
#     print(nragents)
#     if nragents > 0:
#         meanMETh = finaldf.loc[row, 'totnontranspmargMEThwkmean']
#         stdMETh = finaldf.loc[row, 'totnontranspmargMEThwkstd']
#         pabove0 = finaldf.loc[row, 'totnontranspmargMEThwkpabove0']
#         non0mean = finaldf.loc[row, 'totnontranspmargMEThwknon0mean']
#         # nragents0 = int(nragents * (1-pabove0))
#         # nragentsnon0 = nragents - nragents0
#         # print("Nr agents 0: ", nragents0, "Nr agents non0: ", nragentsnon0)
#         # create exponential distribution based on mean and std
#         print("measured", meanMETh, stdMETh)

#         exp_data = list(expon.rvs(scale=non0mean, size=int(distrsize*pabove0)))
#         # print(exp_data)
#         vals0 = [0]* int(distrsize * (1-pabove0))
#         exp_data = exp_data + vals0
#         # shuffle
#         rdm.shuffle(exp_data)
#         # print(exp_data)
#         print("functional distribution", np.mean(exp_data), np.std(exp_data))
#         # plt.hist(exp_data, bins="auto")
#         # plt.show()

#         quantiles = np.linspace(0, 1, nragents + 1)  # Divide into n_representative bins
#         bin_edges = np.quantile(exp_data, quantiles)
#         # print("binedges", bin_edges)
#         representative_values = []
#         for i in range(len(bin_edges) - 1):
#             # Find values within this bin
#             bin_values = [val for val in exp_data if bin_edges[i] <= val <= bin_edges[i + 1]]
            
#             if len(bin_values) > 0:
#                 representative_value = rdm.choice(bin_values)
#                 representative_values.append(representative_value)
            
#         # print("finalquantileedges", representative_values)
#         print("assigned distribution", np.mean(representative_values), np.std(representative_values))
#         # plt.hist(representative_values, bins="auto")
#         # plt.show()
#         #shuffling the values
#         rdm.shuffle(representative_values)
#         if len(representative_values) == nragents:
#             agents.loc[rowindex,"nontranspmargMEThwk"] = representative_values
#         else:
#             print("Error: ", len(representative_values), nragents)
#             agents.loc[rowindex,"nontranspmargMEThwk"]  = rdm.sample(representative_values, nragents)
        
#         for var in transportvars:
#             meanMETh = finaldf.loc[row, var]
#             stdMETh = finaldf.loc[row, var.replace("mean", "std")]
#             pabove0 = finaldf.loc[row, var.replace("mean", "pabove0")]
#             non0mean = finaldf.loc[row, var.replace("mean", "non0mean")]
#             print("measured", meanMETh, stdMETh)

#             exp_data = list(expon.rvs(scale=non0mean, size=int(distrsize*pabove0)))
#             # print(exp_data)
#             vals0 = [0]* int(distrsize * (1-pabove0))
#             exp_data = exp_data + vals0
#             # shuffle
#             rdm.shuffle(exp_data)
#             # print(exp_data)
#             print("functional distribution", np.mean(exp_data), np.std(exp_data))
#             # plt.hist(exp_data, bins="auto")
#             # plt.show()

#             quantiles = np.linspace(0, 1, nragents + 1)  # Divide into n_representative bins
#             bin_edges = np.quantile(exp_data, quantiles)
#             # print("binedges", bin_edges)
#             representative_values = []
#             for i in range(len(bin_edges) - 1):
#                 # Find values within this bin
#                 bin_values = [val for val in exp_data if bin_edges[i] <= val <= bin_edges[i + 1]]
                
#                 if len(bin_values) > 0:
#                     representative_value = rdm.choice(bin_values)
#                     representative_values.append(representative_value)
                
#             # print("finalquantileedges", representative_values)
#             print("assigned distribution", np.mean(representative_values), np.std(representative_values))
#             rdm.shuffle(representative_values)
#             if len(representative_values) == nragents:
#                 agents.loc[rowindex,var.replace("mean", "")] = representative_values
#             else:
#                 print("Error: ", len(representative_values), nragents)
#                 agents.loc[rowindex,var.replace("mean", "")]  = rdm.sample(representative_values, nragents)
        
# print(agents["nontranspmargMEThwk"].head(20))

# agents.to_csv(destinations+ f"/Amsterdam_agents_nontranspmargMEThweek{year}.csv", index=False)

agents = pd.read_csv(destinations+ f"/Amsterdam_agents_nontranspmargMEThweek{year}.csv")

plt.hist(agents["nontranspmargMEThwk"], bins="auto",)    
plt.show()
transportvars = ["margwwlmethwkmean", "margwwfmethwkmean", "margwanmethwkmean", "margfietmethwkmean"]

agents["totaltransportMEThwkmean"] = agents[[var.replace("mean","") for var in  transportvars]].sum(axis=1)
for var in transportvars:
    plt.hist(agents[var.replace("mean", "")], bins="auto",)
    plt.show()
    
plt.hist(agents["totaltransportMEThwkmean"], bins="auto",)    
plt.show()

agents.to_csv(destinations+ f"/Amsterdam_agents_nontranspmargMEThweek{year}.csv", index=False)

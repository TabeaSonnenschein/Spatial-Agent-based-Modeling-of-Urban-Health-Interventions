import numpy as np
import pandas as pd
import os

def calculateMortality(exposure, baseline_death, populationtodeathstandardization, RR, increment):
    # We start by calculating the exposure increment by dividing the exposure by 10 to normalise the RR scale. 
    exposureincrement = exposure/increment

    # We then take the exposure increment’s exponent of the RR score to calculate the specific RR of our exposure
    localRisk = RR**exposureincrement

    # then we multiply it by the baseline death and population sample to retrieve the mortality risk
    mortalityRisk_absolut = localRisk*baseline_death * populationtodeathstandardization
    mortalityRisk_standardized = localRisk*baseline_death

    return mortalityRisk_absolut, mortalityRisk_standardized

nb_agents = 21750  #87000 = 10%, 43500 = 5%, 21750 = 2.5%, 8700 = 1%
scenario = "StatusQuo"
path_data = "D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/ModelRuns"

os.chdir(path_data+f"/{scenario}/{nb_agents}Agents/AgentExposure/MeanExposureViz")
aggexposure = pd.read_csv(f"Exposure_A{nb_agents}_Mean_{scenario}_aggregate.csv")

population = 870000
baselinedeath = 800 # per 100000
populationtodeathstandardization = population/100000

RR = 1.02  # per 10 g/m3. 
increment = 10


subgroups_Meta = {"income": ["Low", "Medium", "High"],
            "sex": ["male", "female"], 
            "migration_background": ["Dutch", "Western", "Non-Western"],
            "age_group": ["Aged 0-29", "Aged 30-59", "Aged 60+"],
            "HH_size": ["HH size 1", "HH size 2", "HH size 3", "HH size 4", "HH size 5", "HH size 6", "HH size 7"],
            "absolved_education": ["low", "middle", "high"],
            "HH_type": ["Single Person", "Pair without children", "Pair with children", "Single Parent with children", "Other multiperson household"],
            "student": ["Student", "Not Student"],
            "location": ["inside ring", "outside ring"]
            }


subgroups = [subgroups_Meta[key] for key in subgroups_Meta.keys()]
# unlist the nested list
subgroups = [item for sublist in subgroups for item in sublist]

NO2exposure = aggexposure.loc[aggexposure["timeunit"] == "total", "NO2"].values[0]

mortalityRisk_absolut, mortalityRisk_standardized = calculateMortality(exposure = NO2exposure, baseline_death = baselinedeath, 
                                                                       populationtodeathstandardization = populationtodeathstandardization,
                                                                       RR = RR, increment = increment)

mortality_abs, mortality_std = [], []
mortality_abs.append(mortalityRisk_absolut)
mortality_std.append(mortalityRisk_standardized)


for subgroup in subgroups:
    subgroup_exposure = aggexposure.loc[aggexposure["timeunit"] == "total", f"NO2_{subgroup}"].values[0]
    mortalityRisk_absolut, mortalityRisk_standardized = calculateMortality(exposure = subgroup_exposure, baseline_death = baselinedeath, 
                                                                       populationtodeathstandardization = populationtodeathstandardization,
                                                                       RR = RR, increment = increment)

    # mortality_abs.append(mortalityRisk_absolut)
    mortality_std.append(mortalityRisk_standardized)
    
pd.DataFrame({"Subgroup": ["Total"]+subgroups, "Mortality": mortality_std}).to_csv(f"D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/NO2_Mortality_{nb_agents}Agents_{scenario}.csv", index = False)




# lifetable analysis
# stopping by 80


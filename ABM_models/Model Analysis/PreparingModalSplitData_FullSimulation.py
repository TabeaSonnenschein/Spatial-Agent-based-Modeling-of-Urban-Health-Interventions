import matplotlib.pyplot as plt
import pandas as pd
import os
import seaborn as sns
import ast
import datetime
####################################################

nb_agents = 21750  #87000 = 10%, 43500 = 5%, 21750 = 2.5%, 8700 = 1%
path_data = "D:\PhD EXPANSE\Data\Amsterdam\ABMRessources\ABMData\ModelRuns"

# scenario = "SpeedInterv"
scenario = "StatusQuo"
# scenario = "PedStrWidth"
# scenario = "RetaiDnsDiv"
# scenario = "LenBikRout"
# scenario = "PedStrWidthOutskirt"
# scenario = "PedStrWidthCenter"
# scenario = "AmenityDnsExistingAmenityPlaces"
# scenario = "AmenityDnsDivExistingAmenityPlaces"
# scenario = "PedStrLen"
# scenario = "PedStrWidthOutskirt"
# scenario = "PedStrWidthCenter"
# scenario = "PedStrLenCenter"
# scenario = "PedStrLenOutskirt"
# scenario = "PrkPriceInterv"

# identify model run for scenario
experimentoverview = pd.read_csv("D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/ExperimentOverview.csv")
modelruns = experimentoverview.loc[experimentoverview["Experiment"] == scenario, "Model Run"].values


os.chdir(os.path.join(path_data,scenario, f"{nb_agents}Agents/ModalSplit"))

for modelrun in modelruns:
    # read the txt file, which consists of a list of dictionaries and transform to a dataframe
    with open(f"ModalSplitLog{nb_agents}_{scenario}_{modelrun}.txt") as f:
        content = f.readlines()
    content = [x.strip() for x in content]
    content = [x.split(", ") for x in content]
    content = content[2:]

    hours = [x[0] for x in content]
    dict = [", ".join(x[1:]).replace("Counter(", "").replace(")", "") for x in content]
    dict = [ast.literal_eval(x) if x != "" else ast.literal_eval("{'bike': 0, 'walk': 0, 'transit': 0, 'drive': 0}") for x in dict ]

    # transform the list of dictionaries to a dataframe
    modalsplit_df = pd.DataFrame.from_dict(dict)
    modalsplit_df["hour"] = hours
    modalsplit_df["date"] = modalsplit_df["hour"].str.split(" ").str[0]
    modalsplit_df["hour"] = modalsplit_df["hour"].str.split(" ").str[1]
    modalsplit_df["hour"] = modalsplit_df["hour"].str.split(":").str[0]
    modalsplit_df["month"] = modalsplit_df["date"].str.split("-").str[1]
    modalsplit_df["day"] = modalsplit_df["date"].str.split("-").str[2]
    try:
        modalsplit_df['date'] = pd.to_datetime(modalsplit_df['date'], format='%Y-%m-%d', errors='coerce')
    except Exception as e:
        print("Error converting dates:", e)
    modalsplit_df["weekday"] = modalsplit_df['date'].dt.day_name()




    print(modalsplit_df.head())

    modalsplit_df.to_csv(f"ModalSplitLog{nb_agents}_{scenario}_{modelrun}.csv", index=False)

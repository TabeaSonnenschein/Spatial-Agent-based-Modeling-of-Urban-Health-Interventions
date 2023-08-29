import matplotlib.pyplot as plt
import pandas as pd
import os
import seaborn as sns
import ast
####################################################

nb_agents = 43500
path_data = "C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/"

# modelrun = "SpeedInterv"
# modelrun = "StatusQuo"
# modelrun = "PedStrWidth"
# modelrun = "RetaiDnsDiv"
modelrun = "LenBikRout"

os.chdir(path_data)

# read the txt file, which consists of a list of dictionaries and transform to a dataframe
with open(f"ModalSplitLog{nb_agents}_{modelrun}.txt") as f:
    content = f.readlines()
content = [x.strip() for x in content]
content = [x.split(", ") for x in content]
content = content[2:]

hours = [x[0] for x in content]
dict = [", ".join(x[1:]).replace("Counter(", "").replace(")", "") for x in content]
print(dict)
dict = [ast.literal_eval(x) for x in dict]

# transform the list of dictionaries to a dataframe
modalsplit_df = pd.DataFrame.from_dict(dict)
modalsplit_df["hour"] = hours
modalsplit_df["hour"] = modalsplit_df["hour"].str.split(" ").str[1]

print(modalsplit_df.head())

modalsplit_df.to_csv(f"ModalSplitLog{nb_agents}_{modelrun}.csv", index=False)
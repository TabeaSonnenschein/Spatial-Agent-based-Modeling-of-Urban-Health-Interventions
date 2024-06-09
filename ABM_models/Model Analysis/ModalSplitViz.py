import matplotlib.pyplot as plt
import pandas as pd
import os
import seaborn as sns
import ast
####################################################

nb_agents = 21750  #87000 = 10%, 43500 = 5%, 21750 = 2.5%, 8700 = 1%
path_data = "D:\PhD EXPANSE\Data\Amsterdam\ABMRessources\ABMData\ModelRuns"

# modelrun = "SpeedInterv"
# modelrun = "StatusQuo"
# modelrun = "PedStrWidth"
# modelrun = "RetaiDnsDiv"
# modelrun = "LenBikRout"
# modelrun = "PedStrWidthOutskirt"
# modelrun = "PedStrWidthCenter"
# modelrun = "AmenityDnsExistingAmenityPlaces"
# modelrun  = "AmenityDnsDivExistingAmenityPlaces"
# modelrun = "StatusQuoAllVars"
# modelrun = "PedStrLen"
# modelrun ="PedStrWidthOutskirt"
# modelrun ="PedStrWidthCenter"
# modelrun = "PedStrLenCenter"
# modelrun = "PedStrLenOutskirt"
modelrun = "PrkPriceInterv"

os.chdir(path_data)
modalsplit_df =  pd.read_csv(f"{modelrun}/ModalSplitLog{nb_agents}_{modelrun}.csv")
statQuo_df = pd.read_csv(f"StatusQuo/ModalSplitLog{nb_agents}_StatusQuo.csv")

melted_interv = pd.melt(modalsplit_df, id_vars='hour', var_name='mode_of_transport', value_name='counts')
melted_statquo = pd.melt(statQuo_df, id_vars='hour', var_name='mode_of_transport', value_name='counts')

melted_interv = melted_interv.sort_values(by='mode_of_transport')
melted_statquo = melted_statquo.sort_values(by='mode_of_transport')

melted_interv["hour"] = [int(x[0:2]) for x in  melted_interv["hour"]]
melted_interv["counts"] = [float(x) for x in  melted_interv["counts"]]

melted_statquo["hour"] = [int(x[0:2]) for x in  melted_statquo["hour"]]
melted_statquo["counts"] = [float(x) for x in  melted_statquo["counts"]]

# combined_melted = pd.concat([melted_scenario1, melted_scenario2], keys=['Scenario 1', 'Scenario 2'])
# combined_melted["hour"] = [int(x[0:2]) for x in  combined_melted["hour"]]
# combined_melted["counts"] = [float(x) for x in  combined_melted["counts"]]

# Set up Seaborn style
sns.set(style="whitegrid")

# Create the line plot
plt.figure(figsize=(10, 6))

# Line plot for status quo with dotted lines
sns.lineplot(x='hour', y='counts', hue='mode_of_transport', style='mode_of_transport', dashes=[(2, 2), (2, 2), (2,2), (2,2)], data=melted_statquo, alpha=0.5, legend=False)


# Line plot for intervention with continuous lines
sns.lineplot(x='hour', y='counts', hue='mode_of_transport', style='mode_of_transport', data=melted_interv, dashes=False, markers=False)

plt.plot([], [], ' ', label="dashed lines = status quo")


# Adjust layout and display the plot
# Customize plot
plt.xlabel("Hour")
plt.ylabel("Count")
plt.title(f"Mode of Transport split of the {modelrun} scenario over time")
plt.legend(title="Mode of Transport")
plt.savefig(f"ModalSplitLog{nb_agents}_{modelrun}.png", dpi=600)
plt.show()








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
modelrun = "PedStrWidth"
# modelrun = "RetaiDnsDiv"

os.chdir(path_data)
modalsplit_df =  pd.read_csv(f"ModalSplitLog{nb_agents}_{modelrun}.csv")
statQuo_df = pd.read_csv(f"ModalSplitLog{nb_agents}_StatusQuo.csv")

melted_interv = pd.melt(modalsplit_df, id_vars='hour', var_name='mode_of_transport', value_name='counts')
melted_statquo = pd.melt(statQuo_df, id_vars='hour', var_name='mode_of_transport', value_name='counts')

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
sns.lineplot(x='hour', y='counts', hue='mode_of_transport', style='mode_of_transport', dashes=True, markers=True, data=melted_statquo)
# Line plot for intervention with continuous lines
sns.lineplot(x='hour', y='counts', hue='mode_of_transport', style='mode_of_transport', data=melted_interv)
# Adjust layout and display the plot
# Customize plot
plt.xlabel("Hour")
plt.ylabel("Count")
plt.title("Modal Split Comparison Over Time")
plt.legend(title="Mode of Transport")

plt.show()








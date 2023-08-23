import matplotlib.pyplot as plt
import pandas as pd
import os
import seaborn as sns
####################################################
nb_agents = 43500
path_data = "C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/"

# read agent_df
agent_df = pd.read_csv(path_data+"Population/Amsterdam_population_subset.csv")

# read exposure data
listOfFiles = os.listdir(path=path_data + 'ModelRuns/AgentExposure/')
print(listOfFiles)

# read the exposure data for each hour and merge them into one
for hour in range(24):
    exposure_df = pd.read_csv(path_data + f"ModelRuns/AgentExposure/AgentExposure_A{nb_agents}_M1_H{hour}.csv")
    exposure_df = exposure_df.rename(columns={"NO2": f"NO2_{hour}", "MET": f"MET_{hour}"})
    if hour == 0:
        exposure_df_all = exposure_df
    else:
        exposure_df_all = pd.merge(exposure_df, exposure_df_all, on="agent", how="left")

# merge exposure data with agent_df
agent_df = pd.merge(agent_df, exposure_df_all, left="agent_ID", right="agent", how="left")

# plot of exposure distribution per hour per different sociodemographic groups

# sex
sexdf = agent_df.groupby(['sex'], as_index=False).mean()

# violin plot of NO2 per hour per sex
fig, ax = plt.subplots()
sns.violinplot(data = sexdf, x=time, y = NO2, hue = sex, split= True)

# seethrough scatterplot with line of mean and colors by category (income)

# line timetrend with multiple lines

# age

# income

# education

# migrationbackground

# per district
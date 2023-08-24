import matplotlib.pyplot as plt
import pandas as pd
import os
import seaborn as sns
####################################################
nb_agents = 43500
# path_data = "C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/"
path_data ="/Users/tsonnens/Documents/Exposure Results"
# os.chdir(path_data + 'ModelRuns/AgentExposure/')
os.chdir(path_data)

print("Reading the data")
# read exposure data
exposure_df = pd.read_csv(f"AgentExposure_A{nb_agents}_M1_hourAsRowsMerged.csv")
print(exposure_df.head())
print(exposure_df.info())
print(exposure_df.describe())
for column in exposure_df.select_dtypes(include=['object']):
    print("\nValue counts for", column)
    print(exposure_df[column].value_counts())

# plot of exposure distribution per hour per different sociodemographic groups
# # sex
sexdf = exposure_df[["sex", "hour", "NO2", "MET"]].groupby(["sex", "hour"], as_index=False).mean()
print(sexdf.head())    

# plot the distribution of NO2 per sex per hour


# # violin plot of NO2 per hour per sex
# sns.violinplot(data = sexdf, x=time, y = NO2, hue = sex, split= True)

# seethrough scatterplot with line of mean and colors by category (income)

# line timetrend with multiple lines

# age

# income

# education

# migrationbackground

# per district

print("Plotting the data")
# Set up Seaborn style
sns.set(style="whitegrid")

# Create a scatter plot
plt.figure(figsize=(10, 6))
sns.scatterplot(x="hour", y="NO2", hue="sex", data=exposure_df, alpha=0.4)

# Customize plot
plt.xlabel("Hour")
plt.ylabel("NO2")
plt.title("Scatter Plot of NO2 Over Time by Sex")
plt.legend(title="Sex")

plt.savefig('scatterplot_NO2exposure_by_sex.pdf', dpi = 300)


# Display the plot
plt.show()




# Create your DataFrame 'exposure_df'

# Set up Seaborn style
sns.set(style="whitegrid")

# Define a colormap that transitions from green to red (you can adjust the colormap)
color_map = sns.color_palette("RdYlGn_r", as_cmap=True)

# Create the scatter plot with continuous color spectrum
plt.figure(figsize=(10, 6))
sns.scatterplot(x="hour", y="NO2", hue="incomeclass_int", data=exposure_df, alpha=0.4, palette=color_map)

# Customize plot
plt.xlabel("Hour")
plt.ylabel("NO2")
plt.title("Scatter Plot of NO2 Over Time by Income")
plt.legend(title="Income")


plt.savefig('scatterplot_NO2exposure_by_income.pdf', dpi = 300)


# Display the plot
plt.show()







# # Set up Seaborn style
# sns.set(style="whitegrid")

# # Create a boxplot to show the distribution of exposure per hour by age group
# plt.figure(figsize=(10, 6))
# sns.boxplot(x="sex", y="exposure_per_hour", data=agent_df)
# plt.xlabel("Sex")
# plt.ylabel("Exposure per Hour")
# plt.title("Exposure per Hour by Sex")
# plt.xticks(rotation=45)
# plt.tight_layout()

# # Save the plot as an image
# plt.savefig('exposure_by_age.png')

# # Display the plot
# plt.show()


# # Create a facet grid of scatter plots for exposure by age and gender
# g = sns.FacetGrid(agent_df, col="gender", margin_titles=True)
# g.map(plt.scatter, "age", "exposure_per_hour", alpha=0.5)
# g.set_axis_labels("Age", "Exposure per Hour")
# g.set_titles(col_template="{col_name}")
# plt.tight_layout()

# # Save the facet grid plot
# plt.savefig('exposure_by_age_gender.png')

# # Display the plot
# plt.show()
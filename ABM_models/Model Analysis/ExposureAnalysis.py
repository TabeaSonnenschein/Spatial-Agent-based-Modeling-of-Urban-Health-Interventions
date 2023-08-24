import matplotlib.pyplot as plt
import pandas as pd
import os
import seaborn as sns
####################################################


def ScatterOverTimeColCategory(outcomvar, colcategory, showplots):
    sns.set(style="whitegrid")
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x="hour", y=outcomvar, hue=colcategory, data=exposure_df, alpha=0.4)
    plt.xlabel("Hour")
    plt.ylabel(outcomvar)
    plt.title(f"Distribution of {outcomvar} Over Time by {colcategory}")
    plt.legend(title="Sex")
    plt.savefig(f'scatterplot_{outcomvar}_by_{colcategory}.pdf', dpi = 300)
    if showplots:
        plt.show()
    plt.close()

def ScatterOverTimeColContinous(outcomvar, colvar, showplots):
    sns.set(style="whitegrid")
    color_map = sns.color_palette("RdYlGn_r", as_cmap=True)
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x="hour", y=outcomvar, hue=colvar, data=exposure_df, alpha=0.4, palette=color_map)
    plt.xlabel("Hour")
    plt.ylabel(outcomvar)
    plt.title(f"Distribution of {outcomvar} Over Time by {colvar}")
    plt.legend(title="Sex")
    plt.savefig(f'scatterplot_{outcomvar}_by_{colvar}.pdf', dpi = 300)
    if showplots:
        plt.show()
    plt.close()










######################################################
nb_agents = 43500
# path_data = "C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/"
path_data ="/Users/tsonnens/Documents/Exposure Results"
# os.chdir(path_data + 'ModelRuns/AgentExposure/')
os.chdir(path_data)

modelrun = "StatusQuo"

print("Reading the data")
# read exposure data
exposure_df = pd.read_csv(f"AgentExposure_A{nb_agents}_M1_hourAsRowsMerged.csv")

print("Analyzing the data")
print(exposure_df.head())
print(exposure_df.info())
print(exposure_df.describe())
for column in exposure_df.select_dtypes(include=['object']):
    print("\nValue counts for", column)
    print(exposure_df[column].value_counts())


# Renaming some columns for elegance
exposure_df = exposure_df.rename(columns={"incomeclass_int": "income"})

print("Plotting the data")
figuresToPlot = ["sex_scatterNO2","sex_scatterMET", "income_scatterNO2", "income_scatterMET"]
showplots = False

if "sex_scatterNO2" in figuresToPlot:
    ScatterOverTimeColCategory(outcomvar="NO2", colcategory="sex", showplots=showplots)

if "sex_scatterMET" in figuresToPlot:
    ScatterOverTimeColCategory(outcomvar="MET", colcategory="sex", showplots=showplots)

if "income_scatterNO2" in figuresToPlot:
    ScatterOverTimeColContinous(outcomvar="NO2", colvar="income", showplots=showplots)

if "income_scatterMET" in figuresToPlot:
    ScatterOverTimeColContinous(outcomvar="MET", colvar="income", showplots=showplots)



# plot of exposure distribution per hour per different sociodemographic groups
# # sex
sexdf = exposure_df[["sex", "hour", "NO2", "MET"]].groupby(["sex", "hour"], as_index=False).mean()
print(sexdf.head())    

# plot the distribution of NO2 per sex per hour


# # violin plot of NO2 per hour per sex
# sns.violinplot(data = sexdf, x=time, y = NO2, hue = sex, split= True)

# seethrough scatterplot with line of mean and colors by category (income)

# line timetrend with multiple lines


# radarchart with mean exposure per hour per category (income)

# age

# income

# education

# migrationbackground

# per district




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
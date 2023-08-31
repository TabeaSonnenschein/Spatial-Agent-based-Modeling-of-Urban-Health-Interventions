import matplotlib.pyplot as plt
import pandas as pd
import os
import seaborn as sns
####################################################


def ScatterOverTimeColCategory(outcomvar, colcategory, showplots, modelrun, ylabel = None, collabel = None):
    if ylabel is None:
        ylabel = outcomvar
    if collabel is None:
        collabel = colcategory
    sns.set(style="whitegrid")
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x="hour", y=outcomvar, hue=colcategory, data=exposure_df, alpha=0.4)
    plt.xlabel("Hour")
    plt.ylabel(ylabel)
    plt.title(f"Distribution of {outcomvar} Over Time by {collabel}")
    plt.legend(title=collabel)
    plt.savefig(f'{modelrun}_scatterplot_{outcomvar}_by_{colcategory}.pdf', dpi = 300)
    if showplots:
        plt.show()
    plt.close()
    

def ScatterOverTimeColContinous(outcomvar, colvar, showplots, modelrun, ylabel = None, collabel = None):
    if ylabel is None:
        ylabel = outcomvar
    if collabel is None:
        collabel = colvar
    sns.set(style="whitegrid")
    color_map = sns.color_palette("RdYlGn_r", as_cmap=True)
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x="hour", y=outcomvar, hue=colvar, data=exposure_df, alpha=0.4, palette=color_map)
    plt.xlabel("Hour")
    plt.ylabel(ylabel)
    plt.title(f"Distribution of {outcomvar} Over Time by {collabel}")
    plt.legend(title=collabel)
    plt.savefig(f'{modelrun}_scatterplot_{outcomvar}_by_{colvar}.pdf', dpi = 300)
    if showplots:
        plt.show()
    plt.close()
    

def LineOverTimeColCategory(outcomvar, colcategory, showplots, modelrun, ylabel = None, collabel = None):
    if ylabel is None:
        ylabel = outcomvar
    if collabel is None:
        collabel = colcategory
    sns.set(style="whitegrid")
    plt.figure(figsize=(10, 6))
    sns.lineplot(x="hour", y=outcomvar, hue=colcategory, data=exposure_df, alpha=0.4)
    plt.xlabel("Hour")
    plt.ylabel(ylabel)
    plt.title(f"Distribution of {outcomvar} Over Time by {collabel}")
    plt.legend(title=collabel)
    plt.savefig(f'{modelrun}_lineplot_{outcomvar}_by_{colcategory}.pdf', dpi = 300)
    if showplots:
        plt.show()
    plt.close()
    

def LineOverTimeColContinous(outcomvar, colvar, showplots, modelrun, ylabel = None, collabel = None):
    if ylabel is None:
        ylabel = outcomvar
    if collabel is None:
        collabel = colvar
    sns.set(style="whitegrid")
    color_map = sns.color_palette("RdYlGn_r", as_cmap=True)
    plt.figure(figsize=(10, 6))
    sns.lineplot(x="hour", y=outcomvar, hue=colvar, data=exposure_df, alpha=0.4, palette=color_map)
    plt.xlabel("Hour")
    plt.ylabel(ylabel)
    plt.title(f"Distribution of {outcomvar} Over Time by {collabel}")
    plt.legend(title=collabel)
    plt.savefig(f'{modelrun}_lineplot_{outcomvar}_by_{colvar}.pdf', dpi = 300)
    if showplots:
        plt.show()
    plt.close()
    

def ViolinOverTimeColCategory(outcomvar, colcategory, showplots, modelrun, ylabel = None, collabel = None):
    if ylabel is None:
        ylabel = outcomvar
    if collabel is None:
        collabel = colcategory
    sns.set(style="whitegrid")
    plt.figure(figsize=(10, 6))
    sns.violinplot(x="hour", y=outcomvar, hue=colcategory, data=exposure_df)
    plt.xlabel("Hour")
    plt.ylabel(ylabel)
    plt.title(f"Distribution of {outcomvar} Over Time by {collabel}")
    plt.legend(title=collabel)
    plt.savefig(f'{modelrun}_violinplot_{outcomvar}_by_{colcategory}.pdf', dpi = 300)
    if showplots:
        plt.show()
    plt.close()

def ViolinOverTimeColContinous(outcomvar, colcategory, showplots, modelrun, ylabel = None, collabel = None):
    if ylabel is None:
        ylabel = outcomvar
    if collabel is None:
        collabel = colcategory
    sns.set(style="whitegrid")
    color_map = sns.color_palette("RdYlGn_r", as_cmap=True)
    plt.figure(figsize=(10, 6))
    sns.violinplot(x="hour", y=outcomvar, hue=colcategory, data=exposure_df, palette=color_map)
    plt.xlabel("Hour")
    plt.ylabel(ylabel)
    plt.title(f"Distribution of {outcomvar} Over Time by {collabel}")
    plt.legend(title=collabel)
    plt.savefig(f'{modelrun}_violinplot_{outcomvar}_by_{colcategory}.pdf', dpi = 300)
    if showplots:
        plt.show()
    plt.close()

def PlotVarsInLists(plottypes, outcomevars, continuousstratvars, categoricalstratvars, showplots, modelrun, fullnamedict):
    for plottype in plottypes:
        for outvar in outcomevars:
            if plottype == "scatter":
                for stratvar in continuousstratvars:
                    ScatterOverTimeColContinous(outcomvar=outvar, colvar=stratvar, showplots=showplots, modelrun=modelrun, ylabel=fullnamedict[outvar], collabel=fullnamedict[stratvar])
                for stratvar in categoricalstratvars:
                    ScatterOverTimeColCategory(outcomvar=outvar, colcategory=stratvar, showplots=showplots, modelrun=modelrun, ylabel=fullnamedict[outvar], collabel=fullnamedict[stratvar])
            elif plottype == "line":
                for stratvar in continuousstratvars:
                    LineOverTimeColContinous(outcomvar=outvar, colvar=stratvar, showplots=showplots, modelrun=modelrun, ylabel=fullnamedict[outvar], collabel=fullnamedict[stratvar])
                for stratvar in categoricalstratvars:
                    LineOverTimeColCategory(outcomvar=outvar, colcategory=stratvar, showplots=showplots, modelrun=modelrun, ylabel=fullnamedict[outvar], collabel=fullnamedict[stratvar])
            elif plottype == "violin":
                for stratvar in continuousstratvars:
                    ViolinOverTimeColContinous(outcomvar=outvar, colvar=stratvar, showplots=showplots, modelrun=modelrun, ylabel=fullnamedict[outvar], collabel=fullnamedict[stratvar])
                for stratvar in categoricalstratvars:
                    ViolinOverTimeColCategory(outcomvar=outvar, colcategory=stratvar, showplots=showplots, modelrun=modelrun, ylabel=fullnamedict[outvar], collabel=fullnamedict[stratvar])
    
######################################################
nb_agents = 43500
path_data = "C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/"

modelrun = "StatusQuo"
# modelrun = "SpeedInterv"
# modelrun = "PedStrWidth"
# modelrun = "RetaiDnsDiv"
# modelrun = "LenBikRout"


os.chdir(path_data + 'ModelRuns/AgentExposure/' + modelrun)

print("Reading the data")
# read exposure data
exposure_df = pd.read_csv(f"AgentExposure_A{nb_agents}_M1_{modelrun}_hourAsRowsMerged.csv")

print("Analyzing the data")
print(exposure_df.head())
print(exposure_df.info())
print(exposure_df.describe())
for column in exposure_df.select_dtypes(include=['object']):
    print("\nValue counts for", column)
    print(exposure_df[column].value_counts())


# Renaming some columns for elegance
exposure_df = exposure_df.rename(columns={"incomeclass_int": "income", "migrationbackground": "migr_bck"})

print("Plotting the data")
# scatterplots =  ["sex_scatterNO2","sex_scatterMET", "income_scatterNO2", "income_scatterMET", "migr_bck_scatterNO2", "migr_bcksex_scatterMET"]
# lineplots = ["sex_lineNO2", "sex_lineMET", "income_lineNO2", "income_lineMET", "migr_bck_lineNO2", "migr_bcksex_lineMET"]
# figuresToPlot = lineplots
                 
continuousstratvars = ["income"]
categoricalstratvars = ["sex", "migr_bck"]
plottypes = [ "line", "violin"] # "scatter"
outcomevars = ["NO2", "MET"]

fullnamedict = {
    "income": "Income Percentile",
    "sex": "sex",
    "migr_bck": "Migration Background",
    "NO2": "NO2 (µg/m3)",
    "MET": "Metabolic Equivalent of Task (MET)",
    "NO2_diff": "NO2 Difference (µg/m3)",
    "MET_diff": "Metabolic Equivalent of Task (MET) Difference" }

                
# figuresToPlot = []
showplots = False

PlotVarsInLists(plottypes, outcomevars, continuousstratvars, categoricalstratvars, showplots, modelrun, fullnamedict)

# for plottype in plottypes:
#     for outvar in outcomevars:
#         if plottype == "scatter":
#             for stratvar in continuousstratvars:
#                 ScatterOverTimeColContinous(outcomvar=outvar, colvar=stratvar, showplots=showplots, modelrun=modelrun, ylabel=fullnamedict[outvar], collabel=fullnamedict[stratvar])
#             for stratvar in categoricalstratvars:
#                 ScatterOverTimeColCategory(outcomvar=outvar, colcategory=stratvar, showplots=showplots, modelrun=modelrun, ylabel=fullnamedict[outvar], collabel=fullnamedict[stratvar])
#         elif plottype == "line":
#             for stratvar in continuousstratvars:
#                 LineOverTimeColContinous(outcomvar=outvar, colvar=stratvar, showplots=showplots, modelrun=modelrun, ylabel=fullnamedict[outvar], collabel=fullnamedict[stratvar])
#             for stratvar in categoricalstratvars:
#                 LineOverTimeColCategory(outcomvar=outvar, colcategory=stratvar, showplots=showplots, modelrun=modelrun, ylabel=fullnamedict[outvar], collabel=fullnamedict[stratvar])
#         elif plottype == "violin":
#             for stratvar in continuousstratvars:
#                 ViolinOverTimeColContinous(outcomvar=outvar, colvar=stratvar, showplots=showplots, modelrun=modelrun, ylabel=fullnamedict[outvar], collabel=fullnamedict[stratvar])
#             for stratvar in categoricalstratvars:
#                 ViolinOverTimeColCategory(outcomvar=outvar, colcategory=stratvar, showplots=showplots, modelrun=modelrun, ylabel=fullnamedict[outvar], collabel=fullnamedict[stratvar])

# print("Plotting Scatterplots")

# if "sex_scatterNO2" in figuresToPlot:
#     ScatterOverTimeColCategory(outcomvar="NO2", colcategory="sex", showplots=showplots, modelrun=modelrun, ylabel="NO2 (µg/m3)")

# if "sex_scatterMET" in figuresToPlot:
#     ScatterOverTimeColCategory(outcomvar="MET", colcategory="sex", showplots=showplots, modelrun=modelrun, ylabel="Metabolic Equivalent of Task (MET)")

# if "income_scatterNO2" in figuresToPlot:
#     ScatterOverTimeColContinous(outcomvar="NO2", colvar="income", showplots=showplots, modelrun=modelrun, collabel="Income Percentile", ylabel="NO2 (µg/m3)")

# if "income_scatterMET" in figuresToPlot:
#     ScatterOverTimeColContinous(outcomvar="MET", colvar="income", showplots=showplots, modelrun=modelrun, collabel="Income Percentile", ylabel="Metabolic Equivalent of Task (MET)")

# if "migr_bck_scatterNO2" in figuresToPlot:
#     ScatterOverTimeColCategory(outcomvar="NO2", colcategory="migr_bck", showplots=showplots, modelrun=modelrun, ylabel="NO2 (µg/m3)", collabel="Migration Background")

# if "migr_bcksex_scatterMET" in figuresToPlot:
#     ScatterOverTimeColCategory(outcomvar="MET", colcategory="migr_bck", showplots=showplots, modelrun=modelrun, ylabel="Metabolic Equivalent of Task (MET)", collabel="Migration Background")

# print("Plotting Lineplots")
    
# if "sex_lineNO2" in figuresToPlot:
#     LineOverTimeColCategory(outcomvar="NO2", colcategory="sex", showplots=showplots, modelrun=modelrun, ylabel="NO2 (µg/m3)")

# if "sex_lineMET" in figuresToPlot:
#     LineOverTimeColCategory(outcomvar="MET", colcategory="sex", showplots=showplots, modelrun=modelrun, ylabel="NO2 (µg/m3)")
    
# if "income_lineNO2" in figuresToPlot:
#     LineOverTimeColContinous(outcomvar="NO2", colvar="income", showplots=showplots, modelrun=modelrun, collabel="Income Percentile", ylabel="NO2 (µg/m3)")

# if "income_lineMET" in figuresToPlot:
#     LineOverTimeColContinous(outcomvar="MET", colvar="income", showplots=showplots, modelrun=modelrun, collabel="Income Percentile", ylabel="Metabolic Equivalent of Task (MET)")

# if "migr_bck_lineNO2" in figuresToPlot:
#     LineOverTimeColCategory(outcomvar="NO2", colcategory="migr_bck", showplots=showplots, modelrun=modelrun, ylabel="NO2 (µg/m3)", collabel="Migration Background")

# if "migr_bcksex_lineMET" in figuresToPlot:
#     LineOverTimeColCategory(outcomvar="MET", colcategory="migr_bck", showplots=showplots, modelrun=modelrun, ylabel="Metabolic Equivalent of Task (MET)", collabel="Migration Background")




#########################
### Comparative Plots ###
#########################
modelrun_stat = "StatusQuo"

print("Reading the data")
# read exposure data
exposure_df_statusq = pd.read_csv(path_data + 'ModelRuns/AgentExposure/' + modelrun_stat + f"/AgentExposure_A{nb_agents}_M1_{modelrun_stat}_hourAsRowsMerged.csv")

exposure_comp = pd.merge(exposure_df, exposure_df_statusq, on=["agent_ID", "hour"], how="left", suffixes=("_interv", "_statusq"))
    
# Set up Seaborn style
sns.set(style="whitegrid")

# Create the line plot for NO2 before intervention
plt.figure(figsize=(10, 6))
sns.lineplot(x="hour", y="NO2_statusq", data=exposure_comp, label="Before Intervention")

# Add the line plot for NO2 after intervention
sns.lineplot(x="hour", y="NO2_interv", data=exposure_comp, label="After Intervention")

# Customize plot
plt.xlabel("Hour")
plt.ylabel("NO2")
plt.title("Comparison of NO2 Before and After Intervention Over Time")
plt.legend()

plt.savefig(f'{modelrun}_lineplot_NO2_comparedToStatusQuo.pdf', dpi = 300)

# Display the plot
# plt.show()

# Set up Seaborn style
sns.set(style="whitegrid")

# Create the line plot for NO2 before intervention
plt.figure(figsize=(10, 6))
sns.lineplot(x="hour", y="MET_statusq", data=exposure_comp, label="Before Intervention")

# Add the line plot for NO2 after intervention
sns.lineplot(x="hour", y="MET_interv", data=exposure_comp, label="After Intervention")

# Customize plot
plt.xlabel("Hour")
plt.ylabel("MET")
plt.title("Comparison of MET Before and After Intervention Over Time")
plt.legend()

plt.savefig(f'{modelrun}_lineplot_MET_comparedToStatusQuo.pdf', dpi = 300)

# Display the plot
# plt.show()


# plot the difference between intervention and status quo scenario
exposure_comp["NO2_diff"] = exposure_comp["NO2_statusq"]- exposure_comp["NO2_interv"] 
exposure_comp["MET_diff"] = exposure_comp["MET_statusq"]- exposure_comp["MET_interv"]


PlotVarsInLists(plottypes, ["NO2_diff", "MET_diff"], continuousstratvars, categoricalstratvars, showplots, modelrun, fullnamedict)



# plot of exposure distribution per hour per different sociodemographic groups
# # sex
# sexdf = exposure_df[["sex", "hour", "NO2", "MET"]].groupby(["sex", "hour"], as_index=False).mean()
# print(sexdf.head())    

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
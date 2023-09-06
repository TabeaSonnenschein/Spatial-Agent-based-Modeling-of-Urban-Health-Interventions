import matplotlib.pyplot as plt
import pandas as pd
import os
import seaborn as sns
import geopandas as gpd
####################################################


def ScatterOverTimeColCategory(outcomvar, colcategory, showplots, modelrun, df, ylabel = None, collabel = None):
    if ylabel is None:
        ylabel = outcomvar
    if collabel is None:
        collabel = colcategory
    sns.set(style="whitegrid")
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x="hour", y=outcomvar, hue=colcategory, data=df, alpha=0.4)
    plt.xlabel("Hour")
    plt.ylabel(ylabel)
    plt.title(f"Distribution of {outcomvar} Over Time by {collabel}")
    plt.legend(title=collabel)
    plt.savefig(f'{modelrun}_scatterplot_{outcomvar}_by_{colcategory}.pdf', dpi = 300)
    if showplots:
        plt.show()
    plt.close()
    

def ScatterOverTimeColContinous(outcomvar, colvar, showplots, modelrun, df, ylabel = None, collabel = None):
    if ylabel is None:
        ylabel = outcomvar
    if collabel is None:
        collabel = colvar
    sns.set(style="whitegrid")
    color_map = sns.color_palette("RdYlGn_r", as_cmap=True)
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x="hour", y=outcomvar, hue=colvar, data=df, alpha=0.4, palette=color_map)
    plt.xlabel("Hour")
    plt.ylabel(ylabel)
    plt.title(f"Distribution of {outcomvar} Over Time by {collabel}")
    plt.legend(title=collabel)
    plt.savefig(f'{modelrun}_scatterplot_{outcomvar}_by_{colvar}.pdf', dpi = 300)
    if showplots:
        plt.show()
    plt.close()
    

def LineOverTimeColCategory(outcomvar, colcategory, showplots, modelrun, df, ylabel = None, collabel = None):
    if ylabel is None:
        ylabel = outcomvar
    if collabel is None:
        collabel = colcategory
    sns.set(style="whitegrid")
    plt.figure(figsize=(10, 6))
    sns.lineplot(x="hour", y=outcomvar, hue=colcategory, data=df, alpha=0.4,  errorbar = "sd")
    plt.xlabel("Hour")
    plt.ylabel(ylabel)
    plt.title(f"Distribution of {outcomvar} Over Time by {collabel}")
    plt.legend(title=collabel)
    plt.savefig(f'{modelrun}_lineplot_{outcomvar}_by_{colcategory}.pdf', dpi = 300)
    if showplots:
        plt.show()
    plt.close()
    

def LineOverTimeColContinous(outcomvar, colvar, showplots, modelrun,df,  ylabel = None, collabel = None):
    if ylabel is None:
        ylabel = outcomvar
    if collabel is None:
        collabel = colvar
    sns.set(style="whitegrid")
    color_map = sns.color_palette("RdYlGn_r", as_cmap=True)
    plt.figure(figsize=(10, 6))
    sns.lineplot(x="hour", y=outcomvar, hue=colvar, data=df, alpha=0.4, palette=color_map,  errorbar = "sd")
    plt.xlabel("Hour")
    plt.ylabel(ylabel)
    plt.title(f"Distribution of {outcomvar} Over Time by {collabel}")
    plt.legend(title=collabel)
    plt.savefig(f'{modelrun}_lineplot_{outcomvar}_by_{colvar}.pdf', dpi = 300)
    if showplots:
        plt.show()
    plt.close()
    

def ViolinOverTimeColCategory(outcomvar, colcategory, showplots, modelrun,df, ylabel = None, collabel = None):
    if ylabel is None:
        ylabel = outcomvar
    if collabel is None:
        collabel = colcategory
    sns.set(style="whitegrid")
    plt.figure(figsize=(10, 6))
    sns.violinplot(x="hour", y=outcomvar, hue=colcategory, data=df, linewidth=0)
    plt.xlabel("Hour")
    plt.ylabel(ylabel)
    plt.title(f"Distribution of {outcomvar} Over Time by {collabel}")
    plt.legend(title=collabel)
    plt.savefig(f'{modelrun}_violinplot_{outcomvar}_by_{colcategory}.pdf', dpi = 300)
    if showplots:
        plt.show()
    plt.close()

def ViolinOverTimeColContinous(outcomvar, colvar, showplots, modelrun, df, ylabel = None, collabel = None):
    if ylabel is None:
        ylabel = outcomvar
    if collabel is None:
        collabel = colvar
    sns.set(style="whitegrid")
    color_map = sns.color_palette("RdYlGn_r")
    plt.figure(figsize=(10, 6))
    sns.violinplot(x="hour", y=outcomvar, hue=colvar, data=df, linewidth=0, palette=color_map)
    plt.xlabel("Hour")
    plt.ylabel(ylabel)
    plt.title(f"Distribution of {outcomvar} Over Time by {collabel}")
    plt.legend(title=collabel)
    plt.savefig(f'{modelrun}_violinplot_{outcomvar}_by_{colvar}.pdf', dpi = 300)
    if showplots:
        plt.show()
    plt.close()

def PlotVarsInLists(plottypes, outcomevars, continuousstratvars, categoricalstratvars, df, showplots, modelrun, fullnamedict):
    for plottype in plottypes:
        for outvar in outcomevars:
            if plottype == "scatter":
                for stratvar in continuousstratvars:
                    ScatterOverTimeColContinous(outcomvar=outvar, colvar=stratvar, showplots=showplots, modelrun=modelrun, df=df, ylabel=fullnamedict[outvar], collabel=fullnamedict[stratvar])
                for stratvar in categoricalstratvars:
                    ScatterOverTimeColCategory(outcomvar=outvar, colcategory=stratvar, showplots=showplots, modelrun=modelrun, df=df, ylabel=fullnamedict[outvar], collabel=fullnamedict[stratvar])
            elif plottype == "line":
                for stratvar in continuousstratvars:
                    LineOverTimeColContinous(outcomvar=outvar, colvar=stratvar, showplots=showplots, modelrun=modelrun, df=df, ylabel=fullnamedict[outvar], collabel=fullnamedict[stratvar])
                for stratvar in categoricalstratvars:
                    LineOverTimeColCategory(outcomvar=outvar, colcategory=stratvar, showplots=showplots, modelrun=modelrun, df=df, ylabel=fullnamedict[outvar], collabel=fullnamedict[stratvar])
            elif plottype == "violin":
                for stratvar in continuousstratvars:
                    ViolinOverTimeColContinous(outcomvar=outvar, colvar=stratvar, showplots=showplots, modelrun=modelrun, df=df, ylabel=fullnamedict[outvar], collabel=fullnamedict[stratvar])
                for stratvar in categoricalstratvars:
                    ViolinOverTimeColCategory(outcomvar=outvar, colcategory=stratvar, showplots=showplots, modelrun=modelrun, df=df, ylabel=fullnamedict[outvar], collabel=fullnamedict[stratvar])


def CompareAverageExposure2Scenarios(outcomvar, scenariosuffixes, showplots, modelrun, scenariolabels,ylabel = None ):
    if ylabel is None:
        ylabel = outcomvar
    sns.set(style="whitegrid")
    plt.figure(figsize=(10, 6))
    for count,suffix in enumerate(scenariosuffixes):
        sns.lineplot(x="hour", y=outcomvar+suffix, data=exposure_comp, label=scenariolabels[count])
    plt.xlabel("Hour")
    plt.ylabel(ylabel)
    plt.title(f"Comparison of {outcomvar} Before and After Intervention Over Time")
    plt.legend()
    plt.savefig(f'{modelrun}_lineplot_{outcomvar}_comparedToStatusQuo.pdf', dpi = 300)
    if showplots:
        plt.show()
    plt.close()


def MeanComparisonWithoutTime(outcomvar, stratifier , showplots, modelrun, df, ylabel = None, xlabel = None):
    sns.set(style="whitegrid")
    plt.figure(figsize=(8, 6))
    sns.violinplot(x=stratifier, y=outcomvar, data=df, palette="Set3")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend()
    plt.title(f'{outcomvar} Distributions per {stratifier}')
    plt.savefig(f'{modelrun}_violinplot_{outcomvar}_by_{stratifier}_withoutTime.pdf', dpi = 300)
    if showplots:
        plt.show()


######################################################
######################################################
nb_agents =  21750  #87000 = 10%, 43500 = 5%, 21750 = 2.5%, 8700 = 1%
path_data = "C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/ModelRuns/"
# path_data = "/Users/tsonnens/Documents/dasefwg/"
# modelrun = "StatusQuo"
# modelrun = "SpeedInterv"
# modelrun = "PedStrWidth"
modelrun = "RetaiDnsDiv"
# modelrun = "LenBikRout"


os.chdir(path_data + 'AgentExposure/' + modelrun)

print("Reading the data")
# read exposure data
exposure_df = pd.read_csv(f"AgentExposure_A{nb_agents}_M1_{modelrun}_hourAsRowsMerged.csv")
# Renaming some columns for elegance
exposure_df = exposure_df.rename(columns={"incomeclass_int": "income", "migrationbackground": "migr_bck"})

# restructuring data
exposure_df["income_class"]=exposure_df["income"].apply(lambda x: "Low" if x in range(1,5) else ("Medium" if x in range(5,9) else "High"))
# 1 low # 10 high

print("Analyzing the data")
print(exposure_df.head())
print(exposure_df.info())
print(exposure_df.describe())
for column in exposure_df.select_dtypes(include=['object']):
    print("\nValue counts for", column)
    print(exposure_df[column].value_counts())



print("Plotting the data")
#################################
###  Exposure stratifications ###
#################################
print("Plotting the exposure stratification")
continuousstratvars = ["income"]
categoricalstratvars = ["sex", "migr_bck", "income_class"]
plottypes = [ "line", "violin"] # "scatter"
outcomevars = ["NO2", "MET"]

fullnamedict = {
    "income": "Income Decile: 1 low, 10 high",
    "sex": "sex",
    "migr_bck": "Migration Background",
    "income_class": "Income Group",
    "NO2": "NO2 (µg/m3)",
    "MET": "Metabolic Equivalent of Task (MET)",
    "NO2_diff": "NO2 Difference (µg/m3)",
    "MET_diff": "Metabolic Equivalent of Task (MET) Difference" }
           
showplots = False
PlotVarsInLists(plottypes=plottypes, outcomevars=outcomevars, continuousstratvars=continuousstratvars,
                categoricalstratvars=categoricalstratvars,showplots= showplots, modelrun=modelrun,
                df=exposure_df, fullnamedict=fullnamedict)

#########################
### Comparative Plots ###
#########################
print("Plotting Comparison to Status Quo over Time")
# read exposure data
modelrun_stat = "StatusQuo"
exposure_df_statusq = pd.read_csv(path_data + 'AgentExposure/' + modelrun_stat + f"/AgentExposure_A{nb_agents}_M1_{modelrun_stat}_hourAsRowsMerged.csv")
suffixes = ("_interv", "_statusq")
exposure_comp = pd.merge(exposure_df, exposure_df_statusq, on=["agent_ID", "hour"], how="left", suffixes=suffixes)

for outcomvar in outcomevars:
    CompareAverageExposure2Scenarios(outcomvar, ["_interv", "_statusq"], showplots, modelrun, scenariolabels=[ "After Intervention", "Before Intervention"],ylabel =  fullnamedict[outcomvar])

print("Plotting the difference between intervention and status quo scenario")

# plot the difference between intervention and status quo scenario
exposure_comp["NO2_diff"] = exposure_comp["NO2_interv"] -exposure_comp["NO2_statusq"]
exposure_comp["MET_diff"] = exposure_comp["MET_interv"] - exposure_comp["MET_statusq"]
exposure_comp = exposure_comp.rename(columns={"sex"+suffixes[1]: "sex", "migr_bck"+suffixes[1]: "migr_bck", "neighb_code"+suffixes[1]: "neighb_code"})

print(exposure_comp[["NO2_diff", "MET_diff"]].describe())
PlotVarsInLists(plottypes=plottypes, outcomevars=["NO2_diff", "MET_diff"], continuousstratvars=continuousstratvars,
                categoricalstratvars=categoricalstratvars,showplots= showplots, modelrun=modelrun,
                df=exposure_comp, fullnamedict=fullnamedict)

#ploting the difference between intervention and status quo scenario on average over the day
print("Plotting the difference between intervention and status quo scenario on average over the day")

print(exposure_comp.columns)
# restructuring the data to have the hour as a column
exposure_day = exposure_comp[["agent_ID", "sex", "migr_bck", "income_class", "income", "NO2_diff", "NO2_interv", "NO2_statusq", "MET_diff", "MET_interv", "MET_statusq"]].groupby(["agent_ID", "sex", "migr_bck", "income_class", "income"],  as_index=False).mean()
print(exposure_day.describe())


outcomevars = ["NO2_diff", "NO2_interv", "NO2_statusq", "MET_diff", "MET_interv", "MET_statusq"]

fullnamedict2 = {"NO2_diff": "NO2 Difference (µg/m3)",
                 "NO2_interv": "NO2 Intervention (µg/m3)",
                 "NO2_statusq": "NO2 Status Quo (µg/m3)",
                 "MET_diff": "MET Difference",
                 "MET_interv": "MET Intervention",
                 "MET_statusq": "MET Status Quo"}


for outcomvar in outcomevars:
    for stratifiers in categoricalstratvars:
        MeanComparisonWithoutTime(outcomvar=outcomvar, stratifier=stratifiers, showplots=showplots, modelrun=modelrun, df=exposure_day, ylabel=fullnamedict2[outcomvar], xlabel=fullnamedict[stratifiers])
        
### map the change in exposure per neighborhood
print("Plotting the difference between intervention and status quo scenario per neighborhood")
neighborhoods = gpd.read_file("D:\PhD EXPANSE\Data\Amsterdam\Administrative Units\Amsterdam_Neighborhoods_RDnew.shp")
print(neighborhoods.columns)
exposure_neigh = exposure_comp[["neighb_code", "NO2_diff", "NO2_interv", "NO2_statusq", "MET_diff", "MET_interv", "MET_statusq"]].groupby(["neighb_code"],  as_index=False).mean()
exposure_neigh.rename(columns={"neighb_code": "buurtcode"}, inplace=True)
print(exposure_neigh.head())
neighborhoods = neighborhoods.merge(exposure_neigh, on="buurtcode", how="left")

def PlotPerNeighbOutcome(outcomvar, showplots, modelrun, spatialdata, outcomelabel = None):
    if outcomelabel is None:
        outcomelabel = outcomvar
    spatialdata.plot(outcomvar, antialiased=False, legend = True)
    plt.title(f"{outcomelabel} Per Neighborhood")
    plt.savefig(f'{modelrun}_neighbmap_{outcomvar}.pdf', dpi = 300)
    if showplots:
        plt.show()
    plt.close()

for outcomvar in outcomevars:
    PlotPerNeighbOutcome(outcomvar=outcomvar, showplots=showplots, modelrun=modelrun, spatialdata=neighborhoods, outcomelabel=fullnamedict2[outcomvar])
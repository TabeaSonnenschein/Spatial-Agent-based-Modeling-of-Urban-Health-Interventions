import pandas as pd
import os

path_data = "D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/"
scenario = "StatusQuo"
nb_humans = 21750
# nb_humans = 43500
# read in the data
experimentoverview = pd.read_csv(f"{path_data}ExperimentOverview.csv")
# experimentoverview = experimentoverview.loc[experimentoverview["fullrun"] == True]
modelruns = experimentoverview.loc[(experimentoverview["Experiment"] == scenario)& (experimentoverview["Number of Agents"] == f"{nb_humans}Agents"), "Model Run"].values
subsetnr = [experimentoverview.loc[(experimentoverview["Experiment"] == scenario)& (experimentoverview["Model Run"]== modelrun), "Population Sample"].values[0] for modelrun in modelruns]
print(modelruns, subsetnr)

meanR2 = []

# traffassignfilespath = f"{path_data}TrafficRemainder/TraffCoefficient/new/{nb_humans}/"
traffassignfilespath = f"{path_data}ModelRuns/{scenario}/{nb_humans}Agents/Traffic/"

for count,modelrun in enumerate(modelruns):
    # read in the text data
    TraffAssDat = open(f'{traffassignfilespath}TraffAssignModelPerf{nb_humans}_{scenario}_pop{subsetnr[count]}_{modelrun}.txt', 'r')
    TraffRegressions = TraffAssDat.readlines()
    TraffAssDat.close()
    
    # retrieve the rows that start with 0
    TraffPerform = [line.split(" ")[-1] for line in TraffRegressions if line.startswith('R2')]
    TraffPerform = [float(R2.replace("\n","")) for R2 in TraffPerform]
    
    Timepoints = [line.replace("hour ","").replace(" \n","") for line in TraffRegressions if line.startswith('hour ')]
    Date = [timepoint.split(" ")[0] for timepoint in Timepoints]
    Time = [timepoint.split(" ")[1] for timepoint in Timepoints]

    # create a dataframe
    TraffPerform_df = pd.DataFrame({"Date":Date, "Time":Time, "R2":TraffPerform, "ModelRun":modelrun, "PopulationSample":subsetnr[count]})
    TraffPerform_df.to_csv(f"{traffassignfilespath}TraffAssignModelPerf{nb_humans}_{scenario}_pop{subsetnr[count]}_{modelrun}.csv", index=False)
    meanR2.append(TraffPerform_df["R2"].iloc[23:].mean())

totTraffPerformdf = pd.DataFrame({"ModelRun":modelruns, "PopulationSample":subsetnr, "MeanR2":meanR2})
# add a row with the mean of the mean coefficients
meanmean = pd.DataFrame({"ModelRun":["tot"], "PopulationSample":["tot"], "MeanR2": totTraffPerformdf["MeanR2"].mean()})
totTraffPerformdf = pd.concat([totTraffPerformdf, meanmean], axis=0)
totTraffPerformdf.to_csv(f"{traffassignfilespath}TraffAssignModelPerf{nb_humans}_{scenario}_MeanTraffPerform.csv", index=False)
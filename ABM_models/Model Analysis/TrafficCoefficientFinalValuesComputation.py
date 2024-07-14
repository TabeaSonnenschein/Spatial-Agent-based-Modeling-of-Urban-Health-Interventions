import pandas as pd
import os

path_data = "D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/"
scenario = "StatusQuo"
nb_humans = 21750
# read in the data
# experimentoverview = pd.read_csv(f"{path_data}ExperimentOverview.csv")
# experimentoverview = experimentoverview.loc[experimentoverview["fullrun"] == True]
# modelruns = experimentoverview.loc[experimentoverview["Experiment"] == scenario, "Model Run"].values
modelruns = [300390, 364558, 254724, 90988, 529699, 602810]
subsetnr = [0, 5, 1, 2, 6, 4]
meancoeffs = []

for count,modelrun in enumerate(modelruns):
    # read in the text data
    TraffAssDat = open(f'{path_data}ModelRuns/{scenario}/{nb_humans}Agents/Traffic/TraffAssignModelPerf{nb_humans}_{scenario}_pop{subsetnr[count]}_{modelrun}.txt', 'r')
    TraffRegressions = TraffAssDat.readlines()
    TraffAssDat.close()
    
    # retrieve the rows that start with 0
    TraffCoefficients = [line.split(" ")[-1] for line in TraffRegressions if line.startswith('0')]
    TraffCoefficients = [float(coef.replace("\n","")) for coef in TraffCoefficients]
    
    Timepoints = [line.replace("hour ","").replace(" \n","") for line in TraffRegressions if line.startswith('hour ')]
    Date = [timepoint.split(" ")[0] for timepoint in Timepoints]
    Time = [timepoint.split(" ")[1] for timepoint in Timepoints]


    # create a dataframe
    TraffCoefficients_df = pd.DataFrame({"Date":Date, "Time":Time, "Coefficients":TraffCoefficients, "ModelRun":modelrun, "PopulationSample":subsetnr[count]})
    TraffCoefficients_df.to_csv(f"{path_data}ModelRuns/{scenario}/{nb_humans}Agents/Traffic/TraffAssignModelPerf{nb_humans}_{scenario}_pop{subsetnr[count]}_{modelrun}.csv", index=False)
    meancoeffs.append(TraffCoefficients_df["Coefficients"].iloc[23:].mean())
    
totTraffCoeffdf = pd.DataFrame({"ModelRun":modelruns, "PopulationSample":subsetnr, "MeanCoefficients":meancoeffs})
# add a row with the mean of the mean coefficients
meanmean = pd.DataFrame({"ModelRun":["tot"], "PopulationSample":["tot"], "MeanCoefficients": totTraffCoeffdf["MeanCoefficients"].mean()})
totTraffCoeffdf = pd.concat([totTraffCoeffdf, meanmean], axis=0)
totTraffCoeffdf.to_csv(f"{path_data}ModelRuns/{scenario}/{nb_humans}Agents/Traffic/TraffAssignModelPerf{nb_humans}_{scenario}_MeanTraffCoefficients.csv", index=False)
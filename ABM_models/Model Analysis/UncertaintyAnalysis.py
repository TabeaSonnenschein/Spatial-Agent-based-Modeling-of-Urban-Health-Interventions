import numpy as np
import pandas as pd
import os
import geopandas as gpd
import scipy.stats as st

####  Calculate uncertainty in Monte Carlo simulation
# let the same population sample run 5 times
# difference between population samples
# difference between population sample size

def calculate_uncertainty(runs):
    """
    Calculate standard deviation for each run and then return the mean of the standard deviation
    """
    meanval = np.mean(runs)  # Mean of each sample
    std_devs = np.std(runs)  # Standard deviation for each sample
    mean_uncertainty = np.mean(std_devs)  # Mean of uncertainties (std deviations) across all samples
    uncertainty_percentage = mean_uncertainty/meanval
    return meanval, mean_uncertainty, uncertainty_percentage


def calculate_uncertainty_insublist(runslist):
    length = len(runslist[0])
    meanvals, mean_uncertainties, uncertainty_percentages = [], [], []
    for i in range(length):
        sublist = [run[i] for run in runslist]
        meanval, mean_uncertainty, uncertainty_percentage = calculate_uncertainty(sublist)
        meanvals.append(meanval)
        mean_uncertainties.append(mean_uncertainty)
        uncertainty_percentages.append(uncertainty_percentage)
    return meanvals, mean_uncertainties, uncertainty_percentages

def calculate_CV_CI(runs, confidence_level=0.95):
    """
    Calculate the mean, standard deviation, coefficient of variation (uncertainty percentage),
    and the confidence interval for the coefficient of variation.
    
    Parameters:
    runs (list or np.array): List of values from the different model runs.
    confidence_level (float): Confidence level for the interval, default is 95%.
    
    Returns:
    tuple: mean value, mean standard deviation, coefficient of variation (CV),
           lower bound of CV CI, upper bound of CV CI
    """
    # Calculate mean and standard deviation for the sample
    meanval = np.mean(runs)
    std_dev = np.std(runs)
    
    # Coefficient of variation (CV)
    cv = std_dev / meanval
    
    # Z-score for a 95% confidence level
    if confidence_level == 0.95:
        z = 1.96
    elif confidence_level == 0.99:
        z = 2.576
    else:
        raise ValueError("Unsupported confidence level. Use 0.95 or 0.99.")
    
    n = len(runs) 
    standard_error = std_dev / np.sqrt(n)
    margin_of_error = z * standard_error
        
    # Confidence interval
    lower_bound = meanval - margin_of_error
    upper_bound = meanval + margin_of_error

    return meanval, std_dev, cv, lower_bound, upper_bound

def calculate_CV_CI_insublist(runslist, confidence_level=0.95):
    length = len(runslist[0])
    meanvals, std_devs, cvs, lower_bounds, upper_bounds = [], [], [], [], []
    for i in range(length):
        sublist = [run[i] for run in runslist]
        meanval, std_dev, cv, lower_bound, upper_bound = calculate_CV_CI(sublist, confidence_level)
        meanvals.append(meanval)
        std_devs.append(std_dev)
        cvs.append(cv)
        lower_bounds.append(lower_bound)
        upper_bounds.append(upper_bound)
    return meanvals, std_devs, cvs, lower_bounds, upper_bounds


def CollectValsForRuns(modelruns, path_data, scenario, nb_agents, city_Intids):
    personalNO2,personalNO2wFilter, personalMET, walk, bike, drive, transit, traffic, NO2 = [], [], [], [], [], [], [], [], []
    personalNO2hourly, personalNO2wFilterhourly, personalMEThourly, walkhourly, bikehourly, drivehourly, transithourly, traffichourly, NO2hourly = [], [], [], [], [], [], [], [], []
    personalNO2daily, personalNO2wFilterdaily, personalMETdaily, walkdaily, bikedaily, drivedaily, transitdaily, trafficdaily, NO2daily = [], [], [], [], [], [], [], [], []
    personalNO2monthly, personalNO2wFiltermonthly, personalMETmonthly, walkmonthly, bikemonthly, drivemonthly, transitmonthly, trafficmonthly, NO2monthly = [], [], [], [], [], [], [], [], []
    
    Days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    for run in modelruns:
        print("collecting for run: ", run)
        exposure_df = pd.read_csv(path_data+f"/AgentExposure/{run}/ExposureViz/Exposure_A{nb_agents}_{run}_aggregate.csv")
        exposurestats = exposure_df.loc[exposure_df["timeunit"] == "total", ["NO2", "NO2wFilter", "MET"]].values
        personalNO2.append(exposurestats[0][0])
        personalNO2wFilter.append(exposurestats[0][1])
        
        weeklyMETdf = pd.read_csv(path_data+f"/UpdatedExposure/{run}/ExposureViz/WeeklyMEThours_A{nb_agents}_{run}_aggregate.csv")
        dailyMETdf = pd.read_csv(path_data+f"/UpdatedExposure/{run}/ExposureViz/DailyMEThours_A{nb_agents}_{run}_aggregate.csv")
        hourlyMETdf = pd.read_csv(path_data+f"/UpdatedExposure/{run}/ExposureViz/MarginalMET_A{nb_agents}_{run}_verticalAsRows.csv")
        personalMET.append(weeklyMETdf.loc[weeklyMETdf["timeunit"] == "total", "MET"].values[0])

        exposurestats_hourly = exposure_df.loc[exposure_df["timeunit"].str.contains("hour"), ["NO2", "NO2wFilter", "MET"]]
        personalNO2hourly.append(list(exposurestats_hourly.loc[:,"NO2"].values))
        personalNO2wFilterhourly.append(list(exposurestats_hourly.loc[:,"NO2wFilter"].values))
        METhourly = hourlyMETdf[["METtot", "hour"]].groupby("hour").mean().reset_index()
        personalMEThourly.append(list(METhourly["METtot"].values))
        
        exposurestats_daily = exposure_df.loc[exposure_df["timeunit"].str.contains("weekday"), ["NO2", "NO2wFilter", "MET"]]
        personalNO2daily.append(list(exposurestats_daily.loc[:,"NO2"].values))
        personalNO2wFilterdaily.append(list(exposurestats_daily.loc[:,"NO2wFilter"].values))
        personalMETdaily.append(list(dailyMETdf.loc[dailyMETdf["timeunit"].str.contains("weekday"), "MET"].values))
        
        exposurestats_monthly = exposure_df.loc[exposure_df["timeunit"].str.contains("month"), ["NO2", "NO2wFilter", "MET"]]
        personalNO2monthly.append(list(exposurestats_monthly.loc[:,"NO2"].values))
        personalNO2wFiltermonthly.append(list(exposurestats_monthly.loc[:,"NO2wFilter"].values))
        personalMETmonthly.append(list(weeklyMETdf.loc[weeklyMETdf["timeunit"].str.contains("month"), "MET"].values))
        
        modalsplit_df = pd.read_csv(path_data+f"/ModalSplit/ModalSplitLog{nb_agents}_{scenario}_{run}.csv")
        modalsplit_df["total"] = modalsplit_df["walk"] + modalsplit_df["bike"] + modalsplit_df["drive"] +modalsplit_df["transit"]
        modalsplit_df["walk"] = modalsplit_df["walk"]/modalsplit_df["total"]
        modalsplit_df["bike"] = modalsplit_df["bike"]/modalsplit_df["total"]
        modalsplit_df["drive"] = modalsplit_df["drive"]/modalsplit_df["total"]
        modalsplit_df["transit"] = modalsplit_df["transit"]/modalsplit_df["total"]
        walk.append(np.nanmean(modalsplit_df["walk"].values))
        bike.append(np.nanmean(modalsplit_df["bike"].values))
        drive.append(np.nanmean(modalsplit_df["drive"].values))
        transit.append(np.nanmean(modalsplit_df["transit"].values))
        walkhourly.append([np.mean(modalsplit_df.loc[modalsplit_df["hour"] == hour,"walk"].values) for hour in range(24)])
        bikehourly.append([np.mean(modalsplit_df.loc[modalsplit_df["hour"] == hour,"bike"].values) for hour in range(24)])
        drivehourly.append([np.mean(modalsplit_df.loc[modalsplit_df["hour"] == hour,"drive"].values) for hour in range(24)])
        transithourly.append([np.mean(modalsplit_df.loc[modalsplit_df["hour"] == hour,"transit"].values) for hour in range(24)])
        
        walkdaily.append([np.mean(modalsplit_df.loc[modalsplit_df["weekday"] == day,"walk"].values) for day in Days])
        bikedaily.append([np.mean(modalsplit_df.loc[modalsplit_df["weekday"] == day,"bike"].values) for day in Days])
        drivedaily.append([np.mean(modalsplit_df.loc[modalsplit_df["weekday"] == day,"drive"].values) for day in Days])
        transitdaily.append([np.mean(modalsplit_df.loc[modalsplit_df["weekday"] == day,"transit"].values) for day in Days])
        
        walkmonthly.append([np.mean(modalsplit_df.loc[modalsplit_df["month"] == month,"walk"].values) for month in [1,4,7,10]])
        bikemonthly.append([np.mean(modalsplit_df.loc[modalsplit_df["month"] == month,"bike"].values) for month in [1,4,7,10]])
        drivemonthly.append([np.mean(modalsplit_df.loc[modalsplit_df["month"] == month,"drive"].values) for month in [1,4,7,10]])
        transitmonthly.append([np.mean(modalsplit_df.loc[modalsplit_df["month"] == month,"transit"].values) for month in [1,4,7,10]])
        
        
        NO2_df = pd.read_csv(path_data+f"/NO2/NO2Viz/NO2Means_{scenario}_{run}.csv")
        CityNO2 = pd.DataFrame(NO2_df.loc[NO2_df["int_id"].isin(city_Intids)].iloc[:,1:].mean(axis=0))
        NO2.append(CityNO2.loc["mean_prNO2"].values[0])
        monthcols = [col for col in NO2_df.columns if any(x in col for x in ["M1", "M4", "M7", "M10"])]
        hourcols = [col for col in NO2_df.columns if "H" in col]
        daycols = [col for col in NO2_df.columns if len(col) > 16]
        NO2monthly.append(list(CityNO2.loc[monthcols].values.flatten()))
        NO2hourly.append(list(CityNO2.loc[hourcols].values.flatten()))
        NO2daily.append(list(CityNO2.loc[daycols].values.flatten()))
        
        Traff_df = pd.read_csv(path_data+f"/Traffic/TraffViz/TraffMeans_{scenario}_{run}.csv")
        CityTraff = pd.DataFrame(Traff_df.loc[(Traff_df["int_id"].isin(city_Intids)) & (Traff_df["mean_prTraff"] != 0)].iloc[:,1:].mean(axis=0))
        traffic.append(CityTraff.loc["mean_prTraff"].values[0])
        # replace monthcols.replace("NO2", "Traff") for all elements
        monthcols = [col.replace("NO2", "Traff") for col in monthcols]
        hourcols = [col.replace("NO2", "Traff") for col in hourcols]
        daycols = [col.replace("NO2", "Traff") for col in daycols]
        trafficmonthly.append(list(CityTraff.loc[monthcols].values.flatten()))
        traffichourly.append(list(CityTraff.loc[hourcols].values.flatten()))
        trafficdaily.append(list(CityTraff.loc[daycols].values.flatten()))

    outcomevarstotal = [personalNO2,personalNO2wFilter, personalMET, walk, bike, drive, transit, traffic, NO2]
    outcomevars_hourly = [personalNO2hourly,personalNO2wFilterhourly, personalMEThourly, walkhourly, bikehourly, drivehourly, transithourly, traffichourly, NO2hourly]
    outcomevars_daily = [personalNO2daily,personalNO2wFilterdaily, personalMETdaily, walkdaily, bikedaily, drivedaily, transitdaily, trafficdaily, NO2daily]
    outcomevars_monthly = [personalNO2monthly,personalNO2wFiltermonthly, personalMETmonthly, walkmonthly, bikemonthly, drivemonthly, transitmonthly, trafficmonthly, NO2monthly]

    return outcomevarstotal, outcomevars_hourly, outcomevars_daily, outcomevars_monthly


def create_uncertainty_table(modelruns, outcomevarstotal, outcomevars_hourly, outcomevars_daily, outcomevars_monthly, uncertaintytype):

    outcomevarnames = ["Personal NO2 Exposure unfiltered","Personal NO2 Exposure w. I/O Filter", "Transport MET", "Walk Share", "Bike Share", "Drive Share", "Transit Share", "Traffic Volume", "NO2 (µg/m3)"]
    convidence_level = 0.95
    uncertaintyvars = ["Mean Value", "Mean Standard Deviation", "Coefficient of Variation", f"CI {int(convidence_level*100)}% Lower Bound", f"CI {int(convidence_level*100)}% Upper Bound"]

    modelruns.extend(uncertaintyvars)
    
    ############# Total Means uncertainty
    for count, outcomevar in enumerate(outcomevarstotal):
        meanval, mean_uncertainty, uncertainty_percentage, lowerCV, upperCV = calculate_CV_CI(outcomevar)
        print(f"Uncertainty in {outcomevarnames[count]} is {uncertainty_percentage}")
        outcomevarstotal[count].extend([meanval, mean_uncertainty, uncertainty_percentage, lowerCV, upperCV])
        
    Totaluncertainty = pd.DataFrame({"modelruns": modelruns, 
                    **{outcomevarnames[count]: outcomevarstotal[count] for count in range(len(outcomevarnames))}})
    Totaluncertainty.to_csv("D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/UncertaintyAnalysis" + f"/{uncertaintytype}_{scenario}_{nb_agents}_Total.csv", index=False)

    ############# Hourly Means uncertainty
    for count, outcomevar in enumerate(outcomevars_hourly):
        meanvals, mean_uncertainties, uncertainty_percentages, lowerCIs, upperCIs = calculate_CV_CI_insublist(runslist = outcomevar)
        print(f"Hourly Uncertainty in {outcomevarnames[count]} is {np.mean(uncertainty_percentages)}")
        outcomevars_hourly[count].extend([meanvals, mean_uncertainties, uncertainty_percentages, lowerCIs, upperCIs]) 

    Hourlyuncertainty = pd.DataFrame({"modelruns": modelruns, 
                    **{outcomevarnames[count]+f"_H{hour}": [outcomevars_hourly[count][modelrun][hour] for modelrun in range(len(modelruns))]  for hour in range(24) for count in range(len(outcomevars_hourly)) }})
    Hourlyuncertainty.to_csv("D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/UncertaintyAnalysis" + f"/{uncertaintytype}_{scenario}_{nb_agents}_Hourly.csv", index=False)

    ############# Daily Means uncertainty
    for count, outcomevar in enumerate(outcomevars_daily):
        meanvals, mean_uncertainties, uncertainty_percentages, lowerCIs, upperCIs = calculate_CV_CI_insublist(runslist = outcomevar)
        print(f"Daily Uncertainty in {outcomevarnames[count]} is {np.mean(uncertainty_percentages)}")
        outcomevars_daily[count].extend([meanvals, mean_uncertainties, uncertainty_percentages,  lowerCIs, upperCIs])

    Dailyuncertainty = pd.DataFrame({"modelruns": modelruns, 
                    **{outcomevarnames[count]+f"_D{day}":  [outcomevars_daily[count][modelrun][day] for modelrun in range(len(modelruns))] for day in range(7) for count in range(len(outcomevarnames)) }})
    Dailyuncertainty.to_csv("D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/UncertaintyAnalysis" + f"/{uncertaintytype}_{scenario}_{nb_agents}_Daily.csv", index=False)

    ############# Monthly Means uncertainty
    for count, outcomevar in enumerate(outcomevars_monthly):
        meanvals, mean_uncertainties, uncertainty_percentages, lowerCIs, upperCIs = calculate_CV_CI_insublist(runslist = outcomevar)
        print(f"Monthly Uncertainty in {outcomevarnames[count]} is {np.mean(uncertainty_percentages)}")
        outcomevars_monthly[count].extend([meanvals, mean_uncertainties, uncertainty_percentages,  lowerCIs, upperCIs])

    Monthlyuncertainty = pd.DataFrame({"modelruns": modelruns, 
                    **{outcomevarnames[count]+f"_M{month}": [outcomevars_monthly[count][modelrun][month] for modelrun in range(len(modelruns))] for month in range(4) for count in range(len(outcomevarnames)) }})
    Monthlyuncertainty.to_csv("D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/UncertaintyAnalysis" + f"/{uncertaintytype}_{scenario}_{nb_agents}_Monthly.csv", index=False)

    ############# Join all tables
    JoinedTable = Totaluncertainty.loc[Totaluncertainty["modelruns"].isin(uncertaintyvars)  , ["modelruns"]+ outcomevarnames]
    JoinedTable["TimeUnit"] = "Total"

    HourlyTable = JoinedTable.copy()
    HourlyTable["TimeUnit"] = "Hourly"
    DailyTable = JoinedTable.copy()
    DailyTable["TimeUnit"] = "Daily"
    MonthlyTable = JoinedTable.copy()
    MonthlyTable["TimeUnit"] = "Monthly"
    for outcomevar in outcomevarnames:
        
        hourlyvals = Hourlyuncertainty.loc[Hourlyuncertainty["modelruns"].isin(uncertaintyvars), [col for col in Hourlyuncertainty.columns if outcomevar in col]].mean(axis=1)
        print(hourlyvals)
        HourlyTable[outcomevar] = hourlyvals
        dailyvals = Dailyuncertainty.loc[Dailyuncertainty["modelruns"].isin(uncertaintyvars), [col for col in Dailyuncertainty.columns if outcomevar in col]].mean(axis=1)
        DailyTable[outcomevar] = dailyvals
        monthlyvals = Monthlyuncertainty.loc[Monthlyuncertainty["modelruns"].isin(uncertaintyvars), [col for col in Monthlyuncertainty.columns if outcomevar in col]].mean(axis=1)
        MonthlyTable[outcomevar] = monthlyvals

    JoinedTable = pd.concat([JoinedTable, HourlyTable, DailyTable, MonthlyTable], axis=0)
    JoinedTable = JoinedTable[["TimeUnit", "modelruns"]+outcomevarnames]
    JoinedTable.rename(columns={"modelruns": "Uncertainty Type"}, inplace=True)
    JoinedTable.to_csv("D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/UncertaintyAnalysis" + f"/{uncertaintytype}_{scenario}_{nb_agents}_Joined.csv", index=False)


    return Totaluncertainty, Hourlyuncertainty, Dailyuncertainty, Monthlyuncertainty, JoinedTable


def RestructureJoinedTable(JoinedTable, scenario, nb_agents, uncertaintytype):
    """
    Restructure the joined table so that the outcome variables are in the row and the different uncertainty types are in the columns
    """
    outcomevars = JoinedTable.columns[2:]
    JoinedTable = JoinedTable.melt(id_vars=["TimeUnit", "Uncertainty Type"], var_name="Outcome Variable", value_name="Value")
    JoinedTable = JoinedTable.pivot_table(index=["Outcome Variable", "TimeUnit"], columns="Uncertainty Type", values="Value").reset_index()
    JoinedTable["TimeUnit"] = pd.Categorical(JoinedTable["TimeUnit"], categories=["Total", "Hourly", "Daily", "Monthly"], ordered=True)
    JoinedTable["Outcome Variable"] = pd.Categorical(JoinedTable["Outcome Variable"], categories=outcomevars, ordered=True)
    JoinedTable = JoinedTable.sort_values(by=["Outcome Variable","TimeUnit"])
    JoinedTable = JoinedTable[["Outcome Variable", "TimeUnit", "Mean Value", "Mean Standard Deviation", "Coefficient of Variation", "CI 95% Lower Bound", "CI 95% Upper Bound"]]
    JoinedTable.to_csv(f"D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/UncertaintyAnalysis/{uncertaintytype}_{scenario}_{nb_agents}_JoinedRestructured.csv", index=False)
    return JoinedTable




#################################################################
### Population sample uncertainty
#################################################################
nb_agents = 43500  #87000 = 10%, 43500 = 5%, 21750 = 2.5%, 8700 = 1%
scenario = "StatusQuo"
experimentoverview = pd.read_csv("D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/ExperimentOverview.csv")
AirPollGrid = gpd.read_feather("D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/"+f"SpatialData/AirPollgrid50m.feather")
cityextent = gpd.read_feather("D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/"+f"SpatialData/NoEmissionZone2030.feather")
city_Intids = gpd.sjoin(AirPollGrid,cityextent, how="inner", predicate='intersects')["int_id"].values

uncertaintytypes = [
                    # "PopSampleUncertainty", 
                    # "BehaviorSampleUncertainty", 
                    "PopSizeUncertainty"
                    ]

if "PopSampleUncertainty" in uncertaintytypes:
    # path_data = "D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/ModelRuns"
    # modelruns = experimentoverview.loc[(experimentoverview["Experiment"] == scenario)& (experimentoverview["Number of Agents"] == f"{nb_agents}Agents"), "Model Run"].values
    # modelruns = modelruns.tolist()
    path_data = "D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/UncertaintyAnalysis/popsizes/"
    modelruns = [ 379264, 748744, 765808, 961518]
    
    outcomevarstotal, outcomevars_hourly, outcomevars_daily, outcomevars_monthly = CollectValsForRuns(modelruns = modelruns, 
                                                                                                    path_data = path_data + f"/{scenario}/{nb_agents}Agents",
                                                                                                    scenario = scenario, nb_agents =  nb_agents, 
                                                                                                    city_Intids = city_Intids)

    Totaluncertainty, Hourlyuncertainty, Dailyuncertainty, Monthlyuncertainty, JoinedTable = create_uncertainty_table(modelruns,
                                                                            outcomevarstotal, 
                                                                            outcomevars_hourly, 
                                                                            outcomevars_daily, 
                                                                            outcomevars_monthly, 
                                                                            uncertaintytype="PopSampleUncertainty")

    RestructureJoinedTable(JoinedTable, scenario, nb_agents, uncertaintytype="PopSampleUncertainty")


#############################################################
### behavior sampling uncertainty: Modal Choice, Behavior Choice
#############################################################

if "BehaviorSampleUncertainty" in uncertaintytypes:
    modelruns = [445545, 757283, 229107,107744, 943146]
    path_data = f"D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/UncertaintyAnalysis/samemodelrun"

    outcomevarstotal, outcomevars_hourly, outcomevars_daily, outcomevars_monthly = CollectValsForRuns(modelruns = modelruns, 
                                                                                                    path_data = path_data + f"/{scenario}/{nb_agents}Agents",
                                                                                                    scenario = scenario, nb_agents =  nb_agents, 
                                                                                                    city_Intids = city_Intids)

    Totaluncertainty, Hourlyuncertainty, Dailyuncertainty, Monthlyuncertainty, JoinedTable = create_uncertainty_table(modelruns,
                                                                                                        outcomevarstotal, 
                                                                                                        outcomevars_hourly, 
                                                                                                        outcomevars_daily, 
                                                                                                        outcomevars_monthly, 
                                                                                                        uncertaintytype="BehaviorSampleUncertainty")

    RestructureJoinedTable(JoinedTable, scenario, nb_agents, uncertaintytype="BehaviorSampleUncertainty")


###########################################################
### Pop size uncertainty
###########################################################

if "PopSizeUncertainty" in uncertaintytypes:
    Popsizes = [21750, 43500]
    path_data = "D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/UncertaintyAnalysis/"
    
    outcomevarnames = ["Personal NO2 Exposure unfiltered","Personal NO2 Exposure w. I/O Filter", "Transport MET", "Walk Share", "Bike Share", "Drive Share", "Transit Share", "Traffic Volume", "NO2 (µg/m3)"]

    outcomevarstotals, outcomevars_hourlys, outcomevars_dailys, outcomevars_monthlys = [], [], [], []
    for nb_agents in Popsizes:
        Totaluncertainty = pd.read_csv(path_data + f"/PopSampleUncertainty_{scenario}_{nb_agents}_Total.csv")
        outcomevarstotals.append(Totaluncertainty.loc[Totaluncertainty["modelruns"] =="Mean Value"].iloc[:,1:].values[0].tolist() )
        Hourlyuncertainty = pd.read_csv(path_data + f"/PopSampleUncertainty_{scenario}_{nb_agents}_Hourly.csv")
        hourvals = [Hourlyuncertainty.loc[Hourlyuncertainty["modelruns"] =="Mean Value", [f"{outcomevarname}_H{hour}" for hour in range(24)]].values[0].tolist() for outcomevarname in outcomevarnames]
        outcomevars_hourlys.append(hourvals)
        Dailyuncertainty = pd.read_csv(path_data + f"/PopSampleUncertainty_{scenario}_{nb_agents}_Daily.csv")
        dailyvals = [Dailyuncertainty.loc[Dailyuncertainty["modelruns"] =="Mean Value", [f"{outcomevarname}_D{day}" for day in range(7)]].values[0].tolist() for outcomevarname in outcomevarnames]
        outcomevars_dailys.append(dailyvals )
        Monthlyuncertainty = pd.read_csv(path_data + f"/PopSampleUncertainty_{scenario}_{nb_agents}_Monthly.csv")
        monthlyvals = [Monthlyuncertainty.loc[Monthlyuncertainty["modelruns"] =="Mean Value", [f"{outcomevarname}_M{month}" for month in range(4)]].values[0].tolist() for outcomevarname in outcomevarnames]   
        outcomevars_monthlys.append(monthlyvals)
    
    print(outcomevarstotals)
    print(outcomevars_hourlys)
    print(outcomevars_dailys)
    print(outcomevars_monthlys)
    
    
    outcomevarstotal, outcomevars_hourly, outcomevars_daily, outcomevars_monthly = [], [], [], []
    for outcomeidx in range(len(outcomevarnames)):
        outcometot, outcomehour, outcomeday, outcomemonth = [], [], [], []
        for popidx in range(len(Popsizes)):
            print(outcomeidx, popidx)
            print(outcomevarstotals[popidx][outcomeidx])
            outcometot.append(outcomevarstotals[popidx][outcomeidx])
            outcomehour.append(outcomevars_hourlys[popidx][outcomeidx])
            outcomeday.append(outcomevars_dailys[popidx][outcomeidx])
            outcomemonth.append(outcomevars_monthlys[popidx][outcomeidx])
        print(outcometot)
        outcomevarstotal.append(outcometot)
        outcomevars_hourly.append(outcomehour)
        outcomevars_daily.append(outcomeday)
        outcomevars_monthly.append(outcomemonth)
    
    print(outcomevarstotal)
    print(outcomevars_hourly)
    print(outcomevars_daily)
    print(outcomevars_monthly)
    
    
    Totaluncertainty, Hourlyuncertainty, Dailyuncertainty, Monthlyuncertainty, JoinedTable = create_uncertainty_table(Popsizes,
                                                                            outcomevarstotal, 
                                                                            outcomevars_hourly, 
                                                                            outcomevars_daily, 
                                                                            outcomevars_monthly, 
                                                                            uncertaintytype="PopSizeUncertainty")

    RestructureJoinedTable(JoinedTable, scenario, nb_agents = "all", uncertaintytype="PopSizeUncertainty")
    
    
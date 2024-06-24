import matplotlib.pyplot as plt
import pandas as pd
import os
import seaborn as sns
import ast
import datetime
from pycirclize import Circos
import numpy as np
from matplotlib.lines import Line2D
####################################################


def HourlySplitPerX(data, x, titlesuffix="", filesuffix=""):
            g = sns.FacetGrid(data, col=x, hue="mode_of_transport", col_wrap=4, height=4)
            g.map(sns.lineplot, "hour", "counts").add_legend()
            g.set_axis_labels("Hour", "Counts")
            g.set_titles("{col_name}"+titlesuffix)
            plt.savefig(path_data+f"/{scenario}/{nb_agents}Agents/ModalSplit/ModalSplitViz/"+f"{scenario}_hourly_modal_split_per_{x}_{modelrun}{filesuffix}.png", dpi=600)

def CreateFractionPerOneVar(df, var):
            strat_counts = df.groupby([var, 'mode_of_transport'])['counts'].mean().reset_index()
            tot_counts = strat_counts.groupby(var)['counts'].sum().reset_index()
            merged = pd.merge(strat_counts, tot_counts, on=var, suffixes=('', '_total'))
            merged['fraction'] = (merged['counts'] / merged['counts_total']) * 100
            return merged
        
def stackedBarChart(data, stratvar, y, xlabel, filesuffix = "", nrdecimal = 2, intlabel = False):
            data_pivot = data.pivot(index=stratvar, columns='mode_of_transport', values=y)
            data_pivot = data_pivot.fillna(0)
            ax = data_pivot.plot(kind='bar', stacked=True, figsize=(10, 6))
            plt.xlabel(xlabel)
            plt.ylabel("Percentage of Trips (%)")
            for c in ax.containers:
                labels = [v.get_height() if v.get_height() > 0 else '' for v in c]
                if intlabel:
                    ax.bar_label(c, labels=[int(round(label, 0)) for label in labels], label_type='center')
                else:
                    ax.bar_label(c, labels=[round(label, nrdecimal) for label in labels], label_type='center')
            plt.legend(title="Mode of Transport", bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.tight_layout()
            plt.savefig(path_data+f"/{scenario}/{nb_agents}Agents/ModalSplit/ModalSplitViz/"+f"{scenario}_{stratvar}_modal_split_{modelrun}{filesuffix}.png", dpi=600)        



def plotCircosModalSplit_Timeunits(aggmodalsplit, MSperc_hourmin, MSperc_hourmax, MSperc_hourstep,
                                   MSperc_monthmin, MSperc_monthmax, MSperc_monthstep,
                                   MSabs_hourmin, MSabs_hourmax, MSabs_hourstep,
                                   MSabs_monthmin, MSabs_monthmax, MSabs_monthstep,
                                   suffix = None, abs = "line", perc = "line"):
        outerringdict = {"Hours": 23.4, "Weekdays": 6.4, "Timeunits": 1,"Months": 3.4, 
                        "Total": 0.6
                        }
        outerringdict_xvalues = {
            "Hours": list(range(24)) ,
            "Weekdays": list(range(7)),  # Convert to numeric indices
            "Months": list(range(4)),     # Convert to numeric indices
            "Total": [0]
        }
        outerringdict_labels = {
            "Hours": [f"{x}:00" for x in range(24)] + [""],
            "Weekdays":days_order + [""], 
            "Months": ["January", "April", "July", "October"] + [""],
            "Total": ["Mean"] + [""]
        }

        sectorrows = {"Hours": [f"hour {hour}" for hour in range(24)],
                        "Weekdays": [f"weekday {day}" for day in days_order],
                        "Months": [f"month {month}" for month in [1,4,7,10]],
                        "Total": ["total"]
                    }
        modes = ["bike", "drive", "transit", "walk"]                    
        modecolors = {"bike": "blue", "drive": "red", "transit": "green", "walk": "orange"}
        
        
        axiscol = "dimgray"
        gridcol = "lightgrey"
        axiswidth = 1.3
        # Create Circos plot
        circos = Circos(outerringdict, space=20)

        for sector in circos.sectors:
            print(sector.name)
            if sector.name == "Timeunits":
                # Plot sector name
                MS_perc = sector.add_track((65, 100), r_pad_ratio=0.1)
                MS_perc.axis(ec = "none")
                MS_perc.text("mode (%)", x = MS_perc.start, color="black", adjust_rotation=True, orientation="vertical" ,size=14)

                MS_abs = sector.add_track((20, 55), r_pad_ratio=0.1)
                MS_abs.axis(ec = "none")
                MS_abs.text("mode (abs)", x = MS_abs.start, color="black", adjust_rotation=True, orientation="vertical" ,size=14)

            else:
                # Plot sector name
                sector.text(f"{sector.name}", r=125, size=14)
                sectorrows_df = aggmodalsplit.loc[aggmodalsplit["timeunit"].isin(sectorrows[sector.name])]
                print(sectorrows_df)
                # Create x positions & randomized y values for data plotting
                x = outerringdict_xvalues[sector.name]


                # NO2 line
                MS_perc = sector.add_track((65, 100), r_pad_ratio=0)
                MS_perc.axis(ec = axiscol, lw = axiswidth)
                if sector.name == "Hours":
                    MS_perc_min = MSperc_hourmin
                    MS_perc_max = MSperc_hourmax
                    rangeMSperc =list(np.arange(start=MS_perc_min, stop = MS_perc_max + MSperc_hourstep, step = MSperc_hourstep))

                else:
                    MS_perc_min = MSperc_monthmin
                    MS_perc_max = MSperc_monthmax
                    rangeMSperc =list(np.arange(start=MS_perc_min, stop = MS_perc_max + MSperc_monthstep, step = MSperc_monthstep))
                
                rangeMSperc = [round(val, 1) for val in rangeMSperc]
                MS_perc_max = rangeMSperc[-1]
                print(MS_perc_min, MS_perc_max, MSperc_hourstep, MSperc_monthstep, rangeMSperc)
                MS_perc.yticks(y=rangeMSperc, labels=rangeMSperc,vmin=MS_perc_min, vmax=MS_perc_max, side="left", tick_length=1, label_size=8, label_margin=0.5, line_kws = {"color": axiscol}, text_kws={"color": axiscol})
                for MSpercval in rangeMSperc[1:-1]:
                    MS_perc.line([MS_perc.start, MS_perc.end], [MSpercval, MSpercval], vmin=MS_perc_min, vmax=MS_perc_max, lw=1, ls="dotted", color = gridcol)
                
                # MS_perc.line([MS_perc.start, MS_perc.end], [rangeMSperc[0], rangeMSperc[0]], vmin=MS_perc_min, vmax=MS_perc_max, lw=1.5, color = axiscol)
                # MS_perc.line([MS_perc.start, MS_perc.end], [rangeMSperc[-1], rangeMSperc[-1]], vmin=MS_perc_min, vmax=MS_perc_max, lw=1.5, color = axiscol)
                if perc == "line":
                    if sector.name == "Total":
                        for mode in modes:
                            MS_perc.scatter(x, sectorrows_df[f"{mode}fraction"].values, vmin=MS_perc_min, vmax=MS_perc_max,lw=2, color=modecolors[mode])
                    else:
                        for mode in modes:
                            MS_perc.line(x, sectorrows_df[f"{mode}fraction"].values, vmin=MS_perc_min, vmax=MS_perc_max,lw=2, color=modecolors[mode])
                elif perc == "stackedbar":
                    additivesectorvals = sectorrows_df.copy()
                    for count, mode in enumerate(modes):
                        additivesectorvals[f"{mode}fraction"] = sectorrows_df[[f"{m}fraction" for m in modes[count:]]].sum(axis=1)
                        additivesectorvals[f"{mode}fraction"] = additivesectorvals[f"{mode}fraction"].round(1)
                    for mode in modes:
                            MS_perc.bar(x, additivesectorvals[f"{mode}fraction"].values, width=0.4 , align= "edge", vmin=MS_perc_min, vmax=MS_perc_max, lw=2, color = modecolors[mode])
                            
                MS_perc.xticks_by_interval(
                    1,
                    label_size=8,
                    label_orientation="vertical",
                    label_formatter=lambda v: f"{outerringdict_labels[sector.name][v]}",
                    line_kws={"lw": axiswidth, "color": axiscol},
                    text_kws={"color": axiscol},
                    
                )
                
                print("plotting abs")
                # Plot points
                MS_abs = sector.add_track((20, 55), r_pad_ratio=0)
                MS_abs.axis(ec = axiscol, lw = axiswidth)
                if sector.name == "Hours":
                    MS_abs_min = MSabs_hourmin
                    MS_abs_max = MSabs_hourmax
                    rangeMSabs =list(np.arange(start=MS_abs_min, stop = MS_abs_max + MSabs_hourstep, step = MSabs_hourstep))
                else:
                    MS_abs_min = MSabs_monthmin
                    MS_abs_max = MSabs_monthmax
                    rangeMSabs =list(np.arange(start=MS_abs_min, stop = MS_abs_max + MSabs_monthstep, step = MSabs_monthstep))
                
                rangeMSabs = [int(val) for val in rangeMSabs]
                MS_abs_max = rangeMSabs[-1]
                MS_abs.yticks(y=rangeMSabs, labels=rangeMSabs,vmin=MS_abs_min, vmax=MS_abs_max,  side="left", tick_length=1, label_size=8, label_margin=0.5, line_kws = {"color": axiscol}, text_kws={"color": axiscol})
                for MSabsval in rangeMSabs[1:-1]:
                    MS_abs.line([MS_abs.start, MS_abs.end], [MSabsval, MSabsval], vmin=MS_abs_min, vmax=MS_abs_max,  lw=1, ls="dotted", color = gridcol)
                
                #MS_abs.line([MS_abs.start, MS_abs.end], [rangeMSabs[0], rangeMSabs[0]], vmin=MS_abs_min, vmax=MS_abs_max, lw=1.5, color = axiscol)
                #MS_abs.line([MS_abs.start, MS_abs.end], [rangeMSabs[-1], rangeMSabs[-1]], vmin=MS_abs_min, vmax=MS_abs_max, lw=1.5, color = axiscol)
                if abs == "line":
                    if sector.name == "Total":
                        for mode in modes:
                            MS_abs.scatter(x, sectorrows_df[mode].values, vmin=MS_abs_min, vmax=MS_abs_max, lw=2, color = modecolors[mode])

                    else:
                        for mode in modes:
                            MS_abs.line(x, sectorrows_df[mode].values, vmin=MS_abs_min, vmax=MS_abs_max, lw=2, color = modecolors[mode])
                elif abs == "stackedbar":
                    additivesectorvals = sectorrows_df.copy()
                    for count, mode in enumerate(modes):
                        additivesectorvals[mode] = sectorrows_df[modes[count:]].sum(axis=1)
                    for mode in modes:
                            MS_abs.bar(x, additivesectorvals[mode].values, width=0.4 , align= "edge",  vmin=MS_abs_min, vmax=MS_abs_max, lw=2, color = modecolors[mode])

                MS_abs.xticks_by_interval(1, show_label=False, line_kws={"lw": 1.5, "color": axiscol})
                

        # Create legend
        legend_elements = []
        for mode in modes:
            legend_elements.append(Line2D([0], [0], color=modecolors[mode], lw=1.5, label=f"{mode.capitalize().replace('_', ' ')}"))
        figure = circos.plotfig(dpi=600)
        figure.legend(handles=legend_elements, loc='lower right', ncol=1, title = "Mode of Transport", title_fontsize = "12", fontsize = "10")
        figure.savefig(f"ModeCirclePlot_with_Legend{suffix}.png", dpi=600)

def calc_min_max(df, timeunit_contains, stratvals, colprefix ="", colsuffix = "", roundval = 2):
        min_val = np.min([df.loc[df["timeunit"].str.contains(timeunit_contains), f"{colprefix}{val}{colsuffix}"].min() for val in stratvals])
        max_val = np.max([df.loc[df["timeunit"].str.contains(timeunit_contains), f"{colprefix}{val}{colsuffix}"].max() for val in stratvals])
        step = ((max_val - min_val)/5).round(roundval)
        min_val = (min_val - step).round(roundval)  
        if min_val < 0 or min_val == -0.0:
            min_val = 0
        max_val = (max_val + step).round(roundval)
        step = ((max_val - min_val)/4).round(roundval)
        if step == 0:
            min_val = np.min([df.loc[df["timeunit"].str.contains(timeunit_contains), f"{colprefix}{val}{colsuffix}"].min() for val in stratvals]).round(4)
            max_val = np.max([df.loc[df["timeunit"].str.contains(timeunit_contains), f"{colprefix}{val}{colsuffix}"].max() for val in stratvals]).round(4)      
            step = ((max_val - min_val)/4).round(4)    
            min_val = (min_val - step).round(4)  
            max_val = (max_val + step).round(4)
            step = ((max_val - min_val)/4).round(4)
        return min_val, max_val, step

##########################################
nb_agents = 21750  #87000 = 10%, 43500 = 5%, 21750 = 2.5%, 8700 = 1%
path_data = "D:\PhD EXPANSE\Data\Amsterdam\ABMRessources\ABMData\ModelRuns"
os.chdir(path_data)

# scenario = "SpeedInterv"
scenario = "StatusQuo"
# scenario = "PedStrWidth"
# scenario = "RetaiDnsDiv"
# scenario = "LenBikRout"
# scenario = "PedStrWidthOutskirt"
# scenario = "PedStrWidthCenter"
# scenario = "AmenityDnsExistingAmenityPlaces"
# scenario  = "AmenityDnsDivExistingAmenityPlaces"
# scenario = "StatusQuoAllVars"
# scenario = "PedStrLen"
# scenario ="PedStrWidthOutskirt"
# scenario ="PedStrWidthCenter"
# scenario = "PedStrLenCenter"
# scenario = "PedStrLenOutskirt"
scenario = "PrkPriceInterv"

# identify model run for scenario
experimentoverview = pd.read_csv("D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/ExperimentOverview.csv")
modelruns = experimentoverview.loc[experimentoverview["Experiment"] == scenario, "Model Run"].values
# bestStatusQuo = 481658
modelruns = [708658]
modelruns = [107935, 805895]
# modelruns = [381609]

days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

viztype = [
        # "singleIntervention", 
        "CirclePlot",
        # "statusquocomparison", 
        # "multipleRunComparison",
        # "extentvisualization",
        # "extentcomparison"
        ]

extentname = "parkingprice_interventionextent"

if not os.path.exists(path_data+f"/{scenario}/{nb_agents}Agents/ModalSplit/ModalSplitViz"):
      # Create the directory
      os.mkdir(path_data+f"/{scenario}/{nb_agents}Agents/ModalSplit/ModalSplitViz")
destination = path_data+f"/{scenario}/{nb_agents}Agents/ModalSplit/ModalSplitViz"
      
if "singleIntervention" in viztype:
    for modelrun in modelruns:
        print(f"Processing model run {modelrun}")
        modalsplit_df =  pd.read_csv(f"{scenario}/{nb_agents}Agents/ModalSplit/ModalSplitLog{nb_agents}_{scenario}_{modelrun}.csv")
        modalsplit_df.drop(columns=['date', "day"], inplace=True)
        modalsplit_df['weekday'] = pd.Categorical(modalsplit_df['weekday'], categories=days_order, ordered=True)
        melted_interv = pd.melt(modalsplit_df, id_vars=['hour', 'weekday', 'month'], var_name='mode_of_transport', value_name='counts').reset_index()
        melted_interv['counts'].fillna(0, inplace=True)
        print(melted_interv.head())
        melted_interv.to_csv(f"{scenario}/{nb_agents}Agents/ModalSplit/ModalSplitViz/ModalSplitLogMelted{nb_agents}_{scenario}_{modelrun}.csv", index=False)

        # Plot hourly modal split per day of the week
        mean_per_day = melted_interv.groupby(['weekday', 'hour', 'mode_of_transport'])['counts'].mean().reset_index()
        HourlySplitPerX(mean_per_day, "weekday")
        
        # Plot hourly modal split per month
        mean_per_month = melted_interv.groupby(['month', 'hour', 'mode_of_transport'])['counts'].mean().reset_index()
        HourlySplitPerX(mean_per_month, "month", titlesuffix = " Month")
    
        # Plot monthly modal split in stacked bar chart
        merged = CreateFractionPerOneVar(melted_interv, "month")
        stackedBarChart(data = merged, stratvar = "month", y = "fraction", xlabel = "Month", filesuffix = "")
       
        # Plot weekdaily modal split in stacked bar chart
        merged = CreateFractionPerOneVar(melted_interv, "weekday")
        stackedBarChart(data = merged, stratvar = "weekday", y = "fraction", xlabel = "Weekday", filesuffix = "")

        # Plot hourly modal split in stacked bar chart
        merged = CreateFractionPerOneVar(melted_interv, "hour")
        stackedBarChart(data = merged, stratvar = "hour", y = "fraction", xlabel = "Hour", filesuffix = "", intlabel=True)

if "CirclePlot" in viztype:
    for modelrun in modelruns:
        os.chdir(path_data)
        print("Creating an aggregate dataset")
        modalsplit_df =  pd.read_csv(f"{scenario}/{nb_agents}Agents/ModalSplit/ModalSplitLog{nb_agents}_{scenario}_{modelrun}.csv")
        modalsplit_df.drop(columns=['date', "day"], inplace=True)
        modalsplit_df['weekday'] = pd.Categorical(modalsplit_df['weekday'], categories=days_order, ordered=True)
        outcomevars = ["bike", "drive", "transit", "walk"] 
        modalsplit_df[outcomevars] = modalsplit_df[outcomevars].fillna(0)
        
        print(modalsplit_df.head())
        os.chdir(destination)
        
        timeunits = ["hour", "weekday", "month"]
        outcomevars = ["bike", "drive", "transit", "walk"] 

        aggmodalsplit = modalsplit_df[outcomevars].mean().values
        aggmodalsplit = pd.DataFrame([["total"]+list(aggmodalsplit)], columns=["timeunit"]+outcomevars)
        print(aggmodalsplit)
        for timeunit in timeunits:
            timeunitexposure = pd.DataFrame(modalsplit_df[[timeunit]+outcomevars].groupby(timeunit, as_index=False).mean())
            timeunitexposure["timeunit"] = [f"{timeunit} {unit}" for unit in timeunitexposure[timeunit]]
            print(timeunitexposure.head())
            aggmodalsplit = pd.concat([aggmodalsplit, timeunitexposure[["timeunit"]+outcomevars]], axis=0, ignore_index=True)
            print(aggmodalsplit.head(30))   
        
        aggmodalsplit.index = aggmodalsplit["timeunit"]
        
        aggmodalsplit["Allmodes"] = aggmodalsplit["bike"] + aggmodalsplit["drive"] + aggmodalsplit["transit"] + aggmodalsplit["walk"]
        aggmodalsplit["bikefraction"] = (aggmodalsplit["bike"] / aggmodalsplit["Allmodes"]) 
        aggmodalsplit["drivefraction"] = (aggmodalsplit["drive"] / aggmodalsplit["Allmodes"])
        aggmodalsplit["transitfraction"] = (aggmodalsplit["transit"] / aggmodalsplit["Allmodes"]) 
        aggmodalsplit["walkfraction"] = (aggmodalsplit["walk"] / aggmodalsplit["Allmodes"]) 
        print(aggmodalsplit.head(30))   

        aggmodalsplit.to_csv(f"ModalSplit_A{nb_agents}_{scenario}_{modelrun}_aggregate.csv", index=False)
        
        print("Creating Circos plot")
        os.chdir(destination)
        aggmodalsplit = pd.read_csv(f"ModalSplit_A{nb_agents}_{scenario}_{modelrun}_aggregate.csv")
        timeunits = ["hour", "weekday", "month"]
        outcomevars = ["bike", "drive", "transit", "walk"] 

        modes = ["bike", "drive", "transit", "walk"]
        MSperc_monthmin, MSperc_monthmax, MSperc_monthstep = calc_min_max(aggmodalsplit,  colsuffix = "fraction", 
                                                                        timeunit_contains = "weekday", stratvals = modes,
                                                                        roundval=1)
        MSperc_hourmin, MSperc_hourmax, MSperc_hourstep = calc_min_max(aggmodalsplit,  colsuffix = "fraction", 
                                                                        timeunit_contains = "hour", stratvals = modes,
                                                                        roundval=1)     
        MSabs_monthmin, MSabs_monthmax, MSabs_monthstep = calc_min_max(aggmodalsplit,  colsuffix = "", 
                                                                        timeunit_contains = "weekday", stratvals = modes,
                                                                        roundval=-2)
        MSabs_hourmin, MSabs_hourmax, MSabs_hourstep = calc_min_max(aggmodalsplit,  colsuffix = "",
                                                                        timeunit_contains = "hour", stratvals = modes,
                                                                        roundval=-2)
        print(MSperc_monthmin, MSperc_monthmax, MSperc_monthstep)
        print(MSperc_hourmin, MSperc_hourmax, MSperc_hourstep)
        print(MSabs_monthmin, MSabs_monthmax, MSabs_monthstep)
        print(MSabs_hourmin, MSabs_hourmax, MSabs_hourstep)                                                                       
                                         
                                         
        plotCircosModalSplit_Timeunits(aggmodalsplit, MSperc_hourmin = MSperc_hourmin, MSperc_hourmax = MSperc_hourmax, MSperc_hourstep=MSperc_hourstep,
                                       MSperc_monthmin = MSperc_monthmin, MSperc_monthmax = MSperc_monthmax,MSperc_monthstep=MSperc_monthstep,
                                       MSabs_hourmin = MSabs_hourmin, MSabs_hourmax = MSabs_hourmax,MSabs_hourstep=MSabs_hourstep,
                                       MSabs_monthmin = MSabs_monthmin, MSabs_monthmax = MSabs_monthmax,MSabs_monthstep=MSabs_monthstep,
                                       suffix = f"_{scenario}_{modelrun}_AllLine", abs = "line")

        aggmodalsplit["totaltrips"] = aggmodalsplit["bike"] + aggmodalsplit["drive"] + aggmodalsplit["transit"] + aggmodalsplit["walk"]
        MSabs_monthmin, MSabs_monthmax, MSabs_monthstep = calc_min_max(aggmodalsplit,  timeunit_contains = "weekday", stratvals = ["totaltrips"],
                                                                        roundval=-2)
        MSabs_hourmax = np.max([aggmodalsplit.loc[aggmodalsplit["timeunit"].str.contains("hour"), "totaltrips"].max()])
        
        print(MSabs_hourmin, MSabs_hourmax, MSabs_hourstep)   

        plotCircosModalSplit_Timeunits(aggmodalsplit, MSperc_hourmin = MSperc_hourmin, MSperc_hourmax = MSperc_hourmax, MSperc_hourstep=MSperc_hourstep,
                                       MSperc_monthmin = MSperc_monthmin, MSperc_monthmax = MSperc_monthmax,MSperc_monthstep=MSperc_monthstep,
                                       MSabs_hourmin = 0, MSabs_hourmax = MSabs_hourmax,MSabs_hourstep=3000,
                                       MSabs_monthmin = 0, MSabs_monthmax = MSabs_monthmax,MSabs_monthstep=2000,
                                       suffix = f"_{scenario}_{modelrun}_AbsStackedbar", abs = "stackedbar")


        aggmodalsplit["bikefraction"] = aggmodalsplit["bikefraction"] * 100
        aggmodalsplit["drivefraction"] = aggmodalsplit["drivefraction"] * 100
        aggmodalsplit["transitfraction"] = aggmodalsplit["transitfraction"] * 100
        aggmodalsplit["walkfraction"] = aggmodalsplit["walkfraction"] * 100

        plotCircosModalSplit_Timeunits(aggmodalsplit, MSperc_hourmin = 0, MSperc_hourmax = 100, MSperc_hourstep=20,
                                       MSperc_monthmin = 0, MSperc_monthmax = 100,MSperc_monthstep=20,
                                       MSabs_hourmin = 0, MSabs_hourmax = MSabs_hourmax,MSabs_hourstep=3000,
                                       MSabs_monthmin = 0, MSabs_monthmax = MSabs_monthmax,MSabs_monthstep=2000,
                                       suffix = f"_{scenario}_{modelrun}_AllStackedbar", abs = "stackedbar", perc="stackedbar")
        
    
if "statusquocomparison" in viztype:
    for modelrun in modelruns:
        modalsplit_df =  pd.read_csv(f"{scenario}/{nb_agents}Agents/ModalSplit/ModalSplitLog{nb_agents}_{scenario}_{modelrun}.csv")
        modalsplit_df.drop(columns=['date', "day"], inplace=True)
        modalsplit_df['weekday'] = pd.Categorical(modalsplit_df['weekday'], categories=days_order, ordered=True)
        melted_interv = pd.melt(modalsplit_df, id_vars=['hour', 'weekday', 'month'], var_name='mode_of_transport', value_name='counts').reset_index()
        melted_interv['counts'].fillna(0, inplace=True)
        mean_per_day_interv = melted_interv.groupby(['weekday', 'hour', 'mode_of_transport'])['counts'].mean().reset_index()
        mean_per_month_interv = melted_interv.groupby(['month', 'hour', 'mode_of_transport'])['counts'].mean().reset_index()

        statQuo_df = pd.read_csv(f"StatusQuo/{nb_agents}Agents/ModalSplit/ModalSplitLog{nb_agents}_StatusQuo_{bestStatusQuo}.csv")
        statQuo_df.drop(columns=['date', "day"], inplace=True)
        statQuo_df['weekday'] = pd.Categorical(statQuo_df['weekday'], categories=days_order, ordered=True)
        melted_statquo = pd.melt(statQuo_df, id_vars=['hour', 'weekday', 'month'], var_name='mode_of_transport', value_name='counts').reset_index()
        melted_statquo['counts'].fillna(0, inplace=True)
        mean_per_day_statquo = melted_statquo.groupby(['weekday', 'hour', 'mode_of_transport'])['counts'].mean().reset_index()
        mean_per_month_statquo = melted_statquo.groupby(['month', 'hour', 'mode_of_transport'])['counts'].mean().reset_index()

        # # Plot hourly modal split per day of the week
        # sns.set(style="whitegrid")
        # g = sns.FacetGrid(mean_per_day_combined, col="weekday", hue="mode_of_transport", col_wrap=4, height=4, palette="tab10")
        # g.map_dataframe(sns.lineplot, x="hour", y="counts", style="type", dashes={'Intervention': '', 'Status Quo': (2, 2)}, markers=False)        
        # g.map(sns.lineplot, "hour", "counts").add_legend()
        # g.set_axis_labels("Hour", "Counts")
        # g.set_titles("{col_name}")
        # plt.savefig(path_data+f"/{scenario}/{nb_agents}Agents/ModalSplit/ModalSplitViz/"+f"{scenario}_StatusQuo_hourly_modal_split_per_day_{modelrun}.png", dpi=600)

        # # Plot hourly modal split per day of the week with overlay
        # sns.set(style="whitegrid")
        # palette = sns.color_palette("tab10")
        # g = sns.FacetGrid(mean_per_day_statquo, col="weekday", hue="mode_of_transport", col_wrap=4, height=4, palette=palette)
        # g.map(sns.lineplot, "hour", "counts", linestyle='--', linewidth=2)
        # g.add_legend()
        # g.set_axis_labels("Hour", "Counts")
        # g.set_titles("{col_name}")

        # # for ax in g.axes.flat:
        # #     weekday = ax.get_title().split('=')[-1].strip()
        # #     data_interv = mean_per_day_interv[mean_per_day_interv['weekday'] == weekday]
        # #     for mode in data_interv['mode_of_transport'].unique():
        # #         sns.lineplot(data=data_interv[data_interv['mode_of_transport'] == mode], x="hour", y="counts", ax=ax, linestyle='--', linewidth=2, label=mode)

        # plt.savefig(path_data+f"/{scenario}/{nb_agents}Agents/ModalSplit/ModalSplitViz/"+f"{scenario}_StatusQuo_hourly_modal_split_per_day_{modelrun}.png", dpi=600)
        # plt.close()  

        # Plot hourly modal split per day of the week with overlay
        sns.set(style="whitegrid")
        palette = sns.color_palette("tab10")

        g = sns.FacetGrid(mean_per_day_interv, col="weekday", hue="mode_of_transport", col_wrap=4, height=4, palette=palette)
        g.map(sns.lineplot, "hour", "counts", linestyle='-', linewidth=2)
        g.set_axis_labels("Hour", "Counts")
        g.set_titles("{col_name}")

        for ax in g.axes.flat:
            weekday = ax.get_title().split('=')[-1].strip()
            data_statquo = mean_per_day_statquo[mean_per_day_statquo['weekday'] == weekday]
            for mode in data_statquo['mode_of_transport'].unique():
                sns.lineplot(data=data_statquo[data_statquo['mode_of_transport'] == mode], x="hour", y="counts", ax=ax, linestyle='--', linewidth=2)

        # Create a single legend for both intervention and status quo
        handles, labels = ax.get_legend_handles_labels()
        intervention_handles = [h for h, l in zip(handles, labels) if 'Intervention' in l]
        status_quo_handles = [h for h, l in zip(handles, labels) if 'Status Quo' in l]
        plt.savefig(path_data+f"/{scenario}/{nb_agents}Agents/ModalSplit/ModalSplitViz/"+f"{scenario}_StatusQuo_hourly_modal_split_per_day_{modelrun}.png", dpi=600)


        # # Plot hourly modal split per month
        # g = sns.FacetGrid(mean_per_month_interv, col="month", hue="mode_of_transport", col_wrap=4, height=4)
        # g.map(sns.lineplot, "hour", "counts").add_legend()
        # g.set_axis_labels("Hour", "Counts")
        # g.set_titles("{col_name} Month")
        # plt.savefig(path_data+f"/{scenario}/{nb_agents}Agents/ModalSplit/ModalSplitViz/"+f"{scenario}_hourly_modal_split_per_month_{modelrun}.png", dpi=600)
    
        # melted_interv = melted_interv.sort_values(by='mode_of_transport')
        # melted_statquo = melted_statquo.sort_values(by='mode_of_transport')

        # melted_interv["hour"] = [int(x[0:2]) for x in  melted_interv["hour"]]
        # melted_interv["counts"] = [float(x) for x in  melted_interv["counts"]]

        # melted_statquo["hour"] = [int(x[0:2]) for x in  melted_statquo["hour"]]
        # melted_statquo["counts"] = [float(x) for x in  melted_statquo["counts"]]

        # # combined_melted = pd.concat([melted_scenario1, melted_scenario2], keys=['Scenario 1', 'Scenario 2'])
        # # combined_melted["hour"] = [int(x[0:2]) for x in  combined_melted["hour"]]
        # # combined_melted["counts"] = [float(x) for x in  combined_melted["counts"]]

        # sns.set(style="whitegrid")
        # plt.figure(figsize=(10, 6))
        # sns.lineplot(x='hour', y='counts', hue='mode_of_transport', style='mode_of_transport', dashes=[(2, 2), (2, 2), (2,2), (2,2)], data=melted_statquo, alpha=0.5, legend=False)


        # # Line plot for intervention with continuous lines
        # sns.lineplot(x='hour', y='counts', hue='mode_of_transport', style='mode_of_transport', data=melted_interv, dashes=False, markers=False)

        # plt.plot([], [], ' ', label="dashed lines = status quo")


        # # Adjust layout and display the plot
        # # Customize plot
        # plt.xlabel("Hour")
        # plt.ylabel("Count")
        # plt.title(f"Mode of Transport split of the {scenario} scenario over time")
        # plt.legend(title="Mode of Transport")
        # plt.savefig(f"ModalSplitLog{nb_agents}_{scenario}.png", dpi=600)
        # plt.show()


if "extentvisualization" in viztype:
    for modelrun in modelruns:
        extent_modalsplit = pd.read_csv(f"{scenario}/{nb_agents}Agents/Tracks/TrackViz/ModalSplit_{scenario}_{modelrun}_{extentname}.csv")
        extent_modalsplit["date"] = [f"{daymonth[0]}-{daymonth[1]}-2019" for daymonth in extent_modalsplit[["Day", "Month"]].values]
        extent_modalsplit['date'] = pd.to_datetime(extent_modalsplit['date'], format='%d-%m-%Y', errors='coerce')
        extent_modalsplit["weekday"] = extent_modalsplit['date'].dt.day_name()
        extent_modalsplit['weekday'] = pd.Categorical(extent_modalsplit['weekday'], categories=days_order, ordered=True)

        #rename Hour to hour
        extent_modalsplit.rename(columns={"Hour": "hour"}, inplace=True)
        
        mean_per_day = extent_modalsplit.groupby(['weekday', 'hour'])[['bike', 'transit', 'walk', 'drive']].mean().reset_index()
        mean_per_month = extent_modalsplit.groupby(['Month', 'hour'])[['bike', 'transit', 'walk', 'drive']].mean().reset_index()

        # arange "bike", "drive", "transit", "walk" to mode of transport column and melt
        mean_per_day = pd.melt(mean_per_day, id_vars=['weekday', 'hour'], var_name='mode_of_transport', value_name='counts').reset_index()
        mean_per_month = pd.melt(mean_per_month, id_vars=['Month', 'hour'], var_name='mode_of_transport', value_name='counts').reset_index()


        HourlySplitPerX(mean_per_day, "weekday", filesuffix = f"_{extentname}")
        HourlySplitPerX(mean_per_month, "Month", titlesuffix = " Month",  filesuffix = f"_{extentname}")


        merged = CreateFractionPerOneVar(mean_per_month, "Month")
        print(merged)
        stackedBarChart(data = merged, stratvar = "Month", y = "fraction", xlabel = "Month", filesuffix = f"_{extentname}")

        merged = CreateFractionPerOneVar(mean_per_day, "weekday")
        stackedBarChart(data = merged, stratvar = "weekday", y = "fraction", xlabel = "Weekday", filesuffix = f"_{extentname}")

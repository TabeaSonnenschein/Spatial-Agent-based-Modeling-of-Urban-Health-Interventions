import matplotlib.pyplot as plt
import pandas as pd
import os
import seaborn as sns
import geopandas as gpd
from pycirclize import Circos
import numpy as np
from matplotlib.lines import Line2D
import contextily as cx
from matplotlib_scalebar.scalebar import ScaleBar
from shapely.geometry.point import Point
from itertools import chain

####################################################


def calc_min_max(df, column, timeunit_contains, round_val = 1, hardzero = True, stratvals = None):
        if stratvals is not None:
            origmin_val = np.min([aggexposure.loc[aggexposure["timeunit"].str.contains(timeunit_contains), f"{column}_{val}"].min() for val in stratvals])
            origmax_val = np.max([aggexposure.loc[aggexposure["timeunit"].str.contains(timeunit_contains), f"{column}_{val}"].max() for val in stratvals])
        else:
            origmin_val = np.min([df.loc[df["timeunit"].str.contains(timeunit_contains), column].min()])
            origmax_val = np.max([df.loc[df["timeunit"].str.contains(timeunit_contains), column].max()])
        print(timeunit_contains, column, ": original min",origmin_val, "; original max", origmax_val)
        step = ((origmax_val - origmin_val)/7).round(round_val)
        min_val = (origmin_val - step).round(round_val)  
        if hardzero:
            if min_val < 0:
                min_val = 0
        max_val = (origmax_val + step).round(round_val)
        step = ((max_val - min_val)/5).round(round_val)
        while step == 0:
            round_val += 1
            min_val = np.min([df.loc[df["timeunit"].str.contains(timeunit_contains), column].min()]).round(round_val)
            max_val = np.max([df.loc[df["timeunit"].str.contains(timeunit_contains),column].max()]).round(round_val)      
            step = ((max_val - min_val)/4).round(round_val)    
            min_val = (min_val - step).round(round_val)  
            if hardzero:
                if min_val < 0:
                    min_val = 0
            max_val = (max_val + step).round(round_val)
            step = ((max_val - min_val)/4).round(round_val)
        if round_val == 0:
            min_val = int(min_val)
            max_val = int(max_val)
            step = int(step)
        print(timeunit_contains, column, ": Finalmin",  min_val, ", max", max_val, ", step", step)
        return min_val, max_val, step




def ScatterOverTimeColCategory(timevar, outcomvar, colcategory, showplots, modelrun, df, ylabel = None, collabel = None):
    if ylabel is None:
        ylabel = outcomvar
    if collabel is None:
        collabel = colcategory
    sns.set(style="whitegrid")
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x=timevar, y=outcomvar, hue=colcategory, data=df, alpha=0.4)
    plt.xlabel(timevar)
    plt.ylabel(ylabel)
    plt.title(f"Distribution of {outcomvar} Over Time by {collabel}")
    plt.legend(title=collabel)
    plt.savefig(f'{modelrun}_scatterplot_{outcomvar}_by_{colcategory}_by{timevar}.pdf', dpi = 300)
    if showplots:
        plt.show()
    plt.close()
    

def ScatterOverTimeColContinous(timevar, outcomvar, colvar, showplots, modelrun, df, ylabel = None, collabel = None):
    if ylabel is None:
        ylabel = outcomvar
    if collabel is None:
        collabel = colvar
    sns.set(style="whitegrid")
    color_map = sns.color_palette("RdYlGn_r", as_cmap=True)
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x=timevar, y=outcomvar, hue=colvar, data=df, alpha=0.4, palette=color_map)
    plt.xlabel(timevar)
    plt.ylabel(ylabel)
    plt.title(f"Distribution of {outcomvar} Over Time by {collabel}")
    plt.legend(title=collabel)
    plt.savefig(f'{modelrun}_scatterplot_{outcomvar}_by_{colvar}_by{timevar}.pdf', dpi = 300)
    if showplots:
        plt.show()
    plt.close()
    

def LineOverTimeColCategory(timevar, outcomvar, colcategory, showplots, modelrun, df, ylabel = None, collabel = None):
    if ylabel is None:
        ylabel = outcomvar
    if collabel is None:
        collabel = colcategory
    sns.set(style="whitegrid")
    plt.figure(figsize=(10, 6))
    sns.lineplot(x=timevar, y=outcomvar, hue=colcategory, data=df, alpha=0.4)
    plt.xlabel(timevar)
    plt.ylabel(ylabel)
    plt.title(f"Distribution of {outcomvar} Over Time by {collabel}")
    plt.legend(title=collabel)
    plt.savefig(f'{modelrun}_lineplot_{outcomvar}_by_{colcategory}_by{timevar}.pdf', dpi = 300)
    if showplots:
        plt.show()
    plt.close()
    sns.set(style="whitegrid")
    plt.figure(figsize=(10, 6))
    sns.lineplot(x=timevar, y=outcomvar, hue=colcategory, data=df, alpha=0.4, errorbar=None)
    plt.xlabel(timevar)
    plt.ylabel(ylabel)
    plt.title(f"Distribution of {outcomvar} Over Time by {collabel}")
    plt.legend(title=collabel)
    plt.savefig(f'{modelrun}_lineplot_{outcomvar}_by_{colcategory}_by{timevar}_noerrorbar.pdf', dpi = 300)
    if showplots:
        plt.show()
    plt.close()

def LineOverTimeColContinous(timevar, outcomvar, colvar, showplots, modelrun,df,  ylabel = None, collabel = None):
    if ylabel is None:
        ylabel = outcomvar
    if collabel is None:
        collabel = colvar
    sns.set(style="whitegrid")
    color_map = sns.color_palette("RdYlGn_r", as_cmap=True)
    plt.figure(figsize=(10, 6))
    sns.lineplot(x=timevar, y=outcomvar, hue=colvar, data=df, alpha=0.4, palette=color_map)
    plt.xlabel(timevar)
    plt.ylabel(ylabel)
    plt.title(f"Distribution of {outcomvar} Over Time by {collabel}")
    plt.legend(title=collabel)
    plt.savefig(f'{modelrun}_lineplot_{outcomvar}_by_{colvar}_by{timevar}.pdf', dpi = 300)
    if showplots:
        plt.show()
    plt.close()
    
    sns.set(style="whitegrid")
    color_map = sns.color_palette("RdYlGn_r", as_cmap=True)
    plt.figure(figsize=(10, 6))
    sns.lineplot(x=timevar, y=outcomvar, hue=colvar, data=df, alpha=0.4, palette=color_map, errorbar=None)
    plt.xlabel(timevar)
    plt.ylabel(ylabel)
    plt.title(f"Distribution of {outcomvar} Over Time by {collabel}")
    plt.legend(title=collabel)
    plt.savefig(f'{modelrun}_lineplot_{outcomvar}_by_{colvar}_by{timevar}_noerrorbar.pdf', dpi = 300)
    if showplots:
        plt.show()
    plt.close()
    

def ViolinOverTimeColCategory(timevar, outcomvar, colcategory, showplots, modelrun,df, ylabel = None, collabel = None):
    if ylabel is None:
        ylabel = outcomvar
    if collabel is None:
        collabel = colcategory
    sns.set(style="whitegrid")
    plt.figure(figsize=(10, 6))
    sns.violinplot(x=timevar, y=outcomvar, hue=colcategory, data=df, linewidth=0, palette="Dark2")
    plt.xlabel(timevar)
    plt.ylabel(ylabel)
    plt.title(f"Distribution of {outcomvar} Over Time by {collabel}")
    plt.legend(title=collabel)
    plt.savefig(f'{modelrun}_violinplot_{outcomvar}_by_{colcategory}_by{timevar}.pdf', dpi = 300)
    if showplots:
        plt.show()
    plt.close()

def ViolinOverTimeColContinous(timevar, outcomvar, colvar, showplots, modelrun, df, ylabel = None, collabel = None):
    if ylabel is None:
        ylabel = outcomvar
    if collabel is None:
        collabel = colvar
    sns.set(style="whitegrid")
    color_map = sns.color_palette("RdYlGn_r", as_cmap=False)
    plt.figure(figsize=(10, 6))
    sns.violinplot(x=timevar, y=outcomvar, hue=colvar, data=df, linewidth=0, palette=color_map)
    plt.xlabel(timevar)
    plt.ylabel(ylabel)
    plt.title(f"Distribution of {outcomvar} Over Time by {collabel}")
    plt.legend(title=collabel)
    plt.savefig(f'{modelrun}_violinplot_{outcomvar}_by_{colvar}_by{timevar}.pdf', dpi = 300)
    if showplots:
        plt.show()
    plt.close()

def PlotVarsInLists(plottypes, timevars, outcomevars, continuousstratvars, categoricalstratvars, df, showplots, modelrun, fullnamedict):
    for plottype in plottypes:
        for outvar in outcomevars:
            for timevar in timevars:
                if plottype == "scatter":
                    for stratvar in continuousstratvars:
                        ScatterOverTimeColContinous(timevar=timevar, outcomvar=outvar, colvar=stratvar, showplots=showplots, modelrun=modelrun, df=df, ylabel=fullnamedict[outvar], collabel=fullnamedict[stratvar])
                    for stratvar in categoricalstratvars:
                        ScatterOverTimeColCategory(timevar=timevar, outcomvar=outvar, colcategory=stratvar, showplots=showplots, modelrun=modelrun, df=df, ylabel=fullnamedict[outvar], collabel=fullnamedict[stratvar])
                elif plottype == "line":
                    for stratvar in continuousstratvars:
                        LineOverTimeColContinous(timevar=timevar, outcomvar=outvar, colvar=stratvar, showplots=showplots, modelrun=modelrun, df=df, ylabel=fullnamedict[outvar], collabel=fullnamedict[stratvar])
                    for stratvar in categoricalstratvars:
                        LineOverTimeColCategory(timevar=timevar, outcomvar=outvar, colcategory=stratvar, showplots=showplots, modelrun=modelrun, df=df, ylabel=fullnamedict[outvar], collabel=fullnamedict[stratvar])
                elif plottype == "violin":
                    for stratvar in continuousstratvars:
                        ViolinOverTimeColContinous(timevar=timevar, outcomvar=outvar, colvar=stratvar, showplots=showplots, modelrun=modelrun, df=df, ylabel=fullnamedict[outvar], collabel=fullnamedict[stratvar])
                    for stratvar in categoricalstratvars:
                        ViolinOverTimeColCategory(timevar=timevar, outcomvar=outvar, colcategory=stratvar, showplots=showplots, modelrun=modelrun, df=df, ylabel=fullnamedict[outvar], collabel=fullnamedict[stratvar])


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
    sns.violinplot(x=stratifier, y=outcomvar, data=df, palette="Dark2")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend()
    plt.title(f'{outcomvar} Distributions per {stratifier}')
    plt.savefig(f'{modelrun}_violinplot_{outcomvar}_by_{stratifier}_withoutTime.pdf', dpi = 300)
    if showplots:
        plt.show()


def plotCircosNO2MET_Timeunits(aggexposure, subgroups, subgroupcolors, 
                               NO2monthmin = 23.5, NO2monthmax = 25, NO2monthstep = 0.5, NO2monthround=1,
                               NO2hourmin=20, NO2hourmax = 30, NO2hourstep = 2, NO2hourround=0,
                               METmonthmin = 0.75, METmonthmax = 1.25, METmonthstep = 0.25, METmonthround=2,
                               METhourmin = 0, METhourmax = 2 , METhourstep = 0.5, METhourround=1,
                               suffix = "", hardzero = True):
        outerringdict = {"Hours": 23, "Weekdays": 6, "Timeunits": 1,"Months": 3, 
                        "Total": 0.4
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
                            
        axiscol = "dimgray"
        gridcol = "lightgrey"
        # Create Circos plot
        circos = Circos(outerringdict, space=13)

        for sector in circos.sectors:
            print(sector.name)
            if sector.name == "Timeunits":
                # Plot sector name
                NO2_track = sector.add_track((65, 100), r_pad_ratio=0.1)
                NO2_track.axis(ec = "none")
                NO2_track.text("NO2(µg/m3)", x = NO2_track.start, color="black", adjust_rotation=True, orientation="vertical" ,size=14)

                MET_track = sector.add_track((25, 60), r_pad_ratio=0.1)
                MET_track.axis(ec = "none")
                MET_track.text("MET*", x = MET_track.start, color="black", adjust_rotation=True, orientation="vertical" ,size=14)

            else:
                # Plot sector name
                sector.text(f"{sector.name}", r=125, size=14)
                sectorrows_df = aggexposure.loc[aggexposure["timeunit"].isin(sectorrows[sector.name])]
                print(sectorrows_df)
                METcols = [col for col in sectorrows_df.columns if "MET" in col]
                NO2cols = [col for col in sectorrows_df.columns if "NO2" in col]
                METmin_tot = sectorrows_df[METcols].min().min()
                METmax_tot = sectorrows_df[METcols].max().max()
                NO2min_tot = sectorrows_df[NO2cols].min().min()
                NO2max_tot = sectorrows_df[NO2cols].max().max()
                print("METmin_tot", METmin_tot, "METmax_tot", METmax_tot, "NO2min_tot", NO2min_tot, "NO2max_tot", NO2max_tot)  
                # Create x positions & randomized y values for data plotting
                x = outerringdict_xvalues[sector.name]
                NO2 = sectorrows_df["NO2"].values
                MET =  sectorrows_df["MET"].values
                NO2persubgroup= {}
                METpersubgroup = {}
                for subgroup in subgroups:
                    for value in subgroups[subgroup]:
                        NO2persubgroup[value] = sectorrows_df[[f"NO2_{value}"]].values
                        METpersubgroup[value] = sectorrows_df[[f"MET_{value}"]].values
                        

                # NO2 line
                NO2_track = sector.add_track((65, 100), r_pad_ratio=0.1)
                NO2_track.axis(ec = axiscol)
                if sector.name == "Hours":
                    NO2max = NO2hourmax + NO2hourstep
                    NO2min = NO2hourmin
                    NO2step = NO2hourstep
                    NO2round = NO2hourround
                else:
                    NO2max = NO2monthmax + NO2monthstep
                    NO2min = NO2monthmin
                    NO2step = NO2monthstep
                    NO2round = NO2monthround
                while NO2min > NO2min_tot:
                    NO2min = NO2min - NO2step
                    if hardzero:
                        if NO2min < 0:
                            NO2min = 0
                while NO2max < NO2max_tot:
                    NO2max = NO2max + NO2step
                rangeNO2 =list(np.arange(start=NO2min, stop = NO2max, step = NO2step))
                rangeNO2 = [round(val, NO2round) for val in rangeNO2]
                rangeNO2 = list(dict.fromkeys(rangeNO2))
                while len(rangeNO2) >= 10:
                    rangeNO2 = rangeNO2[::2]
                while rangeNO2[-1] < NO2max:
                    NO2diff = rangeNO2[-1] - rangeNO2[-2]
                    rangeNO2.append((rangeNO2[-1]+NO2diff).round(NO2round))
                NO2max = rangeNO2[-1]    
                NO2min = rangeNO2[0]
                print(rangeNO2)
                NO2_track.yticks(y=rangeNO2, labels=rangeNO2,vmin=NO2min, vmax=NO2max, side="left", tick_length=1, label_size=8, label_margin=0.5, line_kws = {"color": axiscol}, text_kws={"color": axiscol})
                for NO2val in rangeNO2:
                    NO2_track.line([NO2_track.start, NO2_track.end], [NO2val, NO2val], vmin=NO2min, vmax=NO2max, lw=1, ls="dotted", color = gridcol)
                
                if sector.name == "Total":
                    for subgroup in subgroups:
                        for value in subgroups[subgroup]:
                            NO2_track.scatter(x, NO2persubgroup[value], vmin=NO2min, vmax=NO2max, lw=1.5, color=subgroupcolors[subgroup][subgroups[subgroup].index(value)])
                    NO2_track.scatter(x, NO2, vmin=NO2min, vmax=NO2max,lw=2, color="red")
                else:
                    for subgroup in subgroups:
                        for value in subgroups[subgroup]:
                            NO2_track.line(x, NO2persubgroup[value], vmin=NO2min, vmax=NO2max, lw=1.5, color=subgroupcolors[subgroup][subgroups[subgroup].index(value)])
                    NO2_track.line(x, NO2, vmin=NO2min, vmax=NO2max, lw=2, color="red")

                NO2_track.xticks_by_interval(
                    1,
                    label_size=8,
                    label_orientation="vertical",
                    label_formatter=lambda v: f"{outerringdict_labels[sector.name][v]}",
                )
                
                # Plot points
                MET_track = sector.add_track((25, 60), r_pad_ratio=0.1)
                MET_track.axis(ec = axiscol)
                if sector.name == "Hours":
                    METmax = METhourmax + METhourstep
                    METmin = METhourmin
                    METstep = METhourstep
                    METround = METhourround
                else:
                    METmax = METmonthmax + METmonthstep
                    METmin = METmonthmin
                    METstep = METmonthstep
                    METround = METmonthround
                
                while METmin > METmin_tot:
                    METmin = METmin - METstep
                    if hardzero:
                        if METmin < 0:
                            METmin = 0
                while METmax < METmax_tot:
                    METmax = METmax + METstep
                rangeMET =list(np.arange(start=METmin, stop = METmax , step = METstep))
                rangeMET = [round(val, METround) for val in rangeMET]
                rangeMET = list(dict.fromkeys(rangeMET))
                while len(rangeMET) >= 10:
                    rangeMET = rangeMET[::2]
                print(rangeMET, METstep, METmax)
                while rangeMET[-1] < METmax:
                    METdiff = rangeMET[-1] - rangeMET[-2]
                    rangeMET.append((rangeMET[-1]+METdiff).round(METround))
                METmax = rangeMET[-1]
                METmin = rangeMET[0]
                MET_track.yticks(y=rangeMET, labels=rangeMET,vmin=METmin, vmax=METmax,  side="left", tick_length=1, label_size=8, label_margin=0.5, line_kws = {"color": axiscol}, text_kws={"color": axiscol})
                for METval in rangeMET:
                    MET_track.line([MET_track.start, MET_track.end], [METval, METval], vmin=METmin, vmax=METmax,  lw=1, ls="dotted", color = gridcol)
                
                if sector.name == "Total":
                    for subgroup in subgroups:
                        for value in subgroups[subgroup]:
                            MET_track.scatter(x, METpersubgroup[value], vmin=METmin, vmax=METmax, lw=1.5, color=subgroupcolors[subgroup][subgroups[subgroup].index(value)])
                    MET_track.scatter(x, MET, vmin=METmin, vmax=METmax, lw=2, color = "red")

                else:
                    for subgroup in subgroups:
                        for value in subgroups[subgroup]:
                            MET_track.line(x, METpersubgroup[value], vmin=METmin, vmax=METmax, lw=1.5, color=subgroupcolors[subgroup][subgroups[subgroup].index(value)])
                    MET_track.line(x, MET, vmin=METmin, vmax=METmax, lw=2, color = "red")

                # if sector.name == circos.sectors[0].name:
                #     circos.text("NO2(µg/m3)", r=(NO2_track.r_center)-20, deg=-81.5, color="black", adjust_rotation=True, orientation="vertical", size=14)
                #     circos.text("MET", r=MET_track.r_center-5, deg=-80, color="black",adjust_rotation=True, orientation="vertical", size=14)
        # Create legend
        legend_elements = []
        legend_elements.append(Line2D([0], [0], color="red", lw=2, label="All"))
        for subgroup in subgroups:
            for idx, value in enumerate(subgroups[subgroup]):
                legend_elements.append(Line2D([0], [0], color=subgroupcolors[subgroup][idx], lw=1.5, label=f"{subgroup.capitalize().replace('_', ' ')}: {value}"))
        figure = circos.plotfig(dpi=600)
        figure.legend(handles=legend_elements, loc='lower right', ncol=1, title = "Subgroups")
        figure.savefig(f"CirclePlot_with_Legend{suffix}.png", dpi=600)

def plotCircosMeanStrat(stratexposure_df, subgroups, subgroupcolors, outcomevar, meanval, roundval, centertext, redlinelabel = "Mean Exposure", rangeval = None, suffix = None):
        outerringdict = {}
        outerringdict_xvalues = {}
        outerringdict["Mean"] = 0.3
        outerringdict_xvalues["Mean"] = [0]
        for subgroup in subgroups:
            outerringdict[subgroup] = len(subgroups[subgroup])-0.5
            outerringdict_xvalues[subgroup]= list(range(len(subgroups[subgroup])))
        
        outerringdict_labels = subgroups
        outerringdict_labels["Mean"] = ["", ""]
        if rangeval == None:
            if "NO2" in outcomevar:
                minval = -0.5
                maxval = 0.5
                rangeval = [-0.5, -0.25, 0, 0.25, 0.5]
            elif "MET" in outcomevar:
                minval = -0.05
                maxval = 0.05
                rangeval = [-0.05, -0.025, 0, 0.025, 0.05]
        else:
            minval = rangeval[0]
            maxval = rangeval[-1]
        if meanval != 0:
            meanval = meanval.round(roundval)
            absoluterange = [(meanval + val).round(roundval) for val in rangeval]
            absolutemin = absoluterange[0].round(roundval)
            absolutemax = absoluterange[-1].round(roundval)
        else:   
            absoluterange = [(meanval + val) for val in rangeval]
            absolutemin = absoluterange[0]
            absolutemax = absoluterange[-1]
   
        axiscol = "white"
        gridcol = "lightgrey"
        circos = Circos(outerringdict, space=25)

        for sector in circos.sectors:
                print(sector.name)
                # Plot sector name
                if sector.name == "Mean":
                    sector.text(f"{redlinelabel}\n(red line)", r=120, size=14, color="red", adjust_rotation=False, orientation="horizontal")
                else:
                    sector.text(f"{sector.name.capitalize().replace('_', ' ').replace('Hh', 'Household')}", r=140, size=14)
                # Create x positions & randomized y values for data plotting
                x = outerringdict_xvalues[sector.name]

                labeltrack = sector.add_track((98, 99), r_pad_ratio=0)
                labeltrack.axis(ec = "none")
                if sector.name != "Mean":
                    labeltrack.xticks_by_interval(
                        1,
                        label_size=8,
                        label_orientation="vertical",
                        label_formatter=lambda v: f"{outerringdict_labels[sector.name][v]}",
                    )
                
                Track = sector.add_track((35, 98), r_pad_ratio=0)
                if sector.name == "Mean":
                    Track.axis(ec = axiscol, fc="none")
                    for yval in absoluterange:
                        Track.line([Track.start,Track.end], [yval, yval], vmin=absolutemin, vmax=absolutemax, lw=1, ls="dotted", color = gridcol)
                    Track.line([Track.start,Track.end], [meanval,meanval], vmin=absolutemin, vmax=absolutemax, lw=2, color="red")
                    Track.yticks(y=absoluterange, labels=absoluterange,vmin=absolutemin, vmax=absolutemax, side="left", tick_length=1, 
                             label_size=8, label_margin=0.5, line_kws = {"color": gridcol}, text_kws={"color": "dimgray"})
                    
                else:
                    Track.axis(ec = axiscol)
                    for yval in rangeval:
                        Track.line([Track.start,Track.end], [yval, yval], vmin=minval, vmax=maxval, lw=1, ls="dotted", color = gridcol)
                    Track.line([Track.start,Track.end], [0,0], vmin=minval, vmax=maxval, lw=2, color="red")
                    sectordata = list([stratexposure_df.loc[stratexposure_df["Label"] == val, outcomevar].values[0] for val in subgroups[sector.name]])
                    print(x, sectordata, subgroupcolors[sector.name])
                    Track.bar(x=x, height = sectordata, vmin=minval, vmax = maxval , align="edge", width=0.4, color=subgroupcolors[sector.name])
                    # Track.yticks(y=rangeval, labels=rangeval,vmin=minval, vmax=maxval, side="left", tick_length=1, 
                    #          label_size=8, label_margin=0.5, line_kws = {"color": gridcol}, text_kws={"color": "dimgray"})
                if sector.name == "Mean":
                    innerText = sector.add_track((0, 0), r_pad_ratio=0.1)
                    innerText.axis(ec = "none")
                    innerText.text(centertext, x = innerText.start, color="black", adjust_rotation=False, orientation="horizontal" ,size=14)

        figure = circos.plotfig(dpi=600)
        figure.savefig(f"CirclePlot_{outcomevar}_Subgroups_{suffix}.png", dpi=600)


def plotCircosMeanStratRelativ(stratexposure_df, subgroups, subgroupcolors, outcomevar, meanvalStatQ,meanvalScenario, roundval, centertext, redlinelabel = "Mean Exposure", rangeval = None, suffix = None):
        outerringdict = {}
        outerringdict_xvalues = {}
        outerringdict["Mean"] = 0.3
        outerringdict_xvalues["Mean"] = [0]
        for subgroup in subgroups:
            outerringdict[subgroup] = len(subgroups[subgroup])-0.5
            outerringdict_xvalues[subgroup]= list(range(len(subgroups[subgroup])))
        
        outerringdict_labels = subgroups
        outerringdict_labels["Mean"] = ["", ""]
        if rangeval == None:
            if "NO2" in outcomevar:
                minval = -0.5
                maxval = 0.5
                rangeval = [-0.5, -0.25, 0, 0.25, 0.5]
            elif "MET" in outcomevar:
                minval = -0.05
                maxval = 0.05
                rangeval = [-0.05, -0.025, 0, 0.025, 0.05]
        else:
            minval = rangeval[0]
            maxval = rangeval[-1]
        if meanvalStatQ != 0:
            meanvalStatQ = meanvalStatQ.round(roundval)
            absoluterange = [(meanvalStatQ + val).round(roundval) for val in rangeval]
            absolutemin = absoluterange[0].round(roundval)
            absolutemax = absoluterange[-1].round(roundval)
        else:   
            absoluterange = [(meanvalStatQ + val) for val in rangeval]
            absolutemin = absoluterange[0]
            absolutemax = absoluterange[-1]
   
        axiscol = "#FF000000"
        gridcol = "lightgrey"
        circos = Circos(outerringdict, space=24)

        for sector in circos.sectors:
                print(sector.name)
                # Plot sector name
                if sector.name == "Mean":
                    sector.text("Population\nMean", r=140, size=14, color="black", adjust_rotation=False, orientation="horizontal")
                else:
                    sector.text(f"{sector.name.capitalize().replace('_', ' ').replace('Hh', 'Household')}", r=140, size=14)
                # Create x positions & randomized y values for data plotting
                x = outerringdict_xvalues[sector.name]

                labeltrack = sector.add_track((98, 99), r_pad_ratio=0)
                labeltrack.axis(ec = "none")
                if sector.name != "Mean":
                    labeltrack.xticks_by_interval(
                        1,
                        label_size=8,
                        label_orientation="vertical",
                        label_formatter=lambda v: f"{outerringdict_labels[sector.name][v]}",
                    )
                
                Track = sector.add_track((35, 98), r_pad_ratio=0)
                if sector.name == "Mean":
                    Track.axis(ec = axiscol, fc="none")
                    for yval in absoluterange:
                        Track.line([Track.start,Track.end], [yval, yval], vmin=absolutemin, vmax=absolutemax, lw=1, ls="dotted", color = gridcol)
                    Track.scatter([Track.end], [meanvalStatQ], vmin=absolutemin, vmax=absolutemax, lw=2, color="red")
                    Track.scatter([Track.end], [meanvalScenario], vmin=absolutemin, vmax=absolutemax, lw=2, color="black")
                    # Track.line([Track.start,Track.end], [meanval,meanval], vmin=absolutemin, vmax=absolutemax, lw=2, color="red")
                    Track.yticks(y=absoluterange, labels=absoluterange,vmin=absolutemin, vmax=absolutemax, side="left", tick_length=1, 
                             label_size=8, label_margin=0.5, line_kws = {"color": gridcol}, text_kws={"color": "dimgray"})
                    
                else:
                    Track.axis(ec = axiscol)
                    for yval in rangeval:
                        Track.line([Track.start,Track.end], [yval, yval], vmin=minval, vmax=maxval, lw=1, ls="dotted", color = gridcol)
                    # Track.line([Track.start,Track.end], [0,0], vmin=minval, vmax=maxval, lw=1.5, color="red")
                    sectordata_after = list([stratexposure_df.loc[stratexposure_df["Label"] == val, f"{outcomevar}_deviationStatQMean"].values[0] for val in subgroups[sector.name]])
                    sectordata_before = list([stratexposure_df.loc[stratexposure_df["Label"] == val, f"{outcomevar}_StatQdevStatQMean"].values[0] for val in subgroups[sector.name]])
                    bothbelow = [idx for idx in range(len(sectordata_after)) if ((sectordata_after[idx] < 0) and (sectordata_before[idx]<0))]
                    bothabove = [idx for idx in range(len(sectordata_after)) if ((sectordata_after[idx] > 0) and (sectordata_before[idx]>0))]
                    blank = [0 for x in range(len(sectordata_after))]
                    for idx in bothbelow:
                        if sectordata_after[idx] < sectordata_before[idx]:
                            blank[idx] = sectordata_before[idx]
                        else:
                            blank[idx] = sectordata_after[idx]
                    for idx in bothabove:
                        if sectordata_after[idx] < sectordata_before[idx]:
                            blank[idx] = sectordata_after[idx]
                        else:
                            blank[idx] = sectordata_before[idx]
                    print(x, sectordata_after, sectordata_before, subgroupcolors[sector.name])
                    Track.bar(x=x, height = sectordata_before, vmin=minval, vmax = maxval , align="center", width=0.4, color=subgroupcolors[sector.name], alpha=0.5)
                    Track.bar(x=x, height = sectordata_after, vmin=minval, vmax = maxval , align="center", width=0.4, color=subgroupcolors[sector.name], alpha=0.5)
                    Track.bar(x=x, height = blank, vmin=minval, vmax = maxval , align="center", width=0.5, color="white")
                    Track.scatter(x, sectordata_before, vmin=minval, vmax=maxval,lw=2, color="red")
                    Track.scatter(x, sectordata_after, vmin=minval, vmax=maxval,lw=2, color="black")
                    # Track.yticks(y=rangeval, labels=rangeval,vmin=minval, vmax=maxval, side="left", tick_length=1, 
                    #          label_size=8, label_margin=0.5, line_kws = {"color": gridcol}, text_kws={"color": "dimgray"})
                if sector.name == "Mean":
                    innerText = sector.add_track((0, 0), r_pad_ratio=0.1)
                    innerText.axis(ec = "none")
                    innerText.text(centertext, x = innerText.start, color="black", adjust_rotation=False, orientation="horizontal" ,size=14)

         # Create legend
        legend_elements = []
        legend_elements.append(Line2D([0], [0], color="red", marker='o', lw=0, label=f"Exposure Before Intervention"))
        legend_elements.append(Line2D([0], [0], color="black", marker='o', lw=0, label=f"Exposure After Intervention"))
        figure = circos.plotfig(dpi=600)
        figure.legend(handles=legend_elements, loc='lower right', ncol=1, title = "Legend")
        figure.savefig(f"CirclePlot_{outcomevar}_Subgroups_{suffix}.png", dpi=600)




def plotCircosDiffNO2MET_Timeunits(aggexposure, subgroups, subgroupcolors, 
                                   NO2monthmin = -1, NO2monthmax = 1.5, NO2monthstep = 0.5,
                                   NO2hourmin=-1.5, NO2hourmax = 1, NO2hourstep = 0.5,
                                   NO2weekdaymin = -1, NO2weekdaymax = 1, NO2weekdaystep = 0.05,
                                   METmonthmin = -1, METmonthmax = 1, METmonthstep = 0.05,
                                   METhourmin = -1, METhourmax = 1, METhourstep = 0.05,
                                   METweekdaymin = -1, METweekdaymax = 1, METweekdaystep = 0.05,
                                   NO2hourround=2, NO2monthround=2, METhourround=2, METmonthround=2,
                                   suffix = None):
        outerringdict = {"Hours": 23, "Weekdays": 6, "Timeunits": 1,"Months": 3, 
                        "Total": 0.4
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
                            
        axiscol = "dimgray"
        gridcol = "lightgrey"
        # Create Circos plot
        circos = Circos(outerringdict, space=19)
        print(f"Circos plot for {subgroups}")
        for sector in circos.sectors:

            print(sector.name)
            if sector.name == "Timeunits":
                # Plot sector name
                NO2_track = sector.add_track((65, 100), r_pad_ratio=0.1)
                NO2_track.axis(ec = "none")
                NO2_track.text("Δ NO2(µg/m3)", x = NO2_track.start, color="black", adjust_rotation=True, orientation="vertical" ,size=13)

                MET_track = sector.add_track((25, 60), r_pad_ratio=0.1)
                MET_track.axis(ec = "none")
                MET_track.text("Δ MET*", x = MET_track.start, color="black", adjust_rotation=True, orientation="vertical" ,size=13)

            else:
                # Plot sector name
                sector.text(f"{sector.name}", r=125, size=14)
                sectorrows_df = aggexposure.loc[aggexposure["timeunit"].isin(sectorrows[sector.name])]
                # Create x positions & randomized y values for data plotting
                x = outerringdict_xvalues[sector.name]
                NO2 = sectorrows_df["NO2"].values
                MET =  sectorrows_df["MET"].values
                NO2persubgroup= {}
                METpersubgroup = {}
                for subgroup in subgroups:
                    for value in subgroups[subgroup]:
                        NO2persubgroup[value] = sectorrows_df[[f"NO2_{value}"]].values
                        METpersubgroup[value] = sectorrows_df[[f"MET_{value}"]].values
                NO2cols = ["NO2"] + [f"NO2_{value}" for subgroup in subgroups for value in subgroups[subgroup]]
                METcols = ["MET"] + [f"MET_{value}" for subgroup in subgroups for value in subgroups[subgroup]]
                METmin_tot = sectorrows_df[METcols].min().min()
                METmax_tot = sectorrows_df[METcols].max().max()
                NO2min_tot = sectorrows_df[NO2cols].min().min()
                NO2max_tot = sectorrows_df[NO2cols].max().max()
                print("METmin_tot", METmin_tot, "METmax_tot", METmax_tot, "NO2min_tot", NO2min_tot, "NO2max_tot", NO2max_tot)
                # NO2 line
                NO2_track = sector.add_track((65, 100), r_pad_ratio=0.1)
                NO2_track.axis(ec = axiscol)
                if sector.name == "Hours":
                    NO2max = NO2hourmax
                    NO2min = NO2hourmin
                    NO2step = NO2hourstep
                    NO2round = NO2hourround
                elif sector.name == "Weekdays":
                    NO2max = NO2weekdaymax
                    NO2min = NO2weekdaymin
                    NO2step = NO2weekdaystep
                    NO2round = NO2monthround
                else:
                    NO2max = NO2monthmax 
                    NO2min = NO2monthmin
                    NO2step = NO2monthstep
                    NO2round = NO2monthround
                while NO2min > NO2min_tot:
                    NO2min = NO2min - NO2step
                while NO2max < NO2max_tot:
                    NO2max = NO2max + NO2step
                rangeNO2 =list(np.arange(start=NO2min, stop = NO2max, step = NO2step))
                rangeNO2 = [round(val, NO2round) for val in rangeNO2]
                rangeNO2 = list(dict.fromkeys(rangeNO2))
                while len(rangeNO2) >= 10:
                    rangeNO2 = rangeNO2[::2]
                while rangeNO2[-1] < NO2max:
                    NO2diff = rangeNO2[-1] - rangeNO2[-2]
                    rangeNO2.append((rangeNO2[-1]+NO2diff).round(NO2round))
                while rangeNO2[0] > NO2min:
                    NO2diff = rangeNO2[1] - rangeNO2[0]
                    rangeNO2.insert(0, (rangeNO2[0]-NO2diff).round(NO2round))
                NO2max = rangeNO2[-1]
                NO2min = rangeNO2[0]
                print("rangeNO2", rangeNO2, "NO2min", NO2min, "NO2max", NO2max, "NO2hourstep", NO2hourstep, "NO2monthstep", NO2monthstep)
                NO2_track.yticks(y=rangeNO2, labels=rangeNO2,vmin=NO2min, vmax=NO2max, side="left", tick_length=1, label_size=8, label_margin=0.5, line_kws = {"color": axiscol}, text_kws={"color": axiscol})
                for NO2val in rangeNO2:
                    NO2_track.line([NO2_track.start, NO2_track.end], [NO2val, NO2val], vmin=NO2min, vmax=NO2max, lw=1, ls="dotted", color = gridcol)
                
                if sector.name == "Total":
                    for subgroup in subgroups:
                        for value in subgroups[subgroup]:
                            NO2_track.scatter(x, NO2persubgroup[value], vmin=NO2min, vmax=NO2max, lw=1.5, color=subgroupcolors[subgroup][subgroups[subgroup].index(value)])
                    NO2_track.scatter(x, NO2, vmin=NO2min, vmax=NO2max,lw=2, color="red")
                else:
                    for subgroup in subgroups:
                        for value in subgroups[subgroup]:
                            NO2_track.line(x, NO2persubgroup[value], vmin=NO2min, vmax=NO2max, lw=1.5, color=subgroupcolors[subgroup][subgroups[subgroup].index(value)])
                    NO2_track.line(x, NO2, vmin=NO2min, vmax=NO2max, lw=2, color="red")

                NO2_track.xticks_by_interval(
                    1,
                    label_size=8,
                    label_orientation="vertical",
                    label_formatter=lambda v: f"{outerringdict_labels[sector.name][v]}",
                )
                
                # Plot points
                MET_track = sector.add_track((25, 60), r_pad_ratio=0.1)
                MET_track.axis(ec = axiscol)
                if sector.name == "Hours":
                    METmax = METhourmax	
                    METmin = METhourmin
                    METstep = METhourstep
                    METround = METhourround
                elif sector.name == "Weekdays":
                    METmax = METweekdaymax
                    METmin = METweekdaymin
                    METstep = METweekdaystep
                    METround = METmonthround
                else:
                    METmax = METmonthmax
                    METmin = METmonthmin
                    METstep = METmonthstep
                    METround = METmonthround
                while METmin > METmin_tot:
                    METmin = METmin - METstep
                while METmax < METmax_tot:
                    METmax = METmax + METstep
                    
                rangeMET =list(np.arange(start=METmin, stop = METmax, step = METstep))
                rangeMET = [round(val, METround) for val in rangeMET]
                rangeMET = list(dict.fromkeys(rangeMET))
                while len(rangeMET) >= 10:
                    rangeMET = rangeMET[::2]
                while rangeMET[-1] < METmax:
                    METdiff = rangeMET[-1] - rangeMET[-2]
                    rangeMET.append((rangeMET[-1]+METdiff).round(METround))
                while rangeMET[0] > METmin:
                    METdiff = rangeMET[1] - rangeMET[0]
                    rangeMET.insert(0, (rangeMET[0]-METdiff).round(METround))
                METmin = rangeMET[0]
                METmax = rangeMET[-1]
                print("rangeMET", rangeMET, "METmin", METmin, "METmax", METmax, "METhourstep", METhourstep, "METmonthstep", METmonthstep)
                       
                MET_track.yticks(y=rangeMET, labels=rangeMET,vmin=METmin, vmax=METmax,  side="left", tick_length=1, label_size=8, label_margin=0.5, line_kws = {"color": axiscol}, text_kws={"color": axiscol})
                for METval in rangeMET:
                    MET_track.line([MET_track.start, MET_track.end], [METval, METval], vmin=METmin, vmax=METmax,  lw=1, ls="dotted", color = gridcol)
                
                if sector.name == "Total":
                    for subgroup in subgroups:
                        for value in subgroups[subgroup]:
                            MET_track.scatter(x, METpersubgroup[value], vmin=METmin, vmax=METmax, lw=1.5, color=subgroupcolors[subgroup][subgroups[subgroup].index(value)])
                    MET_track.scatter(x, MET, vmin=METmin, vmax=METmax, lw=2, color = "red")

                else:
                    for subgroup in subgroups:
                        for value in subgroups[subgroup]:
                            MET_track.line(x, METpersubgroup[value], vmin=METmin, vmax=METmax, lw=1.5, color=subgroupcolors[subgroup][subgroups[subgroup].index(value)])
                    MET_track.line(x, MET, vmin=METmin, vmax=METmax, lw=2, color = "red")

        # Create legend
        legend_elements = []
        legend_elements.append(Line2D([0], [0], color="red", lw=2, label="All"))
        for subgroup in subgroups:
            for idx, value in enumerate(subgroups[subgroup]):
                legend_elements.append(Line2D([0], [0], color=subgroupcolors[subgroup][idx], lw=1.5, label=f"{subgroup.capitalize().replace('_', ' ')}: {value}"))
        figure = circos.plotfig(dpi=600)
        figure.legend(handles=legend_elements, loc='lower right', ncol=1, title = "Subgroups")
        figure.savefig(f"CirclePlot_with_Legend{suffix}.png", dpi=600)


def PlotPerNeighbOutcome(outcomvar, showplots, modelrun, spatialdata, distance_meters, vmax = None, vmin= None, outcomelabel = None):
    if outcomelabel is None:
        outcomelabel = outcomvar
    ax = spatialdata.plot(outcomvar, antialiased=False, legend = True, vmax = vmax, vmin = vmin)
    cx.add_basemap(ax, crs=spatialdata.crs, source=cx.providers.CartoDB.PositronNoLabels)
    scalebar = ScaleBar(distance_meters, length_fraction=0.2, location="lower right", box_alpha=0.5)  # Adjust the length as needed
    ax.add_artist(scalebar)
    plt.title(f"{outcomelabel} Per Neighborhood")
    plt.savefig(f'{modelrun}_neighbmap_{outcomvar}.png', dpi = 600, bbox_inches='tight', pad_inches=0.1)
    if showplots:
        plt.show()
    plt.close()


######################################################
##########################################
nb_agents = 21750  #87000 = 10%, 43500 = 5%, 21750 = 2.5%, 8700 = 1%
path_data = "D:\PhD EXPANSE\Data\Amsterdam\ABMRessources\ABMData\ModelRuns"
os.chdir(path_data)

# scenario = "StatusQuo"
# scenario = "PrkPriceInterv"
# scenario = "15mCity"
scenario = "15mCityWithDestination"
# scenario = "NoEmissionZone2025"
# scenario = "NoEmissionZone2030"


# identify model run for scenario
experimentoverview = pd.read_csv("D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/ExperimentOverview.csv")
# experimentoverview = experimentoverview[~np.isnan(experimentoverview["Population Sample"])]
modelruns = experimentoverview.loc[(experimentoverview["Experiment"] == scenario)& (experimentoverview["Number of Agents"] == f"{nb_agents}Agents"), "Model Run"].values
# modelruns = [modelrun for modelrun in modelruns if not(modelrun in [669169,509190])]
# modelruns = [365800, 846897, 999180]
# modelruns = [799701]
# modelruns = [ 912787, 493519, 989597]

popsamples = [experimentoverview.loc[experimentoverview["Model Run"]== modelrun, "Population Sample"].values[0] for modelrun in modelruns]
print(modelruns, popsamples)



viztasks = [
            # "Exposure preparation",
            # "Exposure descriptives",
            # "Exposure stratification",
            # "Aggregate exposure df",
            # "Exposure Time Circle plot",
            # "Exposure Circle plot strat",
            # "spatial Exposure mapping",
            # "Comparative plots",
            # "Mean across runs aggregate exposure df",
            # "Mean across runs exposure circle plot",
            # "Mean across runs strat exposure Circle plot",
            # "Mean across runs and Neighborhoods",
            # "Mean across runs aggregate exposure diff df",
            # "Mean across runs exposure diff circle plot",
            "Mean across runs strat exposure diff Circle plot",
            # "Mean across runs and Neighborhoods diff"
            ]
            
categoricalstratvars = ["sex", "migr_bck", "income_class", "age_group", "HH_size", "absolved_education", "HH_type", "student", "location"]
plottypes = [ "line", "violin"] # "scatter"
outcomevars = ["NO2", "MET"]
timevars = ["hour", "weekday", "month"]

fullnamedict = {
    "income": "Income Decile: 1 low, 10 high",
    "sex": "sex",
    "migr_bck": "Migration Background",
    "income_class": "Income Group",
    "age_group": "Age Group",
    "HH_size": "Household Size",
    "absolved_education": "Education Level",
    "HH_type": "Household Type",
    "student": "Student Status",
    "location": "Location",
    "NO2": "NO2 (µg/m3)",
    "MET": "Metabolic Equivalent of Task (MET)",
    "NO2_diff": "NO2 Difference (µg/m3)",
    "MET_diff": "Metabolic Equivalent of Task (MET) Difference" }

subgroups_Meta = {"income": ["Low", "Medium", "High"],
            "sex": ["male", "female"], 
            "migration_background": ["Dutch", "Western", "Non-Western"],
            "age_group": ["Aged 0-29", "Aged 30-59", "Aged 60+"],
            "HH_size": ["HH size 1", "HH size 2", "HH size 3", "HH size 4", "HH size 5", "HH size 6", "HH size 7"],
            "absolved_education": ["low", "middle", "high"],
            "HH_type": ["Single Person", "Pair without children", "Pair with children", "Single Parent with children", "Other multiperson household"],
            "student": ["Student", "Not Student"],
            "location": ["inside ring", "outside ring"]
            }


days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']


########### identify inner ring neighborhoods
innerring = gpd.read_feather("D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/SpatialData/NoEmissionZone2025.feather")
neighborhoods = gpd.read_file("D:\PhD EXPANSE\Data\Amsterdam\Administrative Units\Amsterdam_Neighborhoods_RDnew.shp")
innerringsneighborhoods = innerring.sjoin(neighborhoods, how="inner", predicate='intersects')
innerringsneighborhoods = list(innerringsneighborhoods["buurtcode"].values)



for count, modelrun in enumerate(modelruns):
    print(f"Model run {modelrun}")
    if "Exposure preparation" in viztasks:
        # read exposure data
        os.chdir(path_data+f"/{scenario}/{nb_agents}Agents/AgentExposure/{modelrun}/ExposureViz")
        print("Reading the data")
        # exposure_df_horizon = pd.read_csv(f"Exposure_A{nb_agents}_{modelrun}_horizonAsColumns.csv")
        exposure_df_vertical = pd.read_csv(f"Exposure_A{nb_agents}_{modelrun}_verticalAsRows.csv")

        exposure_df_vertical["date"] = [f"{daymonth[0]}-{daymonth[1]}-2019" for daymonth in exposure_df_vertical[["day", "month"]].values]
        exposure_df_vertical['date'] = pd.to_datetime(exposure_df_vertical['date'], format='%d-%m-%Y', errors='coerce')
        exposure_df_vertical["weekday"] = exposure_df_vertical['date'].dt.day_name()
        exposure_df_vertical['weekday'] = pd.Categorical(exposure_df_vertical['weekday'], categories=days_order, ordered=True)
        # exposure_df_vertical["weekday"] = exposure_df_vertical["weekday"].replace({"Monday": "Sunday", "Tuesday": "Monday", "Wednesday": "Tuesday", "Thursday": "Wednesday", "Friday": "Thursday", "Saturday": "Friday", "Sunday": "Saturday"})


        agent_df = pd.read_csv(path_data+f"/{scenario}/{nb_agents}Agents/Amsterdam_population_subset{nb_agents}_{modelrun}_{popsamples[count]}.csv")
        print("Merging the data")
        exposure_df_vertical = pd.merge(agent_df, exposure_df_vertical, on="agent_ID", how="right")


        # Renaming some columns for elegance
        exposure_df_vertical = exposure_df_vertical.rename(columns={"incomeclass_int": "income", "migrationbackground": "migr_bck"})
        exposure_df_vertical["income"] = exposure_df_vertical["income"].astype(int)
        # restructuring data
        exposure_df_vertical["income_class"]=exposure_df_vertical["income"].apply(lambda x: "Low" if x in range(1,5) else ("Medium" if x in range(5,9) else "High"))
        # 1 low # 10 high
        # restructuring age into groups
        exposure_df_vertical["age_group"]=exposure_df_vertical["age"].apply(lambda x: "Aged 0-29" if x in range(0,30) else ("Aged 30-59" if x in range(30,60) else "Aged 60+"))    
        # renaming binary student variable
        exposure_df_vertical["student"] = exposure_df_vertical["student"].replace({1: "Student", 0: "Not Student"})

        
        # creating HH type from multiple hh variables
        exposure_df_vertical["HH_type"] = ""
        # exposure_df_vertical["Nrchildren"] = exposure_df_vertical["Nrchildren"].astype(int)
        exposure_df_vertical["Nr_adults"] = exposure_df_vertical["HH_size"] - exposure_df_vertical["Nrchildren"]
        exposure_df_vertical.loc[exposure_df_vertical["hh_single"]==1, "HH_type"] = "Single Person"
        exposure_df_vertical.loc[(exposure_df_vertical["HH_size"]==2) & (exposure_df_vertical["havechild"] == 0), "HH_type"] = "Pair without children"
        exposure_df_vertical.loc[(exposure_df_vertical["HH_size"]>2) & (exposure_df_vertical["havechild"] == 1), "HH_type"] = "Pair with children"
        exposure_df_vertical.loc[(exposure_df_vertical["HH_size"]>=2) & (exposure_df_vertical["havechild"] == 1) & (exposure_df_vertical["Nr_adults"]==1), "HH_type"] = "Single Parent with children"
        exposure_df_vertical.loc[(exposure_df_vertical["HH_size"]>=2) & (exposure_df_vertical["Nr_adults"]>2), "HH_type"] = "Other multiperson household"
                
        # make hh_size into a categorical variable
        exposure_df_vertical["HH_size"] = [f"HH size {hhsize}" for hhsize in exposure_df_vertical["HH_size"]]
        continuousstratvars = ["income"]
        
        exposure_df_vertical["location"] = "outside ring"
        exposure_df_vertical.loc[exposure_df_vertical["neighb_code"].isin(innerringsneighborhoods), "location"] = "inside ring"
        
    if "Exposure descriptives" in viztasks:
        print("Analyzing the data")
        print(exposure_df_vertical.head())
        print(exposure_df_vertical.info())
        print(exposure_df_vertical.describe())
        for column in exposure_df_vertical.select_dtypes(include=['object']):
            print("\nValue counts for", column)
            print(exposure_df_vertical[column].value_counts())

    if "Exposure stratification" in viztasks:
        # #################################
        # ###  Exposure stratifications ###
        # #################################
        print("Plotting the exposure stratification")

        showplots = False
        PlotVarsInLists(timevars=timevars,plottypes=plottypes, outcomevars=outcomevars, continuousstratvars=continuousstratvars,
                        categoricalstratvars=categoricalstratvars,showplots= showplots, modelrun=modelrun,
                        df=exposure_df_vertical, fullnamedict=fullnamedict)


    if "Aggregate exposure df" in viztasks:
        # #### create an aggregate dataset
        print("Creating an aggregate dataset")
        timeunits = ["hour", "weekday", "month"]

        aggexposure = exposure_df_vertical[outcomevars].mean().values
        aggexposure = pd.DataFrame([["total"]+list(aggexposure)], columns=["timeunit"]+outcomevars)
        print(aggexposure)
        for timeunit in timeunits:
            timeunitexposure = pd.DataFrame(exposure_df_vertical[[timeunit]+outcomevars].groupby(timeunit, as_index=False).mean())
            timeunitexposure["timeunit"] = [f"{timeunit} {unit}" for unit in timeunitexposure[timeunit]]
            print(timeunitexposure.head())
            aggexposure = pd.concat([aggexposure, timeunitexposure[["timeunit"]+outcomevars]], axis=0, ignore_index=True)
            print(aggexposure.head(30))   
    
        aggexposure.index = aggexposure["timeunit"]
        for strativar in categoricalstratvars:
            stratexposure = pd.DataFrame(exposure_df_vertical[[strativar]+outcomevars].groupby(strativar, as_index=False).mean())
            stratexposure["timeunit"] = "total"
            stratexposure = pd.pivot(index="timeunit", columns=strativar, values=outcomevars, data=stratexposure)
            stratcol = [f"{col[0]}_{col[1]}" for col in stratexposure.columns]
            stratexposure.columns = stratcol
            print(stratexposure.head())
            aggexposure[stratcol] = None
            aggexposure.loc[aggexposure["timeunit"] == "total", stratcol] = stratexposure[stratcol]
            for timeunit in timeunits:
                timeunitexposure = pd.DataFrame(exposure_df_vertical[[timeunit, strativar]+outcomevars].groupby([timeunit, strativar], as_index=False).mean())
                timeunitexposure["timeunit"] = [f"{timeunit} {unit}" for unit in timeunitexposure[timeunit]]
                timeunitexposure = pd.pivot(index="timeunit", columns=strativar, values=outcomevars, data=timeunitexposure)
                timeunitexposure.columns = stratcol
                print(timeunitexposure.head())
                aggexposure.loc[timeunitexposure.index, stratcol] = timeunitexposure[stratcol]
                print(aggexposure.head(30))
            
        aggexposure.to_csv(f"Exposure_A{nb_agents}_{modelrun}_aggregate.csv", index=False)
    
    
    if "Exposure Time Circle plot" in viztasks:
        
        ##########################################################  
        ### Visualize the aggregate data in a circle plot
        ##########################################################
        
        aggexposure = pd.read_csv(f"Exposure_A{nb_agents}_{modelrun}_aggregate.csv")

        subgroupcolorpalette = ["darkviolet", "darkorange", "teal", "green","greenyellow",  "lightseagreen", "aquamarine","olive",  ]
        
        for stratgroup in subgroups_Meta:
            print(f"Plotting the exposure stratification for {stratgroup}")
            subgroups = {stratgroup:subgroups_Meta[stratgroup]}
            subgroupcolors = {stratgroup: subgroupcolorpalette[:len(subgroups[stratgroup])]}
            NO2monthmin, NO2monthmax, NO2monthstep =  calc_min_max(df = aggexposure, column="NO2", timeunit_contains= "month", round_val = 2, hardzero = True, stratvals = subgroups[stratgroup])
            NO2hourmin, NO2hourmax, NO2hourstep =  calc_min_max(df = aggexposure, column="NO2", timeunit_contains= "hour", round_val = 2, hardzero = True, stratvals = subgroups[stratgroup])
            NO2weekdaymin, NO2weekdaymax, NO2weekdaystep =  calc_min_max(df = aggexposure, column="NO2", timeunit_contains= "weekday", round_val = 2, hardzero = True, stratvals = subgroups[stratgroup])
            METmonthmin, METmonthmax, METmonthstep =  calc_min_max(df = aggexposure, column="MET", timeunit_contains= "month", round_val = 2, hardzero = True, stratvals = subgroups[stratgroup])
            METhourmin, METhourmax, METhourstep =  calc_min_max(df = aggexposure, column="MET", timeunit_contains= "hour", round_val = 2, hardzero = True, stratvals = subgroups[stratgroup])
            METweekdaymin, METweekdaymax, METweekdaystep =  calc_min_max(df = aggexposure, column="MET", timeunit_contains= "weekday", round_val = 2, hardzero = True, stratvals = subgroups[stratgroup])
            
            plotCircosNO2MET_Timeunits(aggexposure, subgroups, subgroupcolors,  
                                       NO2monthmin = NO2monthmin, METmonthmin= METmonthmin, 
                                       NO2hourmax=NO2hourmax, NO2hourmin=NO2hourmin,
                                       suffix = f"_{scenario}_{modelrun}_{stratgroup}")   

    if "Exposure Circle plot strat" in viztasks:
        subgroupcolors = {stratgroup: subgroupcolorpalette[count] for count, stratgroup in enumerate(subgroups_Meta)}

        aggexposure_subs = aggexposure.loc[aggexposure["timeunit"]=="total",[f"{outcomevar}_{val}" for subgroup in subgroups_Meta for val in subgroups_Meta[subgroup] for outcomevar in outcomevars]]
        stratexposure_df = pd.DataFrame({f"{outcomevar}": [aggexposure_subs[f"{outcomevar}_{val}"].values for subgroup in subgroups_Meta for val in subgroups_Meta[subgroup]] for outcomevar in outcomevars})
        stratexposure_df["Label"] = [val for subgroup in subgroups_Meta for val in subgroups_Meta[subgroup]]
        stratexposure_df["Group"] = [subgroup for subgroup in subgroups_Meta for val in subgroups_Meta[subgroup]]
        for outcomevar in outcomevars:
            stratexposure_df[outcomevar] = [x[0] for x in stratexposure_df[outcomevar]]
            stratexposure_df[f"{outcomevar}_deviation"] = stratexposure_df[f"{outcomevar}"] - aggexposure.loc[aggexposure["timeunit"]=="total", outcomevar].values[0]
        print(stratexposure_df.head(20))

        stratexposure_df.to_csv(f"Exposure_A{nb_agents}_{modelrun}_aggregate_strat.csv", index=False)
    
        plotCircosMeanStrat(stratexposure_df, subgroups= subgroups_Meta, subgroupcolors = subgroupcolors, outcomevar = "NO2", roundval = 1, suffix = None)

        
    if "spatial Exposure mapping" in viztasks:
        ###########################################
        # map exposure per neighborhood
        ###########################################
        print("Plotting mean status quo scenario exposure per neighborhood")
        crs = 28992    
        points = gpd.GeoSeries(
            [Point(485000, 120000), Point(485001, 120000)], crs=crs
        )  # Geographic WGS 84 - degrees
        points = points.to_crs(32619)  # Projected WGS 84 - meters
        distance_meters = points[0].distance(points[1])
        print(distance_meters)
        neighborhoods = gpd.read_file("D:\PhD EXPANSE\Data\Amsterdam\Administrative Units\Amsterdam_Neighborhoods_RDnew.shp")
        print(neighborhoods.columns)
        exposure_df_vertical
        exposure_neigh = exposure_df_vertical[["neighb_code"] +outcomevars].groupby(["neighb_code"],  as_index=False).mean()
        exposure_neigh.to_csv(f"Exposure_A{nb_agents}_{modelrun}_neigh.csv", index=False)
        exposure_neigh.rename(columns={"neighb_code": "buurtcode"}, inplace=True)
        print(exposure_neigh.head())
        neighborhoods = neighborhoods.merge(exposure_neigh, on="buurtcode", how="left")

        showplots = False
        for outcomvar in outcomevars:
            PlotPerNeighbOutcome(outcomvar=outcomvar, showplots=showplots, modelrun=modelrun, 
                                spatialdata=neighborhoods, outcomelabel=fullnamedict[outcomvar], 
                                distance_meters=distance_meters)

    if "Comparative plots" in viztasks:
        #########################
        ### Comparative Plots ###
        #########################

        aggexposure = pd.read_csv(f"Exposure_A{nb_agents}_{modelrun}_aggregate.csv")
        aggexposurestatquo = pd.read_csv(path_data+f"/{scenario}/{nb_agents}Agents/AgentExposure/MeanExposureViz/Exposure_A{nb_agents}_Mean_{scenario}_aggregate.csv")


        aggexposurediff = aggexposure.copy()
        outcomecols = aggexposure.columns[1:]
        for outcomvar in outcomecols:
            aggexposurediff[f"{outcomvar}_diff"] = aggexposure[f"{outcomvar}"] - aggexposurestatquo[f"{outcomvar}"]
            
        aggexposurediff.to_csv(f"Exposure_A{nb_agents}_{modelrun}_aggregate_diff.csv", index=False)

        differencecols = [f"{outcomvar}_diff" for outcomvar in outcomecols]
        
        aggexposure[outcomecols] = aggexposurediff[differencecols]
        
        subgroupcolorpalette = ["darkviolet", "darkorange", "teal", "lightseagreen", "aquamarine", "greenyellow", "green", "olive" ]

        
        for stratgroup in subgroups_Meta:
            print(f"Plotting the exposure stratification for {stratgroup}")
            subgroups = {stratgroup:subgroups_Meta[stratgroup]}
            subgroupcolors = {stratgroup: subgroupcolorpalette[:len(subgroups[stratgroup])]}
            NO2monthmin, NO2monthmax, NO2monthstep = calc_min_max("NO2", "weekday", subgroups[stratgroup])
            NO2hourmin, NO2hourmax, NO2hourstep = calc_min_max("NO2", "hour", subgroups[stratgroup])
            METmonthmin, METmonthmax, METmonthstep = calc_min_max("MET", "weekday", subgroups[stratgroup])
            METhourmin, METhourmax, METhourstep = calc_min_max("MET", "hour",   subgroups[stratgroup])

            print("NO2month", NO2monthmin, NO2monthmax, NO2monthstep)
            print("NO2hour", NO2hourmin, NO2hourmax, NO2hourstep)
            print("METmonth", METmonthmin, METmonthmax, METmonthstep)
            print("METhour", METhourmin, METhourmax, METhourstep)
            
            plotCircosDiffNO2MET_Timeunits(aggexposure, subgroups, subgroupcolors,  
                                        NO2monthmax=NO2monthmax, NO2monthmin=NO2monthmin, NO2monthstep=NO2monthstep,
                                            NO2hourmax=NO2hourmax, NO2hourmin=NO2hourmin, NO2hourstep=NO2hourstep,
                                            METmonthmax=METmonthmax, METmonthmin=METmonthmin, METmonthstep=METmonthstep,
                                            METhourmax=METhourmax, METhourmin=METhourmin, METhourstep=METhourstep,
                                            suffix = f"_{scenario}_{modelrun}_{stratgroup}_Difference")   

    
if "Mean across runs aggregate exposure df" in viztasks:
    if not os.path.exists(path_data+f"/{scenario}/{nb_agents}Agents/AgentExposure/MeanExposureViz"):
        # Create the directory
        os.mkdir(path_data+f"/{scenario}/{nb_agents}Agents/AgentExposure/MeanExposureViz")
    os.chdir(path_data+f"/{scenario}/{nb_agents}Agents/AgentExposure/MeanExposureViz")
    print("Creating an aggregate time stratification dataset")
    print(modelruns, popsamples)
    aggexposure = pd.read_csv(path_data+f"/{scenario}/{nb_agents}Agents/AgentExposure/{modelruns[0]}/ExposureViz/Exposure_A{nb_agents}_{modelruns[0]}_aggregate.csv")
    cols = aggexposure.columns[1:]
    for count, modelrun in enumerate(modelruns[1:]):
        aggexposure2 = pd.read_csv(path_data+f"/{scenario}/{nb_agents}Agents/AgentExposure/{modelrun}/ExposureViz/Exposure_A{nb_agents}_{modelrun}_aggregate.csv")
        aggexposure[cols] = aggexposure[cols] + aggexposure2[cols]
    aggexposure[cols] = aggexposure[cols]/len(modelruns)
    aggexposure.to_csv(f"Exposure_A{nb_agents}_Mean_{scenario}_aggregate.csv", index=False)    
    
    
if "Mean across runs exposure circle plot" in viztasks:
    os.chdir(path_data+f"/{scenario}/{nb_agents}Agents/AgentExposure/MeanExposureViz")
    aggexposure = pd.read_csv(f"Exposure_A{nb_agents}_Mean_{scenario}_aggregate.csv")
    subgroupcolorpalette = ["darkviolet", "darkorange", "teal", "green","greenyellow",  "lightseagreen", "aquamarine","olive" ]
            
    for stratgroup in subgroups_Meta:
        print(f"Plotting the exposure stratification for {stratgroup}")
        subgroups = {stratgroup:subgroups_Meta[stratgroup]}
        subgroupcolors = {stratgroup: subgroupcolorpalette[:len(subgroups[stratgroup])]}
        NO2monthmin, NO2monthmax, NO2monthstep =  calc_min_max(df = aggexposure, column="NO2", timeunit_contains= "month", round_val = 2, hardzero = True, stratvals = subgroups[stratgroup])
        NO2hourmin, NO2hourmax, NO2hourstep =  calc_min_max(df = aggexposure, column="NO2", timeunit_contains= "hour", round_val = 2, hardzero = True, stratvals = subgroups[stratgroup])
        NO2weekdaymin, NO2weekdaymax, NO2weekdaystep =  calc_min_max(df = aggexposure, column="NO2", timeunit_contains= "weekday", round_val = 2, hardzero = True, stratvals = subgroups[stratgroup])
        METmonthmin, METmonthmax, METmonthstep =  calc_min_max(df = aggexposure, column="MET", timeunit_contains= "month", round_val = 2, hardzero = True, stratvals = subgroups[stratgroup])
        METhourmin, METhourmax, METhourstep =  calc_min_max(df = aggexposure, column="MET", timeunit_contains= "hour", round_val = 2, hardzero = True, stratvals = subgroups[stratgroup])
        METweekdaymin, METweekdaymax, METweekdaystep =  calc_min_max(df = aggexposure, column="MET", timeunit_contains= "weekday", round_val = 2, hardzero = True, stratvals = subgroups[stratgroup])
 
        plotCircosNO2MET_Timeunits(aggexposure, subgroups, subgroupcolors,  
                                      NO2monthmax = NO2monthmax, METmonthmax= METmonthmax,
                                        NO2hourmax=NO2hourmax, NO2hourmin=NO2hourmin,
                                        NO2monthmin=NO2monthmin, NO2monthstep=NO2monthstep,
                                        METhourmax=METhourmax, METhourmin=METhourmin,
                                        METmonthmin=METmonthmin, METmonthstep=METmonthstep,
                                        NO2hourstep=NO2hourstep,  NO2hourround=2, NO2monthround=2,
                                        METhourstep=METhourstep,  METhourround=2, METmonthround=2,
                                    suffix = f"_{scenario}_MeanAcrossRuns_{stratgroup}")   

                      

if "Mean across runs strat exposure Circle plot" in viztasks:
    os.chdir(path_data+f"/{scenario}/{nb_agents}Agents/AgentExposure/MeanExposureViz")
    aggexposure = pd.read_csv(f"Exposure_A{nb_agents}_Mean_{scenario}_aggregate.csv")
    
    subgroupcolorpalette = ["darkviolet", "darkorange", "teal", "olive","greenyellow",  "lightseagreen", "green", "aqua", "maroon", "blue"]
    subgroupcolors = {stratgroup: subgroupcolorpalette[count] for count, stratgroup in enumerate(subgroups_Meta)}
    aggexposure_subs = aggexposure.loc[aggexposure["timeunit"]=="total",[f"{outcomevar}_{val}" for subgroup in subgroups_Meta for val in subgroups_Meta[subgroup] for outcomevar in outcomevars]]
    stratexposure_df = pd.DataFrame({f"{outcomevar}": [aggexposure_subs[f"{outcomevar}_{val}"].values for subgroup in subgroups_Meta for val in subgroups_Meta[subgroup]] for outcomevar in outcomevars})
    stratexposure_df["Label"] = [val for subgroup in subgroups_Meta for val in subgroups_Meta[subgroup]]
    stratexposure_df["Group"] = [subgroup for subgroup in subgroups_Meta for val in subgroups_Meta[subgroup]]
    for outcomevar in outcomevars:
        stratexposure_df[outcomevar] = [x[0] for x in stratexposure_df[outcomevar]]
        stratexposure_df[f"{outcomevar}_deviation"] = stratexposure_df[f"{outcomevar}"] - aggexposure.loc[aggexposure["timeunit"]=="total", outcomevar].values[0]
    print(stratexposure_df.head(20))
    stratexposure_df.to_csv(f"Exposure_A{nb_agents}_{scenario}_aggregate_strat.csv", index=False)

    subgroups_Meta["HH_type"] = ["Single Person", "Pair without\nchildren","Pair with\nchild(ren)", "Single Parent\nwith child(ren)", "Other\nmultiperson HH"]
    stratexposure_df["Label"] = stratexposure_df["Label"].replace({"Pair without children": "Pair without\nchildren",
                                                                   "Pair with children": "Pair with\nchild(ren)", 
                                                                   "Single Parent with children": "Single Parent\nwith child(ren)",
                                                                   "Other multiperson household": "Other\nmultiperson HH"})

    # drop the HH size stratification
    subgroups_Meta.pop("HH_size")
    
    if scenario == "StatusQuo":
        labelprefix = "Status Quo"
    else:
        labelprefix = "Scenario"
    # 
    plotCircosMeanStrat(stratexposure_df, subgroups= subgroups_Meta, redlinelabel=f"{labelprefix} Mean Exposure\nacross population",  rangeval=[-1.5, -0.75, 0, 0.75, 1.5],
                        subgroupcolors = subgroupcolors, meanval= aggexposure.loc[aggexposure["timeunit"]=="total", "NO2"].values[0],
                        outcomevar = "NO2_deviation", roundval = 2, centertext=f"NO2 (µg/m3)\nDeviation\nfrom Mean", suffix = "")


    plotCircosMeanStrat(stratexposure_df, subgroups= subgroups_Meta, redlinelabel="Scenario Mean Exposure\nacross population",
                        subgroupcolors = subgroupcolors, meanval= aggexposure.loc[aggexposure["timeunit"]=="total", "MET"].values[0],
                        outcomevar = "MET_deviation", roundval = 2, centertext=f"Transport MET\nDeviation\nfrom Mean", suffix = "")

if "Mean across runs and Neighborhoods" in viztasks:
    os.chdir(path_data+f"/{scenario}/{nb_agents}Agents/AgentExposure/MeanExposureViz")
    print("Creating an aggregate neighborhood exposure dataset")
    print(modelruns, popsamples)

    exposure_neigh = pd.read_csv(path_data+f"/{scenario}/{nb_agents}Agents/AgentExposure/{modelruns[0]}/ExposureViz/Exposure_A{nb_agents}_{modelruns[0]}_neigh.csv")
    exposure_neigh.sort_values("neighb_code", inplace=True)
    # rename columns with modelrun suffix
    exposure_neigh.columns = [exposure_neigh.columns.values[0]]+[f"{col}_0" for col in exposure_neigh.columns.values[1:]]    
    for count, modelrun in enumerate(modelruns[1:]):
        print(f"Adding data from modelrun {modelrun}")
        exposure_neigh2 = pd.read_csv(path_data+f"/{scenario}/{nb_agents}Agents/AgentExposure/{modelrun}/ExposureViz/Exposure_A{nb_agents}_{modelrun}_neigh.csv")
        exposure_neigh2.sort_values("neighb_code", inplace=True)
        exposure_neigh2.columns = [exposure_neigh2.columns.values[0]]+[f"{col}_{count+1}" for col in exposure_neigh2.columns.values[1:]]   
        exposure_neigh = exposure_neigh.merge(exposure_neigh2, on="neighb_code", how="outer")

        print(exposure_neigh.tail(30))

    for outcomevar in outcomevars:
        exposure_neigh[outcomevar] = exposure_neigh[[f"{outcomevar}_{count}" for count in range(len(modelruns))]].mean(axis=1)
    
    print(exposure_neigh.head(20))
    exposure_neigh.to_csv(f"Exposure_A{nb_agents}_Mean_{scenario}_neigh.csv", index=False)    
    exposure_neigh.rename(columns={"neighb_code": "buurtcode"}, inplace=True)

    outcomecols = exposure_neigh.columns[1:]
    observations = exposure_neigh[outcomecols[0:10]]
    exposure_neigh["count"] = observations.count(axis=1)
    print(exposure_neigh["count"].value_counts())

    # deleting neighborhoods where below 5 observations are available
    exposure_neigh = exposure_neigh.loc[exposure_neigh["count"]>6]
    
    print("Plotting mean status quo scenario exposure per neighborhood")

    crs = 28992    
    points = gpd.GeoSeries(
        [Point(485000, 120000), Point(485001, 120000)], crs=crs
    )  # Geographic WGS 84 - degrees
    points = points.to_crs(32619)  # Projected WGS 84 - meters
    distance_meters = points[0].distance(points[1])
    print(distance_meters)
    neighborhoods = gpd.read_file("D:\PhD EXPANSE\Data\Amsterdam\Administrative Units\Amsterdam_Neighborhoods_RDnew.shp")
    print(neighborhoods.columns)
    neighborhoods = neighborhoods.merge(exposure_neigh, on="buurtcode", how="left")

    fullnamedict["MET"] = "Transport MET (MET/h)"
    showplots = False
    maxvals = {"NO2": 16, "MET": 0.3}
    minvals = {"NO2": None, "MET": 0.1}
    for outcomvar in outcomevars:
        PlotPerNeighbOutcome(outcomvar=outcomvar, showplots=showplots, modelrun="MeanAcrossRuns", 
                            spatialdata=neighborhoods, outcomelabel=fullnamedict[outcomvar], 
                            distance_meters=distance_meters, vmax=maxvals[outcomvar], vmin = minvals[outcomvar])



if "Mean across runs aggregate exposure diff df" in viztasks:
   # read dictionary from textfile
    with open(f"D:\PhD EXPANSE\Data\Amsterdam\ABMRessources\ABMData\IntervRunDict_{scenario}.txt", "r") as f:
        IntervRunDict = eval(f.read())

    # IntervRunDict.pop(0.0)    
    print(IntervRunDict)
    keys = list(IntervRunDict)
    print(keys)
    if not os.path.exists(path_data+f"/{scenario}/{nb_agents}Agents/AgentExposure/MeanExposureViz"):
        # Create the directory
        os.mkdir(path_data+f"/{scenario}/{nb_agents}Agents/AgentExposure/MeanExposureViz")
    os.chdir(path_data+f"/{scenario}/{nb_agents}Agents/AgentExposure/MeanExposureViz")
    print("Creating an aggregate time stratification dataset")
    aggexposureStatusQ = pd.read_csv(path_data+f"/StatusQuo/{nb_agents}Agents/AgentExposure/{IntervRunDict[keys[0]]['StatusQuo']}/ExposureViz/Exposure_A{nb_agents}_{IntervRunDict[keys[0]]['StatusQuo']}_aggregate.csv")
    aggexposureInterv = pd.read_csv(path_data+f"/{scenario}/{nb_agents}Agents/AgentExposure/{IntervRunDict[keys[0]][scenario]}/ExposureViz/Exposure_A{nb_agents}_{IntervRunDict[keys[0]][scenario]}_aggregate.csv")
    cols = aggexposureStatusQ.columns[1:]
    for popsample in keys[1:]:
        aggexposureStatusQ2 = pd.read_csv(path_data+f"/StatusQuo/{nb_agents}Agents/AgentExposure/{IntervRunDict[popsample]['StatusQuo']}/ExposureViz/Exposure_A{nb_agents}_{IntervRunDict[popsample]['StatusQuo']}_aggregate.csv")
        aggexposureInterv2 = pd.read_csv(path_data+f"/{scenario}/{nb_agents}Agents/AgentExposure/{IntervRunDict[popsample][scenario]}/ExposureViz/Exposure_A{nb_agents}_{IntervRunDict[popsample][scenario]}_aggregate.csv")
        aggexposureStatusQ[cols] = aggexposureStatusQ[cols] + aggexposureStatusQ2[cols]
        aggexposureInterv[cols] = aggexposureInterv[cols] + aggexposureInterv2[cols]
    aggexposureStatusQ[cols] = aggexposureStatusQ[cols]/len(keys)
    aggexposureInterv[cols] = aggexposureInterv[cols]/len(keys)
    
    aggexposureInterv.to_csv(f"Exposure_A{nb_agents}_Mean_{scenario}_aggregate.csv", index=False)    
    aggexposureStatusQ.to_csv(f"Exposure_A{nb_agents}_Mean_StatusQuo_{scenario}_aggregate.csv", index=False)
    
    aggexposureDiff = aggexposureInterv.copy()
    aggexposureDiff[cols] = aggexposureInterv[cols] - aggexposureStatusQ[cols]
    aggexposureDiff.to_csv(f"Exposure_A{nb_agents}_Mean_{scenario}_aggregate_diff.csv", index=False)
    
    
if "Mean across runs exposure diff circle plot" in viztasks:
    os.chdir(path_data+f"/{scenario}/{nb_agents}Agents/AgentExposure/MeanExposureViz")
    aggexposure = pd.read_csv(f"Exposure_A{nb_agents}_Mean_{scenario}_aggregate_diff.csv")
    subgroupcolorpalette = ["darkviolet", "darkorange", "teal", "olive","greenyellow",  "lightseagreen", "green", "aqua", "maroon", "blue"]
            
    subgroups_Meta = {"income": ["Low", "Medium", "High"],
            "sex": ["male", "female"], 
            "migration_background": ["Dutch", "Western", "Non-Western"],
            "age_group": ["Aged 0-29", "Aged 30-59", "Aged 60+"],
            "HH_size": ["HH size 1", "HH size 2", "HH size 3", "HH size 4", "HH size 5", "HH size 6", "HH size 7"],
            "absolved_education": ["low", "middle", "high"],
            "HH_type": ["Single Person", "Pair without children", "Pair with children", "Single Parent with children", "Other multiperson household"],
            "student": ["Student", "Not Student"],
            "location": ["inside ring", "outside ring"]
            }

    
    units = ["weekday", "hour", "month"]
    outcomevars = ["NO2", "MET"]
    roundvals = [2,3]
    for stratgroup in subgroups_Meta:
        print(f"Plotting the exposure stratification for {stratgroup}")
        subgroups = {stratgroup:subgroups_Meta[stratgroup]}
        subgroupcolors = {stratgroup: subgroupcolorpalette[:len(subgroups[stratgroup])]}
        NO2monthmin, NO2monthmax, NO2monthstep =  calc_min_max(df = aggexposure, column="NO2", timeunit_contains= "month", round_val = 2, hardzero = False, stratvals = subgroups[stratgroup])
        NO2hourmin, NO2hourmax, NO2hourstep =  calc_min_max(df = aggexposure, column="NO2", timeunit_contains= "hour", round_val =2, hardzero = False, stratvals = subgroups[stratgroup])
        NO2weekdaymin, NO2weekdaymax, NO2weekdaystep =  calc_min_max(df = aggexposure, column="NO2", timeunit_contains= "weekday", round_val =2, hardzero = False, stratvals = subgroups[stratgroup])
        METmonthmin, METmonthmax, METmonthstep =  calc_min_max(df = aggexposure, column="MET", timeunit_contains= "month", round_val = 3, hardzero = False, stratvals = subgroups[stratgroup])
        METhourmin, METhourmax, METhourstep =  calc_min_max(df = aggexposure, column="MET", timeunit_contains= "hour", round_val =3, hardzero = False, stratvals = subgroups[stratgroup])
        METweekdaymin, METweekdaymax, METweekdaystep =  calc_min_max(df = aggexposure, column="MET", timeunit_contains= "weekday", round_val = 3, hardzero = False, stratvals = subgroups[stratgroup])
 
        plotCircosDiffNO2MET_Timeunits(aggexposure, subgroups, subgroupcolors,  
                                      NO2monthmax = NO2monthmax, METmonthmax= METmonthmax,
                                        NO2hourmax=NO2hourmax, NO2hourmin=NO2hourmin,
                                        NO2monthmin=NO2monthmin, NO2monthstep=NO2monthstep,
                                        NO2weekdaymax=NO2weekdaymax, NO2weekdaymin=NO2weekdaymin, NO2weekdaystep=NO2weekdaystep,
                                        METhourmax=METhourmax, METhourmin=METhourmin,
                                        METmonthmin=METmonthmin, METmonthstep=METmonthstep,
                                        METweekdaymin=METweekdaymin, METweekdaymax=METweekdaymax, METweekdaystep=METweekdaystep,
                                        NO2hourstep=NO2hourstep,  METhourstep=METhourstep,  
                                        NO2hourround=3, NO2monthround=3, METhourround=3, METmonthround=4, 
                                    suffix = f"_{scenario}_MeanDiffAcrossRuns_{stratgroup}")   
        

if "Mean across runs strat exposure diff Circle plot" in viztasks:
    os.chdir(path_data+f"/{scenario}/{nb_agents}Agents/AgentExposure/MeanExposureViz")
    aggexposure = pd.read_csv(f"Exposure_A{nb_agents}_Mean_{scenario}_aggregate.csv")
    aggexposureStatusQ = pd.read_csv(f"Exposure_A{nb_agents}_Mean_StatusQuo_{scenario}_aggregate.csv")
        
    subgroupcolorpalette = ["darkviolet", "darkorange", "teal", "olive","greenyellow",  "lightseagreen", "green", "aqua", "maroon", "blue"]
    subgroupcolors = {stratgroup: subgroupcolorpalette[count] for count, stratgroup in enumerate(subgroups_Meta)}
    aggexposure_subs = aggexposure.loc[aggexposure["timeunit"]=="total",[f"{outcomevar}_{val}" for subgroup in subgroups_Meta for val in subgroups_Meta[subgroup] for outcomevar in outcomevars]]
    stratexposure_df = pd.DataFrame({f"{outcomevar}": [aggexposure_subs[f"{outcomevar}_{val}"].values for subgroup in subgroups_Meta for val in subgroups_Meta[subgroup]] for outcomevar in outcomevars})
    stratexposure_df["Label"] = [val for subgroup in subgroups_Meta for val in subgroups_Meta[subgroup]]
    stratexposure_df["Group"] = [subgroup for subgroup in subgroups_Meta for val in subgroups_Meta[subgroup]]
    aggexposure_StatQsubs = aggexposureStatusQ.loc[aggexposureStatusQ["timeunit"]=="total",[f"{outcomevar}_{val}" for subgroup in subgroups_Meta for val in subgroups_Meta[subgroup] for outcomevar in outcomevars]]
    for outcomevar in outcomevars:
        stratexposure_df[outcomevar] = [x[0] for x in stratexposure_df[outcomevar]]
        stratexposure_df[f"{outcomevar}_deviationStatQMean"] = stratexposure_df[f"{outcomevar}"] - aggexposureStatusQ.loc[aggexposureStatusQ["timeunit"]=="total", outcomevar].values[0]
        stratexposure_df[f"{outcomevar}_StatQ"] =[aggexposure_StatQsubs[f"{outcomevar}_{val}"].values[0] for subgroup in subgroups_Meta for val in subgroups_Meta[subgroup]]
        stratexposure_df[f"{outcomevar}_diffStatQ"] = stratexposure_df[f"{outcomevar}"] - stratexposure_df[f"{outcomevar}_StatQ"]
        stratexposure_df[f"{outcomevar}_StatQdevStatQMean"] = stratexposure_df[f"{outcomevar}_StatQ"]- aggexposureStatusQ.loc[aggexposureStatusQ["timeunit"]=="total", outcomevar].values[0]
    print(stratexposure_df.head(20))
    stratexposure_df.to_csv(f"Exposure_A{nb_agents}_{scenario}_aggregate_diff_strat.csv", index=False)


    
    subgroups_Meta["HH_type"] = ["Single Person", "Pair without\nchildren","Pair with\nchild(ren)", "Single Parent\nwith child(ren)", "Other\nmultiperson HH"]
    stratexposure_df["Label"] = stratexposure_df["Label"].replace({"Pair without children": "Pair without\nchildren",
                                                                   "Pair with children": "Pair with\nchild(ren)", 
                                                                   "Single Parent with children": "Single Parent\nwith child(ren)",
                                                                   "Other multiperson household": "Other\nmultiperson HH"})
    subgroups_Meta.pop("HH_size")
    # NO2range = [-3,-2,-1,0,1]
    # NO2range = [-4,-3,-2,-1,0]
    # NO2range = [-5,-2.5, 0,2.5]
    
    # NO2range = None
    # NO2range = [-3, -2, -1, 0, 1, 2]
    NO2range = [-2, -1.5, -1, -0.5, 0, 0.5, 1]
    # NO2range = [-1.5, -1, -0.5, 0, 0.5,1]
    # NO2range = [-0.04, -0.02, 0, 0.02, 0.04]
    # NO2range = [-1.5, -0.75, 0, 0.75, 1.5]
    # NO2range = [-0.7, -0.35, 0, 0.35, 0.7]
    # METrange = [-0.01, -0.005, 0, 0.005, 0.01]
    # METrange = [-0.002, -0.001, 0, 0.001, 0.002]
    # METrange = None
    # METrange = [-0.1, -0.05, 0, 0.05, 0.1]
    METrange = [-0.08, -0.04, 0, 0.04, 0.08]
    # plotCircosMeanStrat(stratexposure_df, subgroups= subgroups_Meta, redlinelabel="Status Quo Mean\nacross popoulation", rangeval = NO2range,
    #                     subgroupcolors = subgroupcolors, meanval= aggexposureStatusQ.loc[aggexposureStatusQ["timeunit"]=="total", "NO2"].values[0],
    #                     outcomevar = "NO2_deviationStatQMean", roundval = 2, centertext=f"NO2 (µg/m3)\nDeviation to\nStatus Quo Mean", suffix = "diff_StatQMean")


    # plotCircosMeanStrat(stratexposure_df, subgroups= subgroups_Meta, redlinelabel="Status Quo Mean\nacross popoulation", 
    #                     subgroupcolors = subgroupcolors, meanval= aggexposureStatusQ.loc[aggexposureStatusQ["timeunit"]=="total", "MET"].values[0],
    #                     outcomevar = "MET_deviationStatQMean", roundval = 2, centertext=f"Transport MET\nDeviation to\nStatus Quo Mean", suffix = "diff_StatQMean")


    # plotCircosMeanStrat(stratexposure_df, subgroups= subgroups_Meta, rangeval= [-0.07, -0.035, 0, 0.035, 0.07],
    #                     subgroupcolors = subgroupcolors, meanval= 0, redlinelabel="Status Quo Mean\nof respective subgroup",
    #                     outcomevar = "NO2_diffStatQ", roundval = 2, centertext=f"NO2 (µg/m3)\nDifference to\nStatus Quo Mean", suffix = "diff_StatQ")


    # plotCircosMeanStrat(stratexposure_df, subgroups= subgroups_Meta, rangeval = METrange,
    #                     subgroupcolors = subgroupcolors, meanval= 0, redlinelabel="Status Quo Mean\nof respective subgroup",
    #                     outcomevar = "MET_diffStatQ", roundval = 2, centertext=f"Transport MET\nDifference to\nStatus Quo Mean", suffix = "diff_StatQ")

    subgroupcolorpalette = ["darkviolet", "darkorange", "teal", "olive","blue", "green", "aqua", "maroon", "blue"]
    subgroupcolors = {stratgroup: subgroupcolorpalette[count] for count, stratgroup in enumerate(subgroups_Meta)}

    plotCircosMeanStratRelativ(stratexposure_df, subgroups= subgroups_Meta, rangeval = NO2range,
                        subgroupcolors = subgroupcolors, 
                        meanvalStatQ= aggexposureStatusQ.loc[aggexposureStatusQ["timeunit"]=="total", "NO2"].values[0], 
                        meanvalScenario= aggexposure.loc[aggexposure["timeunit"]=="total", "NO2"].values[0],
                        redlinelabel="Mean across \n popoulation",
                        outcomevar = "NO2", roundval = 2, centertext=f"NO2 (µg/m3)\nChange from\nStatus Quo", suffix = "diff_beforeafterStatQ")

    plotCircosMeanStratRelativ(stratexposure_df, subgroups= subgroups_Meta, rangeval = METrange,
                        subgroupcolors = subgroupcolors, 
                        meanvalStatQ= aggexposureStatusQ.loc[aggexposureStatusQ["timeunit"]=="total", "MET"].values[0], 
                        meanvalScenario= aggexposure.loc[aggexposure["timeunit"]=="total", "MET"].values[0],
                        redlinelabel="Mean across \n popoulation",
                        outcomevar = "MET", roundval = 3, centertext=f"Transport MET\nChange from\nStatus Quo", suffix = "diff_beforeafterStatQ")



if "Mean across runs and Neighborhoods diff" in viztasks:
    os.chdir(path_data+f"/{scenario}/{nb_agents}Agents/AgentExposure/MeanExposureViz")
    print("Creating an aggregate neighborhood exposure dataset")
    print(modelruns, popsamples)

    exposure_neigh = pd.read_csv(path_data+f"/{scenario}/{nb_agents}Agents/AgentExposure/MeanExposureViz/Exposure_A{nb_agents}_Mean_{scenario}_neigh.csv")
    exposure_neigh.rename(columns={"neighb_code": "buurtcode"}, inplace=True)
    
    exposure_neighStatusQ = pd.read_csv(path_data+f"/StatusQuo/{nb_agents}Agents/AgentExposure/MeanExposureViz/Exposure_A{nb_agents}_Mean_StatusQuo_neigh.csv")
    exposure_neighStatusQ.rename(columns={"neighb_code": "buurtcode"}, inplace=True)

    exposure_neighDiff = exposure_neigh.copy()
    outcomecols = exposure_neigh.columns[1:]
    for outcomvar in outcomevars:
        exposure_neighDiff[f"{outcomvar}_diff"] = exposure_neigh[f"{outcomvar}"] - exposure_neighStatusQ[f"{outcomvar}"]
    
    exposure_neighDiff.to_csv(f"Exposure_A{nb_agents}_Mean_{scenario}_neigh_diff.csv", index=False)
    
    observations = exposure_neigh[outcomecols[0:10]]
    exposure_neighDiff["count"] = observations.count(axis=1)
    print(exposure_neighDiff["count"].value_counts())

    # deleting neighborhoods where below 5 observations are available
    exposure_neighDiff = exposure_neighDiff.loc[exposure_neighDiff["count"]>6]

    
    print("Plotting mean diff to status quo scenario exposure per neighborhood")
    crs = 28992    
    points = gpd.GeoSeries(
        [Point(485000, 120000), Point(485001, 120000)], crs=crs
    )  # Geographic WGS 84 - degrees
    points = points.to_crs(32619)  # Projected WGS 84 - meters
    distance_meters = points[0].distance(points[1])
    print(distance_meters)
    neighborhoods = gpd.read_file("D:\PhD EXPANSE\Data\Amsterdam\Administrative Units\Amsterdam_Neighborhoods_RDnew.shp")
    print(neighborhoods.columns)
    neighborhoods = neighborhoods.merge(exposure_neighDiff, on="buurtcode", how="left")

    diffoutcomevars = [f"{outcomvar}_diff" for outcomvar in outcomevars]
    fullnamedict = {"NO2_diff": "Difference in NO2 (µg/m3)", "MET_diff": "Difference in Transport MET (MET/h)"}
    showplots = False
    maxvals = {"NO2_diff": 0.2, "MET_diff": 0.02}
    minvals = {"NO2_diff": -0.75, "MET_diff": -0.02}

    for outcomvar in diffoutcomevars:
        PlotPerNeighbOutcome(outcomvar=outcomvar, showplots=showplots, modelrun="MeanAcrossRuns", 
                            spatialdata=neighborhoods, outcomelabel=fullnamedict[outcomvar], 
                            distance_meters=distance_meters, vmax=maxvals[outcomvar], vmin = minvals[outcomvar])





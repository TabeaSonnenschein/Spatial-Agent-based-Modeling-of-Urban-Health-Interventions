import matplotlib.pyplot as plt
import pandas as pd
import os
import seaborn as sns
import geopandas as gpd
from pycirclize import Circos
import numpy as np
from matplotlib.lines import Line2D
####################################################


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


def plotCircosNO2MET_Timeunits(aggexposure, subgroups, subgroupcolors, NO2monthmin = 23.5, NO2monthmax = 25, 
                               NO2hourmin=20, NO2hourmax = 30, METmonthmin = 0.75, METmonthmax = 1.25, 
                               METhourmin = 0, METhourmax = 2 , suffix = None):
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
                # Create x positions & randomized y values for data plotting
                x = outerringdict_xvalues[sector.name]
                print(sectorrows_df["NO2"].values)
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
                    NO2max = NO2hourmax
                    NO2min = NO2hourmin
                    rangeNO2 =list(np.arange(start=NO2min, stop = NO2max + 2, step = 2))
                else:
                    NO2max = NO2monthmax
                    NO2min = NO2monthmin
                    rangeNO2 =list(np.arange(start=NO2min, stop = NO2max + 0.5, step = 0.5))
                    
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
                    rangeMET =list(np.arange(start=METmin, stop = METmax + 0.5, step = 0.5))
                else:
                    METmax = METmonthmax
                    METmin = METmonthmin
                    rangeMET =list(np.arange(start=METmin, stop = METmax + 0.25, step = 0.25))
                    
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


def plotCircosDiffNO2MET_Timeunits(aggexposure, subgroups, subgroupcolors, NO2monthmin = -1, NO2monthmax = 1.5, NO2monthstep = 0.5,
                                   NO2hourmin=-1.5, NO2hourmax = 1, NO2hourstep = 0.5,
                                   METmonthmin = -1, METmonthmax = 1, METmonthstep = 0.05,
                                   METhourmin = -1, METhourmax = 1, METhourstep = 0.05,
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
        circos = Circos(outerringdict, space=13)

        for sector in circos.sectors:
            print(sector.name)
            if sector.name == "Timeunits":
                # Plot sector name
                NO2_track = sector.add_track((65, 100), r_pad_ratio=0.1)
                NO2_track.axis(ec = "none")
                NO2_track.text("Diff NO2(µg/m3)", x = NO2_track.start, color="black", adjust_rotation=True, orientation="vertical" ,size=14)

                MET_track = sector.add_track((25, 60), r_pad_ratio=0.1)
                MET_track.axis(ec = "none")
                MET_track.text("Diff MET*", x = MET_track.start, color="black", adjust_rotation=True, orientation="vertical" ,size=14)

            else:
                # Plot sector name
                sector.text(f"{sector.name}", r=125, size=14)
                sectorrows_df = aggexposure.loc[aggexposure["timeunit"].isin(sectorrows[sector.name])]
                print(sectorrows_df)
                # Create x positions & randomized y values for data plotting
                x = outerringdict_xvalues[sector.name]
                print(sectorrows_df["NO2"].values)
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
                    NO2max = NO2hourmax
                    NO2min = NO2hourmin
                    rangeNO2 =list(np.arange(start=NO2min, stop = NO2max + NO2monthstep, step = NO2monthstep))
                    rangeNO2 = [round(val, 2) for val in rangeNO2]
                    NO2max = rangeNO2[-1]
                else:
                    NO2max = NO2monthmax
                    NO2min = NO2monthmin
                    rangeNO2 =list(np.arange(start=NO2min, stop = NO2max + NO2hourstep, step = NO2hourstep))
                    rangeNO2 = [round(val, 2) for val in rangeNO2]
                    NO2max = rangeNO2[-1]

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
                    rangeMET =list(np.arange(start=METmin, stop = METmax + METmonthstep, step = METmonthstep))
                    rangeMET = [round(val, 4) for val in rangeMET]
                    METmin = rangeMET[0]
                    METmax = rangeMET[-1]
                else:
                    METmax = METmonthmax
                    METmin = METmonthmin
                    rangeMET =list(np.arange(start=METmin, stop = METmax + METhourstep, step = METhourstep))
                    rangeMET = [round(val, 4) for val in rangeMET]
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




######################################################
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
# scenario = "PrkPriceInterv"

# identify model run for scenario
experimentoverview = pd.read_csv("D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/ExperimentOverview.csv")
modelruns = experimentoverview.loc[experimentoverview["Experiment"] == scenario, "Model Run"].values
bestStatusQuo = 708658
modelruns = [708658]
# modelruns = [381609]
# modelruns = [805895]

days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
for modelrun in modelruns:
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


    agent_df = pd.read_csv(path_data+f"/{scenario}/{nb_agents}Agents/Amsterdam_population_subset{nb_agents}_{modelrun}.csv")
    print("Merging the data")
    exposure_df_vertical = pd.merge(agent_df, exposure_df_vertical, on="agent_ID", how="right")


    # # Renaming some columns for elegance
    # exposure_df_vertical = exposure_df_vertical.rename(columns={"incomeclass_int": "income", "migrationbackground": "migr_bck"})
    # exposure_df_vertical["income"] = exposure_df_vertical["income"].astype(int)
    # # restructuring data
    # exposure_df_vertical["income_class"]=exposure_df_vertical["income"].apply(lambda x: "Low" if x in range(1,5) else ("Medium" if x in range(5,9) else "High"))
    # # 1 low # 10 high
    # # restructuring age into groups
    # exposure_df_vertical["age_group"]=exposure_df_vertical["age"].apply(lambda x: "Aged 0-29y" if x in range(0,30) else ("Aged 30-59" if x in range(30,60) else "Aged 60+"))    

    # # make hh_size into a categorical variable
    # exposure_df_vertical["HH_size"] = [f"HH size {hhsize}" for hhsize in exposure_df_vertical["HH_size"]]
    
    # # print("Analyzing the data")
    # # print(exposure_df_vertical.head())
    # # print(exposure_df_vertical.info())
    # # print(exposure_df_vertical.describe())
    # # for column in exposure_df_vertical.select_dtypes(include=['object']):
    # #     print("\nValue counts for", column)
    # #     print(exposure_df_vertical[column].value_counts())


    # print("Plotting the data")
    # #################################
    # ###  Exposure stratifications ###
    # #################################
    print("Plotting the exposure stratification")
    continuousstratvars = ["income"]
    categoricalstratvars = ["sex", "migr_bck", "income_class", "age_group", "HH_size"]
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
        "NO2": "NO2 (µg/m3)",
        "MET": "Metabolic Equivalent of Task (MET)",
        "NO2_diff": "NO2 Difference (µg/m3)",
        "MET_diff": "Metabolic Equivalent of Task (MET) Difference" }
            
    # showplots = False
    # PlotVarsInLists(timevars=timevars,plottypes=plottypes, outcomevars=outcomevars, continuousstratvars=continuousstratvars,
    #                 categoricalstratvars=categoricalstratvars,showplots= showplots, modelrun=modelrun,
    #                 df=exposure_df_vertical, fullnamedict=fullnamedict)



    # #### create an aggregate dataset
    # print("Creating an aggregate dataset")
    # timeunits = ["hour", "weekday", "month"]

    # aggexposure = exposure_df_vertical[outcomevars].mean().values
    # aggexposure = pd.DataFrame([["total"]+list(aggexposure)], columns=["timeunit"]+outcomevars)
    # print(aggexposure)
    # for timeunit in timeunits:
    #     timeunitexposure = pd.DataFrame(exposure_df_vertical[[timeunit]+outcomevars].groupby(timeunit, as_index=False).mean())
    #     timeunitexposure["timeunit"] = [f"{timeunit} {unit}" for unit in timeunitexposure[timeunit]]
    #     print(timeunitexposure.head())
    #     aggexposure = pd.concat([aggexposure, timeunitexposure[["timeunit"]+outcomevars]], axis=0, ignore_index=True)
    #     print(aggexposure.head(30))   
    
    # aggexposure.index = aggexposure["timeunit"]
    # for strativar in categoricalstratvars:
    #     stratexposure = pd.DataFrame(exposure_df_vertical[[strativar]+outcomevars].groupby(strativar, as_index=False).mean())
    #     stratexposure["timeunit"] = "total"
    #     stratexposure = pd.pivot(index="timeunit", columns=strativar, values=outcomevars, data=stratexposure)
    #     stratcol = [f"{col[0]}_{col[1]}" for col in stratexposure.columns]
    #     stratexposure.columns = stratcol
    #     print(stratexposure.head())
    #     aggexposure[stratcol] = None
    #     aggexposure.loc[aggexposure["timeunit"] == "total", stratcol] = stratexposure[stratcol]
    #     for timeunit in timeunits:
    #         timeunitexposure = pd.DataFrame(exposure_df_vertical[[timeunit, strativar]+outcomevars].groupby([timeunit, strativar], as_index=False).mean())
    #         timeunitexposure["timeunit"] = [f"{timeunit} {unit}" for unit in timeunitexposure[timeunit]]
    #         timeunitexposure = pd.pivot(index="timeunit", columns=strativar, values=outcomevars, data=timeunitexposure)
    #         timeunitexposure.columns = stratcol
    #         print(timeunitexposure.head())
    #         aggexposure.loc[timeunitexposure.index, stratcol] = timeunitexposure[stratcol]
    #         print(aggexposure.head(30))
        
    # aggexposure.to_csv(f"Exposure_A{nb_agents}_{modelrun}_aggregate.csv", index=False)
    
    ##########################################################  
    ### Visualize the aggregate data in a circle plot
    ##########################################################
    
    # aggexposure = pd.read_csv(f"Exposure_A{nb_agents}_{modelrun}_aggregate.csv")

    # subgroupcolorpalette = ["darkviolet", "darkorange", "teal", "lightseagreen", "aquamarine", "greenyellow", "green", "olive" ]
        
    # subgroups_Meta = {"income": ["Low", "Medium", "High"],
    #             "sex": ["male", "female"], 
    #             "migration_background": ["Dutch", "Western", "Non-Western"],
    #             "age_group": ["Aged 0-29y", "Aged 30-59", "Aged 60+"],
    #             "HH_size": ["HH size 1", "HH size 2", "HH size 3", "HH size 4", "HH size 5", "HH size 6", "HH size 7"]}
    
    # for stratgroup in subgroups_Meta:
    #     print(f"Plotting the exposure stratification for {stratgroup}")
    #     subgroups = {stratgroup:subgroups_Meta[stratgroup]}
    #     subgroupcolors = {stratgroup: subgroupcolorpalette[:len(subgroups[stratgroup])]}
    #     if any([True if aggexposure.loc[aggexposure["timeunit"].str.contains("weekday").index,f"NO2_{val}"].min() < 23.5 else False for val in subgroups[stratgroup]]):
    #         NO2monthmin = 23
    #     else:
    #         NO2monthmin = 23.5
    #     if any([True if aggexposure.loc[aggexposure["timeunit"].str.contains("weekday").index,f"MET_{val}"].min() < 0.75 else False for val in subgroups[stratgroup]]):
    #         METmonthmin = 0.5
    #     else:
    #         METmonthmin = 0.75
    #     if any([True if aggexposure.loc[aggexposure["timeunit"].str.contains("hour").index,f"NO2_{val}"].max() > 30 else False for val in subgroups[stratgroup]]):
    #         NO2hourmax = 32
    #     else:
    #         NO2hourmax = 30
    #     if any([True if aggexposure.loc[aggexposure["timeunit"].str.contains("hour").index,f"NO2_{val}"].min() <25 else False for val in subgroups[stratgroup]]):
    #         NO2hourmin = 18
    #     else:
    #         NO2hourmin = 20
        
    #     plotCircosNO2MET_Timeunits(aggexposure, subgroups, subgroupcolors,  
    #                                NO2monthmin = NO2monthmin, METmonthmin= METmonthmin, 
    #                                NO2hourmax=NO2hourmax, NO2hourmin=NO2hourmin,
    #                                suffix = f"_{scenario}_{modelrun}_{stratgroup}")   

    ###########################################
    # map exposure per neighborhood
    ###########################################
    print("Plotting mean status quo scenario exposure per neighborhood")
    neighborhoods = gpd.read_file("D:\PhD EXPANSE\Data\Amsterdam\Administrative Units\Amsterdam_Neighborhoods_RDnew.shp")
    print(neighborhoods.columns)
    exposure_df_vertical
    exposure_neigh = exposure_df_vertical[["neighb_code"] +outcomevars].groupby(["neighb_code"],  as_index=False).mean()
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

    showplots = False
    for outcomvar in outcomevars:
        PlotPerNeighbOutcome(outcomvar=outcomvar, showplots=showplots, modelrun=modelrun, 
                             spatialdata=neighborhoods, outcomelabel=fullnamedict[outcomvar])


    # #########################
    # ### Comparative Plots ###
    # #########################

    # aggexposure = pd.read_csv(f"Exposure_A{nb_agents}_{modelrun}_aggregate.csv")
    # aggexposurestatquo = pd.read_csv(path_data + f'/StatusQuo/{nb_agents}Agents/AgentExposure/{bestStatusQuo}/ExposureViz/Exposure_A{nb_agents}_{bestStatusQuo}_aggregate.csv')


    # aggexposurediff = aggexposure.copy()
    # outcomecols = aggexposure.columns[1:]
    # for outcomvar in outcomecols:
    #     aggexposurediff[f"{outcomvar}_diff"] = aggexposure[f"{outcomvar}"] - aggexposurestatquo[f"{outcomvar}"]
        
    # aggexposurediff.to_csv(f"Exposure_A{nb_agents}_{modelrun}_aggregate_diff.csv", index=False)

    # differencecols = [f"{outcomvar}_diff" for outcomvar in outcomecols]
    
    # aggexposure[outcomecols] = aggexposurediff[differencecols]
    
    # subgroupcolorpalette = ["darkviolet", "darkorange", "teal", "lightseagreen", "aquamarine", "greenyellow", "green", "olive" ]
        
    # subgroups_Meta = {"income": ["Low", "Medium", "High"],
    #             "sex": ["male", "female"], 
    #             "migration_background": ["Dutch", "Western", "Non-Western"],
    #             "age_group": ["Aged 0-29y", "Aged 30-59", "Aged 60+"],
    #             "HH_size": ["HH size 1", "HH size 2", "HH size 3", "HH size 4", "HH size 5", "HH size 6", "HH size 7"]}
    # def calc_min_max(column_prefix, timeunit_contains, stratvals):
    #     min_val = np.min([aggexposure.loc[aggexposure["timeunit"].str.contains(timeunit_contains), f"{column_prefix}_{val}"].min() for val in stratvals]).round(2)
    #     max_val = np.max([aggexposure.loc[aggexposure["timeunit"].str.contains(timeunit_contains), f"{column_prefix}_{val}"].max() for val in stratvals]).round(2)
    #     step = ((max_val - min_val)/5).round(2)
    #     min_val = (min_val - step).round(2)  
    #     max_val = (max_val + step).round(2)
    #     step = ((max_val - min_val)/5).round(2)
    #     if step == 0:
    #         min_val = np.min([aggexposure.loc[aggexposure["timeunit"].str.contains(timeunit_contains), f"{column_prefix}_{val}"].min() for val in stratvals]).round(4)
    #         max_val = np.max([aggexposure.loc[aggexposure["timeunit"].str.contains(timeunit_contains), f"{column_prefix}_{val}"].max() for val in stratvals]).round(4)      
    #         step = ((max_val - min_val)/4).round(4)    
    #         min_val = (min_val - step).round(4)  
    #         max_val = (max_val + step).round(4)
    #         step = ((max_val - min_val)/4).round(4)
    #     return min_val, max_val, step
    
    # for stratgroup in subgroups_Meta:
    #     print(f"Plotting the exposure stratification for {stratgroup}")
    #     subgroups = {stratgroup:subgroups_Meta[stratgroup]}
    #     subgroupcolors = {stratgroup: subgroupcolorpalette[:len(subgroups[stratgroup])]}
    #     NO2monthmin, NO2monthmax, NO2monthstep = calc_min_max("NO2", "weekday", subgroups[stratgroup])
    #     NO2hourmin, NO2hourmax, NO2hourstep = calc_min_max("NO2", "hour", subgroups[stratgroup])
    #     METmonthmin, METmonthmax, METmonthstep = calc_min_max("MET", "weekday", subgroups[stratgroup])
    #     METhourmin, METhourmax, METhourstep = calc_min_max("MET", "hour",   subgroups[stratgroup])

    #     print("NO2month", NO2monthmin, NO2monthmax, NO2monthstep)
    #     print("NO2hour", NO2hourmin, NO2hourmax, NO2hourstep)
    #     print("METmonth", METmonthmin, METmonthmax, METmonthstep)
    #     print("METhour", METhourmin, METhourmax, METhourstep)
        
    #     plotCircosDiffNO2MET_Timeunits(aggexposure, subgroups, subgroupcolors,  
    #                                    NO2monthmax=NO2monthmax, NO2monthmin=NO2monthmin, NO2monthstep=NO2monthstep,
    #                                     NO2hourmax=NO2hourmax, NO2hourmin=NO2hourmin, NO2hourstep=NO2hourstep,
    #                                     METmonthmax=METmonthmax, METmonthmin=METmonthmin, METmonthstep=METmonthstep,
    #                                     METhourmax=METhourmax, METhourmin=METhourmin, METhourstep=METhourstep,
    #                                     suffix = f"_{scenario}_{modelrun}_{stratgroup}_Difference")   

    
    
    
    
    
    
    
    # print("Plotting Comparison to Status Quo over Time")
    # # read exposure data
    # modelrun_stat = "StatusQuo"
    # exposure_df_statusq = pd.read_csv(path_data + 'AgentExposure/' + modelrun_stat + f"/AgentExposure_A{nb_agents}_M1_{modelrun_stat}_hourAsRowsMerged.csv")
    # suffixes = ("_interv", "_statusq")
    # exposure_comp = pd.merge(exposure_df_vertical, exposure_df_statusq, on=["agent_ID", "hour"], how="left", suffixes=suffixes)

    # for outcomvar in outcomevars:
    #     CompareAverageExposure2Scenarios(outcomvar, ["_interv", "_statusq"], showplots, modelrun, scenariolabels=[ "After Intervention", "Before Intervention"],ylabel =  fullnamedict[outcomvar])

    # print("Plotting the difference between intervention and status quo scenario")

    # # plot the difference between intervention and status quo scenario
    # exposure_comp["NO2_diff"] = exposure_comp["NO2_interv"] -exposure_comp["NO2_statusq"]
    # exposure_comp["MET_diff"] = exposure_comp["MET_interv"] - exposure_comp["MET_statusq"]
    # exposure_comp = exposure_comp.rename(columns={"sex"+suffixes[1]: "sex", "migr_bck"+suffixes[1]: "migr_bck", "neighb_code"+suffixes[1]: "neighb_code"})

    # print(exposure_comp[["NO2_diff", "MET_diff"]].describe())
    # PlotVarsInLists(plottypes=plottypes, outcomevars=["NO2_diff", "MET_diff"], continuousstratvars=continuousstratvars,
    #                 categoricalstratvars=categoricalstratvars,showplots= showplots, modelrun=modelrun,
    #                 df=exposure_comp, fullnamedict=fullnamedict)

    # #ploting the difference between intervention and status quo scenario on average over the day
    # print("Plotting the difference between intervention and status quo scenario on average over the day")

    # print(exposure_comp.columns)
    # # restructuring the data to have the hour as a column
    # exposure_day = exposure_comp[["agent_ID", "sex", "migr_bck", "income_class", "income", "NO2_diff", "NO2_interv", "NO2_statusq", "MET_diff", "MET_interv", "MET_statusq"]].groupby(["agent_ID", "sex", "migr_bck", "income_class", "income"],  as_index=False).mean()
    # print(exposure_day.describe())


    # outcomevars = ["NO2_diff", "NO2_interv", "NO2_statusq", "MET_diff", "MET_interv", "MET_statusq"]

    # fullnamedict2 = {"NO2_diff": "NO2 Difference (µg/m3)",
    #                 "NO2_interv": "NO2 Intervention (µg/m3)",
    #                 "NO2_statusq": "NO2 Status Quo (µg/m3)",
    #                 "MET_diff": "MET Difference",
    #                 "MET_interv": "MET Intervention",
    #                 "MET_statusq": "MET Status Quo"}


    # for outcomvar in outcomevars:
    #     for stratifiers in categoricalstratvars:
    #         MeanComparisonWithoutTime(outcomvar=outcomvar, stratifier=stratifiers, showplots=showplots, modelrun=modelrun, df=exposure_day, ylabel=fullnamedict2[outcomvar], xlabel=fullnamedict[stratifiers])
            
    # ### map the change in exposure per neighborhood
    # print("Plotting the difference between intervention and status quo scenario per neighborhood")
    # neighborhoods = gpd.read_file("D:\PhD EXPANSE\Data\Amsterdam\Administrative Units\Amsterdam_Neighborhoods_RDnew.shp")
    # print(neighborhoods.columns)
    # exposure_neigh = exposure_comp[["neighb_code", "NO2_diff", "NO2_interv", "NO2_statusq", "MET_diff", "MET_interv", "MET_statusq"]].groupby(["neighb_code"],  as_index=False).mean()
    # exposure_neigh.rename(columns={"neighb_code": "buurtcode"}, inplace=True)
    # print(exposure_neigh.head())
    # neighborhoods = neighborhoods.merge(exposure_neigh, on="buurtcode", how="left")

    # def PlotPerNeighbOutcome(outcomvar, showplots, modelrun, spatialdata, outcomelabel = None):
    #     if outcomelabel is None:
    #         outcomelabel = outcomvar
    #     spatialdata.plot(outcomvar, antialiased=False, legend = True)
    #     plt.title(f"{outcomelabel} Per Neighborhood")
    #     plt.savefig(f'{modelrun}_neighbmap_{outcomvar}.pdf', dpi = 300)
    #     if showplots:
    #         plt.show()
    #     plt.close()

    # for outcomvar in outcomevars:
    #     PlotPerNeighbOutcome(outcomvar=outcomvar, showplots=showplots, modelrun=modelrun, spatialdata=neighborhoods, outcomelabel=fullnamedict2[outcomvar])
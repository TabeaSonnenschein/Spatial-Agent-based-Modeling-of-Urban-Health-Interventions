import matplotlib.pyplot as plt
import pandas as pd
import os
import seaborn as sns
import ast
import datetime
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
bestStatusQuo = 481658
modelruns = [481658]
# modelruns = [381609]

days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

viztype = [
        "singleIntervention", 
        # "statusquocomparison", 
        # "multipleRunComparison",
        # "extentvisualization",
        "extentcomparison"
        ]

extentname = "parkingprice_interventionextent"

if not os.path.exists(path_data+f"/{scenario}/{nb_agents}Agents/ModalSplit/ModalSplitViz"):
      # Create the directory
      os.mkdir(path_data+f"/{scenario}/{nb_agents}Agents/ModalSplit/ModalSplitViz")
      
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

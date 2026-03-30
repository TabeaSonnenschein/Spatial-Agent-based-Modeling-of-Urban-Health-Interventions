import pandas as pd
import os
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
from CellAutDisp import PrintSaveSummaryStats, MapSpatialDataFixedColorMapSetofVariables, ParallelMapSpatialDataFixedColorMap, ParallelMapSpatialData_StreetsFixedColorMap, ViolinOverTimeColContinous, SplitYAxis2plusLineGraph, meltPredictions, plotComputationTime,ViolinOverTimeColContinous_WithMaxSubgroups
from shapely import LineString, Point
from shapely.wkt import loads
from matplotlib.collections import LineCollection
import matplotlib.colors as mcolors
from shapely.ops import snap, split, nearest_points
import matplotlib.patches as mpatches
from matplotlib_scalebar.scalebar import ScaleBar
import matplotlib.gridspec as gridspec
import warnings
import contextily as cx


warnings.filterwarnings("ignore", message="invalid value encountered in line_locate_point")


def prepareTrackData(trackdf):
    trackdf["mode"] = trackdf["mode"].str.replace("[", "").str.replace("]", "")
    trackdf["duration"] = trackdf["duration"].str.replace("[", "").str.replace("]", "")
    trackdf["activities"] = trackdf["activities"].str.replace("[", "").str.replace("]", "").str.split(", ")
    trackdf["tripstarttime"] = trackdf["tripstarttime"].str.replace("[", "").str.replace("]", "").str.replace('datetime.datetime(', "").str.split('\), ')
    trackdf["triparrival"] = trackdf["triparrival"].str.replace("[", "").str.replace("]", "").str.replace('datetime.datetime(', "").str.split('\), ')
    trackdf["tripstarttime"] = trackdf["tripstarttime"].apply(lambda x: [y.replace(")", "") for y in x])
    trackdf["triparrival"] = trackdf["triparrival"].apply(lambda x: [y.replace(")", "") for y in x])
    trackdf["trackorder"] = 0
    # set staticagents where mode is empty
    staticagents = trackdf[trackdf["geometry"].isnull()]
    staticagents = staticagents[["agent", "activities", "activitydurations", "visitedplaces"]]
    staticagents["visitedplaces"] = staticagents["visitedplaces"].str.replace("[<", "").str.replace(">]", "")
    staticagents["geometry"] = staticagents["visitedplaces"].apply(lambda x: Point(loads(x)))
    staticagents = gpd.GeoDataFrame(staticagents, geometry="geometry", crs="epsg:28992")
    trackdf = trackdf[trackdf["geometry"].notnull()]
    trackdf["visitedplaces"] = trackdf["visitedplaces"].str.replace("<", "").str.replace(">", "").str.replace("[", "").str.replace("]", "").str.split(", ")
    trackdf_single = trackdf[trackdf["mode"].str.contains(",") == False]
    trackdf_single["tripstarttime"] = trackdf_single["tripstarttime"].apply(lambda x: x[0])
    trackdf_single["triparrival"] = trackdf_single["triparrival"].apply(lambda x: x[0])
    trackdf_multi = trackdf[trackdf["mode"].str.contains(",") == True]
    for index, row in trackdf_multi.iterrows():
        modes = row["mode"].split(",")
        geometries = row["geometry"].split(";")
        durations = row["duration"].split(",")
        for entity in range(len(modes)):
            newRow = row.copy()
            newRow["mode"] = modes[entity]
            newRow["geometry"] = geometries[entity]
            newRow["duration"] = durations[entity]
            newRow["tripstarttime"] = row["tripstarttime"][entity]
            newRow["triparrival"] = row["triparrival"][entity]
            newRow["trackorder"] = entity 
            trackdf_single = trackdf_single._append(newRow)
    trackdf_single["geometry"] = trackdf_single["geometry"].apply(lambda x: LineString(loads(x.split("; ")[0])))
    trackdf_single["mode"] = trackdf_single["mode"].str.strip().str.replace("'", "")
    trackdf_single["start_minute"] = trackdf_single["tripstarttime"].apply(lambda x: int(x.split(", ")[4]))
    trackdf_single["end_minute"] = trackdf_single["triparrival"].apply(lambda x: int(x.split(", ")[4]))
    trackdf_single["start_hour"] = trackdf_single["tripstarttime"].apply(lambda x: int(x.split(", ")[3]))
    trackdf_single["end_hour"] = trackdf_single["triparrival"].apply(lambda x: int(x.split(", ")[3]))
    trackdf_single["start_day"] = trackdf_single["tripstarttime"].apply(lambda x: int(x.split(", ")[2]))
    trackdf_single["end_day"] = trackdf_single["triparrival"].apply(lambda x: int(x.split(", ")[2]))
    trackdf_single["start_month"] = trackdf_single["tripstarttime"].apply(lambda x: int(x.split(", ")[1]))
    trackdf_single["end_month"] = trackdf_single["triparrival"].apply(lambda x: int(x.split(", ")[1]))
    gdf = gpd.GeoDataFrame(trackdf_single, geometry="geometry",crs="epsg:28992")
    return gdf, staticagents



def sampleTrackDataAndFindOverlappingTracks(gdf, sample_size = 1):
    sample = gdf.sample(sample_size)
    track_bounds = sample.total_bounds
    xlength = track_bounds[2]-track_bounds[0]
    ylength = track_bounds[3]-track_bounds[1]
    if xlength > ylength:
        lendiff = xlength - ylength
        track_bounds[1] = track_bounds[1] - lendiff/2
        track_bounds[3] = track_bounds[3] + lendiff/2                
    else:
        lendiff = ylength - xlength
        track_bounds[0] = track_bounds[0] - lendiff/2
        track_bounds[2] = track_bounds[2] + lendiff/2
    track_bounds[0] = track_bounds[0] - 500 
    track_bounds[1] = track_bounds[1] - 500
    track_bounds[2] = track_bounds[2] + 500
    track_bounds[3] = track_bounds[3] + 500
    otheroverlappingtracks = gdf.cx[track_bounds[0]:track_bounds[2], track_bounds[1]:track_bounds[3]]
    return sample, otheroverlappingtracks, track_bounds

def FindMissingAgents(synthpop, trackdf):
    coveredagents = trackdf["agent"].unique()
    allagents = synthpop["agent_ID"].unique()
    missing_agents = [agent for agent in allagents if agent not in coveredagents]
    return missing_agents


def FindingNontravelingAgentslocations(synthpop, trackdf, hour, day, points):
    crs = "epsg:28992"
    missingAgents = FindMissingAgents(synthpop = synthpop, trackdf = trackdf)
    stilllacking = missingAgents
    missinggeometries = gpd.GeoDataFrame()
    localhour = hour 
    localday = day
    while len(stilllacking) > 1500:
        print(len(stilllacking))
        previoushourtracks = pd.read_csv(f"F:/ModelRuns/PrkPriceInterv/21750Agents/Tracks/{samplerun}/AllTracks_{samplerun}_A21750_M{month}_D{localday}_H{localhour-1}_{scenario}.csv")
        gdf = prepareTrackData(previoushourtracks)
        missingagentsgeometries = gdf[gdf["agent"].isin(stilllacking)]
        missinggeometries = missinggeometries._append(missingagentsgeometries)
        stilllacking = [agent for agent in stilllacking if agent not in missingagentsgeometries["agent"].unique()]
        localhour -= 1
        if localhour ==1:
            localhour = 24
            localday -= 1
    missinggeometries["geometry_track"] = missinggeometries["geometry"].apply(lambda x: Point(x.coords[-1]))
    missinggeometries = gpd.GeoDataFrame(missinggeometries[["agent", "geometry_track"]], geometry="geometry_track", crs=crs)
     # Find the nearest points using spatial join
    missinggeometries = gpd.sjoin_nearest(missinggeometries, points, how="left", distance_col="point_distance")
    missinggeometries = missinggeometries.merge(points[['geometry']], left_on='index_right', right_index=True, suffixes=('', '_point'))
    
    missinggeometries = missinggeometries.rename(columns={"geometry": "geometry_point"})
    missinggeometries.loc[missinggeometries["point_distance"] < 25, "geometry_track"] = missinggeometries.loc[missinggeometries["point_distance"] < 25,"geometry_point"]
    
    # making sure the geometry column of  the gpd is set to geometry_track
    missinggeometries = gpd.GeoDataFrame(missinggeometries[["agent", "geometry_track"]], geometry="geometry_track")
    
    print(missinggeometries)
    return missinggeometries

def SnappingLinesToFadeOut(line):
    length = line.length
    segments = []
    segments.extend(split(snap(line,line.interpolate(100), 10), line.interpolate(100)).geoms)
    segments = [segments[0]]
    if length > 100:
        segments.extend(split(snap(segments[-1],segments[-1].interpolate(60), 10), segments[-1].interpolate(60)).geoms)
        segments = [segments[1], segments[-1]]
        segments.extend(split(snap(segments[-1],segments[-1].interpolate(10), 10), segments[-1].interpolate(10)).geoms)
        segments = [segments[0], segments[2], segments[-1]]
        segments.extend(split(snap(segments[-1],segments[-1].interpolate(10), 10), segments[-1].interpolate(10)).geoms)
        segments.extend(split(snap(segments[-1],segments[-1].interpolate(10), 10), segments[-1].interpolate(10)).geoms)
    else:
        segments.extend(split(snap(segments[-1],segments[-1].interpolate(length - 40), 10), segments[-1].interpolate(length - 40)).geoms)
        segments = [segments[1], segments[-1]]
        segments.extend(split(snap(segments[-1],segments[-1].interpolate(10), 10), segments[-1].interpolate(10)).geoms)
        segments = [segments[0], segments[2], segments[-1]]
        segments.extend(split(snap(segments[-1],segments[-1].interpolate(10), 10), segments[-1].interpolate(10)).geoms)
        segments.extend(split(snap(segments[-1],segments[-1].interpolate(10), 10), segments[-1].interpolate(10)).geoms)

    seglengths = [segment.length for segment in segments]
    segments = [segments[0]] + [segments[count+1] for count, value in enumerate(seglengths[1:]) if value < 13]
    return segments



path_data = "D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/"


random_subset = pd.read_csv(path_data+f"Population/Amsterdam_population_subset21750_0.csv")

random_subset["HH_type"] = ""
random_subset["Nrchildren"] = random_subset["Nrchildren"].astype(int)
random_subset["Nr_adults"] = random_subset["HH_size"] - random_subset["Nrchildren"]
random_subset.loc[random_subset["hh_single"]==1, "HH_type"] = "Single Person"
random_subset.loc[(random_subset["HH_size"]==2) & (random_subset["havechild"] == 0), "HH_type"] = "Pair without children"
random_subset.loc[(random_subset["HH_size"]>2) & (random_subset["havechild"] == 1), "HH_type"] = "Pair with children"
random_subset.loc[(random_subset["HH_size"]>=2) & (random_subset["havechild"] == 1) & (random_subset["Nr_adults"]==1), "HH_type"] = "Single Parent with children"
random_subset.loc[(random_subset["HH_size"]>=2) & (random_subset["Nr_adults"]>2), "HH_type"] = "Other multiperson household"


scenario = "StatusQuo"
experimentoverview = pd.read_csv("D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/ExperimentOverview.csv")
modelruns = experimentoverview.loc[experimentoverview["Experiment"] == scenario, "Model Run"].values
popsamples = [experimentoverview.loc[experimentoverview["Model Run"]== modelrun, "Population Sample"].values[0] for modelrun in modelruns]
samplerun = [modelruns[count] for count, popsample in enumerate(popsamples) if popsample == '0'][0]

# samplerun = 670942
samplerun = 870217


# create a color map 
modes = ["bike", "drive", "walk", "transit"]
print(modes)
colors = ["purple", "darkorange", "aqua", "olive","greenyellow",  "lightseagreen", "green", "aqua", "maroon", "blue"] 
modecolorlib = {"bike": colors[0], "drive": colors[1], "walk": colors[2], "transit": colors[3]}

print(modecolorlib)

crs = "epsg:28992"
points = gpd.GeoSeries(
        [Point(485000, 120000), Point(485001, 120000)], crs=crs
    )  # Geographic WGS 84 - degrees
points = points.to_crs(32619)  # Projected WGS 84 - meters
distance_meters = points[0].distance(points[1])
print(distance_meters)

spatial_extent = gpd.read_feather(path_data+"SpatialData/SpatialExtent.feather")
buildings = gpd.read_feather(path_data+"SpatialData/Buildings.feather")
streets = gpd.read_feather(path_data+"SpatialData/Streets.feather")
greenspace = gpd.read_feather(path_data+"SpatialData/Greenspace.feather")



Residences = gpd.read_feather(path_data+"SpatialData/Residences.feather")
Supermarkets = gpd.read_feather(path_data+f"SpatialData/Supermarkets15mCity.feather")
Kindergardens = gpd.read_feather(path_data+f"SpatialData/Kindergardens15mCity.feather")
Restaurants = gpd.read_feather(path_data+f"SpatialData/Restaurants15mCity.feather")
Entertainment = gpd.read_feather(path_data+f"SpatialData/Entertainment15mCity.feather")
ShopsnServ = gpd.read_feather(path_data+f"SpatialData/ShopsnServ15mCity.feather")
Nightlife = gpd.read_feather(path_data+f"SpatialData/Nightlife15mCity.feather")
Profess = gpd.read_feather(path_data+f"SpatialData/Profess15mCity.feather")

# join all the points data
allpoints = gpd.GeoDataFrame(pd.concat([Residences, Supermarkets, Kindergardens, Restaurants, Entertainment, ShopsnServ, Nightlife, Profess], ignore_index=True), crs=crs)
allpoints = allpoints.drop_duplicates(subset="geometry").reset_index(drop=True)
allpoints = allpoints[["geometry"]]

activitydict = {1: "sleep/rest", 2: "eating out", 3: "work", 4: "attending classes/lectures", 5: "at home", 6: "cooking", 7: "gardening", 8: "sports/ outdoor activity", 9: "shopping/services", 10: "social life", 11: "entertainment/culture", 13: "kindergarden"}
activitylocationdict = {1: "home", 2: "restaurant", 3: "office", 4: "school/university", 5: "home", 6: "home", 7: "home", 8: "park", 9: "shops/services", 10: "another person's home", 11: "arts & culture venue", 13: "kindergarden"}


plotvideo = False
nr_plots = 5
nr_hours = 5
hours = [8,12,14,21]
days = [3,4,2,2]

for timeslot in range(len(hours)):
    hour = hours[timeslot]
    month = 1
    day = days[timeslot]
    timestep = hour*6
    date = f"0{day}-0{month}-2019"
    print(date, "hour", hour)
    weekday = pd.to_datetime(date, format="%d-%m-%Y").weekday()
    weekday = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][weekday]

    # scheduledf = pd.read_csv(path_data+f"ActivitySchedules/HETUS2010_Synthpop_schedulesclean_{weekday}.csv")

    # sampleTracks  = pd.read_csv(f"F:/ModelRuns/PrkPriceInterv/21750Agents/Tracks/{samplerun}/AllTracks_{samplerun}_A21750_M{month}_D{day}_H{hour}_{scenario}.csv")
    sampleTracks  = pd.read_csv(path_data+ f"ModelRuns/StatusQuo/21750Agents/ForVisualization/{samplerun}/AllTracks_{samplerun}_A21750_M{month}_D{day}_H{hour}_{scenario}.csv")
    gdf, staticagents = prepareTrackData(sampleTracks)

    gdf = gdf[gdf["geometry"].isvalid]
    if plotvideo:
        while len(unique_activities) < 2:
            tracksample, otheroverlappingtracks, track_bounds = sampleTrackDataAndFindOverlappingTracks(gdf)
            otheroverlappingtracks = otheroverlappingtracks[(otheroverlappingtracks["geometry"].notnull()) & (otheroverlappingtracks["geometry"].is_valid)]
            print(tracksample)

            sampleagent = tracksample["agent"].iloc[0]
            Agentdata = random_subset[random_subset["agent_ID"] == sampleagent]
            print(Agentdata)



    else:
        for plot in range(nr_plots):
            unique_activities, activitylocations, uniqueactivitylocations = [], [], []
            while len(uniqueactivitylocations) < 2:
                tracksample, otheroverlappingtracks, track_bounds = sampleTrackDataAndFindOverlappingTracks(gdf)
                otheroverlappingtracks = otheroverlappingtracks[(otheroverlappingtracks["geometry"].notnull()) & (otheroverlappingtracks["geometry"].is_valid)]
                print(tracksample)
                
                sampleagent = tracksample["agent"].iloc[0]
                Agentdata = random_subset[random_subset["agent_ID"] == sampleagent]
                print(Agentdata)

                unique_activities = [int(float(x)) for x in tracksample["activities"].iloc[0]]
                activitylocations = [activitylocationdict[x] for x in unique_activities]
                uniqueactivitylocations = [activity for count, activity in enumerate(activitylocations) if activity not in activitylocations[:count]]
                locationchange = [count-1 for count in range(1,len(activitylocations)) if activitylocations[count] != activitylocations[count-1]]
                print(unique_activities, activitylocations, uniqueactivitylocations)
        
            if len(unique_activities) > 1:
                trackorder = tracksample["trackorder"].iloc[0]
                try:
                    previousactivity = unique_activities[locationchange[trackorder]]
                    nextactivity = unique_activities[locationchange[trackorder]+1]
                except:
                    previousactivity = unique_activities[locationchange[trackorder-1]]
                    nextactivity = unique_activities[locationchange[trackorder-1]+1]
                else:
                    pass
                # scheduletext = f"\\textbf{{Activity Schedule}}\nPrevious activity: {activitydict[previousactivity]}\nOrigin: {activitylocationdict[previousactivity]}\nNext activity: {activitydict[nextactivity]}\nDestination: {activitylocationdict[nextactivity]}"
                # triptext = f"\\textbf{{Trip}}\nMode: {tracksample['mode'].iloc[0]}\nDuration: {round(float(tracksample['duration'].iloc[0]), 2)} min\nDistance: {round(tracksample['geometry'].iloc[0].length, 2)}m\nDeparture Time: {tracksample['start_hour'].iloc[0]}:{tracksample['start_minute'].iloc[0]:02d}\nArrival Time: {tracksample['end_hour'].iloc[0]}:{tracksample['end_minute'].iloc[0]:02d}"
                scheduletext = f"Previous activity: {activitydict[previousactivity]}\nOrigin: {activitylocationdict[previousactivity]}\nNext activity: {activitydict[nextactivity]}\nDestination: {activitylocationdict[nextactivity]}"
                triptext = f"Mode: {tracksample['mode'].iloc[0]}\nDuration: {round(float(tracksample['duration'].iloc[0]), 2)} min\nDistance: {round(tracksample['geometry'].iloc[0].length, 2)}m\nDeparture Time: {tracksample['start_hour'].iloc[0]}:{tracksample['start_minute'].iloc[0]:02d}\nArrival Time: {tracksample['end_hour'].iloc[0]}:{tracksample['end_minute'].iloc[0]:02d}"
                datetime_text = f"Date: {date}\nWeekday: {weekday}"
                agent_text = f"Agent ID: {sampleagent}\nAge: {Agentdata['age'].iloc[0]}\nSex: {Agentdata['sex'].iloc[0]}\nMigration Background: {Agentdata['migrationbackground'].iloc[0]}\nIncome Decile: {Agentdata['incomeclass_int'].iloc[0]}\nHousehold Size: {Agentdata['HH_size'].iloc[0]}\n{Agentdata['HH_type'].iloc[0]}\nEmployment: {Agentdata['employed'].iloc[0]}\nEducation: {Agentdata['absolved_education'].iloc[0]}\n..."

                # missingGeometries = FindingNontravelingAgentslocations(synthpop = random_subset, trackdf = sampleTracks, hour=hour, day=day, points = allpoints)

                # # Create a figure and axis
                # fig, ax = plt.subplots(figsize=(10, 10))

                fig = plt.figure(figsize=(14, 10))
                gs = gridspec.GridSpec(1, 2, width_ratios=[3, 1])  # Control size ratio between the map and text

                # First subplot: the map
                ax_map = fig.add_subplot(gs[0])

                # Plot the data
                greenspace.plot(ax=ax_map, color="green", label="Green Spaces", alpha=0.2,  zorder= 1)
                buildings.plot(ax=ax_map, color="grey", label="Buildings", alpha=0.55, zorder= 1)
                streets.plot(ax=ax_map, color="lightgrey", linewidth=1, label="Streets", zorder= 2)

                # plot the missing agents locations
                staticagents.plot(ax=ax_map, color="forestgreen", alpha = 0.5, markersize=7, label="Agents Performing Activities", zorder = 3)

                # plot otheroverlappingtracks but color based on modecolorlib
                for mode, color in modecolorlib.items():
                    # otheroverlappingtracks[otheroverlappingtracks["mode"] == mode].plot(ax=ax, color=color, linewidth=1, alpha = 0.7, label=mode)
                    for line in otheroverlappingtracks.loc[otheroverlappingtracks["mode"] == mode, "geometry"]:
                        segments= SnappingLinesToFadeOut(line)
                        n_segments = len(segments)
                        alphas = np.linspace(0.8, 0.1, n_segments)  # Gradually decreasing alpha
                        colors = [mcolors.to_rgba(color, alpha) for alpha in alphas]

                        lc = gpd.GeoDataFrame( geometry=segments, crs=crs)
                        lc.plot(ax=ax_map, color=colors, linewidth=2, zorder=3)

                    # plot a point at the start of the track in the color
                    start_points_overlapping = otheroverlappingtracks[otheroverlappingtracks["mode"] == mode].apply(lambda x: Point(x["geometry"].coords[0]), axis=1)
                    start_points_overlapping = otheroverlappingtracks[otheroverlappingtracks["mode"] == mode]["geometry"].apply(lambda geom: Point(geom.coords[0]))

                    gpd.GeoDataFrame(geometry=start_points_overlapping, crs=crs).plot(ax=ax_map, color=color, markersize=10, zorder  = 4)
                    
                start_point =  Point(loads(tracksample["visitedplaces"].iloc[0][trackorder]))
                if tracksample["end_hour"].iloc[0] == hour:          
                    try:
                        end_point =  Point(loads(tracksample["visitedplaces"].iloc[0][trackorder+1]))
                    except:
                        # take the start and end coordinates of the track
                        end_point =  Point(tracksample["geometry"].iloc[0].coords[-1])
                        start_point =  Point(tracksample["geometry"].iloc[0].coords[0])
                    else:
                        pass
                else:
                    nexthoursampleTracks  = pd.read_csv(path_data+ f"ModelRuns/StatusQuo/21750Agents/ForVisualization/{samplerun}/AllTracks_{samplerun}_A21750_M{month}_D{day}_H{hour+1}_{scenario}.csv")
                    gdf_nexthour, staticagents_nexthour = prepareTrackData(nexthoursampleTracks)
                    nexthoursample = gdf_nexthour[gdf_nexthour["agent"] == tracksample["agent"].iloc[0]]
                    end_point =  Point(loads(nexthoursample["visitedplaces"].iloc[0][0]))
                    start_point =  Point(loads(tracksample["visitedplaces"].iloc[0][-1]))
                    
                tracksample.plot(ax=ax_map, color=modecolorlib[tracksample["mode"].iloc[0]], linewidth=3, label="Sample Track", zorder=5)
                gpd.GeoDataFrame(geometry=[start_point]).plot(ax=ax_map, color="blue", label="Origin", markersize=100, zorder=6)
                gpd.GeoDataFrame(geometry=[end_point]).plot(ax=ax_map, color="red", label="Destination", markersize=100, zorder = 6)


                ax_map.set_xlim([track_bounds[0], track_bounds[2]])  # Adding small padding
                ax_map.set_ylim([track_bounds[1], track_bounds[3]])
                cx.add_basemap(ax_map, crs=greenspace.crs, source=cx.providers.CartoDB.PositronNoLabels)

                ax_map.set_title("ABM Scene")
                ax_map.set_xlabel("Longitude")
                ax_map.set_ylabel("Latitude") 

                scalebar = ScaleBar(distance_meters, length_fraction=0.2, location="lower right", box_alpha=0.5)  # Adjust the length as needed
                ax_map.add_artist(scalebar)

                # plot text on the agent data on the left side
                fulltext = datetime_text + "\n\n\n" + triptext + "\n\n\n"+ agent_text + "\n\n\n" + scheduletext + "\n\n"

                # Second subplot: Text and Legend
                # plt.rc('text', usetex=True)
                ax_text = fig.add_subplot(gs[1])
                ax_text.axis('off')

                ax_text.text(0, 0.97, datetime_text, fontsize=10, color="black", ha="left", va="top")
                
                ax_text.text(0.5, 0.90, "Trip", fontsize=12, color="black", weight="bold", ha="center", va="top")
                ax_text.text(0, 0.87, triptext, fontsize=10, color="black", ha="left", va="top")

                ax_text.text(0.5, 0.73, "Activity Schedule", fontsize=12, color="black", weight="bold", ha="center", va="top")
                ax_text.text(0, 0.70, scheduletext, fontsize=10, color="black", ha="left", va="top")

                ax_text.text(0.5, 0.58, "Agent Attributes", fontsize=12, color="black", weight="bold", ha="center", va="top")
                ax_text.text(0, 0.55, agent_text, fontsize=10, color="black", ha="left", va="top")

                
                # ax_text.text(0, 0.99, fulltext, fontsize=10, color="black",
                #             ha="left", va="top", bbox=dict(facecolor='white', alpha=0.5, edgecolor = "white"))

                legend_elements = [
                    mpatches.Patch(facecolor='green', alpha = 0.2, edgecolor='green', label='Green Spaces'),
                    mpatches.Patch(facecolor='grey', edgecolor='grey', label='Buildings', alpha = 0.55),
                    plt.Line2D([0], [0], color='lightgrey', lw=1, label='Roads'),
                    plt.Line2D([0], [0], color='red', marker='o', lw=0, markersize=10, label='Destination'),
                    plt.Line2D([0], [0], color='blue', marker='o',  lw=0,  markersize=10, label='Origin'),
                    plt.Line2D([0], [0],color='forestgreen', alpha =0.5, marker='o',  lw=0,  markersize=7, label='Agents Performing Activities'),
                    plt.Line2D([0], [0], color=modecolorlib[tracksample["mode"].iloc[0]], lw=3, label='Sample Track')
                ]
                for mode, color in modecolorlib.items():
                    legend_elements.append(plt.Line2D([0], [0], color=color, lw=2, label=mode))

                # legend_elements.append(mpatches.Patch(facecolor='white', alpha = 0.5, edgecolor='white', label='Basemap: CartoDB'))
                
                # Position the custom legend outside the plot
                ax_text.legend(handles=legend_elements, loc='lower left', frameon=False, borderaxespad=0.,edgecolor = "white", title = "Map Legend", title_fontproperties={'weight':'bold', 'size':'12'}, fontsize=10)
                # plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05, wspace=0.3)

                # generate a random number
                random = np.random.randint(1000)

                # Show the plot
                plt.savefig(f"D:/PhD EXPANSE/Written Paper/04- Case study 1 - Transport Interventions/figures/Methodsdocs/ABMScene_{samplerun}_M{month}_D{day}_H{hour}_{scenario}_{random}.png", 
                            dpi = 600, bbox_inches = 'tight')
                plt.close()
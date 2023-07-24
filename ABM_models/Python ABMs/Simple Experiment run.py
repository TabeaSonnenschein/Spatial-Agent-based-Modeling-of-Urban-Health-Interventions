import os
import csv
import math
import random
from datetime import datetime, timedelta
from mesa import Agent, Model
from mesa.space import ContinuousSpace
from mesa.time import SimultaneousActivation
from mesa.datacollection import DataCollector
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
import pandas as pd
import shapefile as shp
# import mesa_geo
import fiona
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
from shapely.ops import nearest_points, transform
import shapely as shp
from shapely.geometry import LineString, Point, Polygon
from sklearn.neighbors import BallTree
import numpy as np
from geopandas.tools import sjoin
from functools import partial
import pyproj
import geopy.distance as distance
import requests as rq
import polyline
import subprocess

# Read Main Data
path_data = "C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/"

# Synthetic Population
print("Reading Population Data")
nb_humans = 400
pop_df = pd.read_csv(path_data+"Population/Agent_pop_clean.csv")
random_subset = pd.DataFrame(pop_df.sample(n=nb_humans))
random_subset.to_csv(path_data+"Population/Amsterdam_population_subset.csv", index=False)

# Activity Schedules
print("Reading Activity Schedules")
scheduledf_monday = pd.read_csv(path_data+"ActivitySchedules/HETUS2010_Synthpop_schedules_day1.csv")
scheduledf_tuesday = pd.read_csv(path_data+"ActivitySchedules/HETUS2010_Synthpop_schedules_day2.csv")
scheduledf_wednesday = pd.read_csv(path_data+"ActivitySchedules/HETUS2010_Synthpop_schedules_day3.csv")
scheduledf_thursday = pd.read_csv(path_data+"ActivitySchedules/HETUS2010_Synthpop_schedules_day4.csv")
scheduledf_friday = pd.read_csv(path_data+"ActivitySchedules/HETUS2010_Synthpop_schedules_day5.csv")
scheduledf_saturday = pd.read_csv(path_data+"ActivitySchedules/HETUS2010_Synthpop_schedules_day6.csv")
scheduledf_sunday = pd.read_csv(path_data+"ActivitySchedules/HETUS2010_Synthpop_schedules_day7.csv")

# Coordinate Reference System and CRS transformers
crs = "epsg:28992"
proj_WSG84 = pyproj.Proj('epsg:4326')  # WSG84
proj_CRS = pyproj.Proj(crs)
project_to_WSG84 = partial(pyproj.transform, proj_CRS, proj_WSG84)

# Start OSRM Servers
print("Starting OSRM Servers")
subprocess.call([r"C:\Users\Tabea\Documents\GitHub\Spatial-Agent-based-Modeling-of-Urban-Health-Interventions\start_OSRM_Servers.bat"])



def get_nearest(src_points, candidates, k_neighbors=1):
    """Find nearest neighbors for all source points from a set of candidate points"""

    # Create tree from the candidate points
    tree = BallTree(candidates, leaf_size=15, metric='haversine')

    # Find closest points and distances
    distances, indices = tree.query(src_points, k=k_neighbors)

    # Transpose to get distances and indices into arrays
    distances = distances.transpose()
    indices = indices.transpose()

    # Get closest indices and distances (i.e. array at index 0)
    # note: for the second closest points, you would take index 1, etc.
    closest = indices[0]
    closest_dist = distances[0]

    # Return indices and distances
    return (closest, closest_dist)


# careful with projection!!
def nearest_neighbor(left_gdf, right_gdf, return_dist=False):
    """
    For each point in left_gdf, find closest point in right GeoDataFrame and return them.

    NOTICE: Assumes that the input Points are in WGS84 projection (lat/lon).
    """

    left_geom_col = left_gdf.geometry.name
    right_geom_col = right_gdf.geometry.name

    # Ensure that index in right gdf is formed of sequential numbers
    right = right_gdf.copy().reset_index(drop=True)

    # Parse coordinates from points and insert them into a numpy array as RADIANS
    left_radians = np.array(left_gdf[left_geom_col].apply(
        lambda geom: (geom.x * np.pi / 180, geom.y * np.pi / 180)).to_list())
    right_radians = np.array(right[right_geom_col].apply(
        lambda geom: (geom.x * np.pi / 180, geom.y * np.pi / 180)).to_list())

    # Find the nearest points
    # -----------------------
    # closest ==> index in right_gdf that corresponds to the closest point
    # dist ==> distance between the nearest neighbors (in meters)

    closest, dist = get_nearest(
        src_points=left_radians, candidates=right_radians)

    # Return points from right GeoDataFrame that are closest to points in left GeoDataFrame
    closest_points = right.loc[closest]

    # Ensure that the index corresponds the one in left_gdf
    closest_points = closest_points.reset_index(drop=True)

    # Add distance if requested
    if return_dist:
        # Convert to meters from radians
        earth_radius = 6371000  # meters
        closest_points['distance'] = dist * earth_radius

    return closest_points


def buffer_in_meters(lng, lat, radius, crs):
    proj_meters = pyproj.Proj('epsg:3857')
    proj_latlng = pyproj.Proj(crs)

    project_to_meters = partial(pyproj.transform, proj_latlng, proj_meters)
    project_to_latlng = partial(pyproj.transform, proj_meters, proj_latlng)

    pt_latlng = Point(lng, lat)
    pt_meters = transform(project_to_meters, pt_latlng)

    buffer_meters = pt_meters.buffer(radius)
    return transform(project_to_latlng, buffer_meters)




def get_distance_meters(lng1, lat1, lng2, lat2, project_to_WSG84):
    # function to calculate distance between two points in meters based on geopandas
    pt1_CRS = Point(lng1, lat1)
    pt2_CRS = Point(lng2, lat2)
    pt1_WSG84 = transform(project_to_WSG84, pt1_CRS)
    pt2_WSG84 = transform(project_to_WSG84, pt2_CRS)
    return distance.distance(pt1_WSG84.coords, pt2_WSG84.coords).meters


class Humans(Agent):
    """
    Humans:
  - have realistic attributes for the city
  - have a daily activity schedule
  - have mobility behavior
  - have a home location
  - have personal exposure
    """

    def __init__(self, vector, model):
        self.unique_id = vector[0]
        super().__init__(self.unique_id, model)

        # socio-demographic attributes
        self.Neighborhood = vector[1]
        self.age = vector[2]                  # integer age 0- 100
        self.sex = vector[3]  				        # female, male
        self.migrationbackground = vector[4]  # Dutch, Western, Non-Western
        self.hh_single = vector[5] 				    # 1 = yes, 0 = no
        self.is_child = vector[6]				      # 1 = yes, 0 = no
        self.has_child = vector[7]				    # 1 = yes, 0 = no
        self.current_edu = vector[8]          # "high", "middle", "low", "no_current_edu"
        self.absolved_edu = vector[9]		      # "high", "middle", "low", 0
        self.BMI = vector[10]                 # "underweight", "normal_weight", "moderate_overweight", "obese"
        self.employment_status = vector[11]   # "has_personal_income", "no_personal_income"
        self.edu_int = vector[12] 	          # 1,2,3
        self.car_access = vector[13]          # 1 = yes, 0 = no
        self.biking_habit = vector[14]        # 1 = yes, 0 = no
        self.driving_habit = vector[15]       # 1 = yes, 0 = no
        self.transit_habit = vector[16]       # 1 = yes, 0 = no
        self.incomeclass = vector[17]         # income deciles 1-10

        # Activity Schedules
        self.ScheduleID = vector[18]          # Schedule IDs
        self.MondaySchedule = scheduledf_monday.loc[scheduledf_monday["ScheduleID"]== self.ScheduleID, ].values[0][1:]
        self.TuesdaySchedule = scheduledf_tuesday.loc[scheduledf_tuesday["ScheduleID"]== self.ScheduleID, ].values[0][1:]
        self.WednesdaySchedule = scheduledf_wednesday.loc[scheduledf_wednesday["ScheduleID"]== self.ScheduleID, ].values[0][1:]
        self.ThursdaySchedule = scheduledf_thursday.loc[scheduledf_thursday["ScheduleID"]== self.ScheduleID, ].values[0][1:]
        self.FridaySchedule = scheduledf_friday.loc[scheduledf_friday["ScheduleID"]== self.ScheduleID, ].values[0][1:]
        self.SaturdaySchedule = scheduledf_saturday.loc[scheduledf_saturday["ScheduleID"]== self.ScheduleID, ].values[0][1:]
        self.SundaySchedule = scheduledf_sunday.loc[scheduledf_sunday["ScheduleID"]== self.ScheduleID, ].values[0][1:]
        self.former_activity = self.TuesdaySchedule[int((self.model.hour * 6) + (self.model.minute / 10)-1)]
        self.activity = "perform_activity"
        
        
        # regular destinations
        try:
            self.Residence = model.Residences.loc[model.Residences["nghb_cd"] == self.Neighborhood, "geometry"].sample(1).values[0].coords[0]
        # there are some very few synthetic population agents that come from a neighborhood without residential buildings (CENSUS)
        except:
            self.Residence = model.Residences["geometry"].sample(1).values[0].coords[0]
        else:
            pass
        if self.current_edu == "high":
            self.University = model.Universities["geometry"].sample(1).values[0].coords[0]
        elif self.current_edu != "no_current_edu":
            # select school that is closest to self.Residence
            self.School = [(p.x, p.y) for p in nearest_points(Point(
                self.Residence[0], self.Residence[1]), self.model.Schools["geometry"].unary_union)][1]
        if 3 in np.concatenate((self.MondaySchedule, self.TuesdaySchedule, self.WednesdaySchedule, self.ThursdaySchedule, self.FridaySchedule, self.SaturdaySchedule, self.SundaySchedule), axis=None):
            self.Workplace = self.model.Profess["geometry"].sample(1).values[0].coords[0]

        # mobility behavior variables
        self.path_memory = 0
        self.traveldecision = 0

    def ScheduleManager(self):
      # identifying the current activity
      if self.model.weekday == 0:
        self.current_activity = self.MondaySchedule[int((self.model.hour * 6) + (self.model.minute / 10))]
      if self.model.weekday == 1:
        self.current_activity = self.TuesdaySchedule[int((self.model.hour * 6) + (self.model.minute / 10))]
      if self.model.weekday == 2:
        self.current_activity = self.WednesdaySchedule[int((self.model.hour * 6) + (self.model.minute / 10))]
      if self.model.weekday == 3:
        self.current_activity = self.ThursdaySchedule[int((self.model.hour * 6) + (self.model.minute / 10))]
      if self.model.weekday == 4:
        self.current_activity = self.FridaySchedule[int((self.model.hour * 6) + (self.model.minute / 10))]
      if self.model.weekday == 5:
        self.current_activity = self.SaturdaySchedule[int((self.model.hour * 6) + (self.model.minute / 10))]
      if self.model.weekday == 6:
        self.current_activity = self.SundaySchedule[int((self.model.hour * 6) + (self.model.minute / 10))]

        # identifying whether activity changed and if so, where the new activity is locatec and whether we have a saved route towards that destination
      if self.current_activity != self.former_activity:
        print("Activity changed")
        if self.current_activity == 3:  # 3 = work
          self.commute = 1
          self.destination_activity = self.Workplace
          if "self.homeTOwork" in locals() and (self.former_activity == 5 or self.former_activity == 1):  # 1 = sleep/rest, 5 = at home
            self.track_path = self.homeTOwork
            self.track_geometry = self.homeTOwork_geometry
            self.modalchoice = self.homeTOwork_mode
            self.track_duration = self.homeTOwork_duration
            self.path_memory = 1
            print("saved pathway")

        elif self.current_activity == 4:  # 4 = school/university
          self.edu_trip = 1
          if self.current_edu == "high":
            self.destination_activity = self.University
          else:
            self.destination_activity = self.School
          # 1 = sleep/rest, 5 = at home, 6 = cooking
          if "self.homeTOschool" in locals() and (self.former_activity in [5, 1, 6, 7]): 
            self.track_path = self.homeTOschool
            self.track_geometry = self.homeTOschool_geometry
            self.modalchoice = self.homeTOschool_mode
            self.track_duration = self.homeTOschool_duration
            self.path_memory = 1
            print("saved pathway")

        elif self.current_activity == "groceries_shopping":
          self.destination_activity = self.Supermarket
          self.groceries = 1
          # 1 = sleep/rest, 5 = at home, 6 = cooking
          if "self.homeTOsuperm" in locals() and (self.former_activity in [5, 1, 6, 7]):
            self.track_path = self.homeTOsuperm
            self.track_geometry = self.homeTOsuperm_geometry
            self.track_duration = self.homeTOsuperm_duration
            self.modalchoice = self.homeTOsuperm_mode
            self.path_memory = 1
            print("saved pathway")

        elif self.current_activity == "kindergarden":
          self.destination_activity = self.Kindergarden
          # 1 = sleep/rest, 5 = at home, 6 = cooking
          if "self.homeTOkinderga" in locals() and (self.former_activity in [5, 1, 6, 7]):
            self.track_path = self.homeTOkinderga
            self.track_geometry = self.homeTOkinderga_geometry
            self.track_duration = self.homeTOkinderga_duration
            self.modalchoice = self.homeTOkinderga_mode
            self.path_memory = 1
            print("saved pathway")

            # 1 = sleep/rest, 5 = at home, 6 = cooking
        elif self.current_activity in [5, 1, 6, 7]:
          print("home")
          self.destination_activity = self.Residence
          if "self.workTOhome" in locals() and self.former_activity == 3:  # 3 = work
              self.track_path = self.workTOhome
              self.track_geometry = self.workTOhome_geometry
              self.modalchoice = self.homeTOwork_mode
              self.track_duration = self.homeTOwork_duration
              self.path_memory = 1
              print("saved pathway_ return")

          elif "self.schoolTOhome" in locals() and self.former_activity == 4:  # 4 = school/university
              self.track_path = self.schoolTOhome
              self.track_geometry = self.schoolTOhome_geometry
              self.modalchoice = self.homeTOschool_mode
              self.track_duration = self.homeTOschool_duration
              self.path_memory = 1
              print("saved pathway_ return")

          elif "self.supermTOhome" in locals() and self.location == self.Supermarket:
              self.track_path = self.supermTOhome
              self.track_geometry = self.supermTOhome_geometry
              self.modalchoice = self.homeTOsuperm_mode
              self.track_duration = self.homeTOsuperm_duration
              self.path_memory = 1
              print("saved pathway_ return")

          elif "self.kindergaTOhome" in locals() and self.location == self.Kindergarden:
              self.track_path = self.kindergaTOhome
              self.track_geometry = self.kindergaTOhome_geometry
              self.modalchoice = self.homeTOkinderga_mode
              self.track_duration = self.homeTOkinderga_duration
              self.path_memory = 1
              print("saved pathway_ return")

        elif self.current_activity == 11:
          self.leisure = 1
          self.destination_activity = self.model.Entertainment["geometry"].sample(1).values[0].coords[0]

        elif self.current_activity == 2:  # 2 = eating
          print("eating")
          if any(self.model.Restaurants["geometry"].within(buffer_in_meters(self.pos[0], self.pos[1], 500, self.model.crs))):
              self.nearRestaurants = self.model.Restaurants["geometry"].intersection(
                  buffer_in_meters(self.pos[0], self.pos[1], 500, self.model.crs))
              self.destination_activity = self.nearRestaurants[~self.nearRestaurants.is_empty].sample(
                  1).values[0].coords[0]
          else:
              self.destination_activity = [(p.x, p.y) for p in nearest_points(Point(
                  self.pos[0], self.pos[1]), self.model.Restaurants["geometry"].unary_union)][1]

        elif self.current_activity == 10:  # 10 = social life
          self.destination_activity = self.model.Residences["geometry"].sample(1).values[0].coords[0]

        elif self.current_activity in [12, 9, 8]:  # 12 = traveling
          self.destination_activity = self.model.Residences["geometry"].sample(1).values[0].coords[0]

        print("Current Activity: ", self.current_activity," Former Activity: ", self.former_activity)

        # Identifuing whether agent needs to travel to new destination
        if self.destination_activity != self.pos:
          # self.route_eucl_line = line(container(point(self.location), point(self.destination_activity.location)))
          self.trip_distance = get_distance_meters(self.pos[0], self.pos[1], self.destination_activity[0], self.destination_activity[1], project_to_WSG84)
          print(self.trip_distance)
          if self.path_memory != 1:
              self.traveldecision = 1
          else:
              self.activity = "traveling"
              # self.track_path =  path((self.track_geometry add_point(point(self.destination_activity))))

          self.path_memory = 0

        else:
          self.activity = "perform_activity"
          self.traveldecision = 0

    def PerceiveEnvironment(self):
      # variables to be joined to route
    # ["popDns"::mean(myself.popDns), "retaiDns"::mean(myself.retaiDns), 
    #     "greenCovr"::mean(myself.greenCovr), "RdIntrsDns"::mean(myself.RdIntrsDns), 
    #     "TrafAccid"::mean(myself.TrafAccid), "NrTrees"::mean(myself.NrTrees), 
    #     "MeanTraffV"::mean(myself.MeanTraffV), "HighwLen"::mean(myself.HighwLen), "AccidPedes"::mean(myself.AccidPedes),
    #     "PedStrWidt"::mean(myself.PedStrWidt),"PedStrLen"::mean(myself.PedStrLen), 
    #     "LenBikRout"::mean(myself.LenBikRout), "DistCBD"::mean(myself.DistCBD), 
    #     "retailDiv"::mean(myself.retailDiv), "MeanSpeed"::mean(myself.MeanSpeed), "MaxSpeed"::mean(myself.MaxSpeed), 
    #     "NrStrLight"::mean(myself.NrStrLight), "CrimeIncid"::mean(myself.CrimeIncid), 
    #     "MaxNoisDay"::mean(myself.MaxNoisDay),"OpenSpace"::mean(myself.OpenSpace), 
    #     "PNonWester"::mean(myself.PNonWester), "PWelfarDep"::mean(myself.PWelfarDep)]);
      #variables to be joined to current location
      
      # (["pubTraDns"::myself.pubTraDns, "DistCBD"::myself.DistCBD]);
      #variables to be joined to destination
    # (["pubTraDns"::myself.pubTraDns, 
    #     "NrParkSpac"::myself.NrParkSpac, "PrkPricPre"::myself.PrkPricPre, 
    #     "PrkPricPos"::myself.PrkPricPos]);
      pass

    def ModeChoice(self):
      self.modechoice = "bike"

    # OSRM Routing Machine
    def Routing(self):
      if self.modechoice == "bike":
        self.server = "http://127.0.0.1:5001/"
        self.lua_profile = "bike"
      elif self.modechoice == "car":
        self.server = "http://127.0.0.1:5000/"
        self.lua_profile = "car"
      elif self.modechoice == "foot":
        self.server = "http://127.0.0.1:5002/"
        self.lua_profile = "foot"
      
      self.orig_point = transform(project_to_WSG84, Point(self.pos[0], self.pos[1]))
      self.dest_point = transform(project_to_WSG84, Point(self.destination_activity[0], self.destination_activity[1]))
      self.url = (self.server + "route/v1/"+ self.lua_profile + "/" + str(self.orig_point.y)+ ","+ str(self.orig_point.x)+ ";"+ str(self.dest_point.y)+ ","+ str(self.dest_point.x) + "?overview=full&geometries=polyline")
      self.res = rq.get(self.url).json()
      self.route = polyline.decode(self.res['routes'][0]['geometry'])


    def AtPlaceExposure(self):
      pass
    
    def TravelExposure(self):
      pass

    def step(self):
        # Schedule Manager
        if self.model.minute % 10 == 0 or self.model.minute == 0:
            self.ScheduleManager()
        else:
            pass

        # Travel Decision
        if self.traveldecision == 1:
            self.ModeChoice()
            self.activity = "traveling"
            
        if self.activity == "traveling":
            self.Routing()

class TransportAirPollutionExposureModel(Model):
    def __init__(self, nb_humans, path_data, crs="epsg:28992",
                 starting_date=datetime(2019, 1, 1, 6, 50, 0), steps_minute=5, modelrunname="intervention_scenario"):
        # Insert the global definitions, variables, and actions here
        self.path_data = path_data
        self.starting_datetime = starting_date
        self.steps_minute = timedelta(minutes=steps_minute)
        self.current_datetime = starting_date
        self.minute = self.current_datetime.minute
        self.weekday = self.current_datetime.weekday()
        self.hour = self.current_datetime.hour
        self.nb_humans = nb_humans
        self.modelrunname = modelrunname
        self.crs = crs
        self.schedule = SimultaneousActivation(self)
        print("Current time: ", self.current_datetime)
        print("Nr of Humans: ", self.nb_humans)

        # Load the spatial built environment
        self.buildings = gpd.read_feather(path_data+"FeatherDataABM/Buildings.feather")
        self.streets = gpd.read_feather(path_data+"FeatherDataABM/Streets.feather")
        self.greenspace = gpd.read_feather(path_data+"FeatherDataABM/Greenspace.feather")
        self.Residences = gpd.read_feather(path_data+"FeatherDataABM/Residences.feather")
        self.Schools = gpd.read_feather(path_data+"FeatherDataABM/Schools.feather")
        self.Supermarkets = gpd.read_feather(path_data+"FeatherDataABM/Supermarkets.feather")
        self.Universities = gpd.read_feather(path_data+"FeatherDataABM/Universities.feather")
        self.Kindergardens = gpd.read_feather(path_data+"FeatherDataABM/Kindergardens.feather")
        self.Restaurants = gpd.read_feather(path_data+"FeatherDataABM/Restaurants.feather")
        self.Entertainment = gpd.read_feather(path_data+"FeatherDataABM/Entertainment.feather")
        self.ShopsnServ = gpd.read_feather(path_data+"FeatherDataABM/ShopsnServ.feather")
        self.Nightlife = gpd.read_feather(path_data+"FeatherDataABM/Nightlife.feather")
        self.Profess = gpd.read_feather(path_data+"FeatherDataABM/Profess.feather")
        self.spatial_extent = gpd.read_feather(path_data+"FeatherDataABM/SpatialExtent.feather")
        self.EnvBehavDeterms = gpd.read_feather(path_data+"FeatherDataABM/EnvBehavDeterminants.feather")
        self.extentbox = self.spatial_extent.total_bounds
        self.continoussp = ContinuousSpace(x_max=self.extentbox[2], y_max=self.extentbox[3],
                                           torus=bool, x_min=self.extentbox[0], y_min=self.extentbox[1])

        # Load Weather data and set initial weather conditions
        self.monthly_weather_df = pd.read_csv(path_data+"Weather/monthlyWeather2019TempDiff.csv") 
        #self.daily_weather_df = pd.read_csv("D:/PhD EXPANSE/Data/Amsterdam/Weather/dailyWeather2019.csv")
        self.temperature = self.monthly_weather_df.loc[self.monthly_weather_df["month"] == self.current_datetime.month, "Temperature"].values[0]
        self.winddirection = self.monthly_weather_df.loc[self.monthly_weather_df["month"] == self.current_datetime.month, "Winddirection"].values[0]
        self.windspeed = self.monthly_weather_df.loc[self.monthly_weather_df["month"] == self.current_datetime.month, "Windspeed"].values[0]
        self.rain = self.monthly_weather_df.loc[self.monthly_weather_df["month"] == self.current_datetime.month, "Rain"].values[0]
        self.tempdifference = self.monthly_weather_df.loc[self.monthly_weather_df["month"] == self.current_datetime.month, "TempDifference"].values[0]
        print("temperature: " , self.temperature , "rain: " , self.rain , " wind: ", self.windspeed, " wind direction: ", self.winddirection, "tempdifference: ", self.tempdifference)


        # Create the agents
        for i in range(self.nb_humans):
            agent = Humans(vector=list(random_subset.iloc[i]), model=self)
            # Add the agent to a Home in their neighborhood
            self.continoussp.place_agent(agent, agent.Residence)
            self.schedule.add(agent)

        # self.dc = DataCollector(model_reporters={"agent_count":
        #                             lambda m: m.schedule.get_type_count(Humans)},
        #                         agent_reporters={"age": lambda m: (a.age for a in m.schedule.agents_by_type[Humans].values())})
    def DetermineWeather(self):
      self.temperature = self.monthly_weather_df.loc[self.monthly_weather_df["month"] == self.current_datetime.month, "Temperature"].values[0]
      self.winddirection = self.monthly_weather_df.loc[self.monthly_weather_df["month"] == self.current_datetime.month, "Winddirection"].values[0]
      self.windspeed = self.monthly_weather_df.loc[self.monthly_weather_df["month"] == self.current_datetime.month, "Windspeed"].values[0]
      self.rain = self.monthly_weather_df.loc[self.monthly_weather_df["month"] == self.current_datetime.month, "Rain"].values[0]
      self.tempdifference = self.monthly_weather_df.loc[self.monthly_weather_df["month"] == self.current_datetime.month, "TempDifference"].values[0]
      print("temperature: " , self.temperature , "rain: " , self.rain , " wind: ", self.windspeed, " wind direction: ", self.winddirection, "tempdifference: ", self.tempdifference)


    def step(self):
        # manage time variables
        self.current_datetime += self.steps_minute
        self.minute = self.current_datetime.minute
        if self.minute == 0:  # new hour
            self.hour = self.current_datetime.hour
        if self.current_datetime.hour == 0: # new day
            self.weekday = self.current_datetime.weekday()
        if self.current_datetime.day == 1 and self.current_datetime.hour == 0: # new month
            self.DetermineWeather()


        self.schedule.step()

        # self.dc.collect(self)


m = TransportAirPollutionExposureModel(
    nb_humans=nb_humans, path_data=path_data)
for t in range(1000):
    m.step()
# model_df = m.dc.get_model_vars_dataframe()
# agent_df = m.dc.get_agent_vars_dataframe()
# agent_df.head()

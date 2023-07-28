import os
import csv
import math
import random
from datetime import datetime, timedelta
from mesa import Agent, Model
from mesa.space import ContinuousSpace
from mesa.time import SimultaneousActivation, BaseScheduler
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
from shapely.ops import nearest_points, substring,transform,snap, split
import shapely as shp
from shapely.geometry import LineString, Point, Polygon, GeometryCollection
from sklearn.neighbors import BallTree
import numpy as np
from geopandas.tools import sjoin
from functools import partial
from pyproj import Transformer
import geopy.distance as distance
import requests as rq
import polyline
import subprocess
from sklearn_pmml_model.tree import PMMLTreeClassifier
import random
import multiprocessing
import cProfile
import pstats
import coiled
from distributed import Client
import dask_geopandas as dgp
import itertools as it
import warnings
warnings.filterwarnings("ignore", module="shapely")
  



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


def get_distance_meters(lng1, lat1, lng2, lat2, project_to_WSG84):
    '''function to calculate distance between two points in meters based on geopandas'''
    pt1_WSG84 =  transform(project_to_WSG84, Point(lng1, lat1))
    pt2_WSG84 = transform(project_to_WSG84, Point(lng2, lat2))
    return distance.distance(pt1_WSG84.coords, pt2_WSG84.coords).meters



def add_suffix(lst,  suffix): 
    return  list(map(lambda x: x + suffix, lst))


def reverse_geom(geom):
    def _reverse(x, y, z=None):
        if z:
            return x[::-1], y[::-1], z[::-1]
        return x[::-1], y[::-1]
    return transform(_reverse, geom)

def flip(x, y):
    """Flips the x and y coordinate values"""
    return y, x
  
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
        # self.age = vector[2]                  # integer age 0- 100
        # self.sex = vector[3]  				        # female, male
        # self.migrationbackground = vector[4]  # Dutch, Western, Non-Western
        # self.hh_single = vector[5] 				    # 1 = yes, 0 = no
        # self.is_child = vector[6]				      # 1 = yes, 0 = no
        # self.has_child = vector[7]				    # 1 = yes, 0 = no
        self.current_edu = vector[8]          # "high", "middle", "low", "no_current_edu"
        # self.absolved_edu = vector[9]		      # "high", "middle", "low", 0
        # self.BMI = vector[10]                 # "underweight", "normal_weight", "moderate_overweight", "obese"
        # self.employment_status = vector[11]   # 1 = employed, 0 = unemployed
        # self.edu_int = vector[12] 	          # 1,2,3
        # self.car_access = vector[13]          # 1 = yes, 0 = no
        # self.biking_habit = vector[14]        # 1 = yes, 0 = no
        # self.driving_habit = vector[15]       # 1 = yes, 0 = no
        # self.transit_habit = vector[16]       # 1 = yes, 0 = no
        # self.incomeclass = vector[17]         # income deciles 1-10
        self.IndModalPreds = [vector[i] for i in [19,2,13,20,21,22,17,11,12,5,7,15,14,16]]    # individual modal choice predictions: ["sex_male", "age", "car_access", 
                                                             # "Western", "Non_Western", "Dutch", 'income','employed',
                                                             #'edu_3_levels','HH_size', 'Nrchildren', 'driving_habit','biking_habit',
                                                             # 'transit_habit']
        # need to add hhsize and nrchildren

        # Activity Schedules
        self.ScheduleID = vector[18]          # Schedule IDs
        self.MondaySchedule = model.scheduledf_monday.loc[model.scheduledf_monday["ScheduleID"]== self.ScheduleID, ].values[0][1:]
        self.TuesdaySchedule = model.scheduledf_tuesday.loc[model.scheduledf_tuesday["ScheduleID"]== self.ScheduleID, ].values[0][1:]
        self.WednesdaySchedule = model.scheduledf_wednesday.loc[model.scheduledf_wednesday["ScheduleID"]== self.ScheduleID, ].values[0][1:]
        self.ThursdaySchedule = model.scheduledf_thursday.loc[model.scheduledf_thursday["ScheduleID"]== self.ScheduleID, ].values[0][1:]
        self.FridaySchedule = model.scheduledf_friday.loc[model.scheduledf_friday["ScheduleID"]== self.ScheduleID, ].values[0][1:]
        self.SaturdaySchedule = model.scheduledf_saturday.loc[model.scheduledf_saturday["ScheduleID"]== self.ScheduleID, ].values[0][1:]
        self.SundaySchedule = model.scheduledf_sunday.loc[model.scheduledf_sunday["ScheduleID"]== self.ScheduleID, ].values[0][1:]
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
            self.School = [(p.x, p.y) for p in nearest_points(Point(tuple(self.Residence)), self.model.Schools["geometry"].unary_union)][1]
        if 3 in np.concatenate((self.MondaySchedule, self.TuesdaySchedule, self.WednesdaySchedule, self.ThursdaySchedule, self.FridaySchedule, self.SaturdaySchedule, self.SundaySchedule), axis=None):
            self.Workplace = self.model.Profess["geometry"].sample(1).values[0].coords[0]

        # mobility behavior variables
        self.path_memory = 0
        self.traveldecision = 0
        self.thishourtrack, self.thishourmode = [], []

  
    def ScheduleManager(self):
      # identifying the current activity
      if self.model.weekday == 0:
        self.current_activity = self.MondaySchedule[self.model.activitystep]
      if self.model.weekday == 1:
        self.current_activity = self.TuesdaySchedule[self.model.activitystep]
      if self.model.weekday == 2:
        self.current_activity = self.WednesdaySchedule[self.model.activitystep]
      if self.model.weekday == 3:
        self.current_activity = self.ThursdaySchedule[self.model.activitystep]
      if self.model.weekday == 4:
        self.current_activity = self.FridaySchedule[self.model.activitystep]
      if self.model.weekday == 5:
        self.current_activity = self.SaturdaySchedule[self.model.activitystep]
      if self.model.weekday == 6:
        self.current_activity = self.SundaySchedule[self.model.activitystep]

        # identifying whether activity changed and if so, where the new activity is locatec and whether we have a saved route towards that destination
      if self.current_activity != self.former_activity:
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
          if "self.homeTOschool_geometry" in locals() and (self.former_activity in [5, 1, 6, 7]): 
            self.track_geometry = self.homeTOschool_geometry
            self.modalchoice = self.homeTOschool_mode
            self.track_duration = self.homeTOschool_duration
            self.path_memory = 1
            print("saved pathway")

        elif self.current_activity == "groceries_shopping":
          self.destination_activity = self.Supermarket
          self.groceries = 1
          # 1 = sleep/rest, 5 = at home, 6 = cooking
          if "self.homeTOsuperm_geometry" in locals() and (self.former_activity in [5, 1, 6, 7]):
            self.track_geometry = self.homeTOsuperm_geometry
            self.track_duration = self.homeTOsuperm_duration
            self.modalchoice = self.homeTOsuperm_mode
            self.path_memory = 1
            print("saved pathway")

        elif self.current_activity == "kindergarden":
          self.destination_activity = self.Kindergarden
          # 1 = sleep/rest, 5 = at home, 6 = cooking
          if "self.homeTOkinderga_geometry" in locals() and (self.former_activity in [5, 1, 6, 7]):
            self.track_geometry = self.homeTOkinderga_geometry
            self.track_duration = self.homeTOkinderga_duration
            self.modalchoice = self.homeTOkinderga_mode
            self.path_memory = 1
            print("saved pathway")

            # 1 = sleep/rest, 5 = at home, 6 = cooking
        elif self.current_activity in [5, 1, 6, 7]:
          self.destination_activity = self.Residence
          if "self.workTOhome_geometry" in locals() and self.former_activity == 3:  # 3 = work
              self.track_geometry = self.workTOhome_geometry
              self.modalchoice = self.homeTOwork_mode
              self.track_duration = self.homeTOwork_duration
              self.path_memory = 1
              print("saved pathway_ return")

          elif "self.schoolTOhome_geometry" in locals() and self.former_activity == 4:  # 4 = school/university
              self.track_geometry = self.schoolTOhome_geometry
              self.modalchoice = self.homeTOschool_mode
              self.track_duration = self.homeTOschool_duration
              self.path_memory = 1
              print("saved pathway_ return")

          elif "self.supermTOhome_geometry" in locals() and self.location == self.Supermarket:
              self.track_geometry = self.supermTOhome_geometry
              self.modalchoice = self.homeTOsuperm_mode
              self.track_duration = self.homeTOsuperm_duration
              self.path_memory = 1
              print("saved pathway_ return")

          elif "self.kindergaTOhome_geometry" in locals() and self.location == self.Kindergarden:
              self.track_geometry = self.kindergaTOhome_geometry
              self.modalchoice = self.homeTOkinderga_mode
              self.track_duration = self.homeTOkinderga_duration
              self.path_memory = 1
              print("saved pathway_ return")

        elif self.current_activity == 11:
          self.leisure = 1
          self.destination_activity = self.model.Entertainment["geometry"].sample(1).values[0].coords[0]

        elif self.current_activity == 2:  # 2 = eating
          if any(self.model.Restaurants["geometry"].within( Point(tuple(self.pos)).buffer(500))):
              self.nearRestaurants = self.model.Restaurants["geometry"].intersection(Point(tuple(self.pos)).buffer(500))
              self.destination_activity = self.nearRestaurants[~self.nearRestaurants.is_empty].sample(1).values[0].coords[0]

          else:
              self.destination_activity = [(p.x, p.y) for p in nearest_points(Point(tuple(self.pos)), self.model.Restaurants["geometry"].unary_union)][1]

        elif self.current_activity == 10:  # 10 = social life
          self.destination_activity = self.model.Residences["geometry"].sample(1).values[0].coords[0]

        elif self.current_activity in [12, 9, 8]:  # 12 = traveling
          self.destination_activity = self.model.Residences["geometry"].sample(1).values[0].coords[0]

        #print("Current Activity: ", self.current_activity," Former Activity: ", self.former_activity)

        # Identifuing whether agent needs to travel to new destination
        if self.destination_activity != self.pos:
          if self.path_memory != 1:
              self.traveldecision = 1
              self.route_eucl_line = LineString([Point(tuple(self.pos)), Point(tuple(self.destination_activity))])
              self.trip_distance = get_distance_meters(self.pos[0], self.pos[1], self.destination_activity[0], self.destination_activity[1], project_to_WSG84)
          else:
              self.activity = "traveling"
              self.arrival_time = self.model.current_datetime + timedelta(minutes=self.track_duration)
              self.AssignTripToTraffic()
          self.path_memory = 0

        else:
          self.activity = "perform_activity"
          self.traveldecision = 0

    def PerceiveEnvironment(self):
      # variables to be joined to route
      self.RouteVars = gpd.GeoDataFrame(data = {'id': ['1'], 'geometry': [self.route_eucl_line]}, geometry="geometry", crs=crs).sjoin(self.model.EnvBehavDeterms, how="left")[self.model.routevariables].mean(axis=0).values
      #variables to be joined to current location
      self.OrigVars = gpd.GeoDataFrame(data = {'id': ['1'], 'geometry': [Point(tuple(self.pos))]}, geometry="geometry", crs=crs).sjoin(self.model.EnvBehavDeterms, how="left")[self.model.originvariables].values[0]
      #variables to be joined to destination
      self.DestVars = gpd.GeoDataFrame(data = {'id': ['1'], 'geometry': [Point(tuple(self.destination_activity))]}, geometry="geometry",crs=crs).sjoin(self.model.EnvBehavDeterms, how="left")[self.model.destinvariables].values[0]
      
    def ModeChoice(self):
      self.pred_df = pd.DataFrame(np.concatenate((self.RouteVars, self.OrigVars, self.DestVars, self.IndModalPreds, [self.trip_distance]), axis=None).reshape(1, -1), 
                                  columns=(self.model.routevariables_suff + self.model.originvariables_suff + self.model.destinvariables_suff + self.model.personalvariables + self.model.tripvariables)).fillna(0)
      self.modechoice =self.model.ModalChoiceModel.predict(self.pred_df[self.model.OrderPredVars].values)[0].replace("1", "bike").replace("2", "drive").replace("3", "transit").replace("4", "walk")

    # OSRM Routing Machine
    def Routing(self):
      if self.modechoice == "bike":
        self.server = "http://127.0.0.1:5001/"
        self.lua_profile = "bike"
      elif self.modechoice == "drive":
        self.server = "http://127.0.0.1:5000/"
        self.lua_profile = "car"
      elif self.modechoice == "walk":
        self.server = "http://127.0.0.1:5002/"
        self.lua_profile = "foot"
      elif self.modechoice == "transit":
        self.server = "http://127.0.0.1:5002/"
        self.lua_profile = "foot"
      
      self.orig_point = transform(project_to_WSG84, Point(tuple(self.pos)))
      self.dest_point = transform(project_to_WSG84, Point(tuple(self.destination_activity)))
      self.url = (self.server + "route/v1/"+ self.lua_profile + "/" + str(self.orig_point.x)+ ","+ str(self.orig_point.y)+ ";"+ str(self.dest_point.x)+ ","+ str(self.dest_point.y) + "?overview=full&geometries=polyline")
      self.res = rq.get(self.url).json()
      self.track_geometry = transform(projecy_to_crs, transform(flip, LineString(polyline.decode(self.res['routes'][0]['geometry']))))
      self.track_duration = (self.res['routes'][0]['duration'])/60  # minutes
      if self.modechoice == "transit":
        self.track_duration = self.track_duration/10
      self.trip_distance = self.res['routes'][0]['distance']  # meters

    def SavingRoute(self):
      if(self.former_activity in [5, 1, 6, 7]):
        if self.current_activity == 3 : 
            self.homeTOwork_mode = self.modechoice
            self.homeTOwork_geometry = self.track_geometry 
            self.homeTOwork_duration = self.track_duration
            self.workTOhome_geometry = reverse_geom(self.track_geometry)
		
        elif self.current_activity == 4: 
            self.homeTOschool_mode = self.modechoice
            self.homeTOschool_geometry = self.track_geometry  
            self.homeTOschool_duration = self.track_duration
            self.schoolTOhome_geometry = reverse_geom(self.track_geometry)
			
        elif self.current_activity == "kindergarden" : 
            self.homeTOkinderga_mode = self.modechoice
            self.homeTOkinderga_geometry = self.track_geometry 
            self.homeTOkinderga_duration = self.track_duration
            self.kindergaTOhome_geometry = reverse_geom(self.track_geometry)

        elif self.current_activity == "groceries_shopping": 
            self.homeTOsuperm_mode = self.modechoice
            self.homeTOsuperm_geometry = self.track_geometry 
            self.homeTOsuperm_duration = self.track_duration
            self.supermTOhome_geometry = reverse_geom(self.track_geometry)
    
    def TravelingAlongRoute(self):
      if self.model.current_datetime >= self.arrival_time:
          self.activity = "perform_activity"
          self.pos = self.destination_activity

    def AssignTripToTraffic(self):
      if self.arrival_time.hour != self.model.hour:
          print("multihour trip")
          self.track_length = self.track_geometry.length
          self.trip_segments = [((60 - self.model.minute)/self.track_duration)]
          if (60/(self.track_duration-(60 - self.model.minute))) <1:  #if the trip intersects more than two hour slots
            self.trip_segments.extend(list(it.repeat(60/self.track_duration,int((self.track_duration-(60 - self.model.minute))/60))))
          self.segment_geometry = [self.track_geometry]
          for x in self.trip_segments:
            self.segment_geometry.extend(split(snap(self.segment_geometry[-1],self.segment_geometry[-1].interpolate(x * self.track_length), 10), self.segment_geometry[-1].interpolate(x * self.track_length)).geoms)
          print("here is the issue")
          self.segment_geometry = [self.segment_geometry[x] for x in list(range(1, len(self.segment_geometry)-1,2))+[len(self.segment_geometry)-1]]
          print(len(self.segment_geometry))
          self.thishourtrack.append(self.segment_geometry[0])
          self.thishourmode.append(self.modechoice)
          self.nexthourstracks = self.segment_geometry[1:]
          self.nexthoursmodes = list(it.repeat(self.modechoice, len(self.nexthourstracks)))
      else:
          self.thishourtrack.append(self.track_geometry)
          self.thishourmode.append(self.modechoice)
    

       
    def AtPlaceExposure(self):
      pass
    
    def TravelExposure(self):
      self.thishourtrack = gpd.GeoDataFrame(data = {'id': range(len(self.thishourtrack)), 'geometry':self.thishourtrack}, geometry="geometry", crs=crs).overlay(self.model.AirPollGrid, how="intersection")
      self.thishourtrack['length'] = self.thishourtrack.length
      
      
      self.thishourmode = [self.nexthoursmodes[0]]
      self.thishourtrack = [self.nexthourstracks[0]]
      self.nexthourstracks.pop(0)
      self.nexthoursmodes.pop(0)
      
    def step(self):
        # Schedule Manager
        if self.model.minute % 10 == 0 or self.model.minute == 0:
            self.ScheduleManager()
        else:
            pass

        # Travel Decision
        if self.traveldecision == 1:
            self.PerceiveEnvironment()
            self.ModeChoice()
            self.Routing()
            self.SavingRoute()
            self.arrival_time = self.model.current_datetime + timedelta(minutes=self.track_duration)
            self.activity = "traveling"
            self.traveldecision = 0
            self.AssignTripToTraffic()
            
        if self.activity == "traveling":
            self.TravelingAlongRoute()



class TransportAirPollutionExposureModel(Model):
    def __init__(self, nb_humans, path_data, crs="epsg:28992",
                 starting_date=datetime(2019, 1, 1, 6, 50, 0), steps_minute=10, modelrunname="intervention_scenario"):
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
        # self.schedule = ParallelScheduler(self)
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

        # Read the Environmental Stressor Data and Model
        self.AirPollGrid = gpd.read_feather(path_data+"FeatherDataABM/AirPollgrid50m.feather")

        # Read the Mode of Transport Choice Model
        print("Reading Mode of Transport Choice Model")
        self.ModalChoiceModel = PMMLTreeClassifier(pmml=path_data+"ModalChoiceModel/modalChoice.pmml")
        self.ModalChoiceModel.splitter = "random"
        self.OrderPredVars = [x for x in self.ModalChoiceModel.fields][1:]


        # self.modelvars = "allvars"
        self.modelvars = "allvars_strict"
        if self.modelvars == "allvars":
            self.routevariables = ["popDns", "retaiDns","greenCovr", "RdIntrsDns", "TrafAccid", "NrTrees", "MeanTraffV", "HighwLen", "AccidPedes",
                         "PedStrWidt", "PedStrLen", "LenBikRout", "DistCBD", "retailDiv", "MeanSpeed", "MaxSpeed", "NrStrLight", "CrimeIncid",
                          "MaxNoisDay", "OpenSpace", "PNonWester", "PWelfarDep"]
            self.personalvariables = ["sex_male", "age", "car_access", "Western", "Non_Western", "Dutch", 'income','employed',
                                   'edu_3_levels','HH_size', 'Nrchildren', 'student', 'driving_habit','biking_habit','transit_habit']
            self.tripvariables = ["trip_distance", "purpose_commute", 'purpose_leisure','purpose_groceries_shopping',
                                  'purpose_education', 'purpose_bring_person']
            self.weathervariables = ['Rain', 'Temperature', 'Winddirection', 'Windspeed']
            self.originvariables = ["pubTraDns", "DistCBD"]
            self.destinvariables = ["pubTraDns", "DistCBD", "NrParkSpac", "PrkPricPre", "PrkPricPos"]
            
        elif self.modelvars == "allvars_strict":
            self.routevariables = ["popDns", "retaiDns","greenCovr", "RdIntrsDns", "TrafAccid", "NrTrees", "MeanTraffV", "HighwLen", "AccidPedes",
                         "PedStrWidt", "PedStrLen", "LenBikRout", "DistCBD", "retailDiv", "MeanSpeed", "MaxSpeed", "MinSpeed", "NrStrLight", "CrimeIncid",
                          "MaxNoisDay", "MxNoisNigh", "OpenSpace", "PNonWester", "PWelfarDep", "pubTraDns", "SumTraffVo"]
            self.personalvariables = ["sex_male", "age", "car_access", "Western", "Non_Western", "Dutch", 'income','employed',
                                  'edu_3_levels','HH_size', 'Nrchildren', 'driving_habit','biking_habit','transit_habit']
            self.tripvariables = ["trip_distance"]
            self.originvariables = ["pubTraDns", "DistCBD"]
            self.destinvariables = ["pubTraDns", "DistCBD"]
        
        self.routevariables_suff = add_suffix(self.routevariables, ".route")
        self.originvariables_suff = add_suffix(self.originvariables, ".orig")
        self.destinvariables_suff = add_suffix(self.destinvariables, ".dest")

        # Activity Schedules
        print("Reading Activity Schedules")
        self.scheduledf_monday = pd.read_csv(path_data+"ActivitySchedules/HETUS2010_Synthpop_schedules_day1.csv")
        self.scheduledf_tuesday = pd.read_csv(path_data+"ActivitySchedules/HETUS2010_Synthpop_schedules_day2.csv")
        self.scheduledf_wednesday = pd.read_csv(path_data+"ActivitySchedules/HETUS2010_Synthpop_schedules_day3.csv")
        self.scheduledf_thursday = pd.read_csv(path_data+"ActivitySchedules/HETUS2010_Synthpop_schedules_day4.csv")
        self.scheduledf_friday = pd.read_csv(path_data+"ActivitySchedules/HETUS2010_Synthpop_schedules_day5.csv")
        self.scheduledf_saturday = pd.read_csv(path_data+"ActivitySchedules/HETUS2010_Synthpop_schedules_day6.csv")
        self.scheduledf_sunday = pd.read_csv(path_data+"ActivitySchedules/HETUS2010_Synthpop_schedules_day7.csv")


        # Create the agents
        print("Creating Agents")
        print(datetime.now())
        for i in range(self.nb_humans):
            agent = Humans(vector=list(random_subset.iloc[i]), model=self)
            # Add the agent to a Home in their neighborhood
            self.continoussp.place_agent(agent, agent.Residence)
            self.schedule.add(agent)
 
        print(datetime.now())
        # self.dc = DataCollector(model_reporters={"agent_count":
        #                             lambda m: m.schedule.get_type_count(Humans)},
        #                         agent_reporters={"age": lambda m: (a.age for a in m.schedule.agents_by_type[Humans].values())})
        print("Starting Simulation")
        
    def DetermineWeather(self):
      self.temperature = self.monthly_weather_df.loc[self.monthly_weather_df["month"] == self.current_datetime.month, "Temperature"].values[0]
      self.winddirection = self.monthly_weather_df.loc[self.monthly_weather_df["month"] == self.current_datetime.month, "Winddirection"].values[0]
      self.windspeed = self.monthly_weather_df.loc[self.monthly_weather_df["month"] == self.current_datetime.month, "Windspeed"].values[0]
      self.rain = self.monthly_weather_df.loc[self.monthly_weather_df["month"] == self.current_datetime.month, "Rain"].values[0]
      self.tempdifference = self.monthly_weather_df.loc[self.monthly_weather_df["month"] == self.current_datetime.month, "TempDifference"].values[0]
      print("temperature: " , self.temperature , "rain: " , self.rain , " wind: ", self.windspeed, " wind direction: ", self.winddirection, "tempdifference: ", self.tempdifference)

    def TrafficAssignment(self):
      pass
    
    def OnRoadEmission(self):
      pass
    
    def OffRoadDispersion(self):
      pass
    
    def step(self):
        # manage time variables
        self.current_datetime += self.steps_minute
        print(self.current_datetime)
        self.minute = self.current_datetime.minute
        if self.minute == 0:  # new hour
            print("Current time: ", self.current_datetime)
            self.hour = self.current_datetime.hour
        self.activitystep = int((self.hour * 6) + (self.minute / 10))
        if self.current_datetime.hour == 0: # new day
            self.weekday = self.current_datetime.weekday()
        if self.current_datetime.day == 1 and self.current_datetime.hour == 0: # new month
            self.DetermineWeather()


        self.schedule.step()

        # self.dc.collect(self)


if __name__ == "__main__":
  # Read Main Data
    path_data = "C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/"

    # Synthetic Population
    print("Reading Population Data")
    nb_humans = 400
    pop_df = pd.read_csv(path_data+"Population/Agent_pop_clean.csv")
    random_subset = pd.DataFrame(pop_df.sample(n=nb_humans))
    random_subset.to_csv(path_data+"Population/Amsterdam_population_subset.csv", index=False)

    # Coordinate Reference System and CRS transformers
    crs = "epsg:28992"
    project_to_WSG84 = Transformer.from_crs(crs, "epsg:4326", always_xy=True).transform
    projecy_to_crs = Transformer.from_crs("epsg:4326", crs, always_xy=True).transform
    project_to_meters = Transformer.from_crs(crs, 'epsg:3857')
    project_to_latlng = Transformer.from_crs('epsg:3857', crs, always_xy=True).transform
    
    # Start OSRM Servers
    print("Starting OSRM Servers")
    subprocess.call([r"C:\Users\Tabea\Documents\GitHub\Spatial-Agent-based-Modeling-of-Urban-Health-Interventions\start_OSRM_Servers.bat"])


    m = TransportAirPollutionExposureModel(
      nb_humans=nb_humans, path_data=path_data)
    for t in range(100):
      m.step()
    
      # # Profile the ABM run
      # cProfile.run('m.step()', 'profile_results')
      # # Print or save the profiling results
      # with open(path_data+'profile_results.txt', 'w') as f:
      #     p = pstats.Stats('profile_results', stream=f)
      #     # p.strip_dirs().sort_stats('cumulative').print_stats()
      #     p.strip_dirs().sort_stats('time').print_stats()


      
# model_df = m.dc.get_model_vars_dataframe()
# agent_df = m.dc.get_agent_vars_dataframe()
# agent_df.head()

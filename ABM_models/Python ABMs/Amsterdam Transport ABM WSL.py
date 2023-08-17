from datetime import datetime, timedelta
from mesa import Agent, Model
from mesa.space import ContinuousSpace
from mesa.time import SimultaneousActivation, BaseScheduler
from mesa.datacollection import DataCollector
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.ops import nearest_points, substring,transform,snap, split
import shapely as shp
from shapely.geometry import LineString, Point, Polygon, GeometryCollection
from sklearn.neighbors import BallTree
import numpy as np
from geopandas.tools import sjoin
from pyproj import Transformer
import geopy.distance as distance
import requests as rq
import polyline
import subprocess
from sklearn_pmml_model.tree import PMMLTreeClassifier
import itertools as it
import warnings
import concurrent.futures as cf
import cProfile
import pstats

from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import time
import multiprocessing as mp
# import logging
# import multiprocessing.util
# multiprocessing.util.log_to_stderr(level=logging.DEBUG)


warnings.filterwarnings("ignore", module="shapely")
import dns.resolver
nameserver = dns.resolver.Resolver().nameservers[0]
print("Localhost:", nameserver)
import os
n = os.cpu_count()*2

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

# ## Parallelized agent functions
# def PerceiveEnvironment(route, orig, dest, EnvBehavDeterms):
#   # variables to be joined to route
#   RouteVars = gpd.GeoDataFrame(data = {'id': ['1'], 'geometry': [route]}, geometry="geometry", crs="epsg:28992").sjoin(EnvBehavDeterms, how="left")[["popDns", "retaiDns","greenCovr", "RdIntrsDns", "TrafAccid", "NrTrees", "MeanTraffV", "HighwLen", "AccidPedes",
#                          "PedStrWidt", "PedStrLen", "LenBikRout", "DistCBD", "retailDiv", "MeanSpeed", "MaxSpeed", "MinSpeed", "NrStrLight", "CrimeIncid",
#                           "MaxNoisDay", "MxNoisNigh", "OpenSpace", "PNonWester", "PWelfarDep", "pubTraDns", "SumTraffVo"]].mean(axis=0).values
#   #variables to be joined to current location
#   OrigVars = gpd.GeoDataFrame(data = {'id': ['1'], 'geometry': [Point(tuple(orig))]}, geometry="geometry", crs="epsg:28992").sjoin(EnvBehavDeterms, how="left")[["pubTraDns", "DistCBD"]].values[0]
#   #variables to be joined to destination
#   DestVars = gpd.GeoDataFrame(data = {'id': ['1'], 'geometry': [Point(tuple(dest))]}, geometry="geometry",crs="epsg:28992").sjoin(EnvBehavDeterms, how="left")[["pubTraDns", "DistCBD"]].values[0]
#   return RouteVars, OrigVars, DestVars
    
def RetrieveRoutes(thishourmode, thishourtrack):
   if "drive" in thishourmode:
      return([thishourtrack[count] for count, value in enumerate(thishourmode) if value == "drive"])


class Humans(Agent):
    """
    Humans:
  - have realistic attributes for the city
  - have a daily activity schedule
  - have mobility behavior
  - have a home location
  - have personal exposure
    """

    def __init__(self,x, model):
        vector = random_subset.iloc[x]
        self.unique_id = vector[0]
        super().__init__(self.unique_id, model)
        # socio-demographic attributes
        self.Neighborhood = vector[1]
        self.current_edu = vector[8]          # "high", "middle", "low", "no_current_edu"
        self.IndModalPreds = [vector[i] for i in [19,2,13,20,21,22,17,11,12,5,7,15,14,16]]    # individual modal choice predictions: ["sex_male", "age", "car_access", 
                                                             # "Western", "Non_Western", "Dutch", 'income','employed',
                                                             #'edu_3_levels','HH_size', 'Nrchildren', 'driving_habit','biking_habit',
                                                             # 'transit_habit']
        # need to add hhsize and nrchildren

        # Activity Schedules
        self.ScheduleID = vector[18]          # Schedule IDs
        self.WeekSchedules = []
        for i in range(7):
          self.WeekSchedules.append(list(schedulelist[i].loc[schedulelist[i]["ScheduleID"]== self.ScheduleID, ].values[0][1:]))
        self.former_activity = self.WeekSchedules[self.model.weekday][self.model.activitystep]
        self.activity = "perform_activity"
        self.weekday = self.model.weekday
        self.activitystep=self.model.activitystep
        
        # regular destinations
        try:
            self.Residence = Residences.loc[Residences["nghb_cd"] == self.Neighborhood, "geometry"].sample(1).values[0].coords[0]
        # there are some very few synthetic population agents that come from a neighborhood without residential buildings (CENSUS)
        except:
            self.Residence = Residences["geometry"].sample(1).values[0].coords[0]
        else:
            pass
        if self.current_edu == "high":
            self.University = Universities["geometry"].sample(1).values[0].coords[0]
        elif self.current_edu != "no_current_edu":
            # select school that is closest to self.Residence
            self.School = [(p.x, p.y) for p in nearest_points(Point(tuple(self.Residence)), Schools["geometry"].unary_union)][1]
        if 3 in list(np.concatenate(self.WeekSchedules).flat):
            self.Workplace = Profess["geometry"].sample(1).values[0].coords[0]

        # mobility behavior variables
        self.path_memory = 0
        self.traveldecision = 0
        self.thishourtrack, self.thishourmode = [], []
        self.nexthoursmodes, self.nexthourstracks = [], []  

        # exposure variables
        self.visitedPlaces = [Point(tuple(self.Residence))]
        self.newplace = 0
        self.durationPlaces = [0]
        self.hourlytravelNO2, self.hourlyplaceNO2, self.hourlyNO2 = 0,0,0
        
    def ScheduleManager(self, current_datetime):
      # identifying the current activity
      self.current_activity = self.WeekSchedules[self.weekday][self.activitystep]
      # identifying whether activity changed and if so, where the new activity is locatec and whether we have a saved route towards that destination
      if self.current_activity != self.former_activity:
        # print("Current Activity: ", self.current_activity," Former Activity: ", self.former_activity)
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
          self.destination_activity = Entertainment["geometry"].sample(1).values[0].coords[0]

        elif self.current_activity == 2:  # 2 = eating
          if any(Restaurants["geometry"].within( Point(tuple(self.pos)).buffer(500))):
              self.nearRestaurants = Restaurants["geometry"].intersection(Point(tuple(self.pos)).buffer(500))
              self.destination_activity = self.nearRestaurants[~self.nearRestaurants.is_empty].sample(1).values[0].coords[0]

          else:
              self.destination_activity = [(p.x, p.y) for p in nearest_points(Point(tuple(self.pos)), Restaurants["geometry"].unary_union)][1]

        elif self.current_activity == 10:  # 10 = social life
          self.destination_activity = Residences["geometry"].sample(1).values[0].coords[0]

        elif self.current_activity in [12, 9, 8]:  # 12 = traveling
          self.destination_activity = Residences["geometry"].sample(1).values[0].coords[0]


        # Identifuing whether agent needs to travel to new destination
        if self.destination_activity != self.pos:
          if self.path_memory != 1:
              self.traveldecision = 1
              self.route_eucl_line = LineString([Point(tuple(self.pos)), Point(tuple(self.destination_activity))])
              self.trip_distance = self.route_eucl_line.length
          else:
              self.activity = "traveling"
              self.arrival_time = current_datetime + timedelta(minutes=self.track_duration)
          self.path_memory = 0
          self.newplace = 1
        else:
          self.activity = "perform_activity"
          self.traveldecision = 0

    def PerceiveEnvironment(self):
      # variables to be joined to route
      self.RouteVars = gpd.GeoDataFrame(data = {'id': ['1'], 'geometry': [self.route_eucl_line]}, geometry="geometry", crs=crs).sjoin(EnvBehavDeterms, how="left")[routevariables].mean(axis=0).values
      #variables to be joined to current location
      self.OrigVars = gpd.GeoDataFrame(data = {'id': ['1'], 'geometry': [Point(tuple(self.pos))]}, geometry="geometry", crs=crs).sjoin(EnvBehavDeterms, how="left")[originvariables].values[0]
      #variables to be joined to destination
      self.DestVars = gpd.GeoDataFrame(data = {'id': ['1'], 'geometry': [Point(tuple(self.destination_activity))]}, geometry="geometry",crs=crs).sjoin(EnvBehavDeterms, how="left")[destinvariables].values[0]

    def ModeChoice(self):
      self.pred_df = pd.DataFrame(np.concatenate((self.RouteVars, self.OrigVars, self.DestVars, self.IndModalPreds, [self.trip_distance]), axis=None).reshape(1, -1), 
                                  columns=(routevariables_suff + originvariables_suff + destinvariables_suff + personalvariables + tripvariables)).fillna(0)
      self.modechoice =ModalChoiceModel.predict(self.pred_df[OrderPredVars].values)[0].replace("1", "bike").replace("2", "drive").replace("3", "transit").replace("4", "walk")

    # OSRM Routing Machine
    def Routing(self):
      if self.modechoice == "bike":
        self.server = ":5001/"
        self.lua_profile = "bike"
      elif self.modechoice == "drive":
        self.server = ":5000/"
        self.lua_profile = "car"
      elif self.modechoice == "walk":
        self.server = ":5002/"
        self.lua_profile = "foot"
      elif self.modechoice == "transit":
        self.server = ":5002/"
        self.lua_profile = "foot"
      
      self.orig_point = transform(project_to_WSG84, Point(tuple(self.pos)))
      self.dest_point = transform(project_to_WSG84, Point(tuple(self.destination_activity)))
      self.url = ("http://" + nameserver + self.server + "route/v1/"+ self.lua_profile + "/" + str(self.orig_point.x)+ ","+ str(self.orig_point.y)+ ";"+ str(self.dest_point.x)+ ","+ str(self.dest_point.y) + "?overview=full&geometries=polyline")
      self.res = rq.get(self.url).json()
      self.track_geometry = transform(projecy_to_crs, transform(flip, LineString(polyline.decode(self.res['routes'][0]['geometry']))))
      self.track_duration = (self.res['routes'][0]['duration'])/60  # minutes
      if self.modechoice == "transit":
        self.track_duration = self.track_duration/10
      self.trip_distance = self.res['routes'][0]['distance']  # meters

    def RoutingDummy(self):
      self.track_geometry = self.route_eucl_line
      self.track_duration  = 20
      self.trip_distance = 200
      
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
    
    def TravelingAlongRoute(self, current_datetime):
      if current_datetime >= self.arrival_time:
          self.activity = "perform_activity"
          self.pos = self.destination_activity

    def TripSegmentsPerHour(self):
      if self.arrival_time.hour != self.hour:
          self.track_length = self.track_geometry.length
          self.trip_segments = [((60 - self.minute)/self.track_duration)]
          if (self.track_duration-(60 - self.minute)) > 60:  #if the trip intersects more than two hour slots
            self.trip_segments.extend(list(it.repeat(60/self.track_duration,int((self.track_duration-(60 - self.minute))/60))))
          self.segment_geometry = [self.track_geometry]
          for x in self.trip_segments:
            self.segment_geometry.extend(split(snap(self.segment_geometry[-1],self.segment_geometry[-1].interpolate(x * self.track_length), 10), self.segment_geometry[-1].interpolate(x * self.track_length)).geoms)
          self.segment_geometry = [self.segment_geometry[x] for x in list(range(1, len(self.segment_geometry)-1,2))+[len(self.segment_geometry)-1]]
          self.thishourtrack.append(self.segment_geometry[0])
          self.thishourmode.append(self.modechoice)
          self.nexthourstracks = self.segment_geometry[1:]
          self.nexthoursmodes = list(it.repeat(self.modechoice, len(self.nexthourstracks)))
      else:
          self.thishourtrack.append(self.track_geometry)
          self.thishourmode.append(self.modechoice)
    
       
    def PlaceTracker(self):
        if self.newplace == 1:
          self.visitedPlaces.append(Point(tuple(self.pos)))
          self.durationPlaces.append(1)
          self.newplace = 0
        else:
          self.durationPlaces[-1] += 1



    def AtPlaceExposure(self):
        self.thishourplaces = gpd.sjoin(gpd.GeoDataFrame(data = {'duration': self.durationPlaces, 'geometry':self.visitedPlaces}, geometry="geometry", crs=crs),AirPollGrid, how="inner", predicate= "intersects")
        self.hourlyplaceNO2 = sum(self.thishourplaces['NO2'] * (self.thishourplaces['duration']/6))
        if self.activity== "perform_activity":
          self.visitedPlaces = [self.visitedPlaces[-1]]
          self.durationPlaces = [0]
        else:
          self.visitedPlaces = []
          self.durationPlaces = []
    
    def TravelExposure(self):
      if len(self.thishourtrack) > 0:       # transform overlay function to point in polygon, get points along line (10m), joining points with grid cellsize/2
        self.thishourtrack = gpd.GeoDataFrame(data = {'mode': self.thishourmode, 'geometry':self.thishourtrack}, geometry="geometry", crs=crs).overlay(AirPollGrid, how="intersection")
        self.thishourtrack['length'] = self.thishourtrack.length
        self.thishourtrack['speed']= self.thishourtrack['mode'].replace({'bike': 12000, 'drive': 30000, 'walk': 5000, 'transit': 50000})
        self.hourlytravelNO2 = sum(self.thishourtrack['NO2'] * (self.thishourtrack['length'] / self.thishourtrack['speed']))
        if len(self.nexthourstracks) > 0:
          self.thishourmode = [self.nexthoursmodes[0]]
          self.thishourtrack = [self.nexthourstracks[0]]
          self.nexthourstracks.pop(0)
          self.nexthoursmodes.pop(0)
        else:
          self.thishourmode = []
          self.thishourtrack = []
  
    def ManageTime(self, current_datetime):
        self.minute = current_datetime.minute
        self.hour = current_datetime.hour
        if self.minute == 0:  # new hour
            self.hour = current_datetime.hour
        self.activitystep = int((self.hour * 6) + (self.minute / 10))
        if self.hour == 0: # new day
            self.weekday = current_datetime.weekday()
  
    def step(self,  current_datetime):
        self.ManageTime(current_datetime)
        # Schedule Manager
        if self.minute % 10 == 0 or self.minute == 0:
            self.ScheduleManager(current_datetime)

        # Travel Decision
        if self.traveldecision == 1:
            self.PerceiveEnvironment()
            self.ModeChoice()
            self.Routing()
            self.SavingRoute()
            self.arrival_time = current_datetime + timedelta(minutes=self.track_duration)
            self.activity = "traveling"
            self.traveldecision = 0
            self.TripSegmentsPerHour()
            
        if self.activity == "traveling":
            self.TravelingAlongRoute(current_datetime)
        if self.activity == "perform_activity":
            self.PlaceTracker()
        
        if self.minute == 0:
            # self.TravelExposure()
            # self.AtPlaceExposure()
            self.hourlyNO2 = self.hourlyplaceNO2 + self.hourlytravelNO2
            self.hourlytravelNO2, self.hourlyplaceNO2 = 0,0
        self.former_activity = self.current_activity
        return self


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
        self.activitystep = int((self.hour * 6) + (self.minute / 10))
        self.nb_humans = nb_humans
        self.modelrunname = modelrunname
        self.crs = crs
        self.schedule = SimultaneousActivation(self)
        print("Current time: ", self.current_datetime)
        print("Nr of Humans: ", self.nb_humans)
        self.extentbox = spatial_extent.total_bounds
        self.continoussp = ContinuousSpace(x_max=self.extentbox[2], y_max=self.extentbox[3],
                                           torus=bool, x_min=self.extentbox[0], y_min=self.extentbox[1])
        
        # Create the agents
        print("Creating Agents")
        print(datetime.now())
        with ctx_in_main.Pool() as pool:
            self.agents = pool.starmap(Humans, [(x, self) for x in range(self.nb_humans)]) 
        for agent in self.agents:
            self.continoussp.place_agent(agent, agent.Residence)
            #self.schedule.add(agent)


        # Load Weather data and set initial weather conditions
        self.monthly_weather_df = pd.read_csv(path_data+"Weather/monthlyWeather2019TempDiff.csv") 
        #self.daily_weather_df = pd.read_csv("D:/PhD EXPANSE/Data/Amsterdam/Weather/dailyWeather2019.csv")
        self.temperature = self.monthly_weather_df.loc[self.monthly_weather_df["month"] == self.current_datetime.month, "Temperature"].values[0]
        self.winddirection = self.monthly_weather_df.loc[self.monthly_weather_df["month"] == self.current_datetime.month, "Winddirection"].values[0]
        self.windspeed = self.monthly_weather_df.loc[self.monthly_weather_df["month"] == self.current_datetime.month, "Windspeed"].values[0]
        self.rain = self.monthly_weather_df.loc[self.monthly_weather_df["month"] == self.current_datetime.month, "Rain"].values[0]
        self.tempdifference = self.monthly_weather_df.loc[self.monthly_weather_df["month"] == self.current_datetime.month, "TempDifference"].values[0]
        print("temperature: " , self.temperature , "rain: " , self.rain , " wind: ", self.windspeed, " wind direction: ", self.winddirection, "tempdifference: ", self.tempdifference)

        print("Starting Simulation")
        
    def DetermineWeather(self):
      self.temperature = self.monthly_weather_df.loc[self.monthly_weather_df["month"] == self.current_datetime.month, "Temperature"].values[0]
      self.winddirection = self.monthly_weather_df.loc[self.monthly_weather_df["month"] == self.current_datetime.month, "Winddirection"].values[0]
      self.windspeed = self.monthly_weather_df.loc[self.monthly_weather_df["month"] == self.current_datetime.month, "Windspeed"].values[0]
      self.rain = self.monthly_weather_df.loc[self.monthly_weather_df["month"] == self.current_datetime.month, "Rain"].values[0]
      self.tempdifference = self.monthly_weather_df.loc[self.monthly_weather_df["month"] == self.current_datetime.month, "TempDifference"].values[0]
      print("temperature: " , self.temperature , "rain: " , self.rain , " wind: ", self.windspeed, " wind direction: ", self.winddirection, "tempdifference: ", self.tempdifference)

    def TrafficAssignment(self):
      with mp.Pool() as pool:
          self.HourlyTraffic = pool.starmap(RetrieveRoutes, [(agent.thishourmode, agent.thishourtrack) for agent in self.agents], chunksize = 500)
          pool.close()
          pool.join()
          pool.terminate()
      self.HourlyTraffic = list(it.chain.from_iterable(list(filter(lambda x: x is not None, self.HourlyTraffic))))
      print("Nr of hourly traffic tracks: ", len(self.HourlyTraffic))
      TraffAssDat.write(f"hourly Traff tracks: {len(self.HourlyTraffic)} \n")
      if len(self.HourlyTraffic) > 0:   
        self.drivenroads = gpd.sjoin_nearest( carroads, gpd.GeoDataFrame(data = {'count': [1]*len(self.HourlyTraffic), 'geometry':self.HourlyTraffic}, geometry="geometry", crs=crs), how="inner")[["fid", "count"]] # map matching, improve with leuvenmapmatching
        self.drivenroads = carroads.merge(self.drivenroads.groupby(['fid']).sum(), on="fid")
        self.AirPollGrid = gpd.sjoin(self.drivenroads, AirPollGrid, how="right", predicate="intersects")
        self.AirPollGrid.loc[self.AirPollGrid["ON_ROAD"] == 1,'count'] = self.AirPollGrid.loc[self.AirPollGrid["ON_ROAD"] == 1,'count'].fillna(0)
        print("joined traffic tracks to grid")
        # self.AirPollGrid.plot("count", antialiased=False, legend = True) 
        # plt.title(f"Traffic of {nb_humans} assigned at {self.hour} o'clock")
        # plt.savefig(path_data + f'ModelRuns/TrafficMaps/TrafficGrid_{nb_humans}Agents_{self.hour}_assigned.png')
        # plt.close()
        # self.AirPollGrid.plot(f"TrV{self.hour-1}_{self.hour}", antialiased=False, legend = True) 
        # plt.title(f"Traffic observed at {self.hour} o'clock")
        # plt.savefig(path_data + f'ModelRuns/TrafficMaps/TrafficGrid{self.hour}_observed.png')
        # plt.close()
        predictors = ["count", "MaxSpeedLimit"]
        # self.AirPollGrid["speed_TV_interact"] = self.AirPollGrid["count"] * self.AirPollGrid["MaxSpeedLimit"]
        reg = LinearRegression().fit(self.AirPollGrid.query('ON_ROAD == 1')[predictors], self.AirPollGrid.query('ON_ROAD == 1')[f"TrV{self.hour-1}_{self.hour}"])
        TraffAssDat.write(f"Intercept: {reg.intercept_} \n") 
        TraffAssDat.write(pd.DataFrame(zip(predictors, reg.coef_)).to_string()) 
        self.R2 =  reg.score(self.AirPollGrid.query('ON_ROAD == 1')[predictors], self.AirPollGrid.query('ON_ROAD == 1')[f"TrV{self.hour-1}_{self.hour}"])
        TraffAssDat.write(f"\nR2 {self.R2}\n")
        self.AirPollGrid["TraffV"] = np.nan
        self.AirPollGrid.loc[self.AirPollGrid["ON_ROAD"] == 1,"TraffV"] = reg.predict(self.AirPollGrid.query('ON_ROAD == 1')[predictors])
        self.AirPollGrid.plot("TraffV", antialiased=False, legend = True) 
        plt.title(f"Traffic predicted at {self.hour} o'clock")
        plt.savefig(path_data + f'ModelRuns/TrafficMaps/TrafficGrid_{nb_humans}Agents_{self.hour}_predicted_{self.R2}.png')
        plt.close()

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
            TraffAssDat.write(f"hour {self.current_datetime} \n")
            # print("Current time: ", self.current_datetime)
            self.hour = self.current_datetime.hour
            self.TrafficAssignment()
        self.activitystep = int((self.hour * 6) + (self.minute / 10))
        if self.current_datetime.hour == 0: # new day
            self.weekday = self.current_datetime.weekday()
        if self.current_datetime.day == 1 and self.current_datetime.hour == 0: # new month
            self.DetermineWeather()

                 
        print(datetime.now())
        
        with ctx_in_main.Pool() as pool:
            self.agents = pool.starmap(Humans.step, [(agent, self.current_datetime) for agent in self.agents],  chunksize=1000)
            pool.close()
            pool.join()
            pool.terminate()
              
        

if __name__ == "__main__":
    mp.set_start_method('forkserver')
    ctx_in_main = mp.get_context('forkserver')
    
    
  # Read Main Data
    path_data = "/mnt/c/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/"

    # Synthetic Population
    print("Reading Population Data")
    nb_humans = 8700     #87000 = 10%, 43500 = 5%, 21750 = 2.5%, 8700 = 1%
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
    schedulelist = [scheduledf_monday, scheduledf_tuesday, scheduledf_wednesday, scheduledf_thursday, scheduledf_friday, scheduledf_saturday, scheduledf_sunday]
    del scheduledf_monday, scheduledf_tuesday, scheduledf_wednesday, scheduledf_thursday, scheduledf_friday, scheduledf_saturday, scheduledf_sunday

    # Coordinate Reference System and CRS transformers
    crs = "epsg:28992"
    project_to_WSG84 = Transformer.from_crs(crs, "epsg:4326", always_xy=True).transform
    projecy_to_crs = Transformer.from_crs("epsg:4326", crs, always_xy=True).transform
    project_to_meters = Transformer.from_crs(crs, 'epsg:3857')
    project_to_latlng = Transformer.from_crs('epsg:3857', crs, always_xy=True).transform

    # Load the spatial built environment
    spatial_extent = gpd.read_feather(path_data+"FeatherDataABM/SpatialExtent.feather")
    buildings = gpd.read_feather(path_data+"FeatherDataABM/Buildings.feather")
    streets = gpd.read_feather(path_data+"FeatherDataABM/Streets.feather")
    greenspace = gpd.read_feather(path_data+"FeatherDataABM/Greenspace.feather")
    Residences = gpd.read_feather(path_data+"FeatherDataABM/Residences.feather")
    Schools = gpd.read_feather(path_data+"FeatherDataABM/Schools.feather")
    Supermarkets = gpd.read_feather(path_data+"FeatherDataABM/Supermarkets.feather")
    Universities = gpd.read_feather(path_data+"FeatherDataABM/Universities.feather")
    Kindergardens = gpd.read_feather(path_data+"FeatherDataABM/Kindergardens.feather")
    Restaurants = gpd.read_feather(path_data+"FeatherDataABM/Restaurants.feather")
    Entertainment = gpd.read_feather(path_data+"FeatherDataABM/Entertainment.feather")
    ShopsnServ = gpd.read_feather(path_data+"FeatherDataABM/ShopsnServ.feather")
    Nightlife = gpd.read_feather(path_data+"FeatherDataABM/Nightlife.feather")
    Profess = gpd.read_feather(path_data+"FeatherDataABM/Profess.feather")
    EnvBehavDeterms = gpd.read_feather(path_data+"FeatherDataABM/EnvBehavDeterminants.feather")
    carroads = gpd.read_feather(path_data+"FeatherDataABM/carroads.feather")

    # Read the Environmental Stressor Data and Model
    # cellsize = 50
    AirPollGrid = gpd.read_feather(path_data+"FeatherDataABM/AirPollgrid50m.feather")
    AirPollPred = pd.read_csv(path_data+"Air Pollution Determinants/Pred_50m.csv")
    AirPollGrid[["NO2", "ON_ROAD"]] = AirPollPred[["baseline_NO2", "ON_ROAD"]]
    TraffDat = pd.read_csv(path_data+ "Air Pollution Determinants/AirPollRaster50m_TraffVdata.csv")
    AirPollGrid = AirPollGrid.merge(TraffDat[['int_id','StreetIntersectDensity', 'MaxSpeedLimit', 'MinSpeedLimit', 'MeanSpeedLimit']], how = "left", on = "int_id")
    print("AirPollGrid Columns: ", AirPollGrid.columns)
    
    # Start OSRM Servers
    print("Starting OSRM Servers")
    OSRMservers = subprocess.Popen(['cmd.exe', '/c', 'C:/Users/Tabea/Documents/GitHub/Spatial-Agent-based-Modeling-of-Urban-Health-Interventions/start_OSRM_Servers.bat'],stdout = subprocess.DEVNULL )


    # Read the Mode of Transport Choice Model
    print("Reading Mode of Transport Choice Model")
    ModalChoiceModel = PMMLTreeClassifier(pmml=path_data+"ModalChoiceModel/modalChoice.pmml")
    ModalChoiceModel.splitter = "random"
    OrderPredVars = [x for x in ModalChoiceModel.fields][1:]


    # modelvars = "allvars"
    modelvars = "allvars_strict"
    if modelvars == "allvars":
        routevariables = ["popDns", "retaiDns","greenCovr", "RdIntrsDns", "TrafAccid", "NrTrees", "MeanTraffV", "HighwLen", "AccidPedes",
                        "PedStrWidt", "PedStrLen", "LenBikRout", "DistCBD", "retailDiv", "MeanSpeed", "MaxSpeed", "NrStrLight", "CrimeIncid",
                        "MaxNoisDay", "OpenSpace", "PNonWester", "PWelfarDep"]
        personalvariables = ["sex_male", "age", "car_access", "Western", "Non_Western", "Dutch", 'income','employed',
                                'edu_3_levels','HH_size', 'Nrchildren', 'student', 'driving_habit','biking_habit','transit_habit']
        tripvariables = ["trip_distance", "purpose_commute", 'purpose_leisure','purpose_groceries_shopping',
                                'purpose_education', 'purpose_bring_person']
        weathervariables = ['Rain', 'Temperature', 'Winddirection', 'Windspeed']
        originvariables = ["pubTraDns", "DistCBD"]
        destinvariables = ["pubTraDns", "DistCBD", "NrParkSpac", "PrkPricPre", "PrkPricPos"]
        
    elif modelvars == "allvars_strict":
        routevariables = ["popDns", "retaiDns","greenCovr", "RdIntrsDns", "TrafAccid", "NrTrees", "MeanTraffV", "HighwLen", "AccidPedes",
                        "PedStrWidt", "PedStrLen", "LenBikRout", "DistCBD", "retailDiv", "MeanSpeed", "MaxSpeed", "MinSpeed", "NrStrLight", "CrimeIncid",
                        "MaxNoisDay", "MxNoisNigh", "OpenSpace", "PNonWester", "PWelfarDep", "pubTraDns", "SumTraffVo"]
        personalvariables = ["sex_male", "age", "car_access", "Western", "Non_Western", "Dutch", 'income','employed',
                                'edu_3_levels','HH_size', 'Nrchildren', 'driving_habit','biking_habit','transit_habit']
        tripvariables = ["trip_distance"]
        originvariables = ["pubTraDns", "DistCBD"]
        destinvariables = ["pubTraDns", "DistCBD"]
    
    routevariables_suff = add_suffix(routevariables, ".route")
    originvariables_suff = add_suffix(originvariables, ".orig")
    destinvariables_suff = add_suffix(destinvariables, ".dest")

    TraffAssDat = open(path_data+'TraffAssignModelPerf.txt', 'a',buffering=1)
    TraffAssDat.write(f"Number of Agents: {nb_humans} \n")

    ctx_in_main.set_forkserver_preload([random_subset, schedulelist])

    m = TransportAirPollutionExposureModel(nb_humans=nb_humans, path_data=path_data)
    
    profile = False
    
    if profile:
      f = open(path_data+'profile_results.txt', 'w')
      for t in range(144):      
        # Profile the ABM run
        cProfile.run('m.step()', 'profile_results')
        # Print or save the profiling results
        p = pstats.Stats('profile_results', stream=f)
        # p.strip_dirs().sort_stats('cumulative').print_stats()
        p.strip_dirs().sort_stats('time').print_stats()
      f.close()
      
    else:
      for t in range(144):
        m.step()
        
    OSRMservers.terminate()    
    TraffAssDat.close()

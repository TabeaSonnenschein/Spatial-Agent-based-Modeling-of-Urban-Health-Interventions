from datetime import datetime, timedelta
from mesa import Agent, Model
from mesa.space import ContinuousSpace
from mesa.time import SimultaneousActivation
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
import pandas as pd
import geopandas as gpd
import matplotlib
matplotlib.use('Agg')
# matplotlib.use('TKAgg')
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
import multiprocessing as mp
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import time
import multiprocessing as mp
from multiprocessing import Pool
from scipy.stats import pearsonr
import gc
from statistics import mean
import os
import xarray as xr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from xrspatial.utils import ngjit
from collections import Counter
import os
import random

# my own functions
import CellularAut_utils
import Math_utils

# import logging
# import multiprocessing.util
# multiprocessing.util.log_to_stderr(level=logging.DEBUG)

warnings.filterwarnings("ignore", module="shapely")


def init_worker_init(schedules, Resid, univers, Scho, Prof, modvars):
    global schedulelist, Residences, Universities, Schools, Profess, Entertainment, Restaurants, modelvars
    schedulelist = schedules
    Residences = Resid
    Universities = univers
    Schools = Scho
    Profess = Prof
    modelvars = modvars

    # initialize worker processes
def init_worker_simul(Resid, Entertain, Restaur, envdeters, modalchoice, ordprevars, cols, projectWSG84, projcrs, crs_string, routevars, originvars, destinvars, Grid, airpolgr, modvars, PCst, FacLoad):
    global Residences, Entertainment, Restaurants, EnvBehavDeterms, ModalChoiceModel, OrderPredVars, colvars, project_to_WSG84, projecy_to_crs, crs, routevariables, originvariables, destinvariables, EnvStressGrid, AirPollGrid, modelvars, PCstat, FactorLoadings
    Residences = Resid
    Entertainment = Entertain
    Restaurants = Restaur
    EnvBehavDeterms = envdeters
    ModalChoiceModel = modalchoice
    OrderPredVars = ordprevars
    colvars = cols
    project_to_WSG84 = projectWSG84
    projecy_to_crs = projcrs
    crs = crs_string
    routevariables = routevars
    originvariables = originvars
    destinvariables = destinvars
    EnvStressGrid = Grid
    AirPollGrid = airpolgr
    modelvars = modvars
    PCstat = PCst
    FactorLoadings = FacLoad
    
    
def worker_process( agents, current_datetime, WeaVars):
    global Residences, Entertainment, Restaurants, EnvBehavDeterms, ModalChoiceModel, OrderPredVars, colvars, project_to_WSG84, projecy_to_crs, crs, routevariables, originvariables, destinvariables
    global WeatherVars
    WeatherVars = WeaVars
    for agent in agents:
        agent.step(current_datetime)
    return agents

def hourly_worker_process( agents, current_datetime, NO2, WeaVars):
    global Residences, Entertainment, Restaurants, EnvBehavDeterms, ModalChoiceModel, OrderPredVars, colvars, project_to_WSG84, projecy_to_crs, crs, routevariables, originvariables, destinvariables, EnvStressGrid
    EnvStressGrid[:] = np.array(NO2).reshape(EnvStressGrid.shape)
    global WeatherVars
    WeatherVars = WeaVars
    for agent in agents:
        agent.Exposure()
        agent.step(current_datetime)
    return agents


def worker_process_strict( agents, current_datetime):
    global Residences, Entertainment, Restaurants, EnvBehavDeterms, ModalChoiceModel, OrderPredVars, colvars, project_to_WSG84, projecy_to_crs, crs, routevariables, originvariables, destinvariables
    for agent in agents:
        agent.step(current_datetime)
    return agents

def hourly_worker_process_strict( agents, current_datetime, NO2):
    global Residences, Entertainment, Restaurants, EnvBehavDeterms, ModalChoiceModel, OrderPredVars, colvars, project_to_WSG84, projecy_to_crs, crs, routevariables, originvariables, destinvariables, EnvStressGrid
    EnvStressGrid[:] = np.array(NO2).reshape(EnvStressGrid.shape)
    for agent in agents:
        agent.Exposure()
        agent.step(current_datetime)
    return agents

def TraffSpatialJoint(tracks, dum):
    global AirPollGrid
    drivengrids = gpd.sjoin(AirPollGrid[["int_id", "geometry"]], gpd.GeoDataFrame(data = {'count': [1]*len(tracks), 'geometry':tracks}, geometry="geometry", crs=crs) , how="left", predicate="intersects")[["int_id", "count"]]
    TraffGrid = AirPollGrid[["int_id", "geometry"]].merge(drivengrids.groupby(['int_id'], as_index=False).sum(), on="int_id")
    return list(TraffGrid['count'].fillna(0))

def RetrieveRoutes(thishourmode, thishourtrack):
   if "drive" in thishourmode:
      return([thishourtrack[count] for count, value in enumerate(thishourmode) if value == "drive"])

def RetrieveExposure(agents, dum):
    return [[agent.unique_id, agent.hourlyNO2, agent.hourlyMET]  for agent in agents]
  
def RetrieveModalSplitStep(agents, dum):
    return [[agent.unique_id, agent.modalchoice, agent.track_duration, agent.trip_distance]  for agent in agents]

def RetrieveModalSplitHour(agents, dum):
    return [agent.thishourmode  for agent in agents]

class Humans(Agent):
    """
    Humans:
  - have realistic attributes for the city
  - have a daily activity schedule
  - have mobility behavior
  - have a home location
  - have personal exposure
    """

    def __init__(self,vector, model):
        global schedulelist, Residences, Universities, Schools, Profess, modelvars
        self.unique_id = vector[0]
        super().__init__(self.unique_id, model)
        # socio-demographic attributes
        self.Neighborhood = vector[1]
        self.current_edu = vector[8]          # "high", "middle", "low", "no_current_edu"
        if modelvars == "allvars_strict":
            self.IndModalPreds = [vector[i] for i in [19,2,13,20,21,22,17,11,12,23,24,15,14,16]]    # individual modal choice predictions: ["sex_male", "age", "car_access", "Western", 
                                                                # "Non_Western", "Dutch", 'income','employed',
                                                                # 'edu_3_levels','HH_size', 'Nrchildren', 'driving_habit','biking_habit','transit_habit']
        else:
            self.IndModalPreds = [vector[i] for i in [19,2,13,20,21,22,17,11,12,23,24,25,15,14,16]] # "sex_male", "age", "car_access", 
                                                                # "Western", "Non_Western", "Dutch", 'income','employed',
                                                                #'edu_3_levels','HH_size', 'Nrchildren', 'student', 'driving_habit','biking_habit',
                                                                # 'transit_habit']
        # need to add hhsize and nrchildren

        # Activity Schedules
        self.ScheduleID = vector[18]          # Schedule IDs
        self.WeekSchedules = []
        self.WeekLocations = []
        for x in range(7):
          self.WeekSchedules.append(list(schedulelist[x].loc[schedulelist[x]["SchedID"] == self.ScheduleID, ].values[0][1:145]))
          self.WeekLocations.append(list(schedulelist[x].loc[schedulelist[x]["SchedID"] == self.ScheduleID, ].values[0][145:]))
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
        elif (self.current_edu != "no_current_edu") or (4 in list(np.concatenate(self.WeekSchedules).flat)):
            # select school that is closest to self.Residence
            self.School = [(p.x, p.y) for p in nearest_points(Point(tuple(self.Residence)), Schools["geometry"].unary_union)][1]
        if 3 in list(np.concatenate(self.WeekSchedules).flat):
            self.Workplace = Profess["geometry"].sample(1).values[0].coords[0]

        # mobility behavior variables
        self.path_memory = 0
        self.traveldecision = 0
        self.thishourtrack, self.thishourmode, self.thishourduration = [], [], []
        self.nexthoursmodes, self.nexthourstracks, self.nexthourduration = [], [], []

        # exposure variables
        self.newplace, self.newactivity = 0, 0
        self.visitedPlaces, self.durationPlaces, self.activities, self.durationActivties =  [Point(tuple(self.Residence))], [0], [self.WeekSchedules[self.weekday][self.activitystep]], [0]
        self.hourlytravelNO2, self.hourlyplaceNO2, self.hourlyNO2 = 0,0,0
        self.hourlytravelMET, self.hourlyplaceMET, self.hourlyMET = 0,0,0
        
    def ScheduleManager(self, current_datetime):
      # identifying the current activity
      self.current_activity = self.WeekSchedules[self.weekday][self.activitystep]
      # identifying whether activity changed and if so, where the new activity is locatec and whether we have a saved route towards that destination
      if self.current_activity != self.former_activity:
        commute,leisure,groceries,edu_trip = 0,0,0,0
        # print("Current Activity: ", self.current_activity," Former Activity: ", self.former_activity)
        if self.current_activity == 3:  # 3 = work
          commute = 1
          self.destination_activity = self.Workplace
          if "self.homeTOwork" in locals() and  (self.former_activity in [5, 1, 6, 7]):  # 1 = sleep/rest, 5 = at home, 6 = cooking, 7 = gardening
            self.track_path = self.homeTOwork
            self.track_geometry = self.homeTOwork_geometry
            self.modalchoice = self.homeTOwork_mode
            self.track_duration = self.homeTOwork_duration
            self.path_memory = 1
            print("saved pathway")

        elif self.current_activity == 4:  # 4 = school/university
          edu_trip = 1
          if self.current_edu == "high":
            self.destination_activity = self.University
          else:
            self.destination_activity = self.School
          # 1 = sleep/rest, 5 = at home, 6 = cooking, 7 = gardening
          if "self.homeTOschool_geometry" in locals() and (self.former_activity in [5, 1, 6, 7]): 
            self.track_geometry = self.homeTOschool_geometry
            self.modalchoice = self.homeTOschool_mode
            self.track_duration = self.homeTOschool_duration
            self.path_memory = 1
            print("saved pathway")

        elif self.current_activity == "groceries_shopping":
          self.destination_activity = self.Supermarket
          groceries = 1
          # 1 = sleep/rest, 5 = at home, 6 = cooking, 7 = gardening
          if "self.homeTOsuperm_geometry" in locals() and (self.former_activity in [5, 1, 6, 7]):
            self.track_geometry = self.homeTOsuperm_geometry
            self.track_duration = self.homeTOsuperm_duration
            self.modalchoice = self.homeTOsuperm_mode
            self.path_memory = 1
            print("saved pathway")

        elif self.current_activity == "kindergarden":
          self.destination_activity = self.Kindergarden
          # 1 = sleep/rest, 5 = at home, 6 = cooking, 7 = gardening
          if "self.homeTOkinderga_geometry" in locals() and (self.former_activity in [5, 1, 6, 7]):
            self.track_geometry = self.homeTOkinderga_geometry
            self.track_duration = self.homeTOkinderga_duration
            self.modalchoice = self.homeTOkinderga_mode
            self.path_memory = 1
            print("saved pathway")

        # 1 = sleep/rest, 5 = at home, 6 = cooking, 7 = gardening
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

        elif self.current_activity == 11: # entertainment / culture
          leisure = 1
          self.destination_activity = Entertainment["geometry"].sample(1).values[0].coords[0]

        elif self.current_activity == 2:  # 2 = eating
          if self.WeekLocations[self.weekday][self.activitystep] == 0:
            self.destination_activity = self.pos
          else:
            if any(Restaurants["geometry"].within( Point(tuple(self.pos)).buffer(500))):
                nearRestaurants = Restaurants["geometry"].intersection(Point(tuple(self.pos)).buffer(500))
                self.destination_activity = nearRestaurants[~nearRestaurants.is_empty].sample(1).values[0].coords[0]
            else:
                self.destination_activity = [(p.x, p.y) for p in nearest_points(Point(tuple(self.pos)), Restaurants["geometry"].unary_union)][1]

        elif self.current_activity == 10:  # 10 = social life
          leisure = 1
          if self.WeekLocations[self.weekday][self.activitystep] == 0:
            self.destination_activity = self.pos
          else:
            self.destination_activity = Residences["geometry"].sample(1).values[0].coords[0]

        elif self.current_activity in [9, 8]:  # 9 = shopping/services, 8 = walking the dog
          self.destination_activity = Residences["geometry"].sample(1).values[0].coords[0]


        # Identifuing whether agent needs to travel to new destination
        if self.destination_activity != self.pos:
          if self.path_memory != 1:
              self.traveldecision = 1
              self.route_eucl_line = LineString([Point(tuple(self.pos)), Point(tuple(self.destination_activity))])
              self.trip_distance = self.route_eucl_line.length
              self.TripVars = [commute,leisure,groceries,edu_trip,0]  #"purpose_commute", 'purpose_leisure','purpose_groceries_shopping','purpose_education', 'purpose_bring_person'
          else:
              self.TripSegmentsPerHour()
              self.activity = "traveling"
              self.arrival_time = current_datetime + timedelta(minutes=self.track_duration)
          self.path_memory = 0
          self.newplace = 1
        else:
          self.activity = "perform_activity"
          self.newactivity = 1
          self.traveldecision = 0

    def ModeChoice(self):
      global EnvBehavDeterms
      # PerceiveEnvironment
      # variables to be joined to route
      RouteVars = gpd.GeoDataFrame(data = {'id': ['1'], 'geometry': [self.route_eucl_line]}, geometry="geometry", crs=crs).sjoin(EnvBehavDeterms, how="left")[routevariables].mean(axis=0).values
      #variables to be joined to current location
      OrigVars = gpd.GeoDataFrame(data = {'id': ['1'], 'geometry': [Point(tuple(self.pos))]}, geometry="geometry", crs=crs).sjoin(EnvBehavDeterms, how="left")[originvariables].values[0]
      #variables to be joined to destination
      DestVars = gpd.GeoDataFrame(data = {'id': ['1'], 'geometry': [Point(tuple(self.destination_activity))]}, geometry="geometry",crs=crs).sjoin(EnvBehavDeterms, how="left")[destinvariables].values[0]
      # preparing dataframes for prediction
      if modelvars == "allvars_strict":
        pred_df = pd.DataFrame(np.concatenate((RouteVars, OrigVars, DestVars, self.IndModalPreds, [self.trip_distance]), axis=None).reshape(1, -1), 
                                columns=colvars).fillna(0)
      else:
        pred_df = pd.DataFrame(np.concatenate((RouteVars, OrigVars, DestVars, self.IndModalPreds, [self.trip_distance],self.TripVars, WeatherVars), axis=None).reshape(1, -1), 
                                columns=colvars).fillna(0)
      if PCstat == "PCA":
        pred_df[FactorLoadings.columns[1:]] = [mean(np.asarray(pred_df.loc[0,FactorLoadings["Vars"]]) * np.asarray(FactorLoadings.iloc[:,i])) for i in range(1, FactorLoadings.shape[1])]
      # predicting modechoice
      self.modechoice = ModalChoiceModel.predict(pred_df[OrderPredVars].values)[0].replace("1", "bike").replace("2", "drive").replace("3", "transit").replace("4", "walk")

    # OSRM Routing Machine
    def Routing(self):
      if self.modechoice == "bike":
        server = ":5001/"
        lua_profile = "bike"
      elif self.modechoice == "drive":
        server = ":5000/"
        lua_profile = "car"
      elif self.modechoice == "walk":
        server = ":5002/"
        lua_profile = "foot"
      elif self.modechoice == "transit":
        server = ":5002/"
        lua_profile = "foot"
      
      orig_point = transform(project_to_WSG84, Point(tuple(self.pos)))
      dest_point = transform(project_to_WSG84, Point(tuple(self.destination_activity)))
      url = ("http://127.0.0.1" + server + "route/v1/"+ lua_profile + "/" + str(orig_point.x)+ ","+ str(orig_point.y)+ ";"+ str(dest_point.x)+ ","+ str(dest_point.y) + "?overview=full&geometries=polyline")
      res = rq.get(url).json()
      self.track_geometry = transform(projecy_to_crs, transform(Math_utils.flip, LineString(polyline.decode(res['routes'][0]['geometry']))))
      self.track_duration = (res['routes'][0]['duration'])/60  # minutes
      if self.modechoice == "transit":
        self.track_duration = self.track_duration/10
      self.trip_distance = res['routes'][0]['distance']  # meters
    
    def SavingRoute(self):
      if(self.former_activity in [5, 1, 6, 7]):
        if self.current_activity == 3 : 
            self.homeTOwork_mode = self.modechoice
            self.homeTOwork_geometry = self.track_geometry 
            self.homeTOwork_duration = self.track_duration
            self.workTOhome_geometry = Math_utils.reverse_geom(self.track_geometry)
		
        elif self.current_activity == 4: 
            self.homeTOschool_mode = self.modechoice
            self.homeTOschool_geometry = self.track_geometry  
            self.homeTOschool_duration = self.track_duration
            self.schoolTOhome_geometry = Math_utils.reverse_geom(self.track_geometry)
			
        elif self.current_activity == "kindergarden" : 
            self.homeTOkinderga_mode = self.modechoice
            self.homeTOkinderga_geometry = self.track_geometry 
            self.homeTOkinderga_duration = self.track_duration
            self.kindergaTOhome_geometry = Math_utils.reverse_geom(self.track_geometry)

        elif self.current_activity == "groceries_shopping": 
            self.homeTOsuperm_mode = self.modechoice
            self.homeTOsuperm_geometry = self.track_geometry 
            self.homeTOsuperm_duration = self.track_duration
            self.supermTOhome_geometry = Math_utils.reverse_geom(self.track_geometry)
    
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
          self.thishourduration.append(60 - self.minute)
          self.nexthourstracks = self.segment_geometry[1:]
          self.nexthourduration = [(self.track_duration-(60 - self.minute))%60]
          if len(self.nexthourstracks)>1:
            self.nexthourduration = list(it.repeat(60, len(self.nexthourstracks)-1)) + self.nexthourduration
          self.nexthoursmodes = list(it.repeat(self.modechoice, len(self.nexthourstracks)))
      else:
          self.thishourtrack.append(self.track_geometry)
          self.thishourmode.append(self.modechoice)
          self.thishourduration.append(self.track_duration)
    
    def TravelingAlongRoute(self, current_datetime):
      if current_datetime >= self.arrival_time:
          self.activity = "perform_activity"
          self.pos = self.destination_activity

    def PlaceTracker(self):
      if self.newplace == 1:
        self.visitedPlaces.append(Point(tuple(self.pos)))
        self.durationPlaces.append(1)
        self.durationActivties.append(1)
        self.activities.append(self.current_activity)
        self.newplace = 0
      elif self.newactivity == 1:
        self.activities.append(self.current_activity)
        self.durationActivties.append(1)
        self.newactivity = 0
      else:
        self.durationPlaces[-1] += 1
        self.durationActivties[-1] += 1
        

    def AtPlaceExposure(self):
      if len(self.visitedPlaces) > 0:
        # NO2
        self.hourlyplaceNO2 = sum(np.multiply([EnvStressGrid.sel(x=point.x, y=point.y, method='nearest').values.item(0) for point in self.visitedPlaces], [x*10 for x in self.durationPlaces]))
        # Metabolic Equivalent of Task
        self.hourlyplaceMET = sum([1.5 * 10 * value if (self.activities[count] != 1) else 0 for count, value in enumerate(self.durationActivties)])  # 1.5 MET for 10 minutes times duration measured in 10minute steps
        
    def ResetPlaceTracks(self):
      if self.activity== "perform_activity":
        self.visitedPlaces = [self.visitedPlaces[-1]]
        self.durationPlaces = [0]
        self.activities = [self.activities[-1]]
        self.durationActivties = [0]
      else:
        self.visitedPlaces = []
        self.durationPlaces = []
        self.activities = []
        self.durationActivties = []
    
    def TravelExposure(self):
      if len(self.thishourtrack) > 0:       # transform overlay function to point in polygon, get points along line (10m), joining points with grid cellsize/2
        # NO2
        trackpoints = [[self.thishourtrack[a].interpolate(d) for d in np.arange(0, self.thishourtrack[a].length, 10)] for a in range(len(self.thishourtrack))]
        trackjoin = [[EnvStressGrid.sel(x=point.x, y=point.y, method='nearest').values.item(0) for point in sublist] for sublist in trackpoints]
        self.hourlytravelNO2 = sum(np.multiply([mean(val) if len(val)>0 else 0 for val in trackjoin], self.thishourduration))
        # Metabolic Equivalent of Task
        self.hourlytravelMET = sum(np.multiply(list(map(lambda x: float(x.replace('bike', "6").replace('drive', "1.5").replace('walk', "3").replace('transit', "2")) , self.thishourmode))
                                                , self.thishourduration))
        
    def ResetTravelTracks(self):
      if len(self.nexthourstracks) > 0:
        self.thishourmode = [self.nexthoursmodes[0]]
        self.thishourtrack = [self.nexthourstracks[0]]
        self.thishourduration = [self.nexthourduration[0]]
        self.nexthourduration.pop(0)
        self.nexthourstracks.pop(0)
        self.nexthoursmodes.pop(0)
      else:
        self.thishourmode = []
        self.thishourtrack = []
        self.thishourduration = []

    def Exposure(self):
        global EnvStressGrid
        self.TravelExposure()
        self.AtPlaceExposure()
        self.hourlyNO2 = (self.hourlyplaceNO2 + self.hourlytravelNO2)/60
        self.hourlytravelNO2, self.hourlyplaceNO2 = 0,0
        self.hourlyMET = (self.hourlyplaceMET + self.hourlytravelMET)/60
        self.hourlytravelMET, self.hourlyplaceMET = 0,0
  
    def ManageTime(self, current_datetime):
        self.minute = current_datetime.minute
        self.hour = current_datetime.hour
        if self.minute == 0:  # new hour
            self.hour = current_datetime.hour
        self.activitystep = int((self.hour * 6) + (self.minute / 10))
        if self.hour == 0: # new day
            self.weekday = current_datetime.weekday()
    
    def step(self, current_datetime):
        global Residences, Entertainment, Restaurants, EnvBehavDeterms, ModalChoiceModel, OrderPredVars, colvars, project_to_WSG84, projecy_to_crs, crs, routevariables, originvariables, destinvariables
        if modelvars == "allvars":
           global WeatherVars
        self.ManageTime(current_datetime)
        if self.minute == 0:
            self.ResetTravelTracks()
            self.ResetPlaceTracks()
        # Schedule Manager
        if self.minute % 10 == 0 or self.minute == 0:
            self.ScheduleManager(current_datetime)

        # Travel Decision
        if self.traveldecision == 1:
            self.ModeChoice()
            self.Routing()
            self.SavingRoute()
            self.arrival_time = current_datetime + timedelta(minutes=self.track_duration)
            self.activity = "traveling"
            self.traveldecision = 0
            self.TripSegmentsPerHour()
        
        # Activity Execution
        if self.activity == "traveling":
            self.TravelingAlongRoute(current_datetime)
        if self.activity == "perform_activity":
            self.PlaceTracker()
        self.former_activity = self.current_activity



class TransportAirPollutionExposureModel(Model):
    def __init__(self, nb_humans, path_data, crs="epsg:28992",
                 starting_date=datetime(2019, 1, 1, 6, 50, 0), steps_minute=10):
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
        self.crs = crs
        self.schedule = SimultaneousActivation(self)
        print("Current time: ", self.current_datetime)
        print("Nr of Humans: ", self.nb_humans)
        self.extentbox = spatial_extent.total_bounds
        self.continoussp = ContinuousSpace(x_max=self.extentbox[2], y_max=self.extentbox[3],
                                           torus=bool, x_min=self.extentbox[0], y_min=self.extentbox[1])
        
        self.hourlyext = 0

        # Create the agents
        print("Creating Agents")
        st = time.time()
        with Pool(initializer=init_worker_init, initargs=(schedulelist, Residences, Universities, Schools, Profess, modelvars)) as pool:
            self.agents = pool.starmap(Humans, [(random_subset.iloc[x],  self) for x in range(self.nb_humans)], chunksize=100) 
            pool.close()
            pool.join()
            pool.terminate()
        for agent in self.agents:
            self.continoussp.place_agent(agent, agent.Residence)
        print("Human Init Time: ", time.time() - st, "Seconds")


        # Load Weather data and set initial weather conditions
        self.monthly_weather_df = pd.read_csv(path_data+"Weather/monthlyWeather2019TempDiff.csv") 
        #self.daily_weather_df = pd.read_csv("D:/PhD EXPANSE/Data/Amsterdam/Weather/dailyWeather2019.csv")
        self.temperature = self.monthly_weather_df.loc[self.monthly_weather_df["month"] == self.current_datetime.month, "Temperature"].values[0]
        self.winddirection = self.monthly_weather_df.loc[self.monthly_weather_df["month"] == self.current_datetime.month, "Winddirection"].values[0]
        self.windspeed = self.monthly_weather_df.loc[self.monthly_weather_df["month"] == self.current_datetime.month, "Windspeed"].values[0]
        self.rain = self.monthly_weather_df.loc[self.monthly_weather_df["month"] == self.current_datetime.month, "Rain"].values[0]
        self.tempdifference = self.monthly_weather_df.loc[self.monthly_weather_df["month"] == self.current_datetime.month, "TempDifference"].values[0]
        self.WeatherVars = [self.rain, self.temperature, self.winddirection, self.windspeed]
        print("temperature: " , self.temperature , "rain: " , self.rain , " wind: ", self.windspeed, " wind direction: ", self.winddirection, "tempdifference: ", self.tempdifference)
        
        # self.weightsmatrix = CellularAut_utils.create_meteo_weightmatrix( params= list(paramvalues["values"].iloc[0:6]) +  list(paramvalues["values"].iloc[15:18]),
        #                        windspeed = self.windspeed , winddirection = self.winddirection, 
        #                        temperature =self.temperature, rain = self.rain, 
        #                        temp_diff = self.tempdifference)
        self.weightsmatrix = CellularAut_utils.create_weight_matrix(prop_rate = 0.7)
        print(self.weightsmatrix)
        
    def DetermineWeather(self):
      self.temperature = self.monthly_weather_df.loc[self.monthly_weather_df["month"] == self.current_datetime.month, "Temperature"].values[0]
      self.winddirection = self.monthly_weather_df.loc[self.monthly_weather_df["month"] == self.current_datetime.month, "Winddirection"].values[0]
      self.windspeed = self.monthly_weather_df.loc[self.monthly_weather_df["month"] == self.current_datetime.month, "Windspeed"].values[0]
      self.rain = self.monthly_weather_df.loc[self.monthly_weather_df["month"] == self.current_datetime.month, "Rain"].values[0]
      self.tempdifference = self.monthly_weather_df.loc[self.monthly_weather_df["month"] == self.current_datetime.month, "TempDifference"].values[0]
      print("temperature: " , self.temperature , "rain: " , self.rain , " wind: ", self.windspeed, " wind direction: ", self.winddirection, "tempdifference: ", self.tempdifference)
    
    def CalculateMonthlyWeightMatrix(self):
      self.weightsmatrix = CellularAut_utils.create_meteo_weightmatrix( params= list(paramvalues["values"].iloc[0:6]) +  list(paramvalues["values"].iloc[15:18]),
                    windspeed = self.windspeed , winddirection = self.winddirection, 
                    temperature =self.temperature, rain = self.rain, 
                    temp_diff = self.tempdifference)
      
    def PlotTrafficCount(self):
        self.TraffGrid.plot("count", antialiased=False, legend = True) 
        plt.title(f"Traffic of {nb_humans} assigned at {self.hour-1} to {self.hour} o'clock")
        plt.savefig(path_data + f'ModelRuns/TrafficMaps/TrafficGrid_assign_A{nb_humans}_H{self.hour-1}_{modelname}.png')
        plt.close()
    
    def PlotObservedTraffic(self):
        self.TraffGrid.plot(self.TraffVcolumn, antialiased=False, legend = True) 
        plt.title(f"Traffic observed at {self.hour-1} to {self.hour} o'clock")
        plt.savefig(path_data + f'ModelRuns/TrafficMaps/TrafficGrid{self.hour-1}_observed.png')
        plt.close()
        
    def TraffCountRegression(self, HourlyTraffic):
        predictors = ["count"]    #also have tried MaxSpeedLimit, but it takes up too much of the traffic coefficient
        reg = LinearRegression().fit(self.TraffGrid.loc[self.TraffGrid["ON_ROAD"] == 1, predictors], self.TraffGrid.loc[self.TraffGrid["ON_ROAD"] == 1,self.TraffVcolumn])
        TraffAssDat.write(f"hour {self.current_datetime} \n")
        TraffAssDat.write(f"hourly Traff tracks: {len(HourlyTraffic)} \n")
        TraffAssDat.write(f"Intercept: {reg.intercept_} \n") 
        TraffAssDat.write(pd.DataFrame(zip(predictors, reg.coef_)).to_string()) 
        self.R2 =  reg.score(self.TraffGrid.loc[self.TraffGrid["ON_ROAD"] == 1,predictors], self.TraffGrid.loc[self.TraffGrid["ON_ROAD"] == 1,self.TraffVcolumn])
        TraffAssDat.write(f"\nR2 {self.R2}\n\n")
        self.TraffGrid["TraffV"] = 0
        self.TraffGrid.loc[self.TraffGrid["ON_ROAD"] == 1,"TraffV"] = reg.predict(self.TraffGrid.loc[self.TraffGrid["ON_ROAD"] == 1,predictors])


    def TrafficRemainderCalc(self, HourlyTraffic):
        # Calculating Remainder
        self.TraffGrid["TraffV"] = 0
        self.TraffGrid.loc[self.TraffGrid["ON_ROAD"] == 1,"TraffV"] = (self.TraffGrid.loc[self.TraffGrid["ON_ROAD"] == 1, "count"]*  TraffVCoeff)
        TraffAssDat.write(f"hour {self.current_datetime} \n")
        TraffAssDat.write(f"hourly Traff tracks: {len(HourlyTraffic)} \n")
        self.R2, _ = pearsonr(self.TraffGrid.loc[self.TraffGrid["ON_ROAD"] == 1,"TraffV"],
                      self.TraffGrid.loc[self.TraffGrid["ON_ROAD"] == 1, self.TraffVcolumn])
        TraffAssDat.write(f"R2 {self.R2*self.R2}\n\n")
        AirPollGrid[f"TraffVrest{self.hour}"] =  0
        Remainders =  (self.TraffGrid.loc[self.TraffGrid["ON_ROAD"] == 1,self.TraffVcolumn])-(self.TraffGrid.loc[self.TraffGrid["ON_ROAD"] == 1,"TraffV"])
        AirPollGrid.loc[AirPollGrid["ON_ROAD"] == 1, f"TraffVrest{self.hour}"] = list(Remainders)

    def TotalTraffCalc(self, HourlyTraffic):
        self.TraffGrid["TraffV"] = 0
        self.TraffGrid.loc[self.TraffGrid["ON_ROAD"] == 1,"TraffV"] = (self.TraffGrid.loc[self.TraffGrid["ON_ROAD"] == 1, "count"]*  TraffVCoeff) \
                                                                          + (AirPollGrid.loc[AirPollGrid["ON_ROAD"] == 1, f"TraffVrest{self.hour}"])
        # self.TraffGrid.loc[self.TraffGrid["ON_ROAD"] == 1,"TraffV"] = (self.TraffGrid.loc[self.TraffGrid["ON_ROAD"] == 1, "count"]*  TraffVCoeff)
        self.TraffGrid.loc[self.TraffGrid["TraffV"] < 0,"TraffV"] = 0
        if TraffStage == "PredictionR2":
            TraffAssDat.write(f"hour {self.current_datetime} \n")
            TraffAssDat.write(f"hourly Traff tracks: {len(HourlyTraffic)} \n")
            self.R2, _ = pearsonr(self.TraffGrid.loc[self.TraffGrid["ON_ROAD"] == 1,"TraffV"], self.TraffGrid.loc[self.TraffGrid["ON_ROAD"] == 1, self.TraffVcolumn])
            TraffAssDat.write(f"R2 {self.R2*self.R2}\n\n")

    def PlotTraffPred(self):
        self.TraffGrid.plot("TraffV", antialiased=False, legend = True) 
        plt.title(f"Traffic predicted at {self.hour} o'clock")
        plt.savefig(path_data + f'ModelRuns/TrafficMaps/TrafficGrid_pred_A{nb_humans}_H{self.hour-1}__{modelname}.png')
        plt.close()

    def TrafficAssignment(self):
        HourlyTraffic = pool.starmap(RetrieveRoutes, [(agent.thishourmode, agent.thishourtrack) for agent in self.agents], chunksize = 500)
        HourlyTraffic = list(it.chain.from_iterable(list(filter(lambda x: x is not None, HourlyTraffic))))
        # gpd.GeoDataFrame(data = {'count': [1]*len(self.HourlyTraffic), 'geometry':self.HourlyTraffic}, geometry="geometry", crs=crs).to_file(path_data + f'ModelRuns/TrafficTracks/TrafficTracks_A{nb_humans}_H{self.hour-1}.shp')
        print("Nr of hourly traffic tracks: ", len(HourlyTraffic))
        if self.hour == 0:
          self.TraffVcolumn = f"TrV23_24"
        else:
          self.TraffVcolumn = f"TrV{self.hour-1}_{self.hour}"
        if len(HourlyTraffic) > 0: 
          if len(HourlyTraffic) > 15:
            counts = pool.starmap(TraffSpatialJoint, [(tracks, 0) for tracks in np.array_split(HourlyTraffic, n)], chunksize=1)
            print("Max", np.max(np.array(counts).sum(axis=0)), "Mean", np.mean(np.array(counts).sum(axis=0)), "Median", np.median(np.array(counts).sum(axis=0)))
            self.TraffGrid = AirPollGrid.loc[:,["int_id", "geometry", "ON_ROAD", "baseline_NO2", self.TraffVcolumn]]
            self.TraffGrid['count'] = np.array(counts).sum(axis=0)
          else:
            drivengrids = gpd.sjoin(AirPollGrid[["int_id", "geometry"]], gpd.GeoDataFrame(data = {'count': [1]*len(HourlyTraffic), 'geometry':HourlyTraffic}, geometry="geometry", crs=crs) , how="left", predicate="intersects")[["int_id", "count"]]
            self.TraffGrid = AirPollGrid.loc[:,["int_id", "geometry", "ON_ROAD", "baseline_NO2", self.TraffVcolumn]].merge(drivengrids.groupby(['int_id'], as_index=False).sum(), on="int_id")
            self.TraffGrid['count'] = self.TraffGrid['count'].fillna(0)
          # # drivenroads = gpd.sjoin_nearest( carroads, gpd.GeoDataFrame(data = {'count': [1]*len(self.HourlyTraffic), 'geometry':self.HourlyTraffic}, geometry="geometry", crs=crs), how="inner", max_distance = 50)[["fid", "count"]] # map matching, improve with leuvenmapmatching
          # drivenroads = carroads.merge(drivenroads.groupby(['fid'], as_index=False).sum(), on="fid")
          # self.TraffGrid = gpd.sjoin(drivenroads, AirPollGrid.drop("count", axis= 1) , how="right", predicate="intersects")
          # self.TraffGrid['count'] = self.TraffGrid['count'].fillna(0)
          # self.TraffGrid = AirPollGrid.drop("count", axis= 1).merge(self.TraffGrid[["int_id", "count"]].groupby(['int_id'], as_index=False).mean(), on="int_id")
          print("joined traffic tracks to grid")
          if TraffStage == "Regression":
              self.TraffCountRegression(HourlyTraffic)
        else:
          self.TraffGrid = AirPollGrid.loc[:,["int_id", "geometry", "ON_ROAD", "baseline_NO2", self.TraffVcolumn]]
          self.TraffGrid['count'] = 0
          
        if TraffStage in ["PredictionNoR2","PredictionR2"]:
          self.TotalTraffCalc(HourlyTraffic)        
        elif TraffStage == "Remainder":
          self.TrafficRemainderCalc(HourlyTraffic)
        else:
          self.TraffGrid["TraffV"] = self.TraffGrid['count']
        self.PlotTraffPred()

    def OnRoadEmission(self):
        self.TraffGrid["TraffNO2"] = self.TraffGrid["TraffV"] * TraffNO2Coeff 
    
    def OffRoadDispersion(self):
        global airpoll_grid_raster, moderator_df
        # assigning the trafficV values to the raster
        airpoll_grid_raster[:] = np.array(self.TraffGrid["TraffNO2"].values).reshape(airpoll_grid_raster.shape)
        # airpoll_grid_raster = CellularAut_utils.cellautom_dispersion(weightmatrix = self.weightsmatrix, 
        #                                                  airpollraster = airpoll_grid_raster, 
        #                                                  monthlyweather = self.monthly_weather_df.loc[self.monthly_weather_df["month"] == self.current_datetime.month],
        #                                                  moderator_df = moderator_df, 
        #                                                  include_baseline_in_dispersion = False,
        #                                                  baseline_NO2 = self.TraffGrid["baseline_NO2"],
        #                                                  params = list(paramvalues["values"]))
        airpoll_grid_raster = CellularAut_utils.cellautom_dispersion_dummy(weightmatrix = self.weightsmatrix, airpollraster = airpoll_grid_raster, nr_repeats=3, multiplier=1.074067,
                                                                            baseline_NO2 = AirPollGrid["baseline_NO2"], include_baseline_in_dispersion = False)
        self.TraffGrid["NO2"] = np.asarray(airpoll_grid_raster[:]).flatten() 
        self.TraffGrid.loc[self.TraffGrid["ON_ROAD"] == 1,"NO2"] = self.TraffGrid.loc[self.TraffGrid["ON_ROAD"] == 1,"TraffNO2"] + self.TraffGrid.loc[self.TraffGrid["ON_ROAD"] == 1,"baseline_NO2"]
        AirPollGrid[f"prNO2_m{self.current_datetime.month}_h{self.hour}"] = self.TraffGrid["NO2"]
    
    def PlotAirPoll(self):
        self.TraffGrid.plot("NO2", antialiased=False, legend = True)
        plt.title(f"NO2 Prediction: Month {self.current_datetime.month}, Hour {self.hour -1}")
        plt.savefig(path_data + f'ModelRuns/NO2/NO2_A{nb_humans}_H{self.hour-1}_M{self.current_datetime.month}_{modelname}.png')
        plt.close()
        time.sleep(1)
    
    def step(self):
        # manage time variables
        self.current_datetime += self.steps_minute
        print(self.current_datetime)
        self.minute = self.current_datetime.minute
        if self.current_datetime.day == 1 and self.current_datetime.hour == 0 and self.current_datetime.minute == 0: # new month
            self.DetermineWeather() 
            # self.CalculateMonthlyWeightMatrix()   
        if self.minute == 0:  # new hour
            print("hourly executiontime Human Steps: ", self.hourlyext)
            self.hourlyext = 0
            # print("Current time: ", self.current_datetime)
            self.hour = self.current_datetime.hour
            st = time.time()
            self.TrafficAssignment()
            print("Traffic Assignment time: ", time.time() - st, "Seconds")
            st = time.time()
            if TraffStage in ["PredictionNoR2", "PredictionR2"]:
              self.OnRoadEmission()
              self.OffRoadDispersion()
              print("Hybrid Dispersion Model: ", time.time() - st, "Seconds")
              self.PlotAirPoll()

        self.activitystep = int((self.hour * 6) + (self.minute / 10))
        if self.current_datetime.hour == 0: # new day
            self.weekday = self.current_datetime.weekday()

        st = time.time()        
        if self.minute == 0:
          ModalSplitH = pool.starmap(RetrieveModalSplitHour, [(agents, 0) for agents in np.array_split(self.agents, n)], chunksize = 1)
          ModalSplitLog.write(f"{self.current_datetime}, {Counter(list(it.chain.from_iterable(filter(None, list(it.chain.from_iterable(ModalSplitH))))))}\n")
          if TraffStage in ["PredictionNoR2", "PredictionR2"]:
            if modelvars == "allvars_strict":
              self.agents = list(it.chain.from_iterable(pool.starmap(hourly_worker_process_strict, [(agents, self.current_datetime, np.array(self.TraffGrid["NO2"]))  for agents in np.array_split(self.agents, n)], chunksize=1)))
            else:
              self.agents = list(it.chain.from_iterable(pool.starmap(hourly_worker_process, [(agents, self.current_datetime, np.array(self.TraffGrid["NO2"]), self.WeatherVars)  for agents in np.array_split(self.agents, n)], chunksize=1)))
            print("collecting and saving exposure")
            AgentExposure = pool.starmap(RetrieveExposure, [(agents, 0) for agents in np.array_split(self.agents, n)], chunksize = 1)
            pd.DataFrame([item for items in AgentExposure for item in items], columns=['agent', 'NO2', 'MET']).to_csv(path_data + f'ModelRuns/AgentExposure/AgentExposure_A{nb_humans}_M{self.current_datetime.month}_H{self.hour-1}_{modelname}.csv', index=False)
          else:
            if modelvars == "allvars_strict":
              self.agents = list(it.chain.from_iterable(pool.starmap(worker_process_strict, [(agents, self.current_datetime)  for agents in np.array_split(self.agents, n)], chunksize=1)))
            else:
              self.agents = list(it.chain.from_iterable(pool.starmap(worker_process, [(agents, self.current_datetime, self.WeatherVars)  for agents in np.array_split(self.agents, n)], chunksize=1)))
        else:
          if modelvars == "allvars_strict":
            self.agents = list(it.chain.from_iterable(pool.starmap(worker_process_strict, [(agents, self.current_datetime)  for agents in np.array_split(self.agents, n)], chunksize=1)))
          else:
            self.agents = list(it.chain.from_iterable(pool.starmap(worker_process, [(agents, self.current_datetime, self.WeatherVars)  for agents in np.array_split(self.agents, n)], chunksize=1)))
            
        gc.collect(generation=0)
        gc.collect(generation=1)
        gc.collect(generation=2)
        self.hourlyext += time.time() - st
        print("Human Step Time: ", time.time() - st, "Seconds")
        


if __name__ == "__main__":  
    print("Starting the script at", datetime.now())
    #############################################################################################################
    ### Setting simulation parameters
    #############################################################################################################
    ## Nr of Processors
    print("Nr of available logical CPUs", os.cpu_count())
    n = os.cpu_count()-4
    print("Nr of assigned processes", n)
    
    
    # Number of Humans
    nb_humans = 21750     #87000 = 10%, 43500 = 5%, 21750 = 2.5%, 8700 = 1%

    # New Population sample or already existing one
    newpop = False
    
    # Length of the simulation run
    NrHours = 26
    NrDays = 1
    
    # Starting Date and Time
    starting_date = datetime(2019, 1, 1, 0, 50, 0)
    
    # Type of scenario
    # modelname = "StatusQuo" 
    # modelname = "SpeedInterv"
    # modelname = "RetaiDnsDiv"
    # modelname = "PedStrWidth"
    # modelname = "LenBikRout"
    # modelname = "PedStrWidthOutskirt"
    # modelname = "PedStrWidthCenter"
    # modelname = "AmenityDnsExistingAmenityPlaces"
    modelname  = "AmenityDnsDivExistingAmenityPlaces"
    
    
    # cellsize of the Airpollution and Traffic grid
    cellsize = 50    # 50m x 50m
    
    # Profiling code or not
    profile = False
    
    # Stage of the Traffic Model
    TraffStage = "PredictionR2" # "Remainder" or "Regression" or "PredictionNoR2" or "PredictionR2" 
    
    # modal choice model
    # modelvars = "allvars_strict"
    modelvars = "allvars"
    
    # PCstat = "PCA"
    PCstat = "NOPCA"
    
    # Traffic Model
    if nb_humans == 21750:
      TraffVCoeff =  3.171920208      # 43500 = 1.93116625	21750 = 3.171920208	8700 = 7.214888208
    elif nb_humans == 43500:
      TraffVCoeff =  1.93116625      # 43500 = 1.93116625	21750 = 3.171920208	8700 = 7.214888208
    elif nb_humans == 8700:
      TraffVCoeff =  7.214888208      # 43500 = 1.93116625	21750 = 3.171920208	8700 = 7.214888208
    TraffNO2Coeff = 0.03096377438925   # for 50m cellsize

    
    #############################################################################################################
    
    # Read Main Data
    path_data = "C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/"
    
    # Synthetic Population
    print("Reading Population Data")
    if newpop:
      pop_df = pd.read_csv(path_data+"Population/Agent_pop_clean.csv")
      random_subset = pd.DataFrame(pop_df.sample(n=nb_humans))
      random_subset.to_csv(path_data+f"Population/Amsterdam_population_subset{nb_humans}.csv", index=False)
    else:
      random_subset = pd.read_csv(path_data+f"Population/Amsterdam_population_subset{nb_humans}.csv")

    random_subset["student"] = 0
    random_subset.loc[random_subset["current_education"] == "high", "student"] = 1

    # Activity Schedules
    print("Reading Activity Schedules")
    # scheduledf_monday = pd.read_csv(path_data+"ActivitySchedules/HETUS2010_Synthpop_schedules_day1.csv")
    # scheduledf_tuesday = pd.read_csv(path_data+"ActivitySchedules/HETUS2010_Synthpop_schedules_day2.csv")
    # scheduledf_wednesday = pd.read_csv(path_data+"ActivitySchedules/HETUS2010_Synthpop_schedules_day3.csv")
    # scheduledf_thursday = pd.read_csv(path_data+"ActivitySchedules/HETUS2010_Synthpop_schedules_day4.csv")
    # scheduledf_friday = pd.read_csv(path_data+"ActivitySchedules/HETUS2010_Synthpop_schedules_day5.csv")
    # scheduledf_saturday = pd.read_csv(path_data+"ActivitySchedules/HETUS2010_Synthpop_schedules_day6.csv")
    # scheduledf_sunday = pd.read_csv(path_data+"ActivitySchedules/HETUS2010_Synthpop_schedules_day7.csv")
    scheduledf_monday = pd.read_csv(path_data+"ActivitySchedules/HETUS2010_Synthpop_schedulesclean_day1.csv")
    scheduledf_tuesday = pd.read_csv(path_data+"ActivitySchedules/HETUS2010_Synthpop_schedulesclean_day2.csv")
    scheduledf_wednesday = pd.read_csv(path_data+"ActivitySchedules/HETUS2010_Synthpop_schedulesclean_day3.csv")
    scheduledf_thursday = pd.read_csv(path_data+"ActivitySchedules/HETUS2010_Synthpop_schedulesclean_day4.csv")
    scheduledf_friday = pd.read_csv(path_data+"ActivitySchedules/HETUS2010_Synthpop_schedulesclean_day5.csv")
    scheduledf_saturday = pd.read_csv(path_data+"ActivitySchedules/HETUS2010_Synthpop_schedulesclean_day6.csv")
    scheduledf_sunday = pd.read_csv(path_data+"ActivitySchedules/HETUS2010_Synthpop_schedulesclean_day7.csv")
    schedulelist = [scheduledf_monday, scheduledf_tuesday, scheduledf_wednesday, scheduledf_thursday, scheduledf_friday, scheduledf_saturday, scheduledf_sunday]
    del scheduledf_monday, scheduledf_tuesday, scheduledf_wednesday, scheduledf_thursday, scheduledf_friday, scheduledf_saturday, scheduledf_sunday

    # Coordinate Reference System and CRS transformers
    crs = "epsg:28992"
    project_to_WSG84 = Transformer.from_crs(crs, "epsg:4326", always_xy=True).transform
    projecy_to_crs = Transformer.from_crs("epsg:4326", crs, always_xy=True).transform

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
    carroads = gpd.read_feather(path_data+"FeatherDataABM/carroads.feather")

    # Load Intervention Environment
    # Status Quo
    if modelname == "StatusQuo":
      EnvBehavDeterms = gpd.read_feather(path_data+"FeatherDataABM/EnvBehavDeterminants.feather")
    # Speed Limit Intervention
    else:
      EnvBehavDeterms = gpd.read_feather(path_data+f"FeatherDataABM/EnvBehavDeterminants{modelname}.feather")
  

  
    # Read the Environmental Stressor Data and Model
    AirPollGrid = gpd.read_feather(path_data+f"FeatherDataABM/AirPollgrid{cellsize}m.feather")
    AirPollPred = pd.read_csv(path_data+f"Air Pollution Determinants/Pred_{cellsize}m.csv")
    TraffDat = pd.read_csv(path_data+ "Air Pollution Determinants/AirPollRaster50m_TraffVdata.csv")
    airpoll_grid_raster = xr.open_dataarray(path_data+ f"Air Pollution Determinants/AirPollDeterm_grid_{cellsize}m.tif", engine="rasterio")[0] # Read raster data using rasterio
    moderator_df = pd.read_csv(path_data+ f"Air Pollution Determinants/moderator_{cellsize}m.csv")     # Read moderator DataFrame
    paramvalues = pd.read_csv(path_data+ f"Air Pollution Determinants/GAparam_results_python_5_{cellsize}m.csv") # Read calibrated parameters
    
    # Preparing Data    
    AirPollGrid[["baseline_NO2", "ON_ROAD"]] = AirPollPred[["baseline_NO2", "ON_ROAD"]]
    AirPollGrid = AirPollGrid.merge(TraffDat[['int_id','StreetIntersectDensity', 'MaxSpeedLimit', 'MinSpeedLimit', 'MeanSpeedLimit']], how = "left", on = "int_id")

    if TraffStage in ["PredictionNoR2", "PredictionR2"]:
      TraffVrest = pd.read_csv(path_data+f"ModelRuns/TrafficMaps/Remainder/AirPollGrid_HourlyTraffRemainder_{nb_humans}.csv")
      AirPollGrid = AirPollGrid.merge(TraffVrest, how = "left", on = "int_id")
        
    # Looking at Data
    print("AirPollGrid Columns: ", AirPollGrid.columns)
    print("AirPollGrid Shape: ", AirPollGrid.shape)    
    print("Moderator Columns: ", moderator_df.columns)
    print("AirPollRaster Shape: ", airpoll_grid_raster.shape)       
    
    # Start OSRM Servers
    print("Starting OSRM Servers")
    subprocess.call([r"C:\Users\Tabea\Documents\GitHub\Spatial-Agent-based-Modeling-of-Urban-Health-Interventions\start_OSRM_Servers.bat"])


    # Read the Mode of Transport Choice Model
    print("Reading Mode of Transport Choice Model")
    if modelvars == "allvars":
        routevariables = ["popDns", "retaiDns","greenCovr", "RdIntrsDns", "TrafAccid", "NrTrees", "MeanTraffV", "HighwLen", "AccidPedes",
                        "PedStrWidt", "PedStrLen", "LenBikRout", "DistCBD", "retailDiv", "MeanSpeed", "MaxSpeed", "NrStrLight", "CrimeIncid",
                        "MaxNoisDay", "OpenSpace", "PNonWester", "PWelfarDep", "SumTraffVo", "pubTraDns", "MxNoisNigh", "MinSpeed", "PrkPricPre", "PrkPricPos" ]
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

    routevariables_suff = Math_utils.add_suffix(routevariables, ".route")
    originvariables_suff = Math_utils.add_suffix(originvariables, ".orig")
    destinvariables_suff = Math_utils.add_suffix(destinvariables, ".dest")

    if modelvars == "allvars_strict":  
        colvars = routevariables_suff + originvariables_suff + destinvariables_suff + personalvariables + tripvariables
    elif modelvars == "allvars":
        colvars = routevariables_suff + originvariables_suff + destinvariables_suff + personalvariables + tripvariables + weathervariables

    ModalChoiceModel = PMMLTreeClassifier(pmml=path_data+f"ModalChoiceModel/modalChoice_{modelvars}{PCstat}.pmml")
    ModalChoiceModel.splitter = "random"
    OrderPredVars = [x for x in ModalChoiceModel.fields][1:]
    print(OrderPredVars)

    if PCstat == "PCA":
        FactorLoadings = pd.read_csv(path_data+f"ModalChoiceModel/{modelvars}_PCLoadings.csv")
    else:
        FactorLoadings = None
  
  
    # Preparing Log Documents
    print("Preparing Log Documents")
    if TraffStage != "PredictionNoR2":
      TraffAssDat = open(f'{path_data}TraffAssignModelPerf{nb_humans}_{modelname}.txt', 'a',buffering=1)
      TraffAssDat.write(f"Number of Agents: {nb_humans} \n")

    ModalSplitLog = open(f'{path_data}ModelRuns/ModalSplit/ModalSplitLog{nb_humans}_{modelname}.txt', 'a',buffering=1)
    ModalSplitLog.write(f"Number of Agents: {nb_humans} \n")


    # Initializing Simulation
    m = TransportAirPollutionExposureModel(nb_humans=nb_humans, path_data=path_data, starting_date=starting_date)
   
    print("Starting Multiprocessing Pool")
    pool =  Pool(processes=n, initializer= init_worker_simul, initargs=(Residences, Entertainment, Restaurants, EnvBehavDeterms, 
                                                          ModalChoiceModel, OrderPredVars, colvars, project_to_WSG84, 
                                                          projecy_to_crs, crs, routevariables, originvariables, 
                                                          destinvariables, airpoll_grid_raster, AirPollGrid[["int_id", "ON_ROAD", "geometry"]], modelvars, PCstat, 
                                                          FactorLoadings))

    print("Starting Simulation")
    if profile:
      f = open(path_data+'profile_results.txt', 'w')
      for t in range(144):      
        # Profile the ABM run
        cProfile.run('m.step()', 'profile_results')
        # Print or save the profiling results
        p = pstats.Stats('profile_results', stream=f)
        # p.strip_dirs().sort_stats('cumulative').print_stats()
        p.strip_dirs().sort_stats('time').print_stats()
        p.print_callees()

      f.close()
    
    else:
      for day in range(NrDays):
        for hour in range(NrHours):
          for t in range(6):
              m.step()


    pool.terminate()         
            
    if TraffStage in ["PredictionNoR2", "PredictionR2"]:
      pd.DataFrame(AirPollGrid).to_csv(path_data+f"ModelRuns/NO2/AirPollGrid_NO2_pred{nb_humans}_{modelname}.csv", index=False)
    elif TraffStage == "Remainder":
      traffrestcols = [f"TraffVrest{hour}" for hour in range(24)]
      pd.DataFrame(AirPollGrid[["int_id"]+ traffrestcols]).to_csv(path_data+f"ModelRuns/TrafficMaps/Remainder/AirPollGrid_HourlyTraffRemainder_{nb_humans}.csv", index=False)
    
    if TraffStage != "PredictionNoR2":
      TraffAssDat.close()

    ModalSplitLog.close()
    print("Finished the script at", datetime.now())
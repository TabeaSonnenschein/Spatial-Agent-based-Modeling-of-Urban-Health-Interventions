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
from sklearn_pmml_model.ensemble import PMMLForestClassifier
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
import joblib as jl
import json
import csv

# my own functions
import CellAutDisp as CAD
import Math_utils

# import logging
# import multiprocessing.util
# multiprocessing.util.log_to_stderr(level=logging.DEBUG)

warnings.filterwarnings("ignore", module="shapely")


def init_worker_init(schedules, Resid, univers, Scho, Prof, Supermark, greenspac, kindergard):
    global schedulelist, Residences, Universities, Schools, Profess, Entertainment, Restaurants, Supermarkets, greenspace, Kindergardens
    schedulelist = schedules
    Residences = Resid
    Universities = univers
    Schools = Scho
    Profess = Prof
    Supermarkets = Supermark
    greenspace = greenspac
    Kindergardens = kindergard

    # initialize worker processes
def init_worker_simul(Resid, Entertain, Restaur, shops, envdeters, modalchoice, ordprevars, cols, projectWSG84, projcrs, crs_string, routevars, originvars, destinvars, Grid, airpolgr):
    global Residences, Entertainment, Restaurants, ShopsnServ, EnvBehavDeterms, ModalChoiceModel, OrderPredVars, colvars, project_to_WSG84, projecy_to_crs, crs, routevariables, originvariables, destinvariables, EnvStressGrid, AirPollGrid
    Residences = Resid
    Entertainment = Entertain
    Restaurants = Restaur
    ShopsnServ = shops
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

def RetrieveNoEVRoutes(thishourmode, thishourtrack, evaccess):
   if (evaccess == 0) & ("drive" in thishourmode):
      return([thishourtrack[count] for count, value in enumerate(thishourmode) if value == "drive"])

def RetrieveExposure(agents, dum):
    return [[agent.unique_id, agent.hourlyNO2, agent.hourlyNO2wFilter, agent.hourlyMET, agent.thishourindoor]  for agent in agents]
  
def RetrieveAllTracksHour(agents, dum):
    return [[agent.unique_id, agent.thishourtrack, agent.thishourmode, agent.thishourduration]  for agent in agents]

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
        global schedulelist, Residences, Universities, Schools, Profess, Entertainment, Restaurants, Supermarkets, greenspace, Kindergardens
        self.unique_id = vector.iloc[0]
        super().__init__(self.unique_id, model)
        # socio-demographic attributes
        self.Neighborhood = vector.iloc[1]
        self.current_edu = vector.iloc[8]          # "high", "middle", "low", "no_current_edu"
        self.IndModalPreds = [vector.iloc[i] for i in [19,2,13,20,21,22,17,11,12,23,24,25,15,14,16]] # "sex_male", "age", "car_access", 
                                                                # "Western", "Non_Western", "Dutch", 'income','employed',
                                                                #'edu_3_levels','HH_size', 'Nrchildren', 'student', 'driving_habit','biking_habit',
                                                                #'transit_habit']

        # Activity Schedules
        self.ScheduleID = vector.iloc[18]          # Schedule IDs
        self.WeekSchedules = []
        self.WeekLocations = []
        for x in range(7):
          self.WeekSchedules.append(list(schedulelist[x].loc[schedulelist[x]["SchedID"] == self.ScheduleID, ].values[0][1:145]))
          self.WeekLocations.append(list(schedulelist[x].loc[schedulelist[x]["SchedID"] == self.ScheduleID, ].values[0][145:]))
        self.former_activity = self.WeekSchedules[self.model.weekday][self.model.activitystep]
        self.activity = "perform_activity"
        self.weekday = self.model.weekday
        self.activitystep=self.model.activitystep
        
        if self.model.scenario == "NoEmissionZone2025":
          self.eletriccaraccess = vector.iloc[27]
        if self.model.scenario == "NoEmissionZone2030":
          self.eletriccaraccess = vector.iloc[28]

        # regular destinations
        try:
            self.Residence = Residences.loc[Residences["nghb_cd"] == self.Neighborhood, "geometry"].sample(1).values[0].coords[0]
        # there are some very few synthetic population agents that come from a neighborhood without residential buildings (CENSUS)
        except:
            self.Residence = Residences["geometry"].sample(1).values[0].coords[0]
        else:
            pass
        if self.model.scenario == "15mCityWithDestination":  
            self.radius15min = Point(self.Residence).buffer(1275)
        if self.current_edu == "high":
            self.University = Universities["geometry"].sample(1).values[0].coords[0]
            self.homeTOschool_geometry, self.schoolTOhome_geometry = None, None
        elif (self.current_edu != "no_current_edu") or (4 in list(np.concatenate(self.WeekSchedules).flat)):
            self.School = [(p.x, p.y) for p in nearest_points(Point(tuple(self.Residence)), Schools["geometry"].unary_union)][1]
            self.homeTOschool_geometry, self.schoolTOhome_geometry = None, None
        if 3 in list(np.concatenate(self.WeekSchedules).flat):
            if self.model.scenario == "15mCityWithDestination":  
                nearProff = Profess["geometry"].intersection(self.radius15min)
                if len(nearProff[~nearProff.is_empty]) == 0:
                  self.Workplace = [(p.x, p.y) for p in nearest_points(Point(tuple(self.Residence)), Profess["geometry"].unary_union)][1]
                else:
                  self.Workplace = nearProff[~nearProff.is_empty].sample(1).values[0].coords[0]
            else:
                self.Workplace = Profess["geometry"].sample(1).values[0].coords[0]
            self.homeTOwork_geometry, self.workTOhome_geometry = None, None
        
        if 8 in list(np.concatenate(self.WeekSchedules).flat):
            self.Park = [(p.x, p.y) for p in nearest_points(Point(tuple(self.Residence)), greenspace["geometry"].unary_union)][1]
        if 13 in list(np.concatenate(self.WeekSchedules).flat):
            if self.model.scenario == "15mCityWithDestination":  
                nearkindergardens = Kindergardens["geometry"].intersection(self.radius15min)
                if len(nearkindergardens[~nearkindergardens.is_empty]) == 0:
                  self.Kindergarden = [(p.x, p.y) for p in nearest_points(Point(tuple(self.Residence)), Kindergardens["geometry"].unary_union)][1]
                else:
                  self.Kindergarden = nearkindergardens[~nearkindergardens.is_empty].sample(1).values[0].coords[0]
            else:
                self.Kindergarden = Kindergardens["geometry"].sample(1).values[0].coords[0]
            self.homeTOkinderga_geometry, self.kindergaTOhome_geometry = None, None
        if 9 in list(np.concatenate(self.WeekSchedules).flat):
            self.Supermarket = [(p.x, p.y) for p in nearest_points(Point(tuple(self.Residence)), Supermarkets["geometry"].unary_union)][1]
            self.homeTOsuperm_geometry, self.supermTOhome_geometry = None, None
        
        self.TripVars = [0,0,0,0,0]  #"purpose_commute", 'purpose_leisure','purpose_groceries_shopping','purpose_education', 'purpose_bring_person'
        self.destination_activity = self.Residence
        
        # mobility behavior variables
        self.path_memory = 0
        self.traveldecision = 0
        self.thishourtrack, self.thishourmode, self.thishourduration = [], [], []
        self.nexthoursmodes, self.nexthourstracks, self.nexthourduration = [], [], []

        # exposure variables
        self.newplace, self.newactivity = 0, 0
        self.visitedPlaces, self.durationPlaces, self.activities, self.durationActivties =  [Point(tuple(self.Residence))], [0], [self.WeekSchedules[self.weekday][self.activitystep]], [0]
        self.thishourindoor = 0
        self.hourlytravelNO2, self.hourlyplaceNO2, self.hourlyplaceNO2wFilter, self.hourlyNO2, self.hourlyNO2wFilter = 0,0,0,0,0
        self.hourlytravelMET, self.hourlyMET = 0,0
        
        
    def ScheduleManager(self, current_datetime):
      global Kindergardens, ShopsnServ
      # identifying the current activity
      self.current_activity = self.WeekSchedules[self.weekday][self.activitystep]
      # identifying whether activity changed and if so, where the new activity is locatec and whether we have a saved route towards that destination
      if self.current_activity != self.former_activity:
        if self.activity == "traveling":
          formerdestination = self.destination_activity
        commute,leisure,groceries,edu_trip = 0,0,0,0
        # print("Current Activity: ", self.current_activity," Former Activity: ", self.former_activity)
        if self.current_activity == 3:  # 3 = work
          commute = 1
          if self.WeekLocations[self.weekday][self.activitystep] == 0:
            self.destination_activity = self.pos
          else:
            self.destination_activity = self.Workplace
            if (self.homeTOwork_geometry != None) and  (self.former_activity in [5, 1, 6, 7]):  # 1 = sleep/rest, 5 = at home, 6 = cooking, 7 = gardening
              self.track_geometry = self.homeTOwork_geometry
              self.modalchoice = self.homeTOwork_mode
              self.track_duration = self.homeTOwork_duration
              self.path_memory = 1

        elif self.current_activity == 4:  # 4 = school/university
          edu_trip = 1
          if self.current_edu == "high":
            self.destination_activity = self.University
          else:
            self.destination_activity = self.School
          # 1 = sleep/rest, 5 = at home, 6 = cooking, 7 = gardening
          if (self.homeTOschool_geometry != None) and (self.former_activity in [5, 1, 6, 7]): 
            self.track_geometry = self.homeTOschool_geometry
            self.modalchoice = self.homeTOschool_mode
            self.track_duration = self.homeTOschool_duration
            self.path_memory = 1

        elif self.current_activity == 9:  # 9 = shopping/services
          if random.random() < 0.72: #number taken from Veenstra et al., 2009
            self.destination_activity = self.Supermarket
            groceries = 1
            if (self.homeTOsuperm_geometry != None) and (self.former_activity in [5, 1, 6, 7]): # 1 = sleep/rest, 5 = at home, 6 = cooking, 7 = gardening
              self.track_geometry = self.homeTOsuperm_geometry
              self.track_duration = self.homeTOsuperm_duration
              self.modalchoice = self.homeTOsuperm_mode
              self.path_memory = 1
          else:
            if self.model.scenario == "15mCityWithDestination":  
                nearShops = ShopsnServ["geometry"].intersection(self.radius15min)
                if len(nearShops[~nearShops.is_empty]) == 0:
                  self.destination_activity = [(p.x, p.y) for p in nearest_points(Point(tuple(self.Residence)), ShopsnServ["geometry"].unary_union)][1]
                else:
                  self.destination_activity = nearShops[~nearShops.is_empty].sample(1).values[0].coords[0]
            else:
                self.destination_activity = ShopsnServ["geometry"].sample(1).values[0].coords[0]
            

        elif self.current_activity == 13: # 13= kindergarden
          self.destination_activity = self.Kindergarden
          # 1 = sleep/rest, 5 = at home, 6 = cooking, 7 = gardening
          if (self.homeTOkinderga_geometry != None) and (self.former_activity in [5, 1, 6, 7]):
            self.track_geometry = self.homeTOkinderga_geometry
            self.track_duration = self.homeTOkinderga_duration
            self.modalchoice = self.homeTOkinderga_mode
            self.path_memory = 1

        # 1 = sleep/rest, 5 = at home, 6 = cooking, 7 = gardening
        elif self.current_activity in [5, 1, 6, 7]:
          self.destination_activity = self.Residence
          if (self.former_activity == 3) and (self.workTOhome_geometry != None) :  # 3 = work
              self.track_geometry = self.workTOhome_geometry
              self.modalchoice = self.homeTOwork_mode
              self.track_duration = self.homeTOwork_duration
              self.path_memory = 1

          elif (self.former_activity == 4) and (self.schoolTOhome_geometry != None):  # 4 = school/university
              self.track_geometry = self.schoolTOhome_geometry
              self.modalchoice = self.homeTOschool_mode
              self.track_duration = self.homeTOschool_duration
              self.path_memory = 1

          elif (self.former_activity == 9) and (self.TripVars[2] == 1) and (self.supermTOhome_geometry != None): # 9 = shopping/services
              self.track_geometry = self.supermTOhome_geometry
              self.modalchoice = self.homeTOsuperm_mode
              self.track_duration = self.homeTOsuperm_duration
              self.path_memory = 1

          elif (self.former_activity == 13) and (self.kindergaTOhome_geometry != None) :
              self.track_geometry = self.kindergaTOhome_geometry
              self.modalchoice = self.homeTOkinderga_mode
              self.track_duration = self.homeTOkinderga_duration
              self.path_memory = 1

        elif self.current_activity == 11: # entertainment / culture
          leisure = 1
          if self.model.scenario == "15mCityWithDestination":  
                nearEntertain = Entertainment["geometry"].intersection(self.radius15min)
                if len(nearEntertain[~nearEntertain.is_empty]) == 0:
                  self.destination_activity = [(p.x, p.y) for p in nearest_points(Point(tuple(self.Residence)), Entertainment["geometry"].unary_union)][1]
                else:
                  self.destination_activity = nearEntertain[~nearEntertain.is_empty].sample(1).values[0].coords[0]
          else:
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
            if self.model.scenario == "15mCityWithDestination":  
                nearFriends = Residences["geometry"].intersection(self.radius15min)
                if len(nearFriends[~nearFriends.is_empty]) == 0:
                  self.destination_activity = [(p.x, p.y) for p in nearest_points(Point(tuple(self.Residence)), Residences["geometry"].unary_union)][1]
                else:
                  self.destination_activity = nearFriends[~nearFriends.is_empty].sample(1).values[0].coords[0]
            else:
                self.destination_activity = Residences["geometry"].sample(1).values[0].coords[0]

        elif self.current_activity == 8: # 8 = sports/ outdoor activity
          self.destination_activity = self.Park

        # Identifying whether agent needs to travel to new destination: if the destination is not the current position and the agent is not already traveling to that destination
        if (self.destination_activity != self.pos) and ((self.activity != "traveling") or ((self.activity == "traveling") and (formerdestination != self.destination_activity))):
          if (self.path_memory != 1) or ((self.activity == "traveling") and (formerdestination != self.destination_activity)):
              if (self.activity == "traveling") and (formerdestination != self.destination_activity): # if the agent is already traveling and the destination has changed, we assume they have arrived at the former destination
                self.pos = formerdestination
              self.traveldecision = 1
              self.route_eucl_line = LineString([Point(tuple(self.pos)), Point(tuple(self.destination_activity))])
              self.trip_distance = self.route_eucl_line.length
              self.TripVars = [commute,leisure,groceries,edu_trip,0]  #"purpose_commute", 'purpose_leisure','purpose_groceries_shopping','purpose_education', 'purpose_bring_person'
          else:
              self.activity = "traveling"
              self.arrival_time = current_datetime + timedelta(minutes=self.track_duration)
              self.TripSegmentsPerHour()
          self.path_memory = 0
          self.newplace = 1
        elif self.activity == "traveling":
          pass
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
      pred_df = pd.DataFrame(np.concatenate((RouteVars, OrigVars, DestVars, self.IndModalPreds, [self.trip_distance],self.TripVars, WeatherVars), axis=None).reshape(1, -1), 
                                columns=colvars).fillna(0)
      # predicting modechoice
      if (self.model.scenario == "NoEmissionZone2030"):
        if (self.eletriccaraccess == 0):
          modechoice_probs = ModalChoiceModel.predict_proba(pred_df[OrderPredVars])
          modechoice_probs[0][1] = 0
          self.modechoice = np.argmax(modechoice_probs) + 1
        else:
          self.modechoice = ModalChoiceModel.predict(pred_df[OrderPredVars])[0]
      else:
        self.modechoice = ModalChoiceModel.predict(pred_df[OrderPredVars])[0]
      self.modechoice = ["bike", "drive", "transit", "walk"][self.modechoice-1]

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
      self.track_duration = round((res['routes'][0]['duration'])/60)  # minutes
      if self.modechoice == "transit":
        self.track_duration =  round(self.track_duration/10,0)
      self.trip_distance = res['routes'][0]['distance']  # meters
    
    def SavingRoute(self):
      if(self.former_activity in [5, 1, 6, 7]):
        if (self.current_activity == 3) and (self.WeekLocations[self.weekday][self.activitystep] == 1): # 3 = work  at workplace (loc == 1)
            self.homeTOwork_mode = self.modechoice
            self.homeTOwork_geometry = self.track_geometry 
            self.homeTOwork_duration = self.track_duration
            self.workTOhome_geometry = Math_utils.reverse_geom(self.track_geometry)
		
        elif self.current_activity == 4: # 4 = school/university
            self.homeTOschool_mode = self.modechoice
            self.homeTOschool_geometry = self.track_geometry  
            self.homeTOschool_duration = self.track_duration
            self.schoolTOhome_geometry = Math_utils.reverse_geom(self.track_geometry)

        elif (self.current_activity == 9) and (self.TripVars[2] == 1): # 9 = shopping/services and TripVars[2] == 1 is groceries
            self.homeTOsuperm_mode = self.modechoice
            self.homeTOsuperm_geometry = self.track_geometry 
            self.homeTOsuperm_duration = self.track_duration
            self.supermTOhome_geometry = Math_utils.reverse_geom(self.track_geometry)
			
        elif self.current_activity == 13 : # 13 = kindergarden
            self.homeTOkinderga_mode = self.modechoice
            self.homeTOkinderga_geometry = self.track_geometry 
            self.homeTOkinderga_duration = self.track_duration
            self.kindergaTOhome_geometry = Math_utils.reverse_geom(self.track_geometry)
    
    def TripSegmentsPerHour(self):
      if self.arrival_time.hour != self.hour:
          self.track_length = self.track_geometry.length
          # identifying the fraction of trip that is in the current hour
          if self.track_duration > 0:
              self.trip_segments = [((60 - self.minute)/self.track_duration)]        
              #if the trip intersects more than two hour slots
              if (self.track_duration-(60 - self.minute)) > 60: 
                # repeat the fraction of trip in one hour for the remaining hours, the fractions should be less than 1 when summed
                self.trip_segments.extend(list(it.repeat(60/self.track_duration,int((self.track_duration-(60 - self.minute))/60))))
                      
              # clip the geometry into segments per hour by splitting the geometry at the fraction of the trip that is in the current hour and all subsequent hours
              self.segment_geometry = [self.track_geometry]
              for x in self.trip_segments:
                # we take take the last geometry in  the list and interpolate a at the length fraction of the trip of that segment
                # snap corrects the interpolated point to the nearest point on the geometry, and then we split the geometry at that point
                self.segment_geometry.extend(split(snap(self.segment_geometry[-1],self.segment_geometry[-1].interpolate(x * self.track_length), 10), self.segment_geometry[-1].interpolate(x * self.track_length)).geoms)
            
              # we take the odd indexed geometries and the last geometry, because when it splits it add the  total remainig geometry and that one is split and added again (all but the last remaining geometry is redundant)
              self.segment_geometry = [self.segment_geometry[x] for x in list(range(1, len(self.segment_geometry)-1,2))+[len(self.segment_geometry)-1]]
            
              # saving the first segment of the trip to be traveled in the current hour
              self.thishourtrack.append(self.segment_geometry[0])
              self.thishourmode.append(self.modechoice)
              self.thishourduration.append(60 - self.minute)
            
              # saving the remaining segments of the trip to be traveled in the next hours
              self.nexthourstracks = self.segment_geometry[1:]
              self.nexthourduration = [(self.track_duration-(60 - self.minute))%60] #modulo of the remaining duration
              if len(self.nexthourstracks)>1:
                self.nexthourduration = list(it.repeat(60, len(self.nexthourstracks)-1)) + self.nexthourduration
              self.nexthoursmodes = list(it.repeat(self.modechoice, len(self.nexthourstracks)))
          else:
            print("Error: Trip duration is 0",self.track_length, self.track_geometry)
            self.thishourtrack.append(self.track_geometry)
            self.thishourmode.append(self.modechoice)
            self.thishourduration.append(self.track_duration)
      else:
          self.thishourtrack.append(self.track_geometry)
          self.thishourmode.append(self.modechoice)
          self.thishourduration.append(self.track_duration)
    
    def TravelingAlongRoute(self, current_datetime):
      if current_datetime >= self.arrival_time:
          self.activity = "perform_activity"
          self.pos = self.destination_activity
          self.durationPlaces.append((10-(self.arrival_time.minute % 10))/10) # the remaining activity time till next 10 minute slot
          self.durationActivties.append((10-(self.arrival_time.minute % 10))/10) # the remaining activity time till next 10 minute slot
          
    def PlaceTracker(self):
      if self.newplace == 1:
        self.visitedPlaces.append(Point(tuple(self.pos)))
        self.durationPlaces[-1] += 1
        self.durationActivties[-1] += 1
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
        indoorfilter = [1 if x == 8 else 0.51 for x in self.activities]  #8 =  outdoor activity hence no filter
        self.hourlyplaceNO2wFilter = sum(np.multiply([EnvStressGrid.sel(x=point.x, y=point.y, method='nearest').values.item(0) for point in self.visitedPlaces], [duration*10*indoorfilter[count] for count, duration in enumerate(self.durationPlaces)]))
        self.thishourindoor = sum([duration*10 for count, duration in enumerate(self.durationPlaces) if self.activities[count] != 8])
        self.hourlyplaceNO2 = sum(np.multiply([EnvStressGrid.sel(x=point.x, y=point.y, method='nearest').values.item(0) for point in self.visitedPlaces], [x*10 for x in self.durationPlaces]))
      else:
        self.thishourindoor = 0

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
    
    def RescaleExcessDuration(self):
      if sum(self.thishourduration) > 60: # seldomly, when people change activities while traveling the additive duration of the trips  can be longer than 60 minutes, so we rescale
          rescaler = 60/sum(self.thishourduration)
          self.thishourduration = [x*rescaler for x in self.thishourduration]
    
    def TravelExposure(self):
      if len(self.thishourtrack) > 0:       # transform overlay function to point in polygon, get points along line (10m), joining points with grid cellsize/2
        # NO2
        trackpoints = [[self.thishourtrack[a].interpolate(d) for d in np.arange(0, self.thishourtrack[a].length, 10)] for a in range(len(self.thishourtrack))]
        trackjoin = [[EnvStressGrid.sel(x=point.x, y=point.y, method='nearest').values.item(0) for point in sublist] for sublist in trackpoints]
        self.hourlytravelNO2 = sum(np.multiply([mean(val) if len(val)>0 else 0 for val in trackjoin], self.thishourduration))
        # self.hourlytravelNO2 = sum(np.multiply([mean(val)*self.model.NO2filters[self.thishourmode[count]] if len(val)>0 else 0 for count, val in enumerate(trackjoin)], self.thishourduration))
        
        # Metabolic Equivalent of Task
        self.hourlytravelMET = sum(np.multiply(list(map(lambda x: float(x.replace('bike', "6.8").replace('drive', "1.65").replace('walk', "3.5").replace('transit', "1.9")) , self.thishourmode))
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
        self.hourlyNO2wFilter = (self.hourlyplaceNO2wFilter + self.hourlytravelNO2)/60
        self.hourlytravelNO2, self.hourlyplaceNO2, self.hourlyplaceNO2wFilter = 0,0,0
        self.hourlyMET = self.hourlytravelMET/60
        self.hourlytravelMET  = 0
  
    def ManageTime(self, current_datetime):
        self.minute = current_datetime.minute
        self.hour = current_datetime.hour
        if self.minute == 0:  # new hour
            self.hour = current_datetime.hour
        self.activitystep = int((self.hour * 6) + (self.minute / 10))
        if self.hour == 0: # new day
            self.weekday = current_datetime.weekday()
    
    def ResetSavedPathNewMonth(self):
        if (self.current_edu == "high") or (self.current_edu != "no_current_edu") or (4 in list(np.concatenate(self.WeekSchedules).flat)):
            self.homeTOschool_geometry, self.schoolTOhome_geometry = None, None
        if 3 in list(np.concatenate(self.WeekSchedules).flat):
            self.homeTOwork_geometry, self.workTOhome_geometry = None, None
        if 13 in list(np.concatenate(self.WeekSchedules).flat):
            self.homeTOkinderga_geometry, self.kindergaTOhome_geometry = None, None
        if 9 in list(np.concatenate(self.WeekSchedules).flat):
          self.homeTOsuperm_geometry, self.supermTOhome_geometry = None, None
    
    def step(self, current_datetime):
        global Residences, Entertainment, Restaurants,  ShopsnServ, EnvBehavDeterms, ModalChoiceModel, OrderPredVars, colvars, project_to_WSG84, projecy_to_crs, crs, routevariables, originvariables, destinvariables
        global WeatherVars
        self.ManageTime(current_datetime)
        # if new month, reset saved pathways
        if (current_datetime.day == 1) and (self.hour == 0) and (self.minute == 0):
            self.ResetSavedPathNewMonth()
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
        if self.minute == 50:
            self.RescaleExcessDuration()



class TransportAirPollutionExposureModel(Model):
    def __init__(self, nb_humans, path_data, crs="epsg:28992",
                 starting_date=datetime(2019, 1, 1, 6, 50, 0), steps_minute=10):
        super().__init__(nb_humans, path_data, crs, starting_date, steps_minute)
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
        print("Weekday: ", self.weekday)
        print("Nr of Humans: ", self.nb_humans)
        self.extentbox = spatial_extent.total_bounds
        self.continoussp = ContinuousSpace(x_max=self.extentbox[2], y_max=self.extentbox[3],
                                           torus=bool, x_min=self.extentbox[0], y_min=self.extentbox[1])
        
        # modal NO2 filters
        # self.NO2filters = {"drive": 1, "bike": 1, "walk": 1, "transit": 1}
        self.scenario = modelname
        
        self.hourlyext = 0
        self.onroadcells = list(AirPollGrid["ON_ROAD"] == 1)
        # Create the agents
        print("Creating Agents")
        st = time.time()
        with Pool(initializer=init_worker_init, initargs=(schedulelist, Residences, Universities, Schools, Profess, Supermarkets, greenspace, Kindergardens)) as pool:
            self.Humans = pool.starmap(Humans, [(random_subset.iloc[x],  self) for x in range(self.nb_humans)], chunksize=100) 
            pool.close()
            pool.join()
            pool.terminate()
        for Human in self.Humans:
            self.continoussp.place_agent(Human, Human.Residence)
        print("Human Init Time: ", time.time() - st, "Seconds")


        # Load Weather data and set initial weather conditions
        self.monthly_weather_df = pd.read_csv(path_data+"Weather/monthlyWeather2019TempDiff.csv") 
        #self.daily_weather_df = pd.read_csv("D:/PhD EXPANSE/Data/Amsterdam/Weather/dailyWeather2019.csv")
        self.WeatherVars = list(self.monthly_weather_df[["Temperature","Rain","Windspeed","Winddirection"]].loc[self.monthly_weather_df["month"]== self.current_datetime.month].values[0])
        print("temperature: " , self.WeatherVars[0] , "rain: " , self.WeatherVars[1], " wind: ", self.WeatherVars[2], " wind direction: ", self.WeatherVars[3])
        
        self.weightsmatrix = CAD.returnCorrectWeightedMatrix(meteolog = False, matrixsize = 3, meteoparams = optimalparams["meteoparams"], meteovalues = self.WeatherVars)
        self.nr_repeats = CAD.provide_meteorepeats(optimalparams["repeatsparams"], self.WeatherVars[2])

        print(self.weightsmatrix)
        
        if modelname == "NoEmissionZone2030":
            self.TraffGrid = AirPollGrid.loc[:,["int_id", "geometry", "ON_ROAD", "baseline_NO2"]]
            self.TraffGrid["NO2"] = self.TraffGrid["baseline_NO2"]
        
    def DetermineWeather(self):
        self.WeatherVars = list(self.monthly_weather_df[["Temperature","Rain","Windspeed","Winddirection"]].loc[self.monthly_weather_df["month"]== self.current_datetime.month].values[0])
        print("temperature: " , self.WeatherVars[0] , "rain: " , self.WeatherVars[1], " wind: ", self.WeatherVars[2], " wind direction: ", self.WeatherVars[3])
      
    def CalculateMonthlyWeightMatrix(self):
        self.weightsmatrix = CAD.returnCorrectWeightedMatrix(meteolog = False, matrixsize = 3, meteoparams = optimalparams["meteoparams"], meteovalues = self.WeatherVars)
        self.nr_repeats = CAD.provide_meteorepeats(optimalparams["repeatsparams"], self.WeatherVars[2])
      
    def PlotTrafficCount(self):
        self.TraffGrid.plot("count", antialiased=False, legend = True) 
        plt.title(f"Traffic of {nb_humans} assigned at {self.hour-1} to {self.hour} o'clock")
        plt.savefig(path_data + f'ModelRuns/{modelname}/{nb_humans}Agents/TrafficMaps/TrafficGrid_{randomID}_assign_A{nb_humans}_M{self.current_datetime.month}_D{self.current_datetime.day}_H{self.hour}_{modelname}.png')
        plt.close()
    
    def PlotObservedTraffic(self):
        self.TraffGrid.plot(self.TraffVcolumn, antialiased=False, legend = True) 
        plt.title(f"Traffic observed at {self.hour-1} to {self.hour} o'clock")
        plt.savefig(path_data + f'ModelRuns/{modelname}/{nb_humans}Agents/TrafficMaps/TrafficGrid_{randomID}_M{self.current_datetime.month}_D{self.current_datetime.day}_H{self.hour}_observed.png')
        plt.close()
        
    def TraffCountRegression(self, HourlyTraffic):
        predictors = ["count"]    #also have tried MaxSpeedLimit, but it takes up too much of the traffic coefficient
        datacells = pd.Series(self.onroadcells) & (self.TraffGrid["count"] > 0)
        reg = LinearRegression().fit(self.TraffGrid.loc[datacells, predictors], self.TraffGrid.loc[datacells,self.TraffVcolumn])
        TraffAssDat.write(f"hour {self.current_datetime} \n")
        TraffAssDat.write(f"hourly Traff tracks: {len(HourlyTraffic)} \n")
        TraffAssDat.write(f"Intercept: {reg.intercept_} \n") 
        TraffAssDat.write(pd.DataFrame(zip(predictors, reg.coef_)).to_string()) 
        self.R2 =  reg.score(self.TraffGrid.loc[self.onroadcells,predictors], self.TraffGrid.loc[self.onroadcells,self.TraffVcolumn])
        TraffAssDat.write(f"\nR2 {self.R2}\n\n")
        self.TraffGrid["TraffV"] = 0.0
        self.TraffGrid.loc[self.onroadcells,"TraffV"] = reg.predict(self.TraffGrid.loc[self.onroadcells,predictors])


    def TrafficRemainderCalc(self, HourlyTraffic):
        # Calculating Remainder
        self.TraffGrid["TraffV"] = 0.0
        self.TraffGrid.loc[self.onroadcells,"TraffV"] = (self.TraffGrid.loc[self.onroadcells, "count"]*  TraffVCoeff)
        TraffAssDat.write(f"hour {self.current_datetime} \n")
        TraffAssDat.write(f"hourly Traff tracks: {len(HourlyTraffic)} \n")
        self.R2, _ = pearsonr(self.TraffGrid.loc[self.onroadcells,"TraffV"],
                      self.TraffGrid.loc[self.onroadcells, self.TraffVcolumn])
        TraffAssDat.write(f"R2 {self.R2*self.R2}\n\n")
        AirPollGrid[f"TraffVrest{self.hour}_{self.current_datetime.day}"] =  0.0
        Remainders =  (self.TraffGrid.loc[self.onroadcells,self.TraffVcolumn])-(self.TraffGrid.loc[self.onroadcells,"TraffV"])
        AirPollGrid.loc[self.onroadcells, f"TraffVrest{self.hour}_{self.current_datetime.day}"] = list(Remainders)

    def TotalTraffCalc(self, HourlyTraffic):
        self.TraffGrid["TraffV"] = 0.0
        self.TraffGrid.loc[self.onroadcells,"TraffV"] = ((self.TraffGrid.loc[self.onroadcells, "count"]*  TraffVCoeff)  + (AirPollGrid.loc[self.onroadcells, f"TraffVrest{self.hour}"]))
        # self.TraffGrid.loc[self.TraffGrid["ON_ROAD"] == 1,"TraffV"] = (self.TraffGrid.loc[self.TraffGrid["ON_ROAD"] == 1, "count"]*  TraffVCoeff)
        self.TraffGrid.loc[self.TraffGrid["TraffV"] < 0,"TraffV"] = 0.0
        if TraffStage == "PredictionR2":
            TraffAssDat.write(f"hour {self.current_datetime} \n")
            TraffAssDat.write(f"hourly Traff tracks: {len(HourlyTraffic)} \n")
            self.R2, _ = pearsonr(self.TraffGrid.loc[self.onroadcells,"TraffV"], self.TraffGrid.loc[self.onroadcells, self.TraffVcolumn])
            TraffAssDat.write(f"R2 {self.R2*self.R2}\n\n")

    def PlotTraffPred(self):
        self.TraffGrid.plot("TraffV", antialiased=False, legend = True) 
        plt.title(f"Traffic predicted at {self.hour} o'clock")
        plt.savefig(path_data + f'ModelRuns/{modelname}/{nb_humans}Agents/TrafficMaps/TrafficGrid_pred_{randomID}_A{nb_humans}_M{self.current_datetime.month}_D{self.current_datetime.day}_H{self.hour}_{modelname}.png')
        plt.close()

    def TrafficAssignment(self):
        global streetLength
        if modelname == "NoEmissionZone2025":
          HourlyTraffic = pool.starmap(RetrieveNoEVRoutes, [(Human.thishourmode, Human.thishourtrack, Human.eletriccaraccess) for Human in self.Humans], chunksize = 500)
        else:
          HourlyTraffic = pool.starmap(RetrieveRoutes, [(Human.thishourmode, Human.thishourtrack) for Human in self.Humans], chunksize = 500)
        HourlyTraffic = list(it.chain.from_iterable(list(filter(lambda x: x is not None, HourlyTraffic))))
        HourlyTraffic = [track for track in HourlyTraffic if track.is_valid]
        # gpd.GeoDataFrame(data = {'count': [1]*len(self.HourlyTraffic), 'geometry':self.HourlyTraffic}, geometry="geometry", crs=crs).to_file(path_data + f'ModelRuns/{modelname}/{nb_humans}Agents/TrafficTracks/TrafficTracks_A{nb_humans}_H{self.hour-1}.shp')
        print("Nr of hourly traffic tracks: ", len(HourlyTraffic))
        if self.hour == 0:
          self.TraffVcolumn = f"TrV23_24"
        else:
          self.TraffVcolumn = f"TrV{self.hour-1}_{self.hour}"
        if len(HourlyTraffic) > 0: 
          if len(HourlyTraffic) > 15:
            counts = pool.starmap(TraffSpatialJoint, [(tracks, 0) for tracks in np.array_split(HourlyTraffic, n)], chunksize=1)
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
        
        if TraffStage == "Remainder":
          self.TrafficRemainderCalc(HourlyTraffic)
        
        print("Max Count", np.max(self.TraffGrid["count"]), "Mean Count", np.mean(self.TraffGrid["count"]), "Median Count", np.median(self.TraffGrid["count"]))
        
        if TraffStage in ["PredictionNoR2","PredictionR2"]:
          self.TotalTraffCalc(HourlyTraffic)     
          self.TraffGrid["TraffIntens"] = np.array(self.TraffGrid["TraffV"]) * streetLength
        else:
          self.TraffGrid["TraffV"] = self.TraffGrid['count']
          
        # self.PlotTraffPred()
        AirPollGrid[f"prTraff_{self.datesuffix}"] = self.TraffGrid["TraffV"]
        AirPollGrid[f"TrCount_{self.datesuffix}"] = self.TraffGrid["count"]
    
    def OnRoadEmission(self):
        self.TraffGrid["TraffNO2"] = (self.TraffGrid["TraffV"] * TraffVNO2Coeff) + (self.TraffGrid["TraffIntens"] * TraffIntensNO2Coeff)
    
    def OffRoadDispersion(self):
        global data_presets, param_presets, adjuster
        # assigning the trafficV values to the raster
        self.TraffGrid["NO2"] = CAD.compute_hourly_dispersion(**data_presets, weightmatrix = self.weightsmatrix,
                          adjuster = adjuster, TrafficNO2 = self.TraffGrid["TraffNO2"],  
                          nr_repeats = self.nr_repeats, **param_presets)
        AirPollGrid[f"prNO2_{self.datesuffix}"] = self.TraffGrid["NO2"]
    
    def PlotAirPoll(self):
        self.TraffGrid.plot("NO2", antialiased=False, legend = True)
        plt.title(f"NO2 Prediction: Month {self.current_datetime.month}, Hour {self.hour -1}")
        plt.savefig(path_data + f'ModelRuns/{modelname}/{nb_humans}Agents/NO2/NO2_{randomID}_A{nb_humans}_M{self.current_datetime.month}_D{self.current_datetime.day}_H{self.hour}_{modelname}.png')
        plt.close()
        time.sleep(1)
    
    def SaveAirPollTraffic(self):
        global AirPollGrid
        pd.DataFrame(AirPollGrid[["int_id"]+[col for col in AirPollGrid.columns if "prNO2" in col]]).to_csv(path_data+f"ModelRuns/{modelname}/{nb_humans}Agents/NO2/{randomID}/AirPollGrid_NO2_{randomID}_M{self.current_datetime.month}_D{self.current_datetime.day}_{modelname}_{randomID}.csv", index=False)
        pd.DataFrame(AirPollGrid[["int_id"]+[col for col in AirPollGrid.columns if "prTraff" in col] +  [col for col in AirPollGrid.columns if "TrCount" in col]]).to_csv(path_data+f"ModelRuns/{modelname}/{nb_humans}Agents/Traffic/{randomID}/AirPollGrid_Traff_{randomID}_M{self.current_datetime.month}_D{self.current_datetime.day}_{modelname}_{randomID}.csv", index=False)
        AirPollGrid = AirPollGrid.drop([col for col in AirPollGrid.columns if "prNO2" in col]+[col for col in AirPollGrid.columns if "prTraff" in col]+  [col for col in AirPollGrid.columns if "TrCount" in col], axis=1)


    
    def step(self):
        # manage time variables
        self.current_datetime += self.steps_minute
        if self.current_datetime.hour == 0 and self.current_datetime.day == 8: # completed a week, so switch month
            if self.current_datetime.month == 10:
                self.current_datetime = self.current_datetime.replace(day=1, month=self.current_datetime.month + 2)
            else:
              self.current_datetime = self.current_datetime.replace(day=1, month=self.current_datetime.month + 3)
        print(self.current_datetime)
        self.minute = self.current_datetime.minute
        if self.current_datetime.day == 1 and self.current_datetime.hour == 0 and self.current_datetime.minute == 0: # new month
            self.DetermineWeather() 
            self.CalculateMonthlyWeightMatrix()   
        if self.minute == 0:  # new hour
            if self.current_datetime.hour == 0:
              if self.current_datetime.day == 1:
                if self.current_datetime.month == 12:
                  self.datesuffix = f"M10_D7_H23"
                else:
                  self.datesuffix = f"M{self.current_datetime.month-3}_D7_H23"
              else:
                self.datesuffix = f"M{self.current_datetime.month}_D{self.current_datetime.day-1}_H23"
            else:
              self.datesuffix = f"M{self.current_datetime.month}_D{self.current_datetime.day}_H{self.current_datetime.hour-1}"
            print(self.datesuffix)
            print("hourly executiontime Human Steps: ", self.hourlyext)
            self.hourlyext = 0
            # print("Current time: ", self.current_datetime)
            self.hour = self.current_datetime.hour
            st = time.time()
            if modelname != "NoEmissionZone2030":
              self.TrafficAssignment()
              print("Traffic Assignment time: ", time.time() - st, "Seconds")
              st = time.time()
              if TraffStage in ["PredictionNoR2", "PredictionR2"]:
                self.OnRoadEmission()
                self.OffRoadDispersion()
                print("Hybrid Dispersion Model: ", time.time() - st, "Seconds")
                # self.PlotAirPoll()
            if self.current_datetime.hour == 0: # new day
              self.weekday = self.current_datetime.weekday()
              if  modelname != "NoEmissionZone2030":
                if TraffStage in ["PredictionNoR2", "PredictionR2"]:
                   self.SaveAirPollTraffic()


        self.activitystep = int((self.hour * 6) + (self.minute / 10))

        st = time.time()        
        if self.minute == 0:
          ModalSplitH = pool.starmap(RetrieveModalSplitHour, [(Human, 0) for Human in np.array_split(self.Humans, n)], chunksize = 1)
          ModalSplitLog.write(f"{self.datesuffix}, {Counter(list(it.chain.from_iterable(filter(None, list(it.chain.from_iterable(ModalSplitH))))))}\n")
          if TraffStage in ["PredictionNoR2", "PredictionR2"]:
            Alltracks = pool.starmap(RetrieveAllTracksHour, [(Human, 0) for Human in np.array_split(self.Humans, n)], chunksize = 1)
            Alltracks = pd.DataFrame(list(filter(lambda x: len(x[1])>0, [item for sublist in Alltracks for item in sublist])), 
                        columns=['agent', 'geometry', 'mode', 'duration'])
            Alltracks["geometry"] = Alltracks["geometry"].apply(lambda x: "; ".join([str(el) for el in x]))
            Alltracks.to_csv(path_data + f'ModelRuns/{modelname}/{nb_humans}Agents/Tracks/{randomID}/AllTracks_{randomID}_A{nb_humans}_{self.datesuffix}_{modelname}.csv', 
                          index=False, quoting=csv.QUOTE_NONNUMERIC, float_format='%.15g')

            self.Humans = list(it.chain.from_iterable(pool.starmap(hourly_worker_process, [(agents, self.current_datetime, np.array(self.TraffGrid["NO2"]), self.WeatherVars)  for agents in np.array_split(self.Humans, n)], chunksize=1)))
            print("collecting and saving exposure")
            AgentExposure = pool.starmap(RetrieveExposure, [(Human, 0) for Human in np.array_split(self.Humans, n)], chunksize = 1)
            pd.DataFrame([item for items in AgentExposure for item in items], columns=['agent', 'NO2', 'NO2wFilter', 'MET', 'indoortime']).to_csv(path_data + f'ModelRuns/{modelname}/{nb_humans}Agents/AgentExposure/{randomID}/AgentExposure_{randomID}_A{nb_humans}_{self.datesuffix}_{modelname}.csv', index=False)
          else:
            self.Humans = list(it.chain.from_iterable(pool.starmap(worker_process, [(Humans, self.current_datetime, self.WeatherVars)  for Humans in np.array_split(self.Humans, n)], chunksize=1)))
        else:
          self.Humans = list(it.chain.from_iterable(pool.starmap(worker_process, [(Humans, self.current_datetime, self.WeatherVars)  for Humans in np.array_split(self.Humans, n)], chunksize=1)))            
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
    n = os.cpu_count() -4
    print("Nr of assigned processes", n)
    
    
    # Number of Humans
    nb_humans = 43500     #87000 = 10%, 43500 = 5%, 21750 = 2.5%, 8700 = 1%

    # New Population sample or already existing one
    newpop = False
    subsetnr = 1
    
    # Length of the simulation run
    NrHours = 24
    NrDays = 7
    NrMonths = 4
    
    # Starting Date and Time
    starting_date = datetime(2019, 1, 1, 0, 0, 0)
    
    # Type of scenario
    modelname = "StatusQuo" 
    # modelname = "PrkPriceInterv"
    # modelname = "15mCity"
    # modelname = "15mCityWithDestination"
    # modelname = "NoEmissionZone2025"
    # modelname = "NoEmissionZone2030"
    
    # cellsize of the Airpollution and Traffic grid
    cellsize = 50    # 50m x 50m
    
    # Profiling code or not
    profile = False
    
    # Stage of the Traffic Model
    TraffStage = "PredictionR2" # "Remainder" or "Regression" or "PredictionNoR2" or "PredictionR2" 
    
    
    # Traffic Model
    if nb_humans == 21750:
      TraffVCoeff =  6.8583637     # 43500 = 3.7927303	21750 =  6.8583637	8700 = 7.214888208
    elif nb_humans == 43500:
      TraffVCoeff =  3.7927303      # 43500 =3.7927303	21750 =  6.8583637	8700 = 7.214888208
    
    TraffVNO2Coeff = 0.02845   # Traffic Volume NO2 coefficient for 50m cellsize
    TraffIntensNO2Coeff = 0.0001072 # Traffic Intensity NO2 coefficient for 50m cellsize

    randomID = random.randint(0, 1000000)
    print(modelname)
 
    
    #############################################################################################################
    
    # Read Main Data
    path_data = "D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/"
    
        
    if not os.path.exists(path_data+"ModelRuns/"+modelname):
      # Create the directory
      os.mkdir(path_data+"ModelRuns/"+modelname)
      if not os.path.exists(path_data+"ModelRuns/"+modelname+"/" + str(nb_humans) + "Agents"):
          os.mkdir(path_data+"ModelRuns/"+modelname+"/" + str(nb_humans)+ "Agents")
          os.mkdir(path_data+"ModelRuns/"+modelname+"/" + str(nb_humans)+ "Agents"+"/AgentExposure")
          os.mkdir(path_data+"ModelRuns/"+modelname+"/" + str(nb_humans)+ "Agents"+"/NO2")
          os.mkdir(path_data+"ModelRuns/"+modelname+"/" + str(nb_humans)+ "Agents"+"/Traffic")
          os.mkdir(path_data+"ModelRuns/"+modelname+"/" + str(nb_humans)+ "Agents"+"/ModalSplit")
          os.mkdir(path_data+"ModelRuns/"+modelname+"/" + str(nb_humans)+ "Agents"+"/Tracks")
          print("Directory " + path_data+"ModelRuns/"+modelname+"/" + str(nb_humans) + "Agents"" created successfully.")
    else:
      print("Directory " +path_data+"ModelRuns/"+ modelname + " already exists.")
      if not os.path.exists(path_data+"ModelRuns/"+modelname+"/" + str(nb_humans)+ "Agents"):
          os.mkdir(path_data+"ModelRuns/"+modelname+"/" + str(nb_humans)+ "Agents")
          os.mkdir(path_data+"ModelRuns/"+modelname+"/" + str(nb_humans)+ "Agents"+"/AgentExposure")
          os.mkdir(path_data+"ModelRuns/"+modelname+"/" + str(nb_humans)+ "Agents"+"/NO2")
          os.mkdir(path_data+"ModelRuns/"+modelname+"/" + str(nb_humans)+ "Agents"+"/Traffic")
          os.mkdir(path_data+"ModelRuns/"+modelname+"/" + str(nb_humans)+ "Agents"+"/ModalSplit")
          os.mkdir(path_data+"ModelRuns/"+modelname+"/" + str(nb_humans)+ "Agents"+"/Tracks")
          print("But directory " + path_data+"ModelRuns/"+modelname+"/"+str(nb_humans) + "Agents" " was created successfully.")
  
    os.mkdir(path_data+"ModelRuns/"+modelname+"/" + str(nb_humans)+ "Agents"+"/AgentExposure/" + str(randomID))
    os.mkdir(path_data+"ModelRuns/"+modelname+"/" + str(nb_humans)+ "Agents"+"/Tracks/" + str(randomID))
    os.mkdir(path_data+"ModelRuns/"+modelname+"/" + str(nb_humans)+ "Agents"+"/NO2/" + str(randomID))
    os.mkdir(path_data+"ModelRuns/"+modelname+"/" + str(nb_humans)+ "Agents"+"/Traffic/" + str(randomID))
    
    # Synthetic Population
    print("Reading Population Data")
    if modelname in ["NoEmissionZone2025", "NoEmissionZone2030"]:
      popsuffix = "ElectricCarOwnership"
    else:
      popsuffix = ""
    if newpop:
      pop_df = pd.read_csv(path_data+f"Population/Agent_pop_clean{popsuffix}.csv")
      random_subset = pd.DataFrame(pop_df.sample(n=nb_humans))
      random_subset.to_csv(path_data+f"Population/Amsterdam_population_subset{nb_humans}{popsuffix}.csv", index=False)
    else:
      random_subset = pd.read_csv(path_data+f"Population/Amsterdam_population_subset{nb_humans}_{subsetnr}{popsuffix}.csv")

    random_subset["student"] = 0
    random_subset.loc[random_subset["current_education"] == "high", "student"] = 1
    random_subset.to_csv(path_data+"ModelRuns/"+modelname+"/" + str(nb_humans)+ f"Agents/Amsterdam_population_subset{nb_humans}_{randomID}_{subsetnr}{popsuffix}.csv", index=False)
    
    # Activity Schedules
    print("Reading Activity Schedules")
    scheduledf_monday = pd.read_csv(path_data+"ActivitySchedules/HETUS2010_Synthpop_schedulesclean_Monday.csv")
    scheduledf_tuesday = pd.read_csv(path_data+"ActivitySchedules/HETUS2010_Synthpop_schedulesclean_Tuesday.csv")
    scheduledf_wednesday = pd.read_csv(path_data+"ActivitySchedules/HETUS2010_Synthpop_schedulesclean_Wednesday.csv")
    scheduledf_thursday = pd.read_csv(path_data+"ActivitySchedules/HETUS2010_Synthpop_schedulesclean_Thursday.csv")
    scheduledf_friday = pd.read_csv(path_data+"ActivitySchedules/HETUS2010_Synthpop_schedulesclean_Friday.csv")
    scheduledf_saturday = pd.read_csv(path_data+"ActivitySchedules/HETUS2010_Synthpop_schedulesclean_Saturday.csv")
    scheduledf_sunday = pd.read_csv(path_data+"ActivitySchedules/HETUS2010_Synthpop_schedulesclean_Sunday.csv")
    schedulelist = [scheduledf_monday, scheduledf_tuesday, scheduledf_wednesday, scheduledf_thursday, scheduledf_friday, scheduledf_saturday, scheduledf_sunday]
    del scheduledf_monday, scheduledf_tuesday, scheduledf_wednesday, scheduledf_thursday, scheduledf_friday, scheduledf_saturday, scheduledf_sunday


    # Coordinate Reference System and CRS transformers
    crs = "epsg:28992"
    project_to_WSG84 = Transformer.from_crs(crs, "epsg:4326", always_xy=True).transform
    projecy_to_crs = Transformer.from_crs("epsg:4326", crs, always_xy=True).transform

    # Load the spatial built environment
    spatial_extent = gpd.read_feather(path_data+"SpatialData/SpatialExtent.feather")
    buildings = gpd.read_feather(path_data+"SpatialData/Buildings.feather")
    streets = gpd.read_feather(path_data+"SpatialData/Streets.feather")
    Residences = gpd.read_feather(path_data+"SpatialData/Residences.feather")
    carroads = gpd.read_feather(path_data+"SpatialData/carroads.feather")
    Universities = gpd.read_feather(path_data+"SpatialData/Universities.feather")
    
    if modelname in ["15mCity", "15mCityWithDestination"]:
      greenspace = gpd.read_feather(path_data+f"SpatialData/GreenspaceCentroids15mCity.feather")
      Schools = gpd.read_feather(path_data+f"SpatialData/Schools15mCity.feather")
      Supermarkets = gpd.read_feather(path_data+f"SpatialData/Supermarkets15mCity.feather")
      Kindergardens = gpd.read_feather(path_data+f"SpatialData/Kindergardens15mCity.feather")
      Restaurants = gpd.read_feather(path_data+f"SpatialData/Restaurants15mCity.feather")
      Entertainment = gpd.read_feather(path_data+f"SpatialData/Entertainment15mCity.feather")
      ShopsnServ = gpd.read_feather(path_data+f"SpatialData/ShopsnServ15mCity.feather")
      Nightlife = gpd.read_feather(path_data+f"SpatialData/Nightlife15mCity.feather")
      Profess = gpd.read_feather(path_data+f"SpatialData/Profess15mCity.feather")
    else:
      greenspace = gpd.read_feather(path_data+"SpatialData/GreenspaceCentroids.feather")
      Schools = gpd.read_feather(path_data+"SpatialData/Schools.feather")
      Supermarkets = gpd.read_feather(path_data+"SpatialData/Supermarkets.feather")
      Kindergardens = gpd.read_feather(path_data+"SpatialData/Kindergardens.feather")
      Restaurants = gpd.read_feather(path_data+"SpatialData/Restaurants.feather")
      Entertainment = gpd.read_feather(path_data+"SpatialData/Entertainment.feather")
      ShopsnServ = gpd.read_feather(path_data+"SpatialData/ShopsnServ.feather")
      Nightlife = gpd.read_feather(path_data+"SpatialData/Nightlife.feather")
      Profess = gpd.read_feather(path_data+"SpatialData/Profess.feather")
    

    # if modelname in ["NoEmissionZone2025", "NoEmissionZone2030"]:
    #   NoEmissionZone = gpd.read_feather(path_data+f"SpatialData/{modelname}.feather")

    # Load Intervention Environment
    # Status Quo
    if modelname in ["StatusQuo","PrkPriceInterv", "NoEmissionZone2025", "NoEmissionZone2030"]:
      EnvBehavDeterms = gpd.read_feather(path_data+"SpatialData/EnvBehavDeterminants.feather")
      if modelname == "PrkPriceInterv":
        EnvBehavDeterms["PrkPricPre"] = EnvBehavDeterms["PrkPricPos"]
    elif modelname in ["15mCity", "15mCityWithDestination"]:
      EnvBehavDeterms = gpd.read_feather(path_data+f"SpatialData/EnvBehavDeterminants15mCity.feather")
      EnvBehavDeterms['retaiDns'] = EnvBehavDeterms['retaiDns15']
      # EnvBehavDeterms['greenCovr'] = EnvBehavDeterms['grenCovr15']
      EnvBehavDeterms['retailDiv'] = EnvBehavDeterms['retDiv15']
    # other Interventions
    else:
      EnvBehavDeterms = gpd.read_feather(path_data+f"SpatialData/EnvBehavDeterminants{modelname}.feather")

 
    # Read the Environmental Stressor Data and Model
    cellsize = "50m"
    suffix = "TrV_TrI_noTrA"
    iter, meteolog = False, False
    matrixsize = 3
    with open(f"{path_data}AirPollutionModelData/optimalparams_{cellsize}_scalingMS{matrixsize}iter{iter}MeteoLog{meteolog}.json", "r") as read_file:
            optimalparams = json.load(read_file)
    del optimalparams["nr_repeats"]
    AirPollGrid = gpd.read_feather(path_data+f"SpatialData/AirPollgrid{cellsize}.feather")
    AirPollPred = pd.read_csv(path_data+f"AirPollutionModelData/Pred_{cellsize}{suffix}.csv")
    AirPollPred.fillna(0, inplace=True)
    AirPollGrid[["baseline_NO2", "ON_ROAD"]] = AirPollPred[["baseline_NO2", "ON_ROAD"]]
    airpoll_grid_raster = xr.open_dataarray(path_data+ f"AirPollutionModelData/AirPollDeterm_grid_{cellsize}.tif", engine="rasterio")[0] # Read raster data using rasterio
    moderator_df = pd.read_csv(path_data+ f"AirPollutionModelData/moderator_{cellsize}.csv")     # Read moderator DataFrame
    streetLength = pd.read_csv(path_data+ f"AirPollutionModelData/StreetLength_{cellsize}.csv")
    streetLength =  np.array(streetLength["StreetLength"])
    
    data_presets = {
        "raster": airpoll_grid_raster,
        "baselineNO2": AirPollPred["baseline_NO2"],
        "onroadindices": AirPollPred.loc[AirPollPred["ON_ROAD"] == 1].index.to_list()
    }
    param_presets = {
        "iter": iter, 
        "baseline": True,
        "baseline_coeff": optimalparams["scalingparams"][0], 
        "traffemissioncoeff_onroad": optimalparams["scalingparams"][1],
        "traffemissioncoeff_offroad": optimalparams["scalingparams"][2]
    }
    adjuster = CAD.provide_adjuster( morphparams = optimalparams["morphparams"], GreenCover = moderator_df["GreenCover"], 
                                    openspace_fraction = moderator_df["openspace_fraction"], 
                                    NrTrees =  moderator_df["NrTrees"], building_height = moderator_df["building_height"], 
                                    neigh_height_diff = moderator_df["neigh_height_diff"])

    # Preparing Data    
    # TraffDat = pd.read_csv(path_data+ "Air Pollution Determinants//CellAutDisp_Data/AirPollRaster50m_TraffVdata.csv")
    # TraffIntDat = pd.read_csv(path_data+ "Air Pollution Determinants//CellAutDisp_Data/AirPollRaster50m_TraffIntensdata.csv")
    # AirPollGrid = AirPollGrid.merge(TraffDat[['int_id','StreetIntersectDensity', 'MaxSpeedLimit', 'MinSpeedLimit', 'MeanSpeedLimit']], how = "left", on = "int_id")

    if TraffStage in ["PredictionNoR2", "PredictionR2"]:
      if modelname == "NoEmissionZone2025":
        TraffVrest = pd.read_csv(path_data+f"TrafficRemainder/AirPollGrid_HourlyTraffRemainder_{nb_humans}_{modelname}.csv")
      else:
        TraffVrest = pd.read_csv(path_data+f"TrafficRemainder/AirPollGrid_HourlyTraffRemainder_{nb_humans}.csv")
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
    routevariables = ["RdIntrsDns", "retaiDns","greenCovr", "popDns", "TrafAccid", "NrTrees", "MeanTraffV", "HighwLen", "AccidPedes",
                        "PedStrWidt", "PedStrLen", "LenBikRout", "DistCBD", "retailDiv", "MeanSpeed", "MaxSpeed", "NrStrLight", "CrimeIncid",
                        "MaxNoisDay", "OpenSpace", "PNonWester", "PWelfarDep", "SumTraffVo", "pubTraDns", "MxNoisNigh", "MinSpeed", "PrkPricPre" ]
    personalvariables = ["sex_male", "age", "car_access", "Western", "Non_Western", "Dutch", 'income','employed',
                                'edu_3_levels','HH_size', 'Nrchildren', 'student', 'driving_habit','biking_habit','transit_habit']
    tripvariables = ["trip_distance", "purpose_commute", 'purpose_leisure','purpose_groceries_shopping',
                                'purpose_education', 'purpose_bring_person']
    weathervariables = ['Temperature', 'Rain', 'Windspeed','Winddirection' ]
    originvariables = ["pubTraDns", "DistCBD"]
    destinvariables = ["pubTraDns", "DistCBD", "NrParkSpac", "PrkPricPre"]
        
    routevariables_suff = Math_utils.add_suffix(routevariables, ".route")
    originvariables_suff = Math_utils.add_suffix(originvariables, ".orig")
    destinvariables_suff = Math_utils.add_suffix(destinvariables, ".dest")

    colvars = routevariables_suff + originvariables_suff + destinvariables_suff + personalvariables + tripvariables + weathervariables
  
    ModalChoiceModel = PMMLForestClassifier(pmml=path_data+f"ModalChoiceModel/RandomForest.pmml")
    ModalChoiceModel.splitter = "random"
    OrderPredVars = []
    with open(path_data+f"ModalChoiceModel/RFfeatures.txt", 'r') as file:
      for line in file.readlines():
          OrderPredVars.append(line.strip())
    print(OrderPredVars)

    # Preparing Log Documents
    print("Preparing Log Documents")
    if TraffStage != "PredictionNoR2":
      TraffAssDat = open(f'{path_data}ModelRuns/{modelname}/{nb_humans}Agents/Traffic/TraffAssignModelPerf{nb_humans}_{modelname}_pop{subsetnr}_{randomID}.txt', 'a',buffering=1)
      TraffAssDat.write(f"Number of Agents: {nb_humans} \n")

    ModalSplitLog = open(f'{path_data}ModelRuns/{modelname}/{nb_humans}Agents/ModalSplit/ModalSplitLog{nb_humans}_{modelname}_{randomID}.txt', 'a',buffering=1)
    ModalSplitLog.write(f"Number of Agents: {nb_humans} \n")


    # Initializing Simulation
    m = TransportAirPollutionExposureModel(nb_humans=nb_humans, path_data=path_data, starting_date=starting_date)
   
    print("Starting Multiprocessing Pool")
    pool =  Pool(processes=n, initializer= init_worker_simul, initargs=(Residences, Entertainment, Restaurants,  ShopsnServ, EnvBehavDeterms, 
                                                          ModalChoiceModel, OrderPredVars, colvars, project_to_WSG84, 
                                                          projecy_to_crs, crs, routevariables, originvariables, 
                                                          destinvariables, airpoll_grid_raster, AirPollGrid[["int_id", "ON_ROAD", "geometry"]]))

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
      for month in range(NrMonths):
        for day in range(NrDays):
          for hour in range(NrHours):
            for t in range(6):
                m.step()


    pool.terminate()         
            
    if TraffStage == "Remainder":
      traffrestcols = [ col for col in AirPollGrid.columns if "TraffVrest" in col]
      pd.DataFrame(AirPollGrid[["int_id"]+ traffrestcols]).to_csv(path_data+"ModelRuns/"+modelname+"/" + str(nb_humans)+ f"Agents/Traffic/AirPollGrid_HourlyTraffRemainder_{nb_humans}_pop{subsetnr}_{randomID}.csv", index=False)
    
    if TraffStage != "PredictionNoR2":
      TraffAssDat.close()

    ModalSplitLog.close()
    print("Finished the script at", datetime.now())
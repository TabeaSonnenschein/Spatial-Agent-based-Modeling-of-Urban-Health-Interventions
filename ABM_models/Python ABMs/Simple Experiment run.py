import os
import csv
import math
import random
from datetime import datetime, timedelta
from mesa import Agent, Model
from mesa.space import MultiGrid
from mesa.time import SimultaneousActivation
from mesa.datacollection import DataCollector
import pandas as pd
import mesa_geo

class Humans(mesa.Agent): 
  """
  Humans: 
- have realistic attributes for the city
- have a daily activity schedule
- have mobility behavior
- have a home location
- have personal exposure
  """

  def __init__(self, vector):
    self.Agent_ID = vector[0]
    self.Neighborhood = vector[1]
    self.age = vector[2]					# integer age 0- 100
    self.sex = vector[3]  				    # female, male
    self.migrationbackground = vector[4]    # Dutch, Western, Non-Western
    self.hh_single = vector[5] 				# 1 = yes, 0 = no
    self.is_child = vector[6]				# 1 = yes, 0 = no
    self.has_child = vector[7]				# 1 = yes, 0 = no
    self.current_edu = vector[8]			# "high", "middle", "low", "no_current_edu"
    self.absolved_edu = vector[9]		    # "high", "middle", "low", 0
    self.BMI = vector[10] 				    #"underweight", "normal_weight", "moderate_overweight", "obese"
    self.employment_status = vector[11] 	#"has_personal_income", "no_personal_income"
    self.edu_int = vector[12] 	            # 1,2,3
    self.car_access = vector[13]            # 1 = yes, 0 = no
    self.biking_habit  = vector[14]         # 1 = yes, 0 = no
    self.driving_habit  = vector[15]        # 1 = yes, 0 = no
    self.transit_habit = vector[16]         # 1 = yes, 0 = no
    self.incomeclass  = vector[17]          # income deciles 1-10
 
		


class TransportAirPollutionExposureModel(mesa.Model):
    def __init__(self, nb_humans = 40000, path_data = "C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam", crs = "+init=EPSG:28992",
                 starting_date = datetime(2018, 1, 1, 6, 50, 0), step = timedelta(minutes=5), steps_minute = 5, modelrunname= "intervention_scenario"):
        # Insert the global definitions, variables, and actions here
        self.path_data = path_data
        self.starting_date = starting_date
        self.step = step
        self.steps_minute = steps_minute
        self.nb_humans = nb_humans
        self.modelrunname = modelrunname
        self.crs = crs
        self.schedule = SimultaneousActivation(self)
        self.grid = ContinuousSpace(width, height, torus=True)
        self.datacollector = DataCollector(model_reporters={}, agent_reporters={})


        # Load the spatial built environment
        self.shape_file_buildings = self.load_shape_file("Amsterdam/Built Environment/Buildings/Buildings_RDNew.shp")
        self.shape_file_buildings2 = self.load_shape_file("Amsterdam/Built Environment/Buildings/Diemen_Buildings.shp")
        self.shape_file_buildings3 = self.load_shape_file(
            "Amsterdam/Built Environment/Buildings/Oude Amstel_buildings.shp")
        self.shape_file_streets = self.load_shape_file(
            "Amsterdam/Built Environment/Transport Infrastructure/Amsterdam_roads_RDNew.shp")
        self.shape_file_greenspace = self.load_shape_file(
            "Amsterdam/Built Environment/Green Spaces/Green Spaces_RDNew_window.shp")
        self.shape_file_Residences = self.load_shape_file(
            "Amsterdam/Built Environment/Buildings/Residences_neighcode_RDNew.shp")
        self.shape_file_Schools = self.load_shape_file(
            "Amsterdam/Built Environment/Facilities/Amsterdam_schools_RDNew.shp")
        self.shape_file_Supermarkets = self.load_shape_file(
            "Amsterdam/Built Environment/Facilities/Amsterdam_supermarkets_RDNew.shp")
        self.shape_file_Universities = self.load_shape_file(
            "Amsterdam/Built Environment/Facilities/Amsterdam_universities_RDNew.shp")
        self.shape_file_Kindergardens = self.load_shape_file(
            "Amsterdam/Built Environment/Facilities/Amsterdam_kindergardens_RDNew.shp")
        self.shape_file_Restaurants = self.load_shape_file(
            "Amsterdam/Built Environment/Facilities/Amsterdam_Foursquarevenues_Food_RDNew.shp")
        self.shape_file_Entertainment = self.load_shape_file(
            "Amsterdam/Built Environment/Facilities/Amsterdam_Foursquarevenues_ArtsEntertainment_RDNew.shp")
        self.shape_file_ShopsnServ = self.load_shape_file(
            "Amsterdam/Built Environment/Facilities/Amsterdam_Foursquarevenues_ShopsServ_RDNew.shp")
        self.shape_file_Nightlife = self.load_shape_file(
            "Amsterdam/Built Environment/Facilities/Amsterdam_Foursquarevenues_Nightlife_RDNew.shp")
        self.shape_file_Profess = self.load_shape_file(
            "Amsterdam/Built Environment/Facilities/Amsterdam_Foursquarevenues_Profess_other_RDNew.shp")
        self.spatial_extent = self.load

		# Create the agents
        pop_df = pd.read_csv(path_data+"Population/Agent_pop.csv", sep = ";")
        random_subset = pop_df.sample(n = nb_humans)
        random_subset = random_subset.to_csv(path_data+"Amsterdam/ModelRuns/Amsterdam_population_subset.csv", sep = ";", index = False)
        random_subset = random_subset.reset_index()
        for i in range(self.nb_humans):
            agent = Humans(self, random_subset.iloc[i])
            self.schedule.add(agent)
			# Add the agent to a Home in their neighborhood
            #self.grid.place_agent(agent, Home)
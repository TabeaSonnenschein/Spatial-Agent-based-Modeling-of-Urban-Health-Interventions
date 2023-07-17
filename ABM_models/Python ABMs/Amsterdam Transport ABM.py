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


projectCRS = "RDNew"

class Humans(mesa.Agent): 
  """
  Humans: 
  - has a metabolism of sugar and spice
  - harvest and trade sugar and spice to survive
  """

  def __init__(self, vector):
    super().__init__(unique_id, model)
    self.pos = pos
    self.moore = moore
    self.sugar = sugar
    self.spice = spice
    self.metabolism_sugar = metabolism_sugar
    self.metabolism_spice = metabolism_spice
    self.vision = vision

    self.Agent_ID = vector[0]
	self.Agent_index = vector[1]
	self.Neighborhood = vector[2]
	self.age = vector[3]					# integer age 0- 100
	self.sex = vector[4]  				# female, male
	self.migrationbackground = vector[5] # Dutch, Western, Non-Western
	self.hh_single = vector[6] 				# 1 = yes, 0 = no
	self.is_child = vector[7]				# 1 = yes, 0 = no
	self.has_child = vector[8]				# 1 = yes, 0 = no
	self.current_edu = vector[9]			# "high", "middle", "low", "no_current_edu"
	self.absolved_edu = vector[10]		# "high", "middle", "low", 0
	self.edu_int = vector[11]
	self.BMI = vector[12] 				#"underweight", "normal_weight", "moderate_overweight", "obese"
	self.scheduletype = vector[13]
	self.agesexgroup = vector[14]    # 
	self.incomegroup = vector[15] # "low", "middle", "high"			
	self.student = vector[16]		
	self.incomeclass  = vector[17]
	self.commute = 0
	self.groceries = 0
	self.leisure = 0
	self.edu_trip = 0
	self.driving_habit  = vector[18]
	self.biking_habit  = vector[19]
	self.transit_habit = vector[20]
	self.employment_status = vector[21]
	self.car_access = vector[22]
	
	self.modal_propensities = [0.00, 0.00, 0.00,0.00]
	self.randomnumber
	
	#/ destination locations
	self.residence
	self.workplace
	self.school
	self.university
	self.kindergarden
	self.supermarket
			
	#/ activity variables
	self.activity
	self.schedule
	#/ weekday and weekend schedule
	self.current_activity
	self.former_activity
	self.destination_activity
	self.traveldecision
	self.perception2 =0
	self.perception3=0
	
	#/ travel variables
	self.track_duration
	self.track_path
	self.track_geometry
	self.modalchoice
	self.path_memory
	self.new_route
	self.make_modalchoice
	self.route_eucl_line
	self.trip_distance 

	#/ saved routes (for efficiency)
	self.homeTOwork
	self.homeTOwork_mode
	self.homeTOwork_geometry
	self.homeTOwork_duration
	self.workTOhome
	self.workTOhome_geometry
	self.homeTOuni
	self.homeTOuni_mode
	self.homeTOuni_geometry
	self.homeTOuni_duration
	self.uniTOhome
	self.uniTOhome_geometry
	self.homeTOschool
	self.homeTOschool_mode
	self.homeTOschool_geometry
	self.homeTOschool_duration	
	self.schoolTOhome
	self.schoolTOhome_geometry
	self.homeTOsuperm
	self.homeTOsuperm_mode
	self.homeTOsuperm_geometry
	self.homeTOsuperm_duration	
	self.supermTOhome
	self.supermTOhome_geometry
	self.homeTOkinderga
	self.homeTOkinderga_mode
	self.homeTOkinderga_geometry
	self.homeTOkinderga_duration	
	self.kindergaTOhome
	self.kindergaTOhome_geometry
	
	#/ exposure variables
	self.bike_exposure
	self.walk_exposure
	self.activity_NO2
	self.hourly_NO2
	self.hourly_mean_NO2	
	self.daily_NO2
	self.yearly_NO2
#	self.hourly_PM2_5
#	self.daily_PM2_5
#	self.yearly_PM2_5
	self.activity_Noise
	self.hourly_Noise
	self.daily_Noise
	self.yearly_Noise
	

	
	#/ Transport Behaviour: Behavioural Factors#/
	# there are also convenience and affordability, but they are defined inside the model
	self.assumed_quality_infrastructure_route = create_map(["popDns", "retaiDns", "greenCovr",  "RdIntrsDns", 
																			"TrafAccid", "AccidPedes", "NrTrees", "MeanTraffV",
										                                    "SumTraffVo", "HighwLen", "PedStrWidt", "PedStrLen", "LenBikRout",
										                                    "DistCBD", "retailDiv", "MaxSpeed", "NrStrLight",
										                                    "CrimeIncid", "MaxNoisDay", "MxNoisNigh", "OpenSpace", 
										                                    "PNonWester", "PWelfarDep"], 
										                                    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,0.0, 0.0, 0.0, 0.0, 0.0,0.0, 0.0, 0.0, 0.0, 0.0,0.0, 0.0, 0.0, 0.0, 0.0,0.0, 0.0, 0.0, 0.0])	
	self.assumed_quality_infrastructure_orig = create_map(["pubTraDns", "DistCBD"],[0.0, 0.0])
	self.assumed_quality_infrastructure_dest = create_map(["pubTraDns", "NrParkSpac","PrkPricPre", "PrkPricPos"],[0.0,0.0,0.0,0.0])
	
	

	
# function that activates every 10 minutes in terms of simulation time
# it checks the current activity and the former activity and decides whether the agent has to travel or not
# if the agent has to travel, it checks the destination activity and the current location and decides which mode to use 	
def schedule_manager when: (((current_date.minute mod 10) == 0) or (current_date.minute == 0)){
		 current_activity = schedule[(int((current_date.minute/10) + (current_date.hour * 6)))]
		 if((int(current_date.minute) != 0) or (int(current_date.hour) != 0)){
		 	former_activity = schedule[int(((current_date.minute/10) + (current_date.hour * 6))-1)]
		 }
		 else{
		 	former_activity = last(schedule) 
		 }
		 if(current_activity != former_activity){
		 	if(current_activity == "work"){
		 		commute = 1
				destination_activity = workplace
				if(homeTOwork != nil and (former_activity == "at_Home" or former_activity == "sleeping")){
					track_path = homeTOwork
					track_geometry = homeTOwork_geometry
					modalchoice = homeTOwork_mode
					track_duration = homeTOwork_duration
					path_memory = 1
					write "saved pathway"
				}		 		
		 	}
		 	else if(current_activity == "school"){
		 		edu_trip = 1
		 		destination_activity = school
		 		if(homeTOschool != nil and (former_activity == "at_Home" or former_activity == "sleeping")){
					track_path = homeTOschool
					track_geometry = homeTOschool_geometry
					modalchoice = homeTOschool_mode
					track_duration = homeTOschool_duration
					path_memory = 1
					write "saved pathway"
				}		
		 	}
		 	else if(current_activity == "university"){
		 		edu_trip = 1
		 		destination_activity = university
		 		if(homeTOuni != nil and (former_activity == "at_Home" or former_activity == "sleeping")){
					track_path = homeTOuni
					track_geometry = homeTOuni_geometry
					track_duration = homeTOuni_duration
					modalchoice = homeTOuni_mode
					path_memory = 1
					write "saved pathway"
				}		
		 	}
		 	else if(current_activity == "groceries_shopping"){
		 		destination_activity = supermarket
		 		groceries = 1
		 		if(homeTOsuperm != nil and (former_activity == "at_Home" or former_activity == "sleeping")){
					track_path = homeTOsuperm
					track_geometry = homeTOsuperm_geometry
					track_duration = homeTOsuperm_duration
					modalchoice = homeTOsuperm_mode
					path_memory = 1
					write "saved pathway"
				}		
		 	}
		 	else if(current_activity == "kindergarden"){
		 		destination_activity = kindergarden
		 		if(homeTOkinderga != nil and (former_activity == "at_Home" or former_activity == "sleeping")){
					track_path = homeTOkinderga
					track_geometry = homeTOkinderga_geometry
					track_duration = homeTOkinderga_duration
					modalchoice = homeTOkinderga_mode
					path_memory = 1
					write "saved pathway"
				}		
		 	}
		 	else if(current_activity == "sleeping" or current_activity == "at_Home"){
		 		destination_activity = self.residence.location
		 		if(workTOhome != nil and former_activity == "work"){
					track_path = workTOhome
					track_geometry = workTOhome_geometry
					modalchoice = homeTOwork_mode
					track_duration = homeTOwork_duration
					path_memory = 1
					write "saved pathway_ return"
		 		}
		 		else if(schoolTOhome != nil and former_activity == "school"){
					track_path = schoolTOhome
					track_geometry = schoolTOhome_geometry
					modalchoice = homeTOschool_mode
					track_duration = homeTOschool_duration
					path_memory = 1
					write "saved pathway_ return"
		 		}
		 		else if(uniTOhome != nil and self.location == university.location){
					track_path = uniTOhome
					track_geometry = uniTOhome_geometry
					modalchoice = homeTOuni_mode
					track_duration = homeTOuni_duration
					path_memory = 1
					write "saved pathway_ return"
		 		}
		 		else if(supermTOhome != nil and self.location == supermarket.location){
					track_path = supermTOhome
					track_geometry = supermTOhome_geometry
					modalchoice = homeTOsuperm_mode
					track_duration = homeTOsuperm_duration
					path_memory = 1
					write "saved pathway_ return"
		 		}
		 		else if(kindergaTOhome != nil and self.location == supermarket.location){
					track_path = kindergaTOhome
					track_geometry = kindergaTOhome_geometry
					modalchoice = homeTOkinderga_mode
					track_duration = homeTOkinderga_duration
					path_memory = 1
					write "saved pathway_ return"
		 		}
		 	}
		 	else if(current_activity == "entertainment" ){
		 		leisure = 1
		 		destination_activity = one_of(Entertainment)
		 		loop while: destination_activity == nil {
		 			destination_activity = one_of(Entertainment)
		 		}
		 	}
		 	else if(current_activity == "eat" ){
		 		if (one_of(Restaurants inside circle(500, self.location)) != nil){
		 			destination_activity = one_of(Restaurants inside circle(500, self.location))
		 		}
		 		else{
		 			destination_activity = closest_to(Restaurants, self.location)
		 		}
		 		loop while: destination_activity == nil {
		 			destination_activity = one_of(Restaurants)
		 		}
		 	}
		 	else if(current_activity == "social_life" ){
		 		destination_activity = one_of(shape_file_Residences)
		 	}
		 	write "Current Activity: " + current_activity + " Former Activity: " + former_activity
		 	if(point(destination_activity.location) != point(self.location)){
		 		route_eucl_line = line(container(point(self.location), point(destination_activity.location)))
		 		trip_distance = (self.location distance_to destination_activity)
		 		if(path_memory != 1){
		 			traveldecision = 1
		 		}
		 		else if(path_memory == 1){
		 			 activity = "traveling"
		 			 track_path =  path((track_geometry add_point(point(destination_activity))))  
		 		}
		 		path_memory = 0
		 	}		 
		 	else{
		 		activity ="perform_activity"
		 		traveldecision = 0
		 	}
		 }
	}
	def Env_Activity_Affordance_Travel_route target:(Perceivable_Environment where (each intersects route_eucl_line))  when: traveldecision == 1 {
    	myself.traveldecision = 0	
    	myself.perception2 = 1
    	write "perceiving route variables"
    	ask myself{
	   		assumed_quality_infrastructure_route = (["popDns"::mean(myself.popDns), "retaiDns"::mean(myself.retaiDns), 
	   			"greenCovr"::mean(myself.greenCovr), "RdIntrsDns"::mean(myself.RdIntrsDns), 
	   			"TrafAccid"::mean(myself.TrafAccid), "NrTrees"::mean(myself.NrTrees), 
	   			"MeanTraffV"::mean(myself.MeanTraffV), "HighwLen"::mean(myself.HighwLen), "AccidPedes"::mean(myself.AccidPedes),
	   			"PedStrWidt"::mean(myself.PedStrWidt),"PedStrLen"::mean(myself.PedStrLen), 
	   			"LenBikRout"::mean(myself.LenBikRout), "DistCBD"::mean(myself.DistCBD), 
	   			"retailDiv"::mean(myself.retailDiv), "MeanSpeed"::mean(myself.MeanSpeed), "MaxSpeed"::mean(myself.MaxSpeed), 
	   			"NrStrLight"::mean(myself.NrStrLight), "CrimeIncid"::mean(myself.CrimeIncid), 
	   			"MaxNoisDay"::mean(myself.MaxNoisDay),"OpenSpace"::mean(myself.OpenSpace), 
	   			"PNonWester"::mean(myself.PNonWester), "PWelfarDep"::mean(myself.PWelfarDep)])
	   	}    	
    }
#    def Env_Activity_Affordance_Travel_orig_dest when: perception2 == 1 {
#    	 perception2 = 0	
#    	 make_modalchoice = 1
#    	
#    }
#    sum((AirPollution overlapping self) collect each.NO2)
    def Env_Activity_Affordance_Travel_orig target:(Perceivable_Environment overlapping self.location) when: perception2 == 1 {
    	myself.perception2 = 0	
    	myself.perception3 = 1
    	write "perceiving orig variables"
    	ask myself{
	   		assumed_quality_infrastructure_orig = (["pubTraDns"::myself.pubTraDns, "DistCBD"::myself.DistCBD])
	   	}    	
    }
    def Env_Activity_Affordance_Travel_dest target:(Perceivable_Environment overlapping self.destination.location)  when: perception3 == 1 {
    	myself.perception3 = 0	
    	myself.make_modalchoice = 1
    	write "perceiving dest variables"
    	
    	ask myself{
	   		assumed_quality_infrastructure_dest = (["pubTraDns"::myself.pubTraDns, 
	   			"NrParkSpac"::myself.NrParkSpac, "PrkPricPre"::myself.PrkPricPre, 
	   			"PrkPricPos"::myself.PrkPricPos])
	   	}    	
    }
    def modalchoice when: make_modalchoice == 1 {
   	write "make modalchoice"
   	new_route = 1
   	make_modalchoice = 0
	if((trip_distance/1000) <= 0.60708){
		if (biking_habit == 0){
			if(driving_habit == 0){
				modal_propensities = [0.026315789, 0.06842105263, 0.1486068, 0.83684210]
			}
			else{
				if(assumed_quality_infrastructure_orig["pubTraDns"] <= 0){
					modal_propensities = [0, 0.277310924, 0.00840336, 0.714285714]
				}
				else{
					modal_propensities = [0.14285714, 0.14285714, 0, 0.714285714]
				}		
			}
		}
		else{
			if(trip_distance/1000 <= 0.3457){
				if(assumed_quality_infrastructure_route["greenCovr"] <= 0.402){
					if(assumed_quality_infrastructure_route["MeanSpeed"] <= 25){
						modal_propensities = [0.2, 0.2, 0, 0.6]
					}
					else{
						modal_propensities = [0.2065727, 0.01408, 0.01563, 0.768779]
					}		
				}
				else{
					modal_propensities = [0.19047, 0, 0.19047, 0.619047]
				}		
			}
			else{
				if(assumed_quality_infrastructure_route["SumTraffVo"] <= 471641.5){
					if(driving_habit == 0){
						if(transit_habit == 0){
							if(assumed_quality_infrastructure_route["AccidPedes"] <= 3.3333){
								modal_propensities = [0.7727272727272, 0, 0, 0.227272727272]
							}
							else{
								modal_propensities = [0.348484848, 0.045454545, 0, 0.60606060606]
							}
						}
						else{
							modal_propensities = [0.3727272, 0.02727272727272, 0, 0.6]
						}
					}
					else{
						if(incomeclass <= 9){
							modal_propensities = [0.468468, 0.054054, 0, 0.606060]
						}
						else{
							modal_propensities = [0.28125, 0.375, 0, 0.34375]
						}
					}		
				}
				else{
					modal_propensities = [0.142857, 0, 0.142857, 0.7142]
				}		
			}
		}
	}
	else{
		if(transit_habit == 0){
			if(biking_habit == 0){
				if(driving_habit == 0){
					if(trip_distance/1000 <= 1.404){
						if(assumed_quality_infrastructure_route["CrimeIncid"] <= 200.6957){
							modal_propensities = [0, 0.3042478, 0.043478, 0.65217391]
						}
						else{
							modal_propensities = [0.571428, 0.14285714, 0, 0.2857]
						}
					}
					else{
						if(car_access == 0){
							if(assumed_quality_infrastructure_route["NrTrees"] <= 94.2){
								modal_propensities = [0.0625, 0.5625, 0.15625, 0.21875]
							}
							else{
								modal_propensities = [0, 0, 1, 0]
							}
						}
						else{
							modal_propensities = [0.10204, 0.857142, 0.0481, 0]
						}
					}
				}
				else{
					if(trip_distance/1000 <= 1.145649){
						modal_propensities = [0.0151515, 0.651515, 0.0151515, 0.3181818]
					}
					else{
						if(assumed_quality_infrastructure_route["TrafAccid"] <= 74.633){
							if(assumed_quality_infrastructure_orig["pubTraDns"] <= 0){
								modal_propensities = [0.01376146, 0.9633027, 0.022935, 0]
							}
							else{
								modal_propensities = [0, 0.8636, 0.13636, 0]
							}
						}
						else{
							modal_propensities = [0, 0.714285714, 0.142857, 0.142857]
						}
					}
				}
			}
			else{
				if(driving_habit <= 0){
					if(trip_distance/1000 <= 1.5056){
						if(assumed_quality_infrastructure_route["greenCovr"] <= 0.2302273){
							if(migrationbackground != "Non-Western"){
								if(assumed_quality_infrastructure_route["RdIntrsDns"] <= 38.13793){
									if(has_child == 0){
										if(car_access == 0){
											modal_propensities = [0.8585858, 0.010101010, 0, 0.13131313]
										}
										else{
											modal_propensities = [0.583333, 0.083333, 0.0625, 0.2708333]
										}
									}
									else{
										modal_propensities = [0.9254658, 0.037267, 0.0062111, 0.0310559]
									}
								}
								else{
									modal_propensities = [0.35714, 0.142857, 0.142857, 0.35714]
								}
							}
							else{
								if(assumed_quality_infrastructure_route["greenCovr"] <= 0.2302273){
									modal_propensities = [1, 0, 0, 0]
								}
								else{
									modal_propensities = [0.53521126, 0.11267605, 0, 0.3521126]
								}
							}
						}
						else{
							modal_propensities = [0.61702127, 0.21276, 0, 0.170212]
						}
					}
					else{
						if(groceries == 0){
							if(assumed_quality_infrastructure_route["PNonWester"] <= 47.80488){
								if(trip_distance/1000 <= 5.593389){
									if(has_child <= 0){
										if(incomeclass <= 9){
											if(assumed_quality_infrastructure_route["MaxSpeed"] <= 35.7142){
												modal_propensities = [0.625, 0.1875, 0, 0.1875]
											}
											else{
												if(assumed_quality_infrastructure_route["MeanTraffV"] <= 2443.014){
													modal_propensities = [0.4285714, 0, 0.57142857, 0]
												}
												else{
													if(age <= 71){
														if(assumed_quality_infrastructure_route["TrafAccid"] <= 94.62162){
															modal_propensities = [0.960854, 0.032, 0, 0.007117]
														}
														else{
															modal_propensities = [0.782608, 0, 0.2173913, 0]
														}
													}
													else{
														modal_propensities = [0.571428, 0, 0.42857, 0]
													}
												}
											}
										}
										else{
											modal_propensities = [0.6875, 0.125, 0.1875, 0]
										}
									}
									else{
										modal_propensities = [0.8915662, 0.0963855, 0.0080321, 0.004016]
									}
								}
								else{
									modal_propensities = [0.6870229, 0.2061068, 0.099236, 0.0076335]
								}
							}
							else{
								if(assumed_quality_infrastructure_route["CrimeIncid"] <= 228.88 ){
									if(commute == 0){
										modal_propensities = [0.24242424, 0.7575757575, 0, 0]
									}
									else{
										modal_propensities = [1, 0, 0, 0]
									}
								}
								else{
									modal_propensities = [0.785714, 0.071428, 0.071428, 0.071428]
								}
							}
						}
						else{
							if(trip_distance/1000 <= 4.368259){
								modal_propensities = [0.7619047, 0.142857, 0, 0.095238]
							}
							else{
								modal_propensities = [0.214285, 0.107142, 0.6785714, 0]
							}
						}
					}	
				}	
				else{
					if(assumed_quality_infrastructure_route["AccidPedes"] <= 6.294521 ){
						if(trip_distance/1000 <= 0.661039){
							modal_propensities = [0.4285714, 0.214285714, 0, 0.3571428]
						}
						else{
							if(trip_distance/1000 <= 2.522454){
								if(assumed_quality_infrastructure_route["AccidPedes"] <= 1.666667 ){
									if(migrationbackground != "Non-Western"){
										if(assumed_quality_infrastructure_route["PedStrWidt"] <= 2.670028){
											modal_propensities = [0.3333, 0.6666666, 0, 0]
										}
										else{
											if(assumed_quality_infrastructure_route["PedStrWidt"] <= 3.463069){
												modal_propensities = [0.6966292, 0.29213483, 0, 0.011235955]
											}
											else{
												modal_propensities = [0.625, 0.25, 0, 0.125]
											}
										}
									}
									else{
										modal_propensities = [0.185185, 0.81481481, 0, 0]
									}
								}
								else{
									modal_propensities = [0.813953, 0.124031, 0.0155038, 0.04651162]
								}
							}
							else{
								if(assumed_quality_infrastructure_route["AccidPedes"] <= 2.589744 ){
									if(assumed_quality_infrastructure_route["MeanTraffV"] <= 7403.784){
										modal_propensities = [0.16762005, 0.7803468, 0.0520231, 0]
									}
									else{
										modal_propensities = [0.558823529, 0.44117647, 0, 0]
									}
								 }
								 else{
								 	if(rain <= 5.6){
								 		if(assumed_quality_infrastructure_route["OpenSpace"] <= 0.2354259){
											modal_propensities = [0.63636363, 0.2727272727, 0.09090909, 0]
								 		}
								 		else{
											modal_propensities = [0, 0.75, 0.125, 0.125]
								 		}
								 	}
								 	else{
										modal_propensities = [0.25, 0, 0.75, 0]
								 	}
								}
							}
						}
					}
					else{
						modal_propensities = [0.4146341463, 0.17073, 0.02439024, 0.3902439]
					}
				}
			}
		}
		else{
			if(trip_distance/1000 <= 2.447767){
				if(biking_habit == 0){
					if(driving_habit == 0){
						if(trip_distance/1000 <= 1.171727){
							modal_propensities = [0.0508474, 0.0169491525, 0.32203389, 0.610169]
						}
						else{
							if(incomeclass <= 8){
								modal_propensities = [0, 0.052631, 0.802631578, 0.144736842105263]
							}
							else{
								modal_propensities = [0.4, 0, 0.6, 0]
							}
						}
					}
					else{
						if(employment_status <= 0){
							modal_propensities = [0, 0, 0.375, 0.625]
						}
						else{
							modal_propensities = [0, 0.67647058, 0.2058823, 0.1176470588]
						}
					}
				}
				else{
					if(driving_habit == 0){
						if(assumed_quality_infrastructure_route["NrStrLight"] <= 28.55172){
							modal_propensities = [0.4444, 0.5, 0, 0.055555]
						}
						else{
							if(assumed_quality_infrastructure_route["nrTrees"] <= 85.47619){
								modal_propensities = [0.61434977, 0.0134529, 0.116591928, 0.2556053]
							}
							else{
								if(assumed_quality_infrastructure_dest["PrkPricPre"] <= 1.4){
									modal_propensities = [0.70129, 0.0519480, 0.233766233, 0.012987]
								}
								else{
									modal_propensities = [0.878787878, 0.015151515, 0.03030303, 0.075757575]
								}
							}
						}
					}
					else{
						if(sex == "male"){
							if(edu_int <= 2){
								modal_propensities = [0.6363636363, 0.18181818, 0.18181818, 0]
							}
							else{
								modal_propensities = [0.03703703, 0.629629, 0.333333, 0]
							}
						}
						else{
							if( hh_single == 0){
								modal_propensities = [0.68, 0.28, 0, 0.04]
							}
							else{
								modal_propensities = [0.375, 0, 0, 0.625]
							}
						}
					}
				}
			}
			else{
				if(driving_habit == 0){
					if(biking_habit == 0){
						if(leisure == 0){
							modal_propensities = [0.0052910052, 0.042328023, 0.93121693121, 0.0211640211]
						}
						else{
							if(assumed_quality_infrastructure_route["TrafAccid"] <= 65.27679){
								if(assumed_quality_infrastructure_route["MeanTraffV"] <= 3834.129){
									modal_propensities = [0.571428, 0.285714, 0.1428571428, 0]
								}
								else{
									modal_propensities = [0, 0.1290322, 0.8709677, 0]
								}
							}
							else{
								modal_propensities = [0, 0, 0.57142857, 0.42857142]
							}
						}
					}
					else{
						if(trip_distance/1000 <= 6.788672){
							if(edu_int <= 2){
								if(groceries ==0){
									if(assumed_quality_infrastructure_route["PedStrWidt"] <= 2.805957){
										modal_propensities = [0.5, 0, 0.375, 0.125]
									}
									else{
										if(edu_trip == 0){
											if(assumed_quality_infrastructure_route["PedStrWidt"] <= 3.118417){
												if(assumed_quality_infrastructure_route["MinSpeed"] <= 28.38462){
													modal_propensities = [0.14285714, 0.14285714, 0.714285714, 0]
												}
												else{
													modal_propensities = [0.5, 0, 0.5, 0]
												}
											}
											else{
												modal_propensities = [0.0909090, 0.1136363636, 0.79545454545, 0]
											}
										}
										else{
											modal_propensities = [0.075471698, 0.01886792, 0.80566037735, 0]
										}
									}
								}
								else{
									modal_propensities = [0.1875, 0, 0.5625, 0.25]
								}
							}
							else{
								if(assumed_quality_infrastructure_route["TrafAccid"] <= 108.6494){
									modal_propensities = [0.5303030303, 0.025252525, 0.4393939, 0.0050505050]
								}
								else{
									modal_propensities = [0.5, 0.5, 0, 0]
								}
							}
						}
						else{
							modal_propensities = [0.0441176, 0.06617647, 0.88970588,0]
						}
					}
				}
				else{
					if(commute == 0){
						modal_propensities = [0.0661764, 0.4264705, 0.46323529,0]
					}
					else{
						if(trip_distance/1000 <= 4.168814){
							if(sex == "male"){
								modal_propensities = [0.666666, 0.266666, 0.06666667,0]
							}
							else{
								modal_propensities = [0, 0, 1,0]
							}
						}
						else{
							modal_propensities = [0.064516, 0.14516129, 0.79032258,0]
						}
					}
				}
			}
		}				
		}
		randomnumber = rnd(1.000)
		if(randomnumber <= modal_propensities[0]){
			modalchoice = "bike"
		}
		else if(randomnumber <= sum(modal_propensities[0]+modal_propensities[1])){
			modalchoice = "car"
		}
		else if(randomnumber <= sum(modal_propensities[0]+modal_propensities[1] + modal_propensities[2])){
			modalchoice = "transit"
		}
		else{
			modalchoice = "walk"
		}
		write "tripdistance " + string(trip_distance) + " " + modalchoice 
   }
	def routing when:  new_route == 1  {
		  activity = "traveling"
		  new_route = 0
		save [string(current_date, 'dd/MM/yyyy'), current_date.hour,current_date.minute, Agent_ID, age, sex, incomeclass, Neighborhood, modalchoice] to: path_data+"Amsterdam/ModelRuns/modalchoice_" + modelrunname + ".csv" type:"csv" rewrite: false
		  
		#/ routing through OSRM via R interface
		unknown a =  R_eval("origin == " + to_R_data(container(self.location CRS_transform("EPSG:4326"))))
		unknown a =  R_eval("destination == " + to_R_data(container(point(destination_activity.location) CRS_transform("EPSG:4326"))))	
		if(modalchoice == "walk"){
		 	loop s over: Rcode_foot_routing.contents{
				unknown a = R_eval(s)
#							write "R>" + a
			}
		 	}
		else if(modalchoice == "bike"){
		 	loop s over: Rcode_bike_routing.contents{
				unknown a = R_eval(s)
			}
		 	}
		else if(modalchoice == "car") {
		 	loop s over: Rcode_car_routing.contents{
				unknown a = R_eval(s)
			}
		 }
		 else if(modalchoice == "transit") {
		 	loop s over: Rcode_car_routing.contents{
				unknown a = R_eval(s)
			}
		 }
		list<point> track = list(R_eval("track_points"))
		track_geometry = to_GAMA_CRS(line(track),  "EPSG:4326") add_point(point(destination_activity))
		track_path =  path(track_geometry)     	  
#		write "trackgeom:"+ track_geometry + "destination: " + destination_activity
		track_duration = float(list(R_eval("route$duration"))[0])  #/minutes
		float track_length = float(list(R_eval("route$distance"))[0])	#/ meters
		if(current_activity == "work" and (former_activity == "at_Home" or former_activity == "sleeping")){
				homeTOwork = track_path
				homeTOwork_mode = modalchoice
				homeTOwork_geometry = track_geometry 
				homeTOwork_duration = track_duration
				workTOhome_geometry = line(reverse(container(geometry_collection(homeTOwork_geometry)))) add_point(residence.location)
				workTOhome = path(workTOhome_geometry)
				}
		else if(current_activity == "school" and (former_activity == "at_Home" or former_activity == "sleeping")){
				homeTOschool = track_path
				homeTOschool_mode = modalchoice
				homeTOschool_geometry = track_geometry 
				homeTOschool_duration = track_duration
				schoolTOhome_geometry = line(reverse(container(geometry_collection(homeTOschool_geometry)))) add_point(residence.location)
				schoolTOhome = path(schoolTOhome_geometry)
			}
		else if(current_activity == "university" and (former_activity == "at_Home" or former_activity == "sleeping")){
				homeTOuni = track_path
				homeTOuni_mode = modalchoice
				homeTOuni_geometry = track_geometry 
				homeTOuni_duration = track_duration
				uniTOhome_geometry = line(reverse(container(geometry_collection(homeTOuni_geometry)))) add_point(residence.location)
				uniTOhome = path(uniTOhome_geometry)
			}
		else if(current_activity == "kindergarden" and (former_activity == "at_Home" or former_activity == "sleeping")){
				homeTOkinderga = track_path
				homeTOkinderga_mode = modalchoice
				homeTOkinderga_geometry = track_geometry 
				homeTOkinderga_duration = track_duration
				kindergaTOhome_geometry = line(reverse(container(geometry_collection(homeTOkinderga_geometry)))) add_point(residence.location)
				kindergaTOhome = path(kindergaTOhome_geometry)
			}
		else if(current_activity == "groceries_shopping" and (former_activity == "at_Home" or former_activity == "sleeping")){
				homeTOsuperm = track_path
				homeTOsuperm_mode = modalchoice
				homeTOsuperm_geometry = track_geometry 
				homeTOsuperm_duration = track_duration
				supermTOhome_geometry = line(reverse(container(geometry_collection(homeTOsuperm_geometry)))) add_point(self.residence.location)
				supermTOhome = path(supermTOhome_geometry)
		}	
		commute = 0
		edu_trip = 0
		groceries = 0
		leisure = 0		
	}
#	def any_activity when: activity == "perform_activity" and current_activity == "name of activity"{
#		e.g. the activity could have an impact on health (sports...)
#	}
	def at_Place_exposure when: activity == "perform_activity"{
#		activity_NO2 = (sum((AirPollution overlapping self) collect each.NO2)) * inhalation_rate["normal"] * AirPollution_Filter["indoor"] * steps_minute
		activity_NO2 = (sum((AirPollution overlapping self) collect each.NO2))* steps_minute
		activity_Noise = (sum((Noise_day overlapping self) collect each.Decibel)) * Noise_Filter["indoor"] * steps_minute
		hourly_NO2 = hourly_NO2 + activity_NO2
		hourly_Noise = hourly_Noise + activity_Noise
	}
	
    def traveling when: activity == "traveling"{
		do follow path: self.track_path speed: travelspeed[modalchoice]
		if((self.location == self.destination_activity.location)){
			self.location = destination_activity.location
#			write "arrived"
			activity = "perform_activity"
#    		activity_NO2 = (sum((AirPollution overlapping self.track_geometry) collect each.NO2)/( length(AirPollution overlapping self.track_geometry) + 1)) * inhalation_rate[modalchoice] * track_duration * AirPollution_Filter[modalchoice]
    		activity_NO2 = (sum((AirPollution overlapping self.track_geometry) collect each.NO2)/( length(AirPollution overlapping self.track_geometry) + 1))  * track_duration
			activity_Noise = (sum((Noise_day overlapping self.track_geometry) collect each.Decibel)/(length(Noise_day overlapping self.track_geometry) +1) )  * track_duration * Noise_Filter[modalchoice]
    		hourly_NO2 = hourly_NO2 + activity_NO2
			hourly_Noise = hourly_Noise + activity_Noise
    		if(modalchoice == "bike"){
    			bike_exposure = bike_exposure + track_duration
    		}
    		else if(modalchoice == "walk"){
    		walk_exposure = walk_exposure + track_duration
    		}
    		
    	}
    }
    def update_exposure when: current_date.minute == 0{
    	daily_NO2 = daily_NO2 + hourly_NO2
    	hourly_mean_NO2 = hourly_NO2/60
    	hourly_NO2 = 0.0
    }

    
    def save_exposure_data when: current_date.minute == 0{
		save [string(current_date, 'dd/MM/yyyy'), current_date.hour, Agent_ID, age, sex, incomeclass, Neighborhood, hourly_mean_NO2] to: path_data+"Amsterdam/ModelRuns/exposure_"+modelrunname+".csv" type:"csv" rewrite: false
	}

 	def step(self):
        # Define the agent's behavior in each step of the model
        pass
    


class TransportAirPollutionExposureModel(mesa.Model):
    def __init__(self, nb_humans = 40000, path_data = "C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam", 
                 starting_date = datetime(2018, 1, 1, 6, 50, 0), step = timedelta(minutes=5), steps_minute = 5, modelrunname= "intervention_scenario"):
        # Insert the global definitions, variables, and actions here
        self.path_data = path_data
        self.starting_date = starting_date
        self.step = step
        self.steps_minute = steps_minute
        self.nb_humans = nb_humans
        self.modelrunname = modelrunname
        self.schedule = SimultaneousActivation(self)
        self.grid = ContinousSpace(width, height, torus=True)
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
		for(i in range(nb_humans)):
			agent = Human(self, random_subset.iloc[i])
			self.schedule.add(agent)
			# Add the agent to a Home in their neighborhood
			
			self.grid.place_agent(agent, Home)

 
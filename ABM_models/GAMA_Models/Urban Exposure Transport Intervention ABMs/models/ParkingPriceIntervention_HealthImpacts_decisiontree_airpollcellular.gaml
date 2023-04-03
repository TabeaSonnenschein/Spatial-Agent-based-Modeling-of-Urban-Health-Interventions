/**
* Name: TransportAirPollutionExposureModel
* Author: Tabea Sonnenschein
* Description:
* Tags: Urban Health; 
*/

model TransportAirPollutionExposureModel
  
global skills: [RSkill]{
	/** Insert the global definitions, variables and actions here */
	
	string path_data <- "C:/Users/Tabea/Documents/PhD EXPANSE/Data/";
	string path_workspace <- "C:/Users/Tabea/Documents/GitHub/Spatial-Agent-based-Modeling-of-Urban-Health-Interventions/";
	
//	loading the spatial built environment
	file shape_file_buildings <- shape_file(path_data+"Amsterdam/Built Environment/Buildings/Buildings_RDNew.shp");
	file shape_file_buildings2 <- shape_file(path_data+"Amsterdam/Built Environment/Buildings/Diemen_Buildings.shp");
	file shape_file_buildings3 <- shape_file(path_data+"Amsterdam/Built Environment/Buildings/Oude Amstel_buildings.shp");
// file shape_file_streets <- shape_file(path_data+"Amsterdam/Built Environment/Transport Infrastructure/cars/Car Traffic_RDNew.shp");
    file shape_file_streets <- shape_file(path_data+"Amsterdam/Built Environment/Transport Infrastructure/Amsterdam_roads_RDNew.shp");
    file shape_file_greenspace <- shape_file(path_data+"Amsterdam/Built Environment/Green Spaces/Green Spaces_RDNew_window.shp");
	file shape_file_Residences <- shape_file(path_data+"Amsterdam/Built Environment/Buildings/Residences_neighcode_RDNew.shp");    
    file shape_file_Schools <- shape_file(path_data+"Amsterdam/Built Environment/Facilities/Amsterdam_schools_RDNew.shp");
    file shape_file_Supermarkets <- shape_file(path_data+"Amsterdam/Built Environment/Facilities/Amsterdam_supermarkets_RDNew.shp");
    file shape_file_Universities <- shape_file(path_data+"Amsterdam/Built Environment/Facilities/Amsterdam_universities_RDNew.shp");
    file shape_file_Kindergardens <- shape_file(path_data+"Amsterdam/Built Environment/Facilities/Amsterdam_kindergardens_RDNew.shp");
    file shape_file_Restaurants <- shape_file(path_data+"Amsterdam/Built Environment/Facilities/Amsterdam_Foursquarevenues_Food_RDNew.shp");
    file shape_file_Entertainment <- shape_file(path_data+"Amsterdam/Built Environment/Facilities/Amsterdam_Foursquarevenues_ArtsEntertainment_RDNew.shp");
    file shape_file_ShopsnServ <- shape_file(path_data+"Amsterdam/Built Environment/Facilities/Amsterdam_Foursquarevenues_ShopsServ_RDNew.shp");
    file shape_file_Nightlife <- shape_file(path_data+"Amsterdam/Built Environment/Facilities/Amsterdam_Foursquarevenues_Nightlife_RDNew.shp");
    file shape_file_Profess <- shape_file(path_data+"Amsterdam/Built Environment/Facilities/Amsterdam_Foursquarevenues_Profess_other_RDNew.shp");
    file spatial_extent <- shape_file(path_data+"Amsterdam/SpatialExtent/Amsterdam Diemen Oude Amstel Extent.shp");  
   	geometry shape <- envelope(spatial_extent); 
   	map<string,rgb> color_per_type <- ["streets"::#aqua, "vegetation":: #green, "buildings":: rgb(40,40,40), "NO2":: #red];
   	list<geometry> Restaurants;
   	list<geometry> Entertainment;
    
    //  loading grid with Environmental Behavior Determinant measures
    //	columnnames before:  "popDns", "retaiDns" , "greenCovr", "pubTraDns"  , "RdIntrsDns", "Intid"
    file rasterfile_EnvDeter <- grid_file(path_data+"Amsterdam/Built Environment/Transport Infrastructure/ModalChoice_determ_200.tif");
    csv_file EnvDeter_data <- csv_file(path_data+"Amsterdam/Built Environment/Transport Infrastructure/ModalChoice_determ_200_clean.csv", ",", string); 
    //	columnnames:  "unqId", "popDns", "retaiDns" , "greenCovr", "pubTraDns",
//                                    "RdIntrsDns", "TrafAccid", "AccidPedes", "NrTrees", "MeanTraffV",
//                                    "SumTraffVo", "HighwLen", "PedStrWidt", "PedStrLen", "LenBikRout",
//                                    "DistCBD", "retailDiv", "MaxSpeed", "MinSpeed", "MeanSpeed", "NrStrLight",
//                                    "CrimeIncid", "MaxNoisDay", "MxNoisNigh", "OpenSpace", "NrParkSpac",
//                                    "PNonWester", "PWelfarDep", "PrkPricPre", "PrkPricPos"	

    //  loading grid with airpollution determinants
    file airpoll_determ_raster <- grid_file(path_data+"Amsterdam/Air Pollution Determinants/AirPollDeterm_grid.tif");
//    csv_file airpoll_determ_data <- csv_file(path_data+"Amsterdam/Air Pollution Determinants/AirPollDeterm_grid50_baselineNO2.csv", ",", string); 
    csv_file airpoll_determ_data <- csv_file(path_data+"Amsterdam/Air Pollution Determinants/Intervention_onroad_impactsgrid.csv", ",", string); 

	//  loading weather data
    csv_file weather_data <- csv_file(path_data+"Amsterdam/Weather/Weather_Amsterdam18_19.csv", ",", string); 

//  loading Environmental Stressor Maps
	file shape_file_NoiseContour_night <- file(path_data+"Amsterdam/Environmental Stressors/Noise/PDOK_NoiseMap2016_Lnight_RDNew_clipped.shp");
	file shape_file_NoiseContour_day <- file(path_data+"Amsterdam/Environmental Stressors/Noise/PDOK_NoiseMap2016_Lden_RDNew_clipped.shp");    
    
//  loading routing code
    file Rcode_foot_routing <- text_file(path_workspace+ "Routing/OSRM_foot.R");
    file Rcode_car_routing <- text_file(path_workspace+ "Routing/OSRM_car.R");
    file Rcode_bike_routing <- text_file(path_workspace+ "Routing/OSRM_bike.R");

//  loading agent population attributes
//    csv_file Synth_Agent_file <- csv_file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Population/Agent_pop.csv", ";", string, true);
    file Rcode_agent_subsetting <- text_file(path_workspace + "ABM_models/GAMA_Models/External_Scripts_for_GAMA_Models/Subsetting_Synthetic_AgentPop_for_GAMA.R");
    csv_file Synth_Agent_file;
    
//  loading agent schedules   /// need more robust method for schedules based on HETUS data
	text_file kids_schedules_file <- text_file(path_data+"Harmonised European Time Use Survey - Eurostat/kids_schedule.txt");
	text_file youngadult_schedules_file <- text_file(path_data+"Harmonised European Time Use Survey - Eurostat/youngadult_schedule.txt");
	text_file adult_schedules_file <- text_file(path_data+"Harmonised European Time Use Survey - Eurostat/adult_schedule.txt");
	text_file elderly_schedules_file <- text_file(path_data+"Harmonised European Time Use Survey - Eurostat/elderly_schedule.txt");

// Global variables transport
	map<string, float> travelspeed <- create_map(["walk", "bike", "car", "transit"], [1.4, 3.33, 11.11, 10.00]); /// meters per seconds (5km/h, 12km/h, 40km/h )
	
// Global variables exposure
	map<string, float> inhalation_rate <- create_map(["walk", "bike", "normal"], [25.0, 40.0, 15.0]); /// breaths per minute  										// needs robust methodology
	map<string, float> Noise_Filter <- create_map(["indoor", "car", "walk", "bike"], [0.20, 0.40, 1, 1]); /// percentage of Noise that remains (is not filtered)							// needs robust methodology
	map<string, float> AirPollution_Filter <- create_map(["indoor", "car",  "walk", "bike"], [0.60, 0.80, 1, 1]); /// percentage of Air Pollution that remains (is not filtered)			// needs robust methodology
	
	grid Perceivable_Environment file: rasterfile_EnvDeter{
		float popDns;
		float retaiDns;
		float greenCovr ;
		float pubTraDns;
		float RdIntrsDns;
		float TrafAccid;
		float AccidPedes;
		float NrTrees;
		float MeanTraffV;
		float SumTraffVo;
		float HighwLen;
		float PedStrWidt;
		float PedStrLen;
		float LenBikRout;
		float DistCBD;
		float retailDiv;
		float MaxSpeed;
		float MeanSpeed;
		float NrStrLight;
		float CrimeIncid;
		float MaxNoisDay;
		float MxNoisNigh;
		float OpenSpace;
		float NrParkSpac;
		float PNonWester;
		float PWelfarDep;
		float PrkPricPre;
		float PrkPricPos;
		list datalist;

	}	
	
	int calculated_emission <- 0;
	int dispersed <- 0;
	grid AirPollution file: airpoll_determ_raster{
		int ON_ROAD <- 0;
		float TrafficVolume <- 0;
		list TrafficV_hourly;
		float NO2<-2;
		float N02_dispersed <- 6;
		float baseline_NO2;
		int indx;
		rgb color <- rgb(0,0,0,0.0);
		//	float PM2_5;
	}



	// weather variables
	int weatherindx;
	float rain;
	float wind;
	float temperature;
	matrix weathermatrix <- matrix(weather_data);
	
	list<int> int_id_airpoll <- columns_list(matrix(airpoll_determ_data)) at 0;
    matrix airpoll_matrix <- matrix(airpoll_determ_data);
    
    // set time and date
//    float step <- 1 #mn;  /// #mn minutes #h hours  #sec seconds #day days #week weeks #year years
    int nb_humans <- 40000;
    float step <- 5 #mn;  /// #mn minutes #h hours  #sec seconds #day days #week weeks #year years
    float steps_minute <- 5;
    date starting_date <- date([2018,1,1,6,50,0]); //correspond the 1st of January 2019, at 6:00:00
    int year;
    string modelrunname <- "intervention_scenario";
    
    init  {
        write "setting up the model";
        write current_date;
        do startR;
//        write R_eval("nb_humans = " + to_R_data(nb_humans));
//        write R_eval("filename = " + to_R_data("Population/Agent_pop.csv"));
//        loop s over: Rcode_agent_subsetting.contents{ 			/// the R code creates a csv file of a random subset of the synthetic agent population of specified size "nb_humans"
//							unknown a <- R_eval(s);
//						}
		Synth_Agent_file <- csv_file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Population/Agent_pop_GAMA.csv", ";", string, true); // this is the file that was created by the R code
		Restaurants <- shape_file_Restaurants where (each.location != nil);
		Entertainment <- shape_file_Entertainment where (each.location != nil);	
		write "entertainment " + length(Entertainment);
		create Homes from: shape_file_Residences with: [Neighborhood:: read('nghb_cd')];
		create Noise_day from: shape_file_NoiseContour_day with: [Decibel :: float(read('bovengrens'))] ;
        create Humans from: Synth_Agent_file with:[Agent_ID :: read('agent_ID'), Neighborhood :: read('neighb_code'), 
	        age:: int(read('age')), sex :: read('sex'), migrationbackground :: read('migrationbackground'),
	        hh_single :: int(read('hh_single')), is_child:: int(read('ischild')), has_child:: int(read('havechild')), 
        	current_edu:: read('current_education'), absolved_edu:: read('absolved_education'), BMI:: read('BMI'), 
        	scheduletype:: read('scheduletype'), employment_status:: read('personal_income'), incomeclass:: read('incomeclass_int'), agesexgroup:: read('agesexgroup'),
        	edu_int:: read("edu_int"), car_access:: read("car_access"), biking_habit::read("bike_habit"), driving_habit::read("car_habit"), transit_habit::read("transit_habit")]; // careful: column 1 is has the index 0 in GAMA      //
    	matrix EnvDeterm_measures <- matrix(EnvDeter_data);
    	write "loading spatial behavior determinants data";
    	ask Perceivable_Environment{
    		datalist <- rows_list(EnvDeterm_measures) at (int(self.grid_value)-1);
			popDns <- float(datalist at 1);
			retaiDns <-  float(datalist at 2);
			greenCovr <-  float(datalist at 3);
			pubTraDns <-  float(datalist at 4);
			RdIntrsDns <-  float(datalist at 5);
			TrafAccid <-  float(datalist at 6);
			AccidPedes <-  float(datalist at 7);
			NrTrees <-  float(datalist at 8);
			MeanTraffV <-  float(datalist at 9);
			SumTraffVo <-  float(datalist at 10);
			HighwLen <-  float(datalist at 11);
			PedStrWidt <-  float(datalist at 12);
			PedStrLen <-  float(datalist at 13);
			LenBikRout <-  float(datalist at 14);
			DistCBD <-  float(datalist at 15);
			retailDiv <-  float(datalist at 16);
			MaxSpeed <-  float(datalist at 17);
			MeanSpeed <- float(datalist at 19);
			NrStrLight <-  float(datalist at 20);
			CrimeIncid <-  float(datalist at 21);
			MaxNoisDay <-  float(datalist at 22);
			MxNoisNigh <-  float(datalist at 23);
			OpenSpace <-  float(datalist at 24);
			NrParkSpac <-  float(datalist at 25);
			PNonWester <-  float(datalist at 26);
			PWelfarDep <-  float(datalist at 27);
			PrkPricPre <-  float(datalist at 28);
			PrkPricPos <-  float(datalist at 29);
    	}
    	write "loading air pollution determinants data";
    	ask AirPollution{
			if(int_id_airpoll contains_value  int(self.grid_value)){
				indx <- index_of(int_id_airpoll , int(self.grid_value));
				ON_ROAD <- 1;
				baseline_NO2 <- airpoll_matrix[1, indx];
				TrafficV_hourly <- rows_list(airpoll_matrix) at indx;
				remove index: 0 from: TrafficV_hourly;
				remove index: 0 from: TrafficV_hourly;
				if (ON_ROAD = 1){
					TrafficVolume <- TrafficV_hourly at current_date.hour;
					NO2 <- (1.992+(0.03096377438925*TrafficVolume)+ baseline_NO2);
					color <- rgb(int((NO2/7)*30),0,0,(0.4 + NO2/100));
					N02_dispersed <- NO2;
				}
			}
    	}
    	 weatherindx <- index_of(column_at(weathermatrix, 0), string(current_date, 'dd/MM/yyyy'));
    	 write string(current_date, 'dd/MM/yyyy');
    	 rain <- weathermatrix[1,weatherindx];
    	 temperature <- weathermatrix[2,weatherindx];
    	 wind <- weathermatrix[4,weatherindx];
    	 write "temperature: " + temperature;
    	 write "wind: "+ wind;
    	 write "Diffusing";
		 diffuse var: N02_dispersed cycle_length:5 on: AirPollution proportion: 0.99 radius: 4;
	 	 ask AirPollution{
    		if (ON_ROAD = 0){
    			NO2 <- N02_dispersed;
				color <- rgb(int((NO2/7)*30),0,0,(0.4 + NO2/100));
				N02_dispersed <- 6;
       		}
    	 }

    	 
    }

    reflex determineWeather when: (current_date.minute = 0 and current_date.hour = 0){
    	 weatherindx <- index_of(column_at(weathermatrix, 0), string(current_date, 'dd/MM/yyyy'));
    	 write string(current_date, 'dd/MM/yyyy');
    	 rain <- weathermatrix[1,weatherindx];
    	 temperature <- weathermatrix[2,weatherindx];
    	 wind <- weathermatrix[4,weatherindx];
    	 write "temperature: " + temperature + "rain: " +  rain + " wind: "+ wind;
    }
    
    reflex RoadEmissions when: current_date.minute = 0 {
		write "On Road emission";
		ask AirPollution where (each.ON_ROAD = 1){
			TrafficVolume <- TrafficV_hourly at current_date.hour;
			NO2 <- (1.992+(0.03096377438925*TrafficVolume)+ baseline_NO2);
			color <- rgb(int((NO2/7)*30),0,0,(0.4 + NO2/100));
			N02_dispersed <- NO2;
		}
		calculated_emission <- 1;
	}
		
	reflex AirPollDispersion when: calculated_emission = 1 {
		write "AirPoll Dispersion";		
		diffuse var: N02_dispersed cycle_length:5 on: AirPollution proportion: 0.99 radius: 4;
		ask AirPollution where (each.ON_ROAD = 0){
			NO2 <- N02_dispersed;
			color <- rgb(int((NO2/7)*30),0,0,(0.4 + NO2/100));
			N02_dispersed <- 6;

		}
		calculated_emission <- 0;
	}
}

species Homes{
	string Neighborhood;
}

species Noise_day{
	float Decibel;
}

species Humans skills:[moving, RSkill] control: simple_bdi parallel: true{
	 // definition of attributes, actions, behaviors	
	 
/////// declaring variables //////////
	 /// individual characteristics
	string Agent_ID;
	int Agent_index;
	string Neighborhood;
	int age;					// integer age 0- 100
	string sex;  				// female, male
	string migrationbackground; // Dutch, Western, Non-Western
	int hh_single; 				// 1 = yes, 0 = no
	int is_child;				// 1 = yes, 0 = no
	int has_child;				// 1 = yes, 0 = no
	string current_edu;			// "high", "middle", "low", "no_current_edu"
	string absolved_edu;		// "high", "middle", "low", 0
	int edu_int;
	string BMI; 				//"underweight", "normal_weight", "moderate_overweight", "obese"
	string scheduletype;
	string agesexgroup;    /// 
	string incomegroup; /// "low", "middle", "high"			
	int student <- 0;		
	int incomeclass; 
	int commute <- 0;
	int groceries <- 0;
	int leisure <- 0;
	int edu_trip <- 0;
	int driving_habit;
	int biking_habit;
	int transit_habit;
	int employment_status;
	int car_access;
	
	list<float> modal_propensities <- [0.00, 0.00, 0.00,0.00];
	float randomnumber;
	
	/// destination locations
	geometry residence;
	geometry workplace;
	geometry school;
	geometry university;
	geometry kindergarden;
	geometry supermarket;
			
	/// activity variables
	string activity;
	list<string> schedule;
	/// weekday and weekend schedule
	string current_activity;
	string former_activity;
	geometry destination_activity;
	int traveldecision;
	int perception2 <-0;
	int perception3<-0;
	
	/// travel variables
	float track_duration;
	path track_path;
	geometry track_geometry;
	string modalchoice;
	int path_memory;
	int new_route;
	int make_modalchoice;
	geometry route_eucl_line;
	float trip_distance ;

	/// saved routes (for efficiency)
	path homeTOwork;
	string homeTOwork_mode;
	geometry homeTOwork_geometry;
	float homeTOwork_duration;
	path workTOhome;
	geometry workTOhome_geometry;
	path homeTOuni;
	string homeTOuni_mode;
	geometry homeTOuni_geometry;
	float homeTOuni_duration;
	path uniTOhome;
	geometry uniTOhome_geometry;
	path homeTOschool;
	string homeTOschool_mode;
	geometry homeTOschool_geometry;
	float homeTOschool_duration;	
	path schoolTOhome;
	geometry schoolTOhome_geometry;
	path homeTOsuperm;
	string homeTOsuperm_mode;
	geometry homeTOsuperm_geometry;
	float homeTOsuperm_duration;	
	path supermTOhome;
	geometry supermTOhome_geometry;
	path homeTOkinderga;
	string homeTOkinderga_mode;
	geometry homeTOkinderga_geometry;
	float homeTOkinderga_duration;	
	path kindergaTOhome;
	geometry kindergaTOhome_geometry;
	
	/// exposure variables
	float bike_exposure;
	float walk_exposure;
	float activity_NO2;
	float hourly_NO2;
	float hourly_mean_NO2;	
	float daily_NO2;
	float yearly_NO2;
//	float hourly_PM2_5;
//	float daily_PM2_5;
//	float yearly_PM2_5;
	float activity_Noise;
	float hourly_Noise;
	float daily_Noise;
	float yearly_Noise;
	
	//////// TRANSPORT BEHAVIOUR ///////////////
	bool probabilistic_choice <- true;
	
	/// Transport Behaviour: Behavioural Factors///
	// there are also convenience and affordability, but they are defined inside the model
	map<string, float> assumed_quality_infrastructure_route <- create_map(["popDns", "retaiDns", "greenCovr",  "RdIntrsDns", 
																			"TrafAccid", "AccidPedes", "NrTrees", "MeanTraffV",
										                                    "SumTraffVo", "HighwLen", "PedStrWidt", "PedStrLen", "LenBikRout",
										                                    "DistCBD", "retailDiv", "MaxSpeed", "NrStrLight",
										                                    "CrimeIncid", "MaxNoisDay", "MxNoisNigh", "OpenSpace", 
										                                    "PNonWester", "PWelfarDep"], 
										                                    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,0.0, 0.0, 0.0, 0.0, 0.0,0.0, 0.0, 0.0, 0.0, 0.0,0.0, 0.0, 0.0, 0.0, 0.0,0.0, 0.0, 0.0, 0.0]);	
	map<string,float> assumed_quality_infrastructure_orig <- create_map(["pubTraDns", "DistCBD"],[0.0, 0.0]);
	map<string,float> assumed_quality_infrastructure_dest <- create_map(["pubTraDns", "NrParkSpac","PrkPricPre", "PrkPricPos"],[0.0,0.0,0.0,0.0]);
	
	

	
	
	
/////// setting up the initial parameters and relations //////////
	init{
		  if(scheduletype = "youngadult"){
		  	schedule <- list(youngadult_schedules_file);
		  }
		  else if (scheduletype = "adult"){
		  	schedule <- list(adult_schedules_file);
		  }
		  else if (scheduletype = "kids"){
		  	schedule <- list(kids_schedules_file);
		  }
		  else if (scheduletype = "elderly"){
		  	schedule <- list(elderly_schedules_file);
		  } 
		  residence <- one_of(Homes where ((each.Neighborhood = self.Neighborhood) and each.location != nil));
		  if(self.residence = nil){
		  	write "|"+ Neighborhood+ "|";
		  	self.residence <- one_of(Homes);
		  }
       	  location <- residence.location;
       	  if(schedule contains "work"){
       	  	    workplace <- one_of(shape_file_Profess);
       	  }
       	  if(schedule contains "school"){
       	  		school <- closest_to(shape_file_Schools, self.location);
       	  }
       	  if(schedule contains "university"){
				university <- closest_to(shape_file_Universities, self.location);
       	  }
       	  if(schedule contains "kindergarden"){
				kindergarden <- closest_to(shape_file_Kindergardens, self.location);
       	  }
       	  if(schedule contains "groceries_shopping"){
				supermarket <-  closest_to(shape_file_Supermarkets, self.location) ;
       	  }       	     	
       	  activity <- "perform_activity";
		if (current_edu = "high"){
			student <- 1;
		}
       	  do startR;
       	 hourly_mean_NO2 <- (AirPollution overlapping self) collect each.NO2;
       	 hourly_NO2 <- hourly_mean_NO2 *current_date.minute;
	}
	
/////// defining the Human transition functions (behaviour and exposure) //////////
	reflex schedule_manager when: (((current_date.minute mod 10) = 0) or (current_date.minute = 0)){
		 current_activity <- schedule[(int((current_date.minute/10) + (current_date.hour * 6)))];
		 if((int(current_date.minute) != 0) or (int(current_date.hour) != 0)){
		 	former_activity <- schedule[int(((current_date.minute/10) + (current_date.hour * 6))-1)];
		 }
		 else{
		 	former_activity <- last(schedule) ;
		 }
		 if(current_activity != former_activity){
		 	if(current_activity = "work"){
		 		commute <- 1;
				destination_activity <- workplace;
				if(homeTOwork != nil and (former_activity = "at_Home" or former_activity = "sleeping")){
					track_path <- homeTOwork;
					track_geometry <- homeTOwork_geometry;
					modalchoice <- homeTOwork_mode;
					track_duration <- homeTOwork_duration;
					path_memory <- 1;
					write "saved pathway";
				}		 		
		 	}
		 	else if(current_activity = "school"){
		 		edu_trip <- 1;
		 		destination_activity <- school;
		 		if(homeTOschool != nil and (former_activity = "at_Home" or former_activity = "sleeping")){
					track_path <- homeTOschool;
					track_geometry <- homeTOschool_geometry;
					modalchoice <- homeTOschool_mode;
					track_duration <- homeTOschool_duration;
					path_memory <- 1;
					write "saved pathway";
				}		
		 	}
		 	else if(current_activity = "university"){
		 		edu_trip <- 1;
		 		destination_activity <- university;
		 		if(homeTOuni != nil and (former_activity = "at_Home" or former_activity = "sleeping")){
					track_path <- homeTOuni;
					track_geometry <- homeTOuni_geometry;
					track_duration <- homeTOuni_duration;
					modalchoice <- homeTOuni_mode;
					path_memory <- 1;
					write "saved pathway";
				}		
		 	}
		 	else if(current_activity = "groceries_shopping"){
		 		destination_activity <- supermarket;
		 		groceries <- 1;
		 		if(homeTOsuperm != nil and (former_activity = "at_Home" or former_activity = "sleeping")){
					track_path <- homeTOsuperm;
					track_geometry <- homeTOsuperm_geometry;
					track_duration <- homeTOsuperm_duration;
					modalchoice <- homeTOsuperm_mode;
					path_memory <- 1;
					write "saved pathway";
				}		
		 	}
		 	else if(current_activity = "kindergarden"){
		 		destination_activity <- kindergarden;
		 		if(homeTOkinderga != nil and (former_activity = "at_Home" or former_activity = "sleeping")){
					track_path <- homeTOkinderga;
					track_geometry <- homeTOkinderga_geometry;
					track_duration <- homeTOkinderga_duration;
					modalchoice <- homeTOkinderga_mode;
					path_memory <- 1;
					write "saved pathway";
				}		
		 	}
		 	else if(current_activity = "sleeping" or current_activity = "at_Home"){
		 		destination_activity <- self.residence.location;
		 		if(workTOhome != nil and former_activity = "work"){
					track_path <- workTOhome;
					track_geometry <- workTOhome_geometry;
					modalchoice <- homeTOwork_mode;
					track_duration <- homeTOwork_duration;
					path_memory <- 1;
					write "saved pathway_ return";
		 		}
		 		else if(schoolTOhome != nil and former_activity = "school"){
					track_path <- schoolTOhome;
					track_geometry <- schoolTOhome_geometry;
					modalchoice <- homeTOschool_mode;
					track_duration <- homeTOschool_duration;
					path_memory <- 1;
					write "saved pathway_ return";
		 		}
		 		else if(uniTOhome != nil and self.location = university.location){
					track_path <- uniTOhome;
					track_geometry <- uniTOhome_geometry;
					modalchoice <- homeTOuni_mode;
					track_duration <- homeTOuni_duration;
					path_memory <- 1;
					write "saved pathway_ return";
		 		}
		 		else if(supermTOhome != nil and self.location = supermarket.location){
					track_path <- supermTOhome;
					track_geometry <- supermTOhome_geometry;
					modalchoice <- homeTOsuperm_mode;
					track_duration <- homeTOsuperm_duration;
					path_memory <- 1;
					write "saved pathway_ return";
		 		}
		 		else if(kindergaTOhome != nil and self.location = supermarket.location){
					track_path <- kindergaTOhome;
					track_geometry <- kindergaTOhome_geometry;
					modalchoice <- homeTOkinderga_mode;
					track_duration <- homeTOkinderga_duration;
					path_memory <- 1;
					write "saved pathway_ return";
		 		}
		 	}
		 	else if(current_activity = "entertainment" ){
		 		leisure <- 1;
		 		destination_activity <- one_of(Entertainment);
		 		loop while: destination_activity = nil {
		 			destination_activity <- one_of(Entertainment);
		 		}
		 	}
		 	else if(current_activity = "eat" ){
		 		if (one_of(Restaurants inside circle(500, self.location)) != nil){
		 			destination_activity <- one_of(Restaurants inside circle(500, self.location));
		 		}
		 		else{
		 			destination_activity <- closest_to(Restaurants, self.location);
		 		}
		 		loop while: destination_activity = nil {
		 			destination_activity <- one_of(Restaurants);
		 		}
		 	}
		 	else if(current_activity = "social_life" ){
		 		destination_activity <- one_of(shape_file_Residences);
		 	}
		 	write "Current Activity: " + current_activity + "; Former Activity: " + former_activity;
		 	if(point(destination_activity.location) != point(self.location)){
		 		route_eucl_line <- line(container(point(self.location), point(destination_activity.location)));
		 		trip_distance <- (self.location distance_to destination_activity);
		 		if(path_memory != 1){
		 			traveldecision <- 1;
		 		}
		 		else if(path_memory = 1){
		 			 activity <- "traveling";
		 			 track_path <-  path((track_geometry add_point(point(destination_activity))));  
		 		}
		 		path_memory <- 0;
		 	}		 
		 	else{
		 		activity <-"perform_activity";
		 		traveldecision <- 0;
		 	}
		 }
	}
	perceive Env_Activity_Affordance_Travel_route target:(Perceivable_Environment where (each intersects route_eucl_line))  when: traveldecision = 1 {
    	myself.traveldecision <- 0;	
    	myself.perception2 <- 1;
    	write "perceiving route variables";
    	ask myself{
	   		assumed_quality_infrastructure_route <- (["popDns"::mean(myself.popDns), "retaiDns"::mean(myself.retaiDns), 
	   			"greenCovr"::mean(myself.greenCovr), "RdIntrsDns"::mean(myself.RdIntrsDns), 
	   			"TrafAccid"::mean(myself.TrafAccid), "NrTrees"::mean(myself.NrTrees), 
	   			"MeanTraffV"::mean(myself.MeanTraffV), "HighwLen"::mean(myself.HighwLen), "AccidPedes"::mean(myself.AccidPedes),
	   			"PedStrWidt"::mean(myself.PedStrWidt),"PedStrLen"::mean(myself.PedStrLen), 
	   			"LenBikRout"::mean(myself.LenBikRout), "DistCBD"::mean(myself.DistCBD), 
	   			"retailDiv"::mean(myself.retailDiv), "MeanSpeed"::mean(myself.MeanSpeed), "MaxSpeed"::mean(myself.MaxSpeed), 
	   			"NrStrLight"::mean(myself.NrStrLight), "CrimeIncid"::mean(myself.CrimeIncid), 
	   			"MaxNoisDay"::mean(myself.MaxNoisDay),"OpenSpace"::mean(myself.OpenSpace), 
	   			"PNonWester"::mean(myself.PNonWester), "PWelfarDep"::mean(myself.PWelfarDep)]);
	   	}    	
    }
//    reflex Env_Activity_Affordance_Travel_orig_dest when: perception2 = 1 {
//    	 perception2 <- 0;	
//    	 make_modalchoice <- 1;
//    	
//    }
//    sum((AirPollution overlapping self) collect each.NO2)
    perceive Env_Activity_Affordance_Travel_orig target:(Perceivable_Environment overlapping self.location) when: perception2 = 1 {
    	myself.perception2 <- 0;	
    	myself.perception3 <- 1;
    	write "perceiving orig variables";
    	ask myself{
	   		assumed_quality_infrastructure_orig <- (["pubTraDns"::myself.pubTraDns, "DistCBD"::myself.DistCBD]);
	   	}    	
    }
    perceive Env_Activity_Affordance_Travel_dest target:(Perceivable_Environment overlapping self.destination.location)  when: perception3 = 1 {
    	myself.perception3 <- 0;	
    	myself.make_modalchoice <- 1;
    	write "perceiving dest variables";
    	
    	ask myself{
	   		assumed_quality_infrastructure_dest <- (["pubTraDns"::myself.pubTraDns, 
	   			"NrParkSpac"::myself.NrParkSpac, "PrkPricPre"::myself.PrkPricPre, 
	   			"PrkPricPos"::myself.PrkPricPos]);
	   	}    	
    }
   reflex modalchoice when: make_modalchoice = 1 {
   	write "make modalchoice";
   	new_route <- 1;
   	make_modalchoice <- 0;
	if((trip_distance/1000) <= 0.60708){
		if (biking_habit = 0){
			if(driving_habit = 0){
				modal_propensities <- [0.026315789, 0.06842105263, 0.1486068, 0.83684210];
			}
			else{
				if(assumed_quality_infrastructure_orig["pubTraDns"] <= 0){
					modal_propensities <- [0, 0.277310924, 0.00840336, 0.714285714];
				}
				else{
					modal_propensities <- [0.14285714, 0.14285714, 0, 0.714285714];
				}		
			}
		}
		else{
			if(trip_distance/1000 <= 0.3457){
				if(assumed_quality_infrastructure_route["greenCovr"] <= 0.402){
					if(assumed_quality_infrastructure_route["MeanSpeed"] <= 25){
						modal_propensities <- [0.2, 0.2, 0, 0.6];
					}
					else{
						modal_propensities <- [0.2065727, 0.01408, 0.01563, 0.768779];
					}		
				}
				else{
					modal_propensities <- [0.19047, 0, 0.19047, 0.619047];
				}		
			}
			else{
				if(assumed_quality_infrastructure_route["SumTraffVo"] <= 471641.5){
					if(driving_habit = 0){
						if(transit_habit = 0){
							if(assumed_quality_infrastructure_route["AccidPedes"] <= 3.3333){
								modal_propensities <- [0.7727272727272, 0, 0, 0.227272727272];
							}
							else{
								modal_propensities <- [0.348484848, 0.045454545, 0, 0.60606060606];
							}
						}
						else{
							modal_propensities <- [0.3727272, 0.02727272727272, 0, 0.6];
						}
					}
					else{
						if(incomeclass <= 9){
							modal_propensities <- [0.468468, 0.054054, 0, 0.606060];
						}
						else{
							modal_propensities <- [0.28125, 0.375, 0, 0.34375];
						}
					}		
				}
				else{
					modal_propensities <- [0.142857, 0, 0.142857, 0.7142];
				}		
			}
		}
	}
	else{
		if(transit_habit = 0){
			if(biking_habit = 0){
				if(driving_habit = 0){
					if(trip_distance/1000 <= 1.404){
						if(assumed_quality_infrastructure_route["CrimeIncid"] <= 200.6957){
							modal_propensities <- [0, 0.3042478, 0.043478, 0.65217391];
						}
						else{
							modal_propensities <- [0.571428, 0.14285714, 0, 0.2857];
						}
					}
					else{
						if(car_access = 0){
							if(assumed_quality_infrastructure_route["NrTrees"] <= 94.2){
								modal_propensities <- [0.0625, 0.5625, 0.15625, 0.21875];
							}
							else{
								modal_propensities <- [0, 0, 1, 0];
							}
						}
						else{
							modal_propensities <- [0.10204, 0.857142, 0.0481, 0];
						}
					}
				}
				else{
					if(trip_distance/1000 <= 1.145649){
						modal_propensities <- [0.0151515, 0.651515, 0.0151515, 0.3181818];
					}
					else{
						if(assumed_quality_infrastructure_route["TrafAccid"] <= 74.633){
							if(assumed_quality_infrastructure_orig["pubTraDns"] <= 0){
								modal_propensities <- [0.01376146, 0.9633027, 0.022935, 0];
							}
							else{
								modal_propensities <- [0, 0.8636, 0.13636, 0];
							}
						}
						else{
							modal_propensities <- [0, 0.714285714, 0.142857, 0.142857];
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
									if(has_child = 0){
										if(car_access = 0){
											modal_propensities <- [0.8585858, 0.010101010, 0, 0.13131313];
										}
										else{
											modal_propensities <- [0.583333, 0.083333, 0.0625, 0.2708333];
										}
									}
									else{
										modal_propensities <- [0.9254658, 0.037267, 0.0062111, 0.0310559];
									}
								}
								else{
									modal_propensities <- [0.35714, 0.142857, 0.142857, 0.35714];
								}
							}
							else{
								if(assumed_quality_infrastructure_route["greenCovr"] <= 0.2302273){
									modal_propensities <- [1, 0, 0, 0];
								}
								else{
									modal_propensities <- [0.53521126, 0.11267605, 0, 0.3521126];
								}
							}
						}
						else{
							modal_propensities <- [0.61702127, 0.21276, 0, 0.170212];
						}
					}
					else{
						if(groceries = 0){
							if(assumed_quality_infrastructure_route["PNonWester"] <= 47.80488){
								if(trip_distance/1000 <= 5.593389){
									if(has_child <= 0){
										if(incomeclass <= 9){
											if(assumed_quality_infrastructure_route["MaxSpeed"] <= 35.7142){
												modal_propensities <- [0.625, 0.1875, 0, 0.1875];
											}
											else{
												if(assumed_quality_infrastructure_route["MeanTraffV"] <= 2443.014){
													modal_propensities <- [0.4285714, 0, 0.57142857, 0];
												}
												else{
													if(age <= 71){
														if(assumed_quality_infrastructure_route["TrafAccid"] <= 94.62162){
															modal_propensities <- [0.960854, 0.032, 0, 0.007117];
														}
														else{
															modal_propensities <- [0.782608, 0, 0.2173913, 0];
														}
													}
													else{
														modal_propensities <- [0.571428, 0, 0.42857, 0];
													}
												}
											}
										}
										else{
											modal_propensities <- [0.6875, 0.125, 0.1875, 0];
										}
									}
									else{
										modal_propensities <- [0.8915662, 0.0963855, 0.0080321, 0.004016];
									}
								}
								else{
									modal_propensities <- [0.6870229, 0.2061068, 0.099236, 0.0076335];
								}
							}
							else{
								if(assumed_quality_infrastructure_route["CrimeIncid"] <= 228.88 ){
									if(commute = 0){
										modal_propensities <- [0.24242424, 0.7575757575, 0, 0];
									}
									else{
										modal_propensities <- [1, 0, 0, 0];
									}
								}
								else{
									modal_propensities <- [0.785714, 0.071428, 0.071428, 0.071428];
								}
							}
						}
						else{
							if(trip_distance/1000 <= 4.368259){
								modal_propensities <- [0.7619047, 0.142857, 0, 0.095238];
							}
							else{
								modal_propensities <- [0.214285, 0.107142, 0.6785714, 0];
							}
						}
					}	
				}	
				else{
					if(assumed_quality_infrastructure_route["AccidPedes"] <= 6.294521 ){
						if(trip_distance/1000 <= 0.661039){
							modal_propensities <- [0.4285714, 0.214285714, 0, 0.3571428];
						}
						else{
							if(trip_distance/1000 <= 2.522454){
								if(assumed_quality_infrastructure_route["AccidPedes"] <= 1.666667 ){
									if(migrationbackground != "Non-Western"){
										if(assumed_quality_infrastructure_route["PedStrWidt"] <= 2.670028){
											modal_propensities <- [0.3333, 0.6666666, 0, 0];
										}
										else{
											if(assumed_quality_infrastructure_route["PedStrWidt"] <= 3.463069){
												modal_propensities <- [0.6966292, 0.29213483, 0, 0.011235955];
											}
											else{
												modal_propensities <- [0.625, 0.25, 0, 0.125];
											}
										}
									}
									else{
										modal_propensities <- [0.185185, 0.81481481, 0, 0];
									}
								}
								else{
									modal_propensities <- [0.813953, 0.124031, 0.0155038, 0.04651162];
								}
							}
							else{
								if(assumed_quality_infrastructure_route["AccidPedes"] <= 2.589744 ){
									if(assumed_quality_infrastructure_route["MeanTraffV"] <= 7403.784){
										modal_propensities <- [0.16762005, 0.7803468, 0.0520231, 0];
									}
									else{
										modal_propensities <- [0.558823529, 0.44117647, 0, 0];
									}
								 }
								 else{
								 	if(rain <= 5.6){
								 		if(assumed_quality_infrastructure_route["OpenSpace"] <= 0.2354259){
											modal_propensities <- [0.63636363, 0.2727272727, 0.09090909, 0];
								 		}
								 		else{
											modal_propensities <- [0, 0.75, 0.125, 0.125];
								 		}
								 	}
								 	else{
										modal_propensities <- [0.25, 0, 0.75, 0];
								 	}
								}
							}
						}
					}
					else{
						modal_propensities <- [0.4146341463, 0.17073, 0.02439024, 0.3902439];
					}
				}
			}
		}
		else{
			if(trip_distance/1000 <= 2.447767){
				if(biking_habit = 0){
					if(driving_habit = 0){
						if(trip_distance/1000 <= 1.171727){
							modal_propensities <- [0.0508474, 0.0169491525, 0.32203389, 0.610169];
						}
						else{
							if(incomeclass <= 8){
								modal_propensities <- [0, 0.052631, 0.802631578, 0.144736842105263];
							}
							else{
								modal_propensities <- [0.4, 0, 0.6, 0];
							}
						}
					}
					else{
						if(employment_status <= 0){
							modal_propensities <- [0, 0, 0.375, 0.625];
						}
						else{
							modal_propensities <- [0, 0.67647058, 0.2058823, 0.1176470588];
						}
					}
				}
				else{
					if(driving_habit = 0){
						if(assumed_quality_infrastructure_route["NrStrLight"] <= 28.55172){
							modal_propensities <- [0.4444, 0.5, 0, 0.055555];
						}
						else{
							if(assumed_quality_infrastructure_route["nrTrees"] <= 85.47619){
								modal_propensities <- [0.61434977, 0.0134529, 0.116591928, 0.2556053];
							}
							else{
								if(assumed_quality_infrastructure_dest["PrkPricPre"] <= 1.4){
									modal_propensities <- [0.70129, 0.0519480, 0.233766233, 0.012987];
								}
								else{
									modal_propensities <- [0.878787878, 0.015151515, 0.03030303, 0.075757575];
								}
							}
						}
					}
					else{
						if(sex = "male"){
							if(edu_int <= 2){
								modal_propensities <- [0.6363636363, 0.18181818, 0.18181818, 0];
							}
							else{
								modal_propensities <- [0.03703703, 0.629629, 0.333333, 0];
							}
						}
						else{
							if( hh_single = 0){
								modal_propensities <- [0.68, 0.28, 0, 0.04];
							}
							else{
								modal_propensities <- [0.375, 0, 0, 0.625];
							}
						}
					}
				}
			}
			else{
				if(driving_habit = 0){
					if(biking_habit = 0){
						if(leisure = 0){
							modal_propensities <- [0.0052910052, 0.042328023, 0.93121693121, 0.0211640211];
						}
						else{
							if(assumed_quality_infrastructure_route["TrafAccid"] <= 65.27679){
								if(assumed_quality_infrastructure_route["MeanTraffV"] <= 3834.129){
									modal_propensities <- [0.571428, 0.285714, 0.1428571428, 0];
								}
								else{
									modal_propensities <- [0, 0.1290322, 0.8709677, 0];
								}
							}
							else{
								modal_propensities <- [0, 0, 0.57142857, 0.42857142];
							}
						}
					}
					else{
						if(trip_distance/1000 <= 6.788672){
							if(edu_int <= 2){
								if(groceries =0){
									if(assumed_quality_infrastructure_route["PedStrWidt"] <= 2.805957){
										modal_propensities <- [0.5, 0, 0.375, 0.125];
									}
									else{
										if(edu_trip = 0){
											if(assumed_quality_infrastructure_route["PedStrWidt"] <= 3.118417){
												if(assumed_quality_infrastructure_route["MinSpeed"] <= 28.38462){
													modal_propensities <- [0.14285714, 0.14285714, 0.714285714, 0];
												}
												else{
													modal_propensities <- [0.5, 0, 0.5, 0];
												}
											}
											else{
												modal_propensities <- [0.0909090, 0.1136363636, 0.79545454545, 0];
											}
										}
										else{
											modal_propensities <- [0.075471698, 0.01886792, 0.80566037735, 0];
										}
									}
								}
								else{
									modal_propensities <- [0.1875, 0, 0.5625, 0.25];
								}
							}
							else{
								if(assumed_quality_infrastructure_route["TrafAccid"] <= 108.6494){
									modal_propensities <- [0.5303030303, 0.025252525, 0.4393939, 0.0050505050];
								}
								else{
									modal_propensities <- [0.5, 0.5, 0, 0];
								}
							}
						}
						else{
							modal_propensities <- [0.0441176, 0.06617647, 0.88970588,0];
						}
					}
				}
				else{
					if(commute = 0){
						modal_propensities <- [0.0661764, 0.4264705, 0.46323529,0];
					}
					else{
						if(trip_distance/1000 <= 4.168814){
							if(sex = "male"){
								modal_propensities <- [0.666666, 0.266666, 0.06666667,0];
							}
							else{
								modal_propensities <- [0, 0, 1,0];
							}
						}
						else{
							modal_propensities <- [0.064516, 0.14516129, 0.79032258,0];
						}
					}
				}
			}
		}				
		}
		randomnumber <- rnd(1.000);
		if(randomnumber <= modal_propensities[0]){
			modalchoice <- "bike";
		}
		else if(randomnumber <= sum(modal_propensities[0]+modal_propensities[1])){
			modalchoice <- "car";
		}
		else if(randomnumber <= sum(modal_propensities[0]+modal_propensities[1] + modal_propensities[2])){
			modalchoice <- "transit";
		}
		else{
			modalchoice <- "walk";
		}
		write "tripdistance " + string(trip_distance) + " " + modalchoice ;
   }
	reflex routing when:  new_route = 1  {
		  activity <- "traveling";
		  new_route <- 0;
		save [string(current_date, 'dd/MM/yyyy'), current_date.hour,current_date.minute, Agent_ID, age, sex, incomeclass, Neighborhood, modalchoice] to: path_data+"Amsterdam/ModelRuns/modalchoice_" + modelrunname + ".csv" type:"csv" rewrite: false;
		  
		/// routing through OSRM via R interface
		unknown a <-  R_eval("origin = " + to_R_data(container(self.location CRS_transform("EPSG:4326"))));
		unknown a <-  R_eval("destination = " + to_R_data(container(point(destination_activity.location) CRS_transform("EPSG:4326"))));	
		if(modalchoice = "walk"){
		 	loop s over: Rcode_foot_routing.contents{
				unknown a <- R_eval(s);
//							write "R>" + a;
			}
		 	}
		else if(modalchoice = "bike"){
		 	loop s over: Rcode_bike_routing.contents{
				unknown a <- R_eval(s);
			}
		 	}
		else if(modalchoice = "car") {
		 	loop s over: Rcode_car_routing.contents{
				unknown a <- R_eval(s);
			}
		 }
		 else if(modalchoice = "transit") {
		 	loop s over: Rcode_car_routing.contents{
				unknown a <- R_eval(s);
			}
		 }
		list<point> track <- list(R_eval("track_points"));
		track_geometry <- to_GAMA_CRS(line(track),  "EPSG:4326") add_point(point(destination_activity));
		track_path <-  path(track_geometry);     	  
//		write "trackgeom:"+ track_geometry + "destination: " + destination_activity;
		track_duration <- float(list(R_eval("route$duration"))[0]);  ///minutes
		float track_length <- float(list(R_eval("route$distance"))[0]);	/// meters
		if(current_activity = "work" and (former_activity = "at_Home" or former_activity = "sleeping")){
				homeTOwork <- track_path;
				homeTOwork_mode <- modalchoice;
				homeTOwork_geometry <- track_geometry ;
				homeTOwork_duration <- track_duration;
				workTOhome_geometry <- line(reverse(container(geometry_collection(homeTOwork_geometry)))) add_point(residence.location);
				workTOhome <- path(workTOhome_geometry);
				}
		else if(current_activity = "school" and (former_activity = "at_Home" or former_activity = "sleeping")){
				homeTOschool <- track_path;
				homeTOschool_mode <- modalchoice;
				homeTOschool_geometry <- track_geometry ;
				homeTOschool_duration <- track_duration;
				schoolTOhome_geometry <- line(reverse(container(geometry_collection(homeTOschool_geometry)))) add_point(residence.location);
				schoolTOhome <- path(schoolTOhome_geometry);
			}
		else if(current_activity = "university" and (former_activity = "at_Home" or former_activity = "sleeping")){
				homeTOuni <- track_path;
				homeTOuni_mode <- modalchoice;
				homeTOuni_geometry <- track_geometry ;
				homeTOuni_duration <- track_duration;
				uniTOhome_geometry <- line(reverse(container(geometry_collection(homeTOuni_geometry)))) add_point(residence.location);
				uniTOhome <- path(uniTOhome_geometry);
			}
		else if(current_activity = "kindergarden" and (former_activity = "at_Home" or former_activity = "sleeping")){
				homeTOkinderga <- track_path;
				homeTOkinderga_mode <- modalchoice;
				homeTOkinderga_geometry <- track_geometry ;
				homeTOkinderga_duration <- track_duration;
				kindergaTOhome_geometry <- line(reverse(container(geometry_collection(homeTOkinderga_geometry)))) add_point(residence.location);
				kindergaTOhome <- path(kindergaTOhome_geometry);
			}
		else if(current_activity = "groceries_shopping" and (former_activity = "at_Home" or former_activity = "sleeping")){
				homeTOsuperm <- track_path;
				homeTOsuperm_mode <- modalchoice;
				homeTOsuperm_geometry <- track_geometry ;
				homeTOsuperm_duration <- track_duration;
				supermTOhome_geometry <- line(reverse(container(geometry_collection(homeTOsuperm_geometry)))) add_point(self.residence.location);
				supermTOhome <- path(supermTOhome_geometry);
		}	
		commute <- 0;
		edu_trip <- 0;
		groceries <- 0;
		leisure <- 0;		
	}
//	reflex any_activity when: activity = "perform_activity" and current_activity = "name of activity"{
//		e.g. the activity could have an impact on health (sports...)
//	}
	reflex at_Place_exposure when: activity = "perform_activity"{
//		activity_NO2 <- (sum((AirPollution overlapping self) collect each.NO2)) * inhalation_rate["normal"] * AirPollution_Filter["indoor"] * steps_minute;
		activity_NO2 <- (sum((AirPollution overlapping self) collect each.NO2))* steps_minute;
		activity_Noise <- (sum((Noise_day overlapping self) collect each.Decibel)) * Noise_Filter["indoor"] * steps_minute;
		hourly_NO2 <- hourly_NO2 + activity_NO2;
		hourly_Noise <- hourly_Noise + activity_Noise;
	}
	
    reflex traveling when: activity = "traveling"{
		do follow path: self.track_path speed: travelspeed[modalchoice];
		if((self.location = self.destination_activity.location)){
			self.location <- destination_activity.location;
//			write "arrived";
			activity <- "perform_activity";
//    		activity_NO2 <- (sum((AirPollution overlapping self.track_geometry) collect each.NO2)/( length(AirPollution overlapping self.track_geometry) + 1)) * inhalation_rate[modalchoice] * track_duration * AirPollution_Filter[modalchoice];
    		activity_NO2 <- (sum((AirPollution overlapping self.track_geometry) collect each.NO2)/( length(AirPollution overlapping self.track_geometry) + 1))  * track_duration;
			activity_Noise <- (sum((Noise_day overlapping self.track_geometry) collect each.Decibel)/(length(Noise_day overlapping self.track_geometry) +1) )  * track_duration * Noise_Filter[modalchoice];
    		hourly_NO2 <- hourly_NO2 + activity_NO2;
			hourly_Noise <- hourly_Noise + activity_Noise;
    		if(modalchoice = "bike"){
    			bike_exposure <- bike_exposure + track_duration;
    		}
    		else if(modalchoice = "walk"){
    		walk_exposure <- walk_exposure + track_duration;
    		}
    		
    	}
    }
    reflex update_exposure when: current_date.minute = 0{
    	daily_NO2 <- daily_NO2 + hourly_NO2;
    	hourly_mean_NO2 <- hourly_NO2/60;
    	hourly_NO2 <- 0.0;
    }
//    reflex acute_exposure_impacts when: current_date.hour = 0{	
//    	daily_NO2 <- 0.0;
////		daily_PM2_5
////		daily_Noise
//    }
//    reflex chronic_exposure_impacts when: current_date.year > year{
////    	yearly_PM10
////		yearly_PM2_5
//// 		yearly_Noise
//    }
    aspect base {
    	if(activity = "perform_activity"){
    		   draw sphere(30) color: #yellow;
    	}
    	else if(activity = "traveling"){
    		if(modalchoice = "bike"){
    			draw cube(60) color: #blue;
    			
    		}
    		else if(modalchoice =  "walk"){
    			draw cube(60) color: #green;
    			
    		}
    		else if(modalchoice =  "car"){
    			draw cube(60) color: #fuchsia;
    		}
    		else if(modalchoice =  "transit"){
    			draw cube(60) color: #chocolate;
    		}
    	}
    	
    }
    reflex save_exposure_data when: current_date.minute = 0{
		save [string(current_date, 'dd/MM/yyyy'), current_date.hour, Agent_ID, age, sex, incomeclass, Neighborhood, hourly_mean_NO2] to: path_data+"Amsterdam/ModelRuns/exposure_"+modelrunname+".csv" type:"csv" rewrite: false;
	}
}


experiment TransportAirPollutionExposureModel type: gui {
	/** Insert here the definition of the input and output of the model */
	parameter "Number of human agents" var: nb_humans min: 10 max: 10000  category: "Human attributes";
//	parameter "Visualize Air Pollution Field" var:display_air_poll among: [true, false] type:bool;
	
	output {
		layout horizontal([1::6000,0::4000]) tabs: false;
	
    	display stats type: java2D synchronized: true {
        	overlay position: {0, 0} size: {1, 0.05} background: #black  border: #black {
    	  	  		draw "Model Time: " + current_date + " , Temperature: " + temperature + " , Rain: " + rain + " , Wind: " + wind color: #white font: font("SansSerif", 17) at: {40#px, 30#px};
				}
  	      chart "Transport Mode distribution" type: histogram background: #black color: #white axes: #white size: {0.5,0.5} position: {0.5, 0.5} label_font: font("SansSerif", 12){
 		       	data "walk" value: Humans count (each.modalchoice = "walk" and each.activity = "traveling") color:#green;
	        	data "bike" value: Humans count (each.modalchoice = "bike" and each.activity = "traveling") color:#blue;
   		     	data "car" value: Humans count (each.modalchoice = "car" and each.activity = "traveling") color:#fuchsia;
   		     	data "transit" value: Humans count (each.modalchoice = "transit" and each.activity = "traveling") color:#chocolate;
   		     	data "not travelling" value: Humans count (each.activity = "perform_activity") color:#yellow;
     	   }
//			chart "Mean Noise Exposure" type: scatter x_label: (string(int(step/60))) + " Minute Steps"  y_label: "Decibel" background: #black color: #white axes: #white size: {0.5,0.45} position: {0, 0.05} label_font: font("SansSerif", 12){
//					data "Noise exposure" value: mean(Humans collect each.activity_Noise) color: #red marker: false style: line;
//			}
			chart "Modal Split Time Trends" type: scatter x_label: (string(int(steps_minute))) + " Minute Steps"  y_label: "Nr People" background: #black color: #white axes: #white size: {0.5,0.45} position: {0, 0.05} label_font: font("SansSerif", 12){
					data "Walkers" value: Humans count (each.modalchoice = "walk" and each.activity = "traveling") color: #green marker: false style: line;
					data "Bikers" value: Humans count (each.modalchoice = "bike" and each.activity = "traveling") color: #blue marker: false style: line;
					data "Drivers" value: Humans count (each.modalchoice = "car" and each.activity = "traveling") color: #fuchsia marker: false style: line;
					data "Transit-Users" value: Humans count (each.modalchoice = "transit" and each.activity = "traveling") color: #chocolate marker: false style: line;
			}
			chart "Mean Hourly NO2 Exposure" type: scatter x_label: (string(int(steps_minute))) + " Minute Steps" y_label: "µg" background: #black color: #white axes: #white size: {0.5,0.45} position: {0.5, 0.05} label_font: font("SansSerif", 12){
//					data "Max hourly exposure" value: max(Humans collect each.hourly_mean_NO2) color: #red marker: false style: line;
					data "Mean hourly exposure" value: mean(Humans collect each.hourly_mean_NO2) color: #white marker: false style: line;
//					data "Min hourly exposure" value: min(Humans collect each.hourly_mean_NO2) color: #green marker: false style: line;
			}
//			chart "Hourly NO2 Exposure" type: heatmap background: #black color: #white axes: #white size: {0.5,0.45} position: {0.5, 0.05} label_font: font("SansSerif", 12)
//			        x_serie_labels: (distribution_of(Humans collect each.hourly_mean_NO2, 20, 0.0, 200.0) at "legend") {
//					data "Hourly exposure µg" value: (distribution_of(Humans collect each.hourly_mean_NO2, 20, 0.0, 200.0) at "legend") color: #red;
//			}
			chart "Agent Age Distribution" type: histogram background: #black color: #white axes: #white size: {0.5,0.25} position: {0, 0.5} {
				data "0-10" value: Humans count (each.age <= 10) color:#teal;
				data "11-20" value: Humans count ((each.age > 10) and (each.age <= 20)) color:#teal;
				data "21-30" value: Humans count ((each.age > 20) and (each.age <= 30)) color:#teal;
				data "31-40" value: Humans count ((each.age > 30) and (each.age <= 40)) color:#teal;
				data "41-50" value: Humans count ((each.age > 40) and (each.age <= 50)) color:#teal;
				data "51-60" value: Humans count ((each.age > 50) and (each.age <= 60)) color:#teal;
				data "61-70" value: Humans count ((each.age > 60) and (each.age <= 70)) color:#teal;
				data "71-80" value: Humans count ((each.age > 70) and (each.age <= 80)) color:#teal;
				data "81 or" value: Humans count (each.age > 81) color:#teal;
			}
			chart "Agent Sex Distribution" type: histogram background: #black color: #white axes: #white size: {0.5,0.25} position: {0, 0.75} label_font: font("SansSerif", 12){
				data "male" value: Humans count (each.sex = "male") color:#teal;
				data "female" value: Humans count (each.sex = "female") color:#teal ;
			}
//			chart "Agent Age Distribution" type: heatmap background: #black color: #white axes: #white size: {0.5,0.5} position: {0, 0.5} 
//                  	x_serie_labels: (distribution_of(Humans collect each.age, 10, 0, 100) at "legend") {
////        				data "Agedistrib" value: (distribution_of(Humans collect each.age, 10, 0, 100) at "values") color: #teal; 
//        				data "male" value: Humans count (each.sex = "male") color:#teal;
//						data "female" value: Humans count (each.sex = "female") color:#teal ;
//			}	
  		 }
  		 display map type:opengl {
   		 	graphics background refresh: false{
    			draw shape color: #black;
    		}
       		graphics Buildings refresh: false{
    			draw shape_file_buildings color: rgb(40,40,40);
    			draw shape_file_buildings2 color: rgb(40,40,40);
    			draw shape_file_buildings3 color: rgb(40,40,40);
    			
			}
			graphics Streets refresh: false{
    			draw shape_file_streets color: #aqua;
			}
			graphics GreenSpace refresh: false{
    			draw shape_file_greenspace color: #green;
			}
       		species Humans aspect: base ;
//			graphics Noise transparency: 0.7{
//			if(current_date.hour < 4 or current_date.hour > 22){
//				draw shape_file_NoiseContour_night color: #purple ;
//			}
//			else{
//				draw shape_file_NoiseContour_day color: #purple ;				
//			}
//			}
			grid AirPollution;
			
        	overlay position: {0, 0, 0} size: {180 #px, 130#px} background: #black rounded: false transparency: 0.0 {
                float y <- 30#px;
                loop type over: color_per_type.keys  {   
                	draw square(10#px) at: { 20#px, y} color: color_per_type[type] border: #white;
                	draw square(10#px) at: { 20#px, y} color: color_per_type[type] border: #white;
                	draw square(10#px) at: { 20#px, y} color: color_per_type[type] border: #white;
                	draw type at: { 50#px, y + 5#px} color: #white font: font("SansSerif", 16, #bold);		// this might look confusing. Unfortunately overlay transparency is automatically set at 0.75 (highly transparent) and that cannot be changed.
                    draw type at: { 50#px, y + 5#px} color: #white font: font("SansSerif", 16, #bold);		// this makes a legend hardly readable. Therefore I draw it multiple times above each other for stronger colors).
                    draw type at: { 50#px, y + 5#px} color: #white font: font("SansSerif", 16, #bold);
                    draw type at: { 50#px, y + 5#px} color: #white font: font("SansSerif", 16, #bold);
                    y <- y + 25#px;
                }
            }    
   		 }
    }
}




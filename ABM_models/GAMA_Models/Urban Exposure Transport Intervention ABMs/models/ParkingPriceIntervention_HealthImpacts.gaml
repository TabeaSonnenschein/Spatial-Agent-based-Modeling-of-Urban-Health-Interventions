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
   	map<string,rgb> color_per_type <- ["streets"::#aqua, "vegetation":: #green, "buildings":: rgb(40,40,40), "NO2":: #purple];
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
    csv_file airpoll_determ_data <- csv_file(path_data+"Amsterdam/Air Pollution Determinants/AirPollDeterm_grid50_baselineNO2.csv", ",", string); 

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
    int nb_humans <- 150;
//    csv_file Synth_Agent_file <- csv_file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Population/Agent_pop.csv", ";", string, true);
    file Rcode_agent_subsetting <- text_file(path_workspace + "ABM_models/GAMA_Models/External_Scripts_for_GAMA_Models/Subsetting_Synthetic_AgentPop_for_GAMA.R");
    csv_file Synth_Agent_file;
    
//  loading agent schedules   /// need more robust method for schedules based on HETUS data
	text_file kids_schedules_file <- text_file(path_data+"Harmonised European Time Use Survey - Eurostat/kids_schedule.txt");
	text_file youngadult_schedules_file <- text_file(path_data+"Harmonised European Time Use Survey - Eurostat/youngadult_schedule.txt");
	text_file adult_schedules_file <- text_file(path_data+"Harmonised European Time Use Survey - Eurostat/adult_schedule.txt");
	text_file elderly_schedules_file <- text_file(path_data+"Harmonised European Time Use Survey - Eurostat/elderly_schedule.txt");

// Global variables transport
	map<string, float> travelspeed <- create_map(["walk", "bike", "car"], [1.4, 3.33, 11.11]); /// meters per seconds (5km/h, 12km/h, 40km/h )
	map<string, float> transport_costs<- create_map(["walk", "bike", "car"], [0, 0.01, 0.2 ]);  // Euros per 1km     												// needs robust methodology
	map<string, float> transport_safety <- create_map(["walk", "bike", "car"], [0.05, 0.66, 0.1 ]);  //Percent of serious traffic accidents (SWOV)    				// needs robust methodology
	float per_car_owners	<- 0.5;
	
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

	grid AirPollution file: airpoll_determ_raster{
		int ON_ROAD <- 0;
		float TrafficVolume <- 0;
		float NO2<-0;
		float N02_dispersed <- 0;
		float baseline_NO2;
		int indx;
		rgb color <- rgb(0,0,0,0.0);
		//	float PM2_5;
		reflex AirPollOnRoads when: (current_date.minute = 0){
			if(ON_ROAD = 1){
				TrafficVolume <- rnd(0.0 , 5000.0);
				NO2 <- (1.992+(0.03096377438925*TrafficVolume)+ baseline_NO2);
				write "trafficvolume: " + TrafficVolume + " NO2:" + NO2;
				color <- rgb(int((NO2/30)*20),0,int((NO2/30)*20),0.6);
			}
		}
	}
	
	reflex AirPollDispersion when: (current_date.minute = 0){
		write "AirPoll Dispersion";
		diffuse var: N02_dispersed on: AirPollution proportion: 0.02;
		ask AirPollution{
			if(ON_ROAD = 0){
				NO2 <- N02_dispersed;
				color <- rgb(int((NO2/30)*20),0,int((NO2/30)*20),0.6);
			}
		}
	}
	
// behaviour model parameters
	// bike params
	float LenBikRout_weight_bike <- 0.0535568;
	float popDns_weight_bike <- 5.4952866882;
	float greenCovr_weight_bike <- 1.1003415;
	float RdIntrsDns_weight_bike <- 0.66820025444;
	float TrafAccid_weight_bike <- 2.132558569;
	float DistCBD_weight_bike  <- -0.545226275;
	float NrTrees_weight_bike <- 0.08073636;
	float MeanTraffV_weight_bike <- 6.6543101;
	float HighwLen_weight_bike <- 4.76492987;
	float MaxSpeed_weight_bike <- -1.179248228;
	float NrStrLight_weight_bike <- 3.170361205;
	float CrimeIncid_weight_bike <- -0.35041186213;
	float MaxNoisDay_weight_bike  <- -2.4310804158;
	float OpenSpace_weight_bike <- 0.26518285;
	float PNonWester_weight_bike <- 2.05723223090172;
	float PWelfarDep_weight_bike <- -0.275174349546;
	float temperature_weight_bike <- 0.09476150;
	float rain_weight_bike <- -2.5408547818;
	float wind_weight_bike  <- 0.25267203152;
	float education_level_weight_bike <- -1.862337484955;
	float leisure_weight_bike <- 1.75662295520306;
	float groceries_weight_bike  <- 1.66421373188;
	float education_trip_weight_bike <- -2.08599987626;
	float commute_weight_bike <- 1.0021468251943;
	float student_weight_bike <- -1.2098534;
	float biking_habit_weight_bike  <- 1.1758591168;
	float male_weight_bike <- 1.58457493;
	float female_weight_bike <- 0.957327493;
	float age_weight_bike  <- -0.4361497277;
	
	// walk params
	float DistCBD_weight_walk <- 6.540438383817;
	float pubTraDns_orig_weight_walk <- 5.872207269;
	float pubTraDns_dest_weight_walk <- 1.16443742811;
	float popDns_weight_walk <- 4.541789855953331;
	float retaiDns_weight_walk <- 1.1126464903;
	float greenCovr_weight_walk <- 5.99439367;
	float RdIntrsDns_weight_walk <- 2.7032258;
	float TrafAccid_weight_walk <- 2.5995512008667;
	float AccidPedes_weight_walk <- -0.08911171555;
	float NrTrees_weight_walk <- 3.802636742;
	float MeanTraffV_weight_walk <- -4.268254235;
	float HighwLen_weight_walk <- 8.747015;
	float PedStrWidt_weight_walk <- 9.618386790;
	float PedStrLen_weight_walk <- 9.19158579;
	float retailDiv_weight_walk <- 7.80363047;
	float MaxSpeed_weight_walk <- 9.37715658545494;
	float NrStrLight_weight_walk <- 10.4553273022175;
	float CrimeIncid_weight_walk <- 4.97089715301991;
	float MaxNoisDay_weight_walk <- 3.28951945900917;
	float OpenSpace_weight_walk <- 0.88767220079;
	float PNonWester_weight_walk <- 5.0633111;
	float PWelfarDep_weight_walk <- 4.166309133172;
	float temperature_weight_walk <- 7.61083075573;
	float rain_weight_walk <- 4.952134922;
	float wind_weight_walk <- 5.849877357482;
	float leisure_weight_walk <- 3.189771562;
	float groceries_weight_walk <- 3568975448;
	float age_weight_walk <- 4.6520638;
	float male_weight_walk <- 5.000992745;
	float female_weight_walk <- 1.96534395;
	
	// car params
	float income_weight_car <- 15.60824969;
	float parking_space_weight_car <- -0.6609428077;
	float parking_price_weight_car <- -0.6544295387;
	float children_weight_car <- 4.601231768;
	float DistCBD_weight_car <- 10.39094151;
	float temperature_weight_car <- 0.3837685286;
	float rain_weight_car <- 4.74307896;
	float commute_weight_car <- 5.61672258377;
	float groceries_weight_car <- -1.34749247;
	float education_level_weight_car <- 15.15723128;
	float driving_habit_weight_car <- 4.98261812;
	float single_hh_weight_car <- 5.42037193477154;
	float NonWestern_weight_car <- 7.87472046911;
	float Western_weight_car <- 2.89664994180;
	float Dutch_weight_car <- 4.59664446115494;
	
	// transit params
	float age_weight_transit <- 9.06730897724628;
	float income_weight_transit <- 4.15292795;
	float DistCBD_weight_transit <- 7.76590441167;
	float pubTraDns_orig_weight_transit <- 13.81745058;
	float pubTraDns_dest_weight_transit <- 8.8849863409996;
	float popDns_weight_transit <- 8.371958255;
	float retaiDns_weight_transit <- 12.20413199;
	float retailDiv_weight_transit <- 9.39293076097965;
	float NrStrLight_weight_transit <- 3.98184259235;
	float CrimeIncid_weight_transit <- 6.1272670924;
	float PNonWester_weight_transit <- 12.44995415;
	float PWelfarDep_weight_transit <- 19.9433657;
	float commute_weight_transit <- 6.995902612805;
	float leisure_weight_transit <- 11.3675303161144;
	float rain_weight_transit <- 15.4244261085;
	float transit_habit_weight_transit <- 11.0012784600258;
	float student_weight_transit <- 7.33357855677;
	float education_trip_weight_transit <- 16.3340566307306;
	float male_weight_transit <- 13.9328315;
	float female_weight_transit <- 3.11775304377;
	float NonWestern_weight_transit <- 9.8592074513;
	float Western_weight_transit <- 12.4649539142847;
	float Dutch_weight_transit <- 9.42348743975;
	
	
	map<string,float> trip_dist_weight_car_age_sex<- create_map(["0-9_male", "10-17_male", "18-34_male", "35-49_male", "50-64_male", "65-110_male","0-9_female", "10-17_female", "18-34_female", "35-49_female", "50-64_female", "65-110_female" ],[4.0902937, 4.060989558, 8.64265,5.91286, 0.385012, 3.63934455, 4.48169, 2.52572, 2.2953, 1.6941, 1.3703, 1.67109]);
	map<string,float> trip_dist_weight_walk_age_sex <-create_map(["0-9_male", "10-17_male", "18-34_male", "35-49_male", "50-64_male", "65-110_male","0-9_female", "10-17_female", "18-34_female", "35-49_female", "50-64_female", "65-110_female" ],[7.10659, 3.15818, 3.46698, 8.04464, 0.989099, 3.075455, -0.3745029, 8.683157, 3.936364, 3.621193670808, 4.4813588,  3.6188870]);
	map<string,float> trip_dist_weight_bike_age_sex <- create_map(["0-9_male", "10-17_male", "18-34_male", "35-49_male", "50-64_male", "65-110_male","0-9_female", "10-17_female", "18-34_female", "35-49_female", "50-64_female", "65-110_female" ],[-3.2813, -1.19097, 2.030356, -0.217929, 1.86363, -1.12224, -2.462022, -1.4956355, 2.05722700, 1.072712, -2.187531, -1.93998]);
	map<string,float> trip_dist_weight_transit_age_sex <- create_map(["0-9_male", "10-17_male", "18-34_male", "35-49_male", "50-64_male", "65-110_male","0-9_female", "10-17_female", "18-34_female", "35-49_female", "50-64_female", "65-110_female"],[13.04582, 5.141811, 10.8149295, 11.4119386, 12.17845, 11.214766, 14.88964, 7.04975, 1.736604, 15.561919, 7.80035, 6.12913]);
	map<string,float> threshold_dist_walk_age_sex <- create_map(["0-9_male", "10-17_male", "18-34_male", "35-49_male", "50-64_male", "65-110_male","0-9_female", "10-17_female", "18-34_female", "35-49_female", "50-64_female", "65-110_female"],[3.0982, 4.7851, 4.6088, 6.23605, 2.5474286973, 5.17048, 4.99129, 6.18411, 2.7662, 4.4659, 4.83505, 6.45586]);
	
	// weather variables
	int weatherindx;
	float rain;
	float wind;
	float temperature;
	matrix weathermatrix <- matrix(weather_data);
	
	list<int> int_id_airpoll <- columns_list(matrix(airpoll_determ_data)) at 0;
    matrix airpoll_matrix <- matrix(airpoll_determ_data);
    
    // set time and date
    float step <- 1 #mn;  /// #mn minutes #h hours  #sec seconds #day days #week weeks #year years
    date starting_date <- date([2019,1,1,6,0,0]); //correspond the 1st of January 2019, at 6:00:00
    int year;
    
    init  {
        write "setting up the model";
        write current_date;
        do startR;
        write R_eval("nb_humans = " + to_R_data(nb_humans));
        write R_eval("filename = " + to_R_data("Population/Agent_pop.csv"));
        loop s over: Rcode_agent_subsetting.contents{ 			/// the R code creates a csv file of a random subset of the synthetic agent population of specified size "nb_humans"
							unknown a <- R_eval(s);
						}
		Synth_Agent_file <- csv_file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Population/Agent_pop_GAMA.csv", ";", string, true); // this is the file that was created by the R code
		Restaurants <- shape_file_Restaurants where (each.location != nil);
		Entertainment <- shape_file_Entertainment where (each.location != nil);	
		create Homes from: shape_file_Residences with: [Neighborhood:: read('nghb_cd')];
		create Noise_day from: shape_file_NoiseContour_day with: [Decibel :: float(read('bovengrens'))] ;
        create Humans from: Synth_Agent_file with:[Agent_ID :: read('Agent_ID'), Neighborhood :: read('neighb_code'), 
	        age:: int(read('age')), sex :: read('sex'), migrationbackground :: read('migrationbackground'),
	        hh_single :: int(read('hh_single')), is_child:: int(read('is_child')), has_child:: int(read('has_child')), 
        	current_edu:: read('current_education'), absolved_edu:: read('absolved_education'), BMI:: read('BMI'), 
        	scheduletype:: read('scheduletype'), incomeclass:: read('incomeclass_int'), agesexgroup:: read('agesexgroup'),
        	edu_int:: read("edu_int")]; // careful: column 1 is has the index 0 in GAMA      //
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
			}
    	}
    	 weatherindx <- index_of(column_at(weathermatrix, 0), string(current_date, 'dd/MM/yyyy'));
    	 write string(current_date, 'dd/MM/yyyy');
    	 rain <- weathermatrix[1,weatherindx];
    	 temperature <- weathermatrix[2,weatherindx];
    	 wind <- weathermatrix[4,weatherindx];
    	 write "temperature: " + temperature;
    	 write "wind: "+ wind;
    }

    reflex determineWeather when: (current_date.minute = 0 and current_date.hour = 0){
    	 weatherindx <- index_of(column_at(weathermatrix, 0), string(current_date, 'dd/MM/yyyy'));
    	 write string(current_date, 'dd/MM/yyyy');
    	 rain <- weathermatrix[1,weatherindx];
    	 temperature <- weathermatrix[2,weatherindx];
    	 wind <- weathermatrix[4,weatherindx];
    	 write "temperature: " + temperature + "rain: " +  rain + " wind: "+ wind;
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
	int male <- 0;
	int female <- 1;
	int Dutch <- 1 ;
	int Western <- 0;
	int NonWestern <- 0;
	
	
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
	float daily_NO2;
	float yearly_PM10;
	float hourly_PM2_5;
	float daily_PM2_5;
	float yearly_PM2_5;
	float activity_Noise;
	float hourly_Noise;
	float daily_Noise;
	float yearly_Noise;
	
	//////// TRANSPORT BEHAVIOUR ///////////////
	bool probabilistic_choice <- true;
	
	/// Transport Behaviour: Behavioural Factors///
	// there are also convenience and affordability, but they are defined inside the model
	map<string, float> assumed_traveltime  <- create_map(["traveltime_bike", "traveltime_walk", "traveltime_car"], [0.0, 0.0, 0.0]);
	map<string, float> assumed_quality_infrastructure_route <- create_map(["popDns", "retaiDns", "greenCovr",  "RdIntrsDns", 
																			"TrafAccid", "AccidPedes", "NrTrees", "MeanTraffV",
										                                    "SumTraffVo", "HighwLen", "PedStrWidt", "PedStrLen", "LenBikRout",
										                                    "DistCBD", "retailDiv", "MaxSpeed", "NrStrLight",
										                                    "CrimeIncid", "MaxNoisDay", "MxNoisNigh", "OpenSpace", 
										                                    "PNonWester", "PWelfarDep"], 
										                                    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,0.0, 0.0, 0.0, 0.0, 0.0,0.0, 0.0, 0.0, 0.0, 0.0,0.0, 0.0, 0.0, 0.0, 0.0,0.0, 0.0, 0.0, 0.0]);	
	map<string,float> assumed_quality_infrastructure_orig <- create_map(["pubTraDns", "DistCBD"],[0.0, 0.0]);
	map<string,float> assumed_quality_infrastructure_dest <- create_map(["pubTraDns", "NrParkSpac","PrkPricPre", "PrkPricPos"],[0.0,0.0,0.0,0.0]);
	
//	float budget <- rnd (800.0 , 5000.0); // Euros per month   								// needs robust methodology
	

	/// Transport Behaviour: Behavioural Constraints///
	int car_owner <- 0;																		// needs robust methodology
	
	/// Transport Behaviour: Utilities ///
	float driving_utility;
	float biking_utility;
	float walking_utility;
	float public_transport_utility;
	
	
	
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
		  residence <- one_of(Homes where ((each.Neighborhood = self.Neighborhood) and each.location != nil)) ;
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
       	  if(age > 20){
       	  	if(flip(per_car_owners)){
       	  		car_owner <- 1;
       	  	}
       	  }    	  	
			if (current_edu = "high"){
				student <- 1;
			}
		if(sex = "male"){
			male <- 1;
			female <- 0; 
		}
		if(migrationbackground = "Western"){
			Western <- 1;
			Dutch <- 0; 
		}
		else if (migrationbackground = "Non-Western"){
			NonWestern <- 1;
			Dutch <- 0;
		}
       	  do startR;
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
	   			"MeanTraffV"::mean(myself.MeanTraffV), "HighwLen"::mean(myself.HighwLen), 
	   			"PedStrWidt"::mean(myself.PedStrWidt),"PedStrLen"::mean(myself.PedStrLen), 
	   			"LenBikRout"::mean(myself.LenBikRout), "DistCBD"::mean(myself.DistCBD), 
	   			"retailDiv"::mean(myself.retailDiv), "MaxSpeed"::mean(myself.MaxSpeed), 
	   			"NrStrLight"::mean(myself.NrStrLight), "CrimeIncid"::mean(myself.CrimeIncid), 
	   			"MaxNoisDay"::mean(myself.MaxNoisDay),"OpenSpace"::mean(myself.OpenSpace), 
	   			"PNonWester"::mean(myself.PNonWester), "PWelfarDep"::mean(myself.PWelfarDep)]);

	   		assumed_traveltime <- ["traveltime_bike"::(trip_distance/travelspeed["bike"]), "traveltime_walk"::(trip_distance/travelspeed["walk"]), "traveltime_car"::(trip_distance/travelspeed["car"])]; 
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
	driving_utility <- (parking_space_weight_car * float(assumed_quality_infrastructure_dest["NrParkSpac"])) 
					+ (parking_price_weight_car * float(assumed_quality_infrastructure_dest["PrkPricPre"])) 
					+ (DistCBD_weight_car * float(assumed_quality_infrastructure_route["DistCBD"])) 
					+ (income_weight_car * incomeclass)
					+ (children_weight_car * has_child) 
					+ (temperature_weight_car * temperature) 
					+ (rain_weight_car * rain) 
					+ (commute_weight_car * commute)
					+ (groceries_weight_car * groceries) 	
					+ (education_level_weight_car * edu_int) 
//					+ (driving_habit_weight_car * driving_habit) 
					+ (Dutch_weight_car * Dutch) 
					+ (Western_weight_car * Western) 
					+ (NonWestern_weight_car * NonWestern) 
					+ (single_hh_weight_car * hh_single) 						
					+ (trip_dist_weight_car_age_sex[agesexgroup] * (trip_distance/1000));
	
	walking_utility <- (DistCBD_weight_walk * (assumed_quality_infrastructure_route["DistCBD"])) 
					+ (pubTraDns_orig_weight_walk * (assumed_quality_infrastructure_orig["pubTraDns"]))
					+ (pubTraDns_dest_weight_walk * (assumed_quality_infrastructure_dest["pubTraDns"]))					
					+ (popDns_weight_walk * (assumed_quality_infrastructure_route["popDns"]))
					+ (retaiDns_weight_walk * (assumed_quality_infrastructure_route["retaiDns"]))
					+ (greenCovr_weight_walk * (assumed_quality_infrastructure_route["greenCovr"]))
					+ (RdIntrsDns_weight_walk * (assumed_quality_infrastructure_route["RdIntrsDns"]))
					+ (TrafAccid_weight_walk * (assumed_quality_infrastructure_route["TrafAccid"]))
					+ (AccidPedes_weight_walk * (assumed_quality_infrastructure_route["AccidPedes"]))					
					+ (NrTrees_weight_walk * (assumed_quality_infrastructure_route["NrTrees"]))
					+ (MeanTraffV_weight_walk * (assumed_quality_infrastructure_route["MeanTraffV"]))
					+ (HighwLen_weight_walk * (assumed_quality_infrastructure_route["HighwLen"]))
					+ (PedStrWidt_weight_walk * (assumed_quality_infrastructure_route["PedStrWidt"]))
					+ (PedStrLen_weight_walk * (assumed_quality_infrastructure_route["PedStrLen"]))
					+ (retailDiv_weight_walk * (assumed_quality_infrastructure_route["retailDiv"]))
					+ (MaxSpeed_weight_walk * (assumed_quality_infrastructure_route["MaxSpeed"]))
					+ (NrStrLight_weight_walk * (assumed_quality_infrastructure_route["NrStrLight"]))
					+ (CrimeIncid_weight_walk * (assumed_quality_infrastructure_route["CrimeIncid"]))					
					+ (MaxNoisDay_weight_walk * (assumed_quality_infrastructure_route["MaxNoisDay"]))
					+ (OpenSpace_weight_walk * (assumed_quality_infrastructure_route["OpenSpace"]))
					+ (PNonWester_weight_walk * (assumed_quality_infrastructure_route["PNonWester"]))
					+ (PWelfarDep_weight_walk * (assumed_quality_infrastructure_route["PWelfarDep"]))
					+ (temperature_weight_walk * temperature)
					+ (rain_weight_walk * rain)
					+ (wind_weight_walk * wind)
					+ (leisure_weight_walk * leisure)
					+ (groceries_weight_walk * groceries)
					+ (male_weight_walk * male)
					+ (female_weight_walk * female)
					+ (age_weight_walk * age)					
					+ (trip_dist_weight_walk_age_sex[agesexgroup] * (trip_distance/1000));					

					
	biking_utility <- (LenBikRout_weight_bike * (assumed_quality_infrastructure_route["LenBikRout"])) 					
					+ (popDns_weight_bike * (assumed_quality_infrastructure_route["popDns"]))
					+ (greenCovr_weight_bike * (assumed_quality_infrastructure_route["greenCovr"]))
					+ (RdIntrsDns_weight_bike * (assumed_quality_infrastructure_route["RdIntrsDns"]))
					+ (TrafAccid_weight_bike * (assumed_quality_infrastructure_route["TrafAccid"]))
					+ (DistCBD_weight_bike * (assumed_quality_infrastructure_orig["DistCBD"]))					
					+ (NrTrees_weight_bike * (assumed_quality_infrastructure_route["NrTrees"]))
					+ (MeanTraffV_weight_bike * (assumed_quality_infrastructure_route["MeanTraffV"]))
					+ (HighwLen_weight_bike * (assumed_quality_infrastructure_route["HighwLen"]))
					+ (MaxSpeed_weight_bike * (assumed_quality_infrastructure_route["MaxSpeed"]))
					+ (NrStrLight_weight_bike * (assumed_quality_infrastructure_route["NrStrLight"]))
					+ (CrimeIncid_weight_bike * (assumed_quality_infrastructure_route["CrimeIncid"]))					
					+ (MaxNoisDay_weight_bike * (assumed_quality_infrastructure_route["MaxNoisDay"]))
					+ (OpenSpace_weight_bike * (assumed_quality_infrastructure_route["OpenSpace"]))
					+ (PNonWester_weight_bike * (assumed_quality_infrastructure_route["PNonWester"]))
					+ (PWelfarDep_weight_bike * (assumed_quality_infrastructure_route["PWelfarDep"]))
					+ (temperature_weight_bike * temperature)
					+ (rain_weight_bike * rain)
					+ (wind_weight_bike * wind)
					+ (leisure_weight_bike * leisure)
					+ (groceries_weight_bike * groceries)
					+ (education_trip_weight_bike * edu_trip)
					+ (commute_weight_bike * commute)
					+ (student_weight_bike * student)
//					+ (biking_habit_weight_bike * biking_habit)
					+ (male_weight_bike * male)
					+ (female_weight_bike * female)
					+ (age_weight_bike * age)					
					+ (trip_dist_weight_bike_age_sex[agesexgroup] * (trip_distance/1000));
	write "drivingutility" + driving_utility;
	if((trip_distance/1000) <= threshold_dist_walk_age_sex[agesexgroup]){
		if(car_owner = 1){
			modalchoice <- ["car", "walk", "bike"] at ([driving_utility, walking_utility, biking_utility] index_of  max([driving_utility, walking_utility, biking_utility]));	
		}
		else{
			modalchoice <- ["walk", "bike"] at ([walking_utility, biking_utility] index_of  max([walking_utility, biking_utility]));			
		}
	}
	else{
		if(car_owner = 1){
			modalchoice <- ["car","bike"] at ([driving_utility, biking_utility] index_of  max([driving_utility, biking_utility]));	
			}
		else{
			modalchoice <- "bike";	
			}				
		}			
		write string(trip_distance) + " " + modalchoice ;
   }
	reflex routing when:  new_route = 1  {
		  activity <- "traveling";
		  new_route <- 0;
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
		activity_NO2 <- (sum((AirPollution overlapping self) collect each.NO2)) * inhalation_rate["normal"] * AirPollution_Filter["indoor"];
		activity_Noise <- (sum((Noise_day overlapping self) collect each.Decibel)) * Noise_Filter["indoor"];
		hourly_NO2 <- hourly_NO2 + activity_NO2;
		hourly_Noise <- hourly_Noise + activity_Noise;
	}
	
    reflex traveling when: activity = "traveling"{
		do follow path: self.track_path speed: travelspeed[modalchoice];
		if((self.location = self.destination_activity.location)){
			self.location <- destination_activity.location;
//			write "arrived";
			activity <- "perform_activity";
    		activity_NO2 <- (sum((AirPollution overlapping self.track_geometry) collect each.NO2)/( length(AirPollution overlapping self.track_geometry) + 1)) * inhalation_rate[modalchoice] * track_duration * AirPollution_Filter[modalchoice];
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
    	hourly_NO2 <- 0.0;
    }
    reflex acute_exposure_impacts when: current_date.hour = 0{	
    	daily_NO2 <- 0.0;
//		daily_PM2_5
//		daily_Noise
    }
    reflex chronic_exposure_impacts when: current_date.year > year{
//    	yearly_PM10
//		yearly_PM2_5
// 		yearly_Noise
    }
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
    	}
    	
    }
}




experiment TransportAirPollutionExposureModel type: gui {
	/** Insert here the definition of the input and output of the model */
	parameter "Number of human agents" var: nb_humans min: 10 max: 10000  category: "Human attributes";
	parameter "Share of adult car owners" var: per_car_owners min: 0.0 max: 1.0 category: "Human attributes";	
//	parameter "Visualize Air Pollution Field" var:display_air_poll among: [true, false] type:bool;
	
	output {
		layout horizontal([1::6000,0::4000]) tabs: false;
	
    	display stats type: java2D synchronized: true {
        	overlay position: {0, 0} size: {1, 0.05} background: #black  border: #black {
    	  	  		draw "Model Time: " + current_date color: #white font: font("SansSerif", 17) at: {40#px, 30#px};
				}
  	      chart "Transport Mode distribution" type: histogram background: #black color: #white axes: #white size: {0.5,0.5} position: {0.5, 0.5} label_font: font("SansSerif", 12){
 		       	data "walk" value: Humans count (each.modalchoice = "walk" and each.activity = "traveling") color:#green;
	        	data "bike" value: Humans count (each.modalchoice = "bike" and each.activity = "traveling") color:#blue;
   		     	data "car" value: Humans count (each.modalchoice = "car" and each.activity = "traveling") color:#fuchsia;
   		     	data "not travelling" value: Humans count (each.activity = "perform_activity") color:#yellow;
     	   }
			chart "Mean Noise Exposure" type: scatter x_label: (string(int(step/60))) + " Minute Steps"  y_label: "Decibel" background: #black color: #white axes: #white size: {0.5,0.45} position: {0, 0.05} label_font: font("SansSerif", 12){
					data "Noise exposure" value: mean(Humans collect each.activity_Noise) color: #red marker: false style: line;
			}
			chart "Mean NO2 Exposure" type: scatter x_label: (string(int(step/60))) + " Minute Steps" y_label: "µg" background: #black color: #white axes: #white size: {0.5,0.45} position: {0.5, 0.05} label_font: font("SansSerif", 12){
					data "NO2 exposure" value: mean(Humans collect each.activity_NO2) color: #red marker: false style: line;
			}
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
//     	  	grid Environment_stressors elevation: (AirPoll_PM2_5 * 20.0) grayscale: true triangulation: true transparency: 0.7;
//			graphics Noise transparency: 0.7{
//			if(current_date.hour < 4 or current_date.hour > 22){
//				draw shape_file_NoiseContour_night color: #purple ;
//			}
//			else{
//				draw shape_file_NoiseContour_day color: #purple ;				
//			}
//			}
//			species AirPollution aspect: airpoll_aspect transparency: 0.7;
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




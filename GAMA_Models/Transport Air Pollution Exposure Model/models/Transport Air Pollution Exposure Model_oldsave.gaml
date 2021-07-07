/**
* Name: TransportAirPollutionExposureModel
* Author: Tabea Sonnenschein
* Tags: 
*/

model TransportAirPollutionExposureModel
  
global skills: [RSkill]{
	/** Insert the global definitions, variables and actions here */
	
//	loading the spatial built environment
	file shape_file_buildings <- file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Built Environment/Buildings/Buildings_RDNew.shp");
	file shape_file_buildings2 <- file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Built Environment/Buildings/Diemen_Buildings.shp");
	file shape_file_buildings3 <- file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Built Environment/Buildings/Oude Amstel_buildings.shp");
    file shape_file_streets <- file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Built Environment/Transport Infrastructure/cars/Car Traffic_RDNew.shp");
    file shape_file_greenspace <- file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Built Environment/Green Spaces/Green Spaces_RDNew.shp");
    file shape_file_Residences <- file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Built Environment/Buildings/Residences_neighcode_RDNew.shp");    
    file shape_file_Schools <- file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/Amsterdam_schools_RDNew.shp");
    file shape_file_Supermarkets <- file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/Amsterdam_supermarkets_RDNew.shp");
    file shape_file_Universities <- file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/Amsterdam_universities_RDNew.shp");
    file shape_file_Kindergardens <- file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/Amsterdam_kindergardens_RDNew.shp");
    file shape_file_Restaurants <- file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Foursquare/Amsterdam_Foursquarevenues_Food_RDNew.shp");
    file shape_file_Entertainment <- file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Foursquare/Amsterdam_Foursquarevenues_ArtsEntertainment_RDNew.shp");
    file shape_file_ShopsnServ <- file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Foursquare/Amsterdam_Foursquarevenues_ShopsServ_RDNew.shp");
    file shape_file_Nightlife <- file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Foursquare/Amsterdam_Foursquarevenues_Nightlife_RDNew.shp");
    file shape_file_Profess <- file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Foursquare/Amsterdam_Foursquarevenues_Profess_other_RDNew.shp");
    file spatial_extent <- file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Amsterdam Diemen Oude Amstel Extent.shp");  
   	geometry shape <- envelope(spatial_extent); 
   	map<string,rgb> color_per_type <- ["streets"::#aqua, "vegetation":: #green, "buildings":: #red];
    
//  loading routing code
    file Rcode_foot_routing <- text_file("C:/Users/Tabea/Documents/GitHub/Spatial-Agent-based-Modeling-of-Urban-Health-Interventions/OSRM_foot.R");
    file Rcode_car_routing <- text_file("C:/Users/Tabea/Documents/GitHub/Spatial-Agent-based-Modeling-of-Urban-Health-Interventions/OSRM_car.R");
    file Rcode_bike_routing <- text_file("C:/Users/Tabea/Documents/GitHub/Spatial-Agent-based-Modeling-of-Urban-Health-Interventions/OSRM_bike.R");
    
//    file shape_file_streetnodes <- file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Built Environment/Transport Infrastructure/cars/Street_Nodes_Amsterdam_RDNew.shp");
//    csv_file OD_Matrix_file <- csv_file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Built Environment/Transport Infrastructure/cars/OD_Matrix_Amsterdam_GAMA4.csv", ',', '"', string);
//    matrix OD_Matrix <- matrix(OD_Matrix_file);
//    list<int> OD_columns <- column_at(OD_Matrix, 0);

//  loading agent population attributes
    int nb_humans <- 100;
//    csv_file Synth_Agent_file <- csv_file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Population/Agent_pop.csv", ",", string, true, {12, 100});
    csv_file Synth_Agent_file <- csv_file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Population/Agent_pop_100.csv", ",", string, true);
	text_file schedules_file <- text_file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Harmonised European Time Use Survey - Eurostat/mock_schedule.txt");

    init {
        write "setting up the model";
//        create StreetNodes from: shape_file_streetnodes with: [Node_ID :: read('Node_ID')];
		create Homes from: shape_file_Residences with: [Neighborhood:: read('nghb_cd')];
        create Humans from: Synth_Agent_file with:[Agent_ID :: read('Agent_ID'), Neighborhood :: read('neighb_code'), 
	        age:: int(read('age')), sex :: read('sex'), migrationbackground :: read('migrationbackground'),
	        hh_single :: int(read('hh_single')), is_child:: int(read('is_child')), has_child:: int(read('has_child')), 
        	current_edu:: read('current_education'), absolved_edu:: read('absolved_education'), BMI:: read('BMI')]; // careful: column 1 is has the index 0 in GAMA
    }
    float step <- 10 #mn;
    date starting_date <- date("2019-01-01", 'yyyy-MM-dd');
    int year;
}

//species StreetNodes {
//	string Node_ID;
//}

species Homes{
	string Neighborhood;
}


species Humans skills:[moving, RSkill]{
	 // definition of attributes, actions, behaviors	
	 /// individual characteristics
	string Agent_ID;
	int Agent_index;
	string Neighborhood;
	int age;
	string sex;
	string migrationbackground;
	int hh_single;
	int is_child;
	int has_child;
	string current_edu;
	string absolved_edu;
	string BMI;
	
	/// destination locations
	geometry residence;
	geometry workplace;
	geometry school;
	geometry university;
	geometry kindergarden;
	geometry supermarket;
	
	/// saved routes (for efficiency)
	path homeTOwork;
	path homeTOuni;
	path homeTOschool;
	
	/// activity variables
	string activity;
	list<string> schedule;
	/// weekday and weekend schedule
	string current_activity;
	string former_activity;
	geometry destination_activity;
	
	/// travel variables
	path track_path;
	string modalchoice;
	float travelspeed;
	int path_memory;

//	int Home_Node;
//	int Home_OD_position;
//	int Destination_Node;
//	int Destination_OD_position;
//	string route_str;
//	list route;
//	int trip_int <- 0;
	
	float bike_exposure;
	float car_exposure;
	float walk_exposure;
	float daiy_PM10;
	float yearly_PM10;
	float daily_PM2_5;
	float yearly_PM2_5;
	float daily_Noise;
	float yearly_Noise;
	init{
		  schedule <- list(schedules_file);

		  residence <- one_of(Homes where (each.Neighborhood = self.Neighborhood)) ;
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
       	  if(schedule contains "kindergarden"){
				supermarket <-  closest_to(shape_file_Supermarkets, self.location) ;
       	  }       	     	
       	  activity <- "perform_activity";
       	  
       	  /// routing through OSRM via R interface
       	  do startR;
//       	  destination_activity <- workplace;		
//		  write R_eval("origin = " + to_R_data(container(residence.location CRS_transform("EPSG:4326"))));
//		  write R_eval("destination = " + to_R_data(container(destination_activity.location CRS_transform("EPSG:4326"))));	
//		  loop s over: Rcode_bike_routing.contents{
//				unknown a <- R_eval(s);
//			}
//		  list<point> track <- list(R_eval("track_points"));
//		  geometry track_geometry <- (to_GAMA_CRS(line(track),  "EPSG:4326")) add_point(destination_activity.location);
//		  track_path <-  path(track_geometry);     	  
//		  float track_duration <- float(list(R_eval("route$duration"))[0]);
//		  float track_length <- float(list(R_eval("route$distance"))[0]);	
//		  travelspeed <- 3.33; /// meters per seconds 40km/h 			
		  
//       	  /// routing through OD Matrix
//       	  Home_Node <- int(Node_ID of (StreetNodes closest_to(self.location)));
//       	  Destination_Node <- int(Node_ID of one_of(StreetNodes where (each.location != self.location)));
//       	  Home_OD_position <- OD_columns index_of int(self.Home_Node);
//       	  Destination_OD_position <- OD_columns index_of int(self.Destination_Node);
//       	  write 'Home_Node: '+ Home_Node + ' postion ' + Home_OD_position + '; and Destination_Node: '+ Destination_Node+ ' postion ' + Destination_OD_position ;
//       	  route_str <- OD_Matrix[(Home_OD_position + 1),Destination_OD_position];
//       	  loop while: (route_str = ""){
//       	  	 Destination_Node <- int(Node_ID of one_of(StreetNodes where (each.location != self.location)));
//       	  	 Destination_OD_position <- OD_columns index_of int(self.Destination_Node);
//       	  	 route_str <- OD_Matrix[Home_OD_position,Destination_OD_position];
//       	  }
//       	  route <- list(route_str);
//       	  write route;

//       	  modalchoice <- "bike";
//       	  current_activity <- schedule[0];
       	  
	}
	reflex schedule_manager when: ((current_date.minute mod 10) = 0) {
		 current_activity <- schedule[int((current_date.minute/10) + (current_date.hour * 6))];
		 if(int((current_date.minute/10)) != 0){
		 	former_activity <- schedule[int(((current_date.minute/10) + (current_date.hour * 6))-1)];
		 }
		 else{
		 	former_activity <- "sleeping";
		 }
		 if(current_activity != former_activity){
		 	if(current_activity = "work"){
				destination_activity <- workplace;
				if(homeTOwork != nil and self.location = residence.location){
					track_path <- homeTOwork;
					path_memory <- 1;
				}		 		
		 	}
		 	else if(current_activity = "school"){
		 		destination_activity <- school;
		 		if(homeTOschool != nil and self.location = residence.location){
					track_path <- homeTOwork;
					path_memory <- 1;
				}		
		 	}
		 	else if(current_activity = "university"){
		 		destination_activity <- university;
		 		if(homeTOuni != nil and self.location = residence.location){
					track_path <- homeTOwork;
					path_memory <- 1;
				}		
		 	}
		 	else if(current_activity = "groceries_shopping"){
		 		destination_activity <- supermarket;
		 	}
		 	else if(current_activity = "kindergarden"){
		 		destination_activity <- kindergarden;
		 	}
		 	else if(current_activity = "sleeping" or current_activity = "at_Home"){
		 		destination_activity <- self.residence;
		 	}
		 	else if(current_activity = "entertainment" ){
		 		destination_activity <- one_of(shape_file_Entertainment);
		 	}
		 	if(destination_activity.location != self.location){
		 		activity <- "commuting";
		 		if(path_memory != 1){
		 			write R_eval("origin = " + to_R_data(container(self.location CRS_transform("EPSG:4326"))));
		 			write R_eval("destination = " + to_R_data(container(destination_activity.location CRS_transform("EPSG:4326"))));	
		 			if((self.location distance_to destination_activity) < 1000){
		 				modalchoice <- "walk";
		 				loop s over: Rcode_foot_routing.contents{
							unknown a <- R_eval(s);
						}
						travelspeed <- 1.4; /// meters per seconds 5km/h
		 			}
		 			else if((self.location distance_to destination_activity) < 3000){
		 		 		modalchoice <- "bike";
		 		 		loop s over: Rcode_bike_routing.contents{
							unknown a <- R_eval(s);
						}
						travelspeed <- 3.33; /// meters per seconds 12km/h
		 			}
		 			else{
		 			 	modalchoice <- "car";		
		 			 	loop s over: Rcode_car_routing.contents{
							unknown a <- R_eval(s);
						}
						travelspeed <- 11.11; /// meters per seconds 40km/h 			
		 			}
		 			list<point> track <- list(R_eval("track_points"));
		 			geometry track_geometry <- (to_GAMA_CRS(line(track),  "EPSG:4326")) add_point(destination_activity.location);
					track_path <-  path(track_geometry);     	  
					float track_duration <- float(list(R_eval("route$duration"))[0]);
					float track_length <- float(list(R_eval("route$distance"))[0]);	
					if(current_activity = "work" and self.location = residence.location){
						homeTOwork <- track_path;
					}
					else if(current_activity = "school" and self.location = residence.location){
						homeTOschool <- track_path;
					}
					else if(current_activity = "university" and self.location = residence.location){
						homeTOuni <- track_path;
					}
		 		}
		 		path_memory <- 0;
		 	}
		 	else{
		 		activity <-"perform_activity";
		 	}
		 }
	}
	reflex perception{
		
	}
	reflex sleeping when: activity = "perform_activity" and current_activity = "sleeping"{
		write "sleeping";
	}
    reflex commuting when: activity = "commuting"{
//    	location <- StreetNodes where (each.Node_ID = self.route[(self.trip_int + 1)]);
////    	track <- line_of_travel
////		traveltime <- time of travel
//    	self.trip_int <- self.trip_int + 1;
//    	if((self.trip_int + 1) >= length(self.route)){

		do follow path: self.track_path speed: travelspeed;
		if(self.location = destination_activity.location){
    		activity <- "perform_activity";
    		if(modalchoice = "bike"){
    			bike_exposure <- bike_exposure + 0;
    		}
    		 else if(modalchoice = "walk"){
    			walk_exposure <- walk_exposure + 0;
    		}
    	}
    }
    reflex acute_exposure_impacts when: current_date.hour = 0{
//    	daily_PM10
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
    	else if(activity = "commuting"){
    		if(modalchoice = "bike"){
    			draw sphere(40) color: #blue;
    			
    		}
    		else if(modalchoice =  "walk"){
    			draw sphere(40) color: #green;
    			
    		}
    		else{
    			draw sphere(40) color: #red;
    		}
    	}
    	
    }
}


//grid Environment_stressors cell_width: 3 cell_height: 2 {
//	float AirPoll_PM2_5;
//	float AirPoll_PM10;
//	float AirPoll_NO2;
//	float AirPoll_O3;
//	float Noise_Decibel;


//}


experiment TransportAirPollutionExposureModel type: gui {
	/** Insert here the definition of the input and output of the model */
	parameter "Number of human agents" var: nb_humans min: 10 max: 10000 category: "Human attributes" ;
	
	output {
	layout #split;
    display map type:opengl {
    	graphics background{
    		draw shape color: #black;
    	}
        graphics Buildings{
    		draw shape_file_buildings color: #red;
    		draw shape_file_buildings2 color: #red;
    		draw shape_file_buildings3 color: #red;
		}
		graphics Streets{
    		draw shape_file_streets color: #aqua;
		}
		graphics GreenSpace{
    		draw shape_file_greenspace color: #green;
		}
        species Humans aspect: base ;
        
        overlay position: { 5, 5 } size: { 180 #px, 100 #px } background: # black transparency: 0.5 border: #black rounded: true
            {
            	//for each possible type, we draw a square with the corresponding color and we write the name of the type
                float y <- 30#px;
                loop type over: color_per_type.keys
                {
                    draw square(10#px) at: { 20#px, y } color: color_per_type[type] border: #white;
                    draw type at: { 40#px, y + 4#px } color: # white font: font("SansSerif", 18, #bold);
                    y <- y + 25#px;
                }

            }
        
    }
    display stats type: opengl{
//		chart " my_chart " type: histogram {
//			datalist ( distribution_of ( Humans collect each.age , 20 ,0 ,100) at " legend ") 
//				value: ( distribution_of ( Humans collect each.age, 20 ,0 ,100) at " values ");
//		}
		chart "Age Distribution" type: histogram background: #white size: {0.5,0.5} position: {0, 0}{
				datalist legend: Humans collect each.age  value: Humans collect each.age;
		}
		
		chart "Agent Age Distribution" type: histogram background: #white size: {0.5,0.5} position: {0, 0.5} {
				data "0-10 years old" value: Humans count (each.age <= 10) color:#blue;
				data "11-20 years old" value: Humans count ((each.age > 10) and (each.age <= 20)) color:#blue;
				data "21-30 years old" value: Humans count ((each.age > 20) and (each.age <= 30)) color:#blue;
				data "31-40 years old" value: Humans count ((each.age > 30) and (each.age <= 40)) color:#blue;
				data "41-50 years old" value: Humans count ((each.age > 40) and (each.age <= 50)) color:#blue;
				data "51-60 years old" value: Humans count ((each.age > 50) and (each.age <= 60)) color:#blue;
				data "61-70 years old" value: Humans count ((each.age > 60) and (each.age <= 70)) color:#blue;
				data "71-80 years old" value: Humans count ((each.age > 70) and (each.age <= 80)) color:#blue;
				data "81 or older" value: Humans count (each.age > 81) color:#blue;
			}
		chart "Agent Sex Distribution" type: histogram background: #white size: {0.5,0.5} position: {0.5, 0.5} {
				data "male" value: Humans count (each.sex = "male") color:#red;
				data "female" value: Humans count (each.sex = "female") color:#red;
			}
			
  	 }
  	 	monitor "time" value: current_date;
  	 	monitor "activity" value: schedules_file[int((current_date.minute/10) + (current_date.hour * 6))];
  	 	monitor "Number of bikers" value: Humans count (each.modalchoice = "bike" and each.activity = "commuting");
  	 	monitor "Number of pedestrians" value: Humans count (each.modalchoice = "walk" and each.activity = "commuting");
  	 	monitor "Number of drivers" value: Humans count (each.modalchoice = "car" and each.activity = "commuting");
  	 	
    }
}




/**
* Name: TransportAirPollutionExposureModel
* Author: Tabea Sonnenschein
* Tags: 
*/

model TransportAirPollutionExposureModel
  
global {
	/** Insert the global definitions, variables and actions here */
	
//	loading the spatial built environment
	file shape_file_buildings <- file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Built Environment/Buildings/Buildings_RDNew.shp");
	file shape_file_buildings2 <- file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Built Environment/Buildings/Diemen_Buildings.shp");
	file shape_file_buildings3 <- file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Built Environment/Buildings/Oude Amstel_buildings.shp");
    file shape_file_streetnodes <- file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Built Environment/Transport Infrastructure/cars/Street_Nodes_Amsterdam_RDNew.shp");
    file shape_file_streets <- file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Built Environment/Transport Infrastructure/cars/Car Traffic_RDNew.shp");
    file shape_file_greenspace <- file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Built Environment/Green Spaces/Green Spaces_RDNew.shp");
    file shape_file_Residences <- file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Built Environment/Buildings/Residences_neighcode_RDNew.shp");
    file shape_file_Schools <- file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/Amsterdam_schools_RDNew.shp");
    file shape_file_Supermarkets <- file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/Amsterdam_supermarkets_RDNew.shp");
    file shape_file_Universities <- file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/Amsterdam_universities_RDNew.shp");
    file shape_file_Kindergardens <- file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Built Environment/Facilities/Amsterdam_kindergardens_RDNew.shp");
    file shape_file_Restaurants <- file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Foursquare/Amsterdam_Foursquarevenues_Food_RDNew.shp");
    file spatial_extent <- file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Amsterdam Diemen Oude Amstel Extent.shp");
    
    
   	geometry shape <- envelope(spatial_extent); 
    
    csv_file OD_Matrix_file <- csv_file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Built Environment/Transport Infrastructure/cars/OD_Matrix_Amsterdam_GAMA4.csv", ',', '"', string);
    matrix OD_Matrix <- matrix(OD_Matrix_file);
    list<int> OD_columns <- column_at(OD_Matrix, 0);
    int nb_humans <- 100;
//    csv_file Synth_Agent_file <- csv_file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Population/Agent_pop.csv", ",", string, true, {12, 100});
    csv_file Synth_Agent_file <- csv_file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Population/Agent_pop_100.csv", ",", string, true);
    init {
        create StreetNodes from: shape_file_streetnodes with: [Node_ID :: read('Node_ID')];
		create Homes from: shape_file_Residences with: [Neighborhood:: read('nghb_cd')];
        create Humans from: Synth_Agent_file with:[Agent_ID :: read('Agent_ID'), Neighborhood :: read('neighb_code'), 
	        age:: int(read('age')), sex :: read('sex'), migrationbackground :: read('migrationbackground'),
	        hh_single :: int(read('hh_single')), is_child:: int(read('is_child')), has_child:: int(read('has_child')), 
        	current_edu:: read('current_education'), absolved_edu:: read('absolved_education'), BMI:: read('BMI')]; // careful: column 1 is has the index 0 in GAMA
    }
    float step <- 10 #mn;
    int year;
}


species StreetNodes {
	string Node_ID;
}

species Homes{
	string Neighborhood;
}


species Humans skills:[moving]{
	 // definition of attributes, actions, behaviors	
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
	geometry residence;
	int Home_Node;
	int Home_OD_position;
	int Destination_Node;
	int Destination_OD_position;
	string route_str;
	list route;
	string activity;
	int trip_int <- 0;
	list schedule;
	string current_activity;
	geometry destination_activity;
	string modalchoice;
	float bike_exposure;
	float car_exposure;
	float walk_exposure;
	geometry track;
	float daiy_PM10;
	float yearly_PM10;
	float daily_PM2_5;
	float yearly_PM2_5;
	float daily_Noise;
	float yearly_Noise;
	init{
		  residence <- one_of(Homes where (each.Neighborhood = self.Neighborhood)) ;
       	  location <- residence.location;
       	  Home_Node <- int(Node_ID of (StreetNodes closest_to(self.location)));
       	  Destination_Node <- int(Node_ID of one_of(StreetNodes where (each.location != self.location)));
       	  Home_OD_position <- OD_columns index_of int(self.Home_Node);
       	  Destination_OD_position <- OD_columns index_of int(self.Destination_Node);
       	  write 'Home_Node: '+ Home_Node + ' postion ' + Home_OD_position + '; and Destination_Node: '+ Destination_Node+ ' postion ' + Destination_OD_position ;
       	  route_str <- OD_Matrix[(Home_OD_position + 1),Destination_OD_position];
       	  loop while: (route_str = ""){
       	  	 Destination_Node <- int(Node_ID of one_of(StreetNodes where (each.location != self.location)));
       	  	 Destination_OD_position <- OD_columns index_of int(self.Destination_Node);
       	  	 route_str <- OD_Matrix[Home_OD_position,Destination_OD_position];
       	  }
       	  route <- list(route_str);
       	  write route;
       	  activity <- "commuting";
//       	  current_activity <- schedule[0];
       	  
	}
	reflex update when: length(schedule) != 0 {
		 current_activity <- schedule[int(step)];
		 if(current_activity != schedule[(int(step)-1)]){
		 	if(current_activity = "work"){
				destination_activity <- one_of(shape_file_Residences);		 		
		 	}
		 	else if(current_activity = "school"){
		 		destination_activity <- closest_to(shape_file_Schools, self.location);
		 	}
		 	else if(current_activity = "university"){
		 		destination_activity <- closest_to(shape_file_Universities, self.location);
		 	}
		 	else if(current_activity = "groceries_shopping"){
		 		destination_activity <- closest_to(shape_file_Supermarkets, self.location);
		 	}
		 	else if(current_activity = "kindergarden"){
		 		destination_activity <- closest_to(shape_file_Kindergardens, self.location);
		 	}
		 	else if(current_activity = "sleeping" or current_activity = "at_Home"){
		 		destination_activity <- self.residence;
		 	}
		 	if(destination_activity != self.location){
		 		activity <- "commuting";
		 		if((self.location distance_to destination_activity) < 500){
		 			modalchoice <- "walk";
		 		}
		 		else if((self.location distance_to destination_activity) < 1500){
		 		 	modalchoice <- "bike";
		 		}
		 		else{
		 		 	modalchoice <- "car";		 			
		 		}
		 	}
		 	else{
		 		activity <-"perform_activity";
		 	}
		 }
	}
	reflex perception{
		
	}
	reflex sleeping when: current_date.hour = 23{
		write "sleeping";
	}
    reflex commuting when: activity = "commuting"{
    	location <- StreetNodes where (each.Node_ID = self.route[(self.trip_int + 1)]);
//    	track <- line_of_travel
//		traveltime <- time of travel
    	self.trip_int <- self.trip_int + 1;
    	if((self.trip_int + 1) >= length(self.route)){
    		activity <- "perform_activity";
    		if(modalchoice = "bike"){
    			bike_exposure <- bike_exposure + 0;
    		}
    		 else if(modalchoice = "walk"){
    			walk_exposure <- 0;
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
    draw sphere(30) color: #yellow;
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
    }
    display stats type: opengl{
		chart " my_chart " type: histogram {
			datalist ( distribution_of ( Humans collect each.age , 20 ,0 ,100) at " legend ") 
				value: ( distribution_of ( Humans collect each.age, 20 ,0 ,100) at " values ");
		}
  	 }
    }
}




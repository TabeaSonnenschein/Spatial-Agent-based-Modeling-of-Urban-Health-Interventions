/**
* Name: TransportAirPollutionExposureModel
* Author: Tabea Sonnenschein
* Tags: 
*/

model TransportAirPollutionExposureModel
  
global {
	/** Insert the global definitions, variables and actions here */
	file shape_file_buildings <- file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Built Environment/Buildings/Buildings_RDNew.shp");
	file shape_file_buildings2 <- file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Built Environment/Buildings/Diemen_Buildings.shp");
	file shape_file_buildings3 <- file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Built Environment/Buildings/Oude Amstel_buildings.shp");
    file shape_file_streetnodes <- file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Built Environment/Transport Infrastructure/cars/Street_Nodes_Amsterdam_RDNew.shp");
    file shape_file_streets <- file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Built Environment/Transport Infrastructure/cars/Car Traffic_RDNew.shp");
    file shape_file_greenspace <- file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Built Environment/Green Spaces/Green Spaces_RDNew.shp");
    file shape_file_Residences <- file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Built Environment/Buildings/Residences_neighcode_RDNew.shp");
//    csv_file OD_Matrix_file <- csv_file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Built Environment/Transport Infrastructure/cars/OD_matrix_columns.csv", ",", string, true);
    csv_file OD_Matrix_file <- csv_file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Built Environment/Transport Infrastructure/cars/OD_Matrix_Amsterdam_GAMA4.csv", ',', '"', string);
    matrix OD_Matrix <- matrix(OD_Matrix_file);
    list<int> OD_columns <- column_at(OD_Matrix, 0);
    geometry shape <- envelope(shape_file_Residences); 
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
	init{
		  residence <- one_of(Homes where (each.Neighborhood = self.Neighborhood)) ;
       	  location <- residence.location;
       	  Home_Node <- Node_ID of (StreetNodes closest_to(self.location));
       	  Destination_Node <- int(Node_ID of one_of(StreetNodes where (each.location != self.location)));
       	  Home_OD_position <- OD_columns index_of int(self.Home_Node);
       	  Destination_OD_position <- OD_columns index_of int(self.Destination_Node);
       	  write 'Home_Node: '+ Home_Node + ' postion ' + Home_OD_position + '; and Destination_Node: '+ Destination_Node+ ' postion ' + Destination_OD_position ;
       	  route_str <- OD_Matrix[(Home_OD_position + 1),Destination_OD_position];
       	  loop while: (route_str = ""){
       	  	 Destination_Node <- Node_ID of one_of(StreetNodes where (each.location != self.location));
       	  	 Destination_OD_position <- OD_columns index_of int(self.Destination_Node);
       	  	 route_str <- OD_Matrix[Home_OD_position,Destination_OD_position];
       	  }
       	  route <- list(route_str);
       	  write route;
       	  activity <- "commuting";
       	  
	}
//	image_file human_icon <- image_file("../includes/images/human_icon.png") ;
	reflex sleeping when: current_date.hour = 23{
		write "sleeping";
	}
    reflex time_to_work when: current_date.hour = 7 {
//    the_target <- any_location_in (working_place);
    }
    reflex commuting when: activity = "commuting"{
    	location <- StreetNodes where (each.Node_ID = self.route[(self.trip_int + 1)]);
    	self.trip_int <- self.trip_int + 1;
    	if((self.trip_int + 1) >= length(self.route)){
    		activity <- "at work";
    	}
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
//    display stats type: opengl{
//		chart " my_chart " type: histogram {
//			datalist ( distribution_of ( Humans collect each.age ,20 ,0 ,100) at " legend ") 
//				value: ( distribution_of ( Humans collect each.age,20 ,0 ,100) at " values ");
//		}
//  	 }
    }
}




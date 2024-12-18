/**
* Name: NewModel
* Based on the internal empty template. 
* Author: Tabea
* Tags: 
*/



model testingModel
  
global{
	/** Insert the global definitions, variables and actions here */
	
	string path_data <- "C:/Users/Tabea/Documents/PhD EXPANSE/Data/Tutorial on ABM for EXPOSOME Science/Data/";
	file shape_file_Residences <- shape_file(path_data+"Residences_neighcode_RDNew.shp");    
	file spatial_extent <- shape_file(path_data+"Amsterdam Diemen Oude Amstel Extent.shp");  
   	geometry shape <- envelope(spatial_extent); 
	file shape_NO2 <- shape_file(path_data + "AmsterdamNO2.shp");
	
	csv_file Synth_Agent_file <- csv_file(path_data + "Agent_pop_subset_3.csv", ";", string, true);
	
	init{
		create Homes from: shape_file_Residences with: [Neighborhood:: read('nghb_cd')];
		create AirPoll from: shape_NO2 with:[NO2:: read('nlbeluxde2')];
		create Humans from: Synth_Agent_file with:[Agent_ID :: read('agent_ID'), Neighborhood :: read('neighb_code')]; 
	}
//	grid PM2 file: PM2_5_raster;
}
species Homes{
	string Neighborhood;
}

species AirPoll{
	float NO2;
}

species Humans skills:[moving] parallel: true{
	string Agent_ID;
	string Neighborhood;
	geometry residence;
	geometry destination_activity;
	geometry route_eucl_line;
	geometry route_contour;
	list<geometry> route_segments;
	list<float> route_segment_lengths;
	reflex traveling {
		destination_activity <- one_of(Homes);
		route_eucl_line <- line(container(point(self.location), point(destination_activity.location)));
		write "Euclid: " + route_eucl_line;
		route_contour <- union(remove_duplicates((AirPoll overlapping self.route_eucl_line) collect each.shape.contour));
//		route_segments <- split_lines((line(route_eucl_line) + polyline(route_contour)));
		route_segments <- split_lines([route_eucl_line , route_contour]) where((self.route_eucl_line  overlaps each) and not(self.route_eucl_line partially_overlaps each));
		write "SPLIT LINES: " +  route_segments;
		route_segment_lengths <- self.route_segments collect each.perimeter;
		write "ROUTE LENGTH: " + route_segment_lengths;
		write "Nr segments: " + length(route_segment_lengths) + ", overlapping cells: " + length(AirPoll overlapping self.route_eucl_line);
			
	}
}


experiment test type: gui {
	/** Insert here the definition of the input and output of the model *
	 */
	 
}

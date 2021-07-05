/**
* Name: workingandtestingfile
* Based on the internal empty template. 
* Author: Tabea
* Tags: 
*/


model workingandtestingfile

/* Insert your model definition here */
global skills: [RSkill]{
	file spatial_extent <- file("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Amsterdam Diemen Oude Amstel Extent.shp");
   	geometry shape <- envelope(spatial_extent); 
	path  track_path;
	float track_duration;
	float track_length;
	file Rcode_routing <- text_file("C:/Users/Tabea/Documents/GitHub/Spatial-Agent-based-Modeling-of-Urban-Health-Interventions/OSRM_bike.R");
	init {
		do startR;
		list<float> orig <- [4.83, 52.36]; 
		write R_eval("origin = " + to_R_data(orig));
		list<float> dest <- [5.2, 53.26]; 
		write R_eval("destination = " + to_R_data(dest));	
	    loop s over: Rcode_routing.contents{
			unknown a <- R_eval(s);
			write "R>"+s;
			write a;
		}
		  list track <- rows_list(matrix(R_eval("track")));
		  write track;
		  geometry track_line <- line(point(track));
		  track_path <- path(track);
		  float track_duration <- list(R_eval("route$duration"))[0];
		  float track_length <- list(R_eval("route$distance"))[0];
		  write track_duration;
		  write track_length;
		  
	}

}



experiment workingandtestingfile type:gui {
	output{
			display map type:opengl {
		 		graphics track_map{
    				draw track_path color: #red;
    	}
		}
	}
}
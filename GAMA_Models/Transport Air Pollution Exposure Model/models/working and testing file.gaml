/**
* Name: workingandtestingfile
* Based on the internal empty template. 
* Author: Tabea
* Tags: 
*/


model workingandtestingfile

/* Insert your model definition here */
global{
	geometry trip;
	file result;
//	file Rscript <- text_file("C:/Users/Tabea/Documents/GitHub/Spatial-Agent-based-Modeling-of-Urban-Health-Interventions/OSRM - routing.txt");
	init {
//		do startR;
	    result <- R_file("C:/Users/Tabea/Documents/GitHub/Spatial-Agent-based-Modeling-of-Urban-Health-Interventions/OSRM - routing.R");
	    trip <- result.contents;
	}

}



experiment workingandtestingfile type:gui {
	output{
			display map type:opengl {
		 		graphics trip_map{
    				draw trip color: #red;
    	}
		}
	}
}
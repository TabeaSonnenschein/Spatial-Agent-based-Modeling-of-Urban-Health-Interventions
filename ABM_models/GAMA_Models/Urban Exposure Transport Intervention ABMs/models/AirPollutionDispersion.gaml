/**
* Name: AirPollutionDispersion
* Based on the internal empty template. 
* Author: Tabea
* Tags: 
*/


model AirPollutionDispersion

/* Insert your model definition here */
global {
	string path_data <- "C:/Users/Tabea/Documents/PhD EXPANSE/Data/";
    //  loading grid with airpollution determinants
    file baselineNO2raster <- grid_file(path_data+"Amsterdam/Air Pollution Determinants/baselineNO2.tif");
//    file airpoll_determ_raster <- grid_file(path_data+"Amsterdam/Air Pollution Determinants/AirPollDeterm_grid.tif");
//    csv_file airpoll_baseline <- csv_file(path_data+"Amsterdam/Air Pollution Determinants/DispersionModel_baselineNO2.csv", ",", string); 
	csv_file airpoll_offroadmeasures <- csv_file(path_data+"Amsterdam/Air Pollution Determinants/DispersionModel_OffroadMeasures_rowcol.csv", ";", string); 
    csv_file airpoll_onroadpred <- csv_file(path_data+"Amsterdam/Air Pollution Determinants/DispersionModel_OnRoadPredictions_rowcol.csv", ";", string); 

	grid AirPollution file: baselineNO2raster{
		int ON_ROAD <- 0;
		int Has_measurement <-0;
		list NO2_hourly;
		list NO2_measured;
		float NO2<-2;
		float N02_dispersed <- 6;
//		float baseline_NO2;
		int indx;
		rgb color <- rgb(0,0,0,0.0);
	}
	
//	list<int>  baseline_NO2_list <- columns_list(matrix(airpoll_baseline)) at 0;
	matrix onroad_matrix <- matrix(airpoll_onroadpred);
	matrix offroad_matrix <- matrix(airpoll_offroadmeasures);
	list<list<int>> int_id_airpoll_onroad <- columns_list(onroad_matrix) at 0;
	list<list<int>> int_id_airpoll_offroad <- columns_list(offroad_matrix) at 0;
	
	
	init{
		write "Adding data to raster";
		write onroad_matrix;
		write int_id_airpoll_onroad;
		write columns_list(offroad_matrix) at 1;
		  ask AirPollution{
//		  	baseline_NO2 <- baseline_NO2_list at (int(self.grid_value)-1);
		  	N02_dispersed <- self.grid_value;
			if(int_id_airpoll_onroad contains_value  [0,self.grid_y, self.grid_x, 0]){
				indx <- index_of(int_id_airpoll_onroad , [0,self.grid_y, self.grid_x, 0]);
				write indx;
				ON_ROAD <- 1;
				NO2_hourly <- rows_list(onroad_matrix) at indx;
				remove index: 0 from: NO2_hourly;
				NO2 <- NO2_hourly at current_date.hour;
				color <- rgb(int((NO2/7)*30),0,0,(0.4 + NO2/100));
				N02_dispersed <- NO2;
			}
			else if (int_id_airpoll_offroad contains_value [0,self.grid_y, self.grid_x, 0]){
				indx <- index_of(int_id_airpoll_offroad , [0,self.grid_y, self.grid_x, 0]);
				Has_measurement <- 1;
				NO2_measured <- rows_list(offroad_matrix) at indx;
				remove index: 0 from: NO2_measured;
			}
    	}
    	write "having added data";
	}
	reflex AirPollDispersion when: current_date.minute = 0  {
		write "AirPoll Dispersion";		
		diffuse var: N02_dispersed cycle_length:5 on: AirPollution proportion: 0.99 radius: 4;
		ask AirPollution where (each.ON_ROAD = 0){
			NO2 <- N02_dispersed;
			color <- rgb(int((NO2/7)*30),0,0,(0.4 + NO2/100));
			N02_dispersed <- 6;
		}
	}
	
}

experiment AirPollutionDispersion type: gui {
	output {
		layout horizontal([1::6000,0::4000]) tabs: false;
	
    	display stats type: java2D synchronized: true {
        	overlay position: {0, 0} size: {1, 0.05} background: #black  border: #black {
    	  	  		draw "Model Time: " + current_date color: #white font: font("SansSerif", 17) at: {40#px, 30#px};
				}
		}
  	    display map type:opengl {
   		 	graphics background refresh: false{
    			draw shape color: #black;
    		}
			grid AirPollution;
   		 }
    }
}




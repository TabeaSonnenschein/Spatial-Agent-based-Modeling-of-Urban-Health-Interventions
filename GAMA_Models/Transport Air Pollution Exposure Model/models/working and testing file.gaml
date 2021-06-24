/**
* Name: workingandtestingfile
* Based on the internal empty template. 
* Author: Tabea
* Tags: 
*/


model workingandtestingfile

/* Insert your model definition here */
global{
	    result <- R_compute_param("C:/YourPath/Mean.R", X);
        write result at 0;
}

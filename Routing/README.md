### THE INSTRUCTIONS COVER:

#### (1) [SETTING UP A LOCAL INSTANCE OF OSRM](https://github.com/TabeaSonnenschein/Spatial-Agent-based-Modeling-of-Urban-Health-Interventions/tree/main/Routing#setting-up-a-local-instance-of-osrm)

#### (2) [STARTING MULTIPLE OSRM SERVERS AFTER HAVING PREPARED DATASETS (MANUALLY OR WITH A BATCH FILE)](https://github.com/TabeaSonnenschein/Spatial-Agent-based-Modeling-of-Urban-Health-Interventions/tree/main/Routing#starting-multiple-servers-after-having-prepared-datasets-needed-every-time-when-using-osrm)

#### (3) [AUTOMATICALLY LETTING THE BATCH FILE TO START THE SERVERS RUN WHEN STARTING GAMA (WITH TASK SCHEDULER)](https://github.com/TabeaSonnenschein/Spatial-Agent-based-Modeling-of-Urban-Health-Interventions/tree/main/Routing#automatically-running-the-batch-file-when-starting-gama)

================================================
# SETTING UP A LOCAL INSTANCE OF OSRM
================================================

Date: 03-07-2021
Author: Tabea Sonnenschein

Instructions for Windows OS:
1.	Clone the repository https://github.com/Project-OSRM/osrm-backend.git to a local folder

2.	Download the OSM data for the region/city for which the routing system should be generated via Geofabrik (e.g. for Amsterdam  Nord-Holland-latest.osm.pbf)

Either click on http://download.geofabrik.de/europe/netherlands/noord-holland-latest.osm.pbf

Or use

wget http://download.geofabrik.de/europe/netherlands/noord-holland-latest.osm.pbf

3.	Save the data in the folder of the local GitHub repository osrm-backend

4.	Copy the OSM data and rename it adding a “_”+ transport_mode, for each mode of transport that should be routed
e.g. one called noord-holland-latest_car.osm.pbf, one called noord-holland-latest_bike.osm.pbf and one called noord-holland-latest_foot.osm.pbf

We need the different names to distinguish the modes of transport for the routing.

5.	(Optional): Download more up to date routing profiles here: https://github.com/fossgis-routing-server/cbf-routing-profiles 
Bike.lua; foot.lua; car.lua and copy them into the osrm-backend/profiles folder. Accept to replace the previous lua files.

6.	Open Command Prompt (cmd) and set the directory to the directory of the GitHub repository osrm-backend
e.g. cd C:\Users\Tabea\Documents\GitHub\osrm-backend
7.	Extract the Road Network using osm-extract for each mode of transport. Here is where OSRM distinguishes for two different routing optimization methods: 
1) Multi-Level Dijkstra (MLD) and 2) Contraction Hierarchies (CH). See here for more information: https://github.com/Project-OSRM/osrm-backend/wiki/Running-OSRM

If you want to use MLD, type in CMD:
1.	osrm-extract  “name of the osm.pbf file”  -p profiles/”name of mode of transport”.lua
2.	osrm-partition  “name of the .osrm file” (this file is the result of step 1.)
3.	osrm-customize “name of the .osrm file” (this file is the result of step 1.)
4.	osrm-routed --algorithm=MLD --threads=1 --port=5000 “name of the .osrm file” (this file is the result of step 1.)


e.g. for the car routing 1. Would be: osrm-extract  noord-holland-latest_car.osm.pbf -p profiles/car.lua; then 2. Would be osrm-partition noord-holland-latest_car.osrm

We want to give each mode of transport a different port. Thus, you can give port 5001 and 5002 to the different modes of transport.
	If you want to use CH, type in CMD
1.	osrm-extract  “name of the osm.pbf file”  -p profiles/”name of mode of transport”.lua
2.	osrm-contract “name of the .osrm file” (this file is the result of step 1.)
3.	osrm-routed --threads=1 --port=5000 “name of the .osrm file” (this file is the result of step 1.)

8.	Use the R scripts OSRM_car.R; OSRM_bike., ect. Of the GitHub repository to access the local OSRM instance and link it to GAMA, for example.
Example server name to be used in R: http://127.0.0.1:5000/


Scripts (to be adjusted and copied):
### CREATING LOCAL INSTANCE BY PREPARING DATASETS AND OSRM FILES (only one time needed)

## Multi-Level Dijkstra (MLD) which best fits use-cases where query performance still needs to be very good; and live-updates to the data need to be made e.g. for regular Traffic updates
cd C:\Users\Tabea\Documents\GitHub\osrm-backend
osrm-extract  noord-holland-latest_car.osm.pbf -p profiles/car.lua
osrm-extract  noord-holland-latest_bike.osm.pbf -p profiles/bicycle.lua
osrm-extract  noord-holland-latest_foot.osm.pbf -p profiles/foot.lua

osrm-partition noord-holland-latest_car.osrm
osrm-partition noord-holland-latest_bike.osrm
osrm-partition noord-holland-latest_foot.osrm

osrm-customize noord-holland-latest_car.osrm
osrm-customize noord-holland-latest_bike.osrm
osrm-customize noord-holland-latest_foot.osrm

osrm-routed --algorithm=MLD --threads=1 --port=5000 noord-holland-latest_car.osrm
osrm-routed --algorithm=MLD --threads=1 --port=5001 noord-holland-latest_bike.osrm
osrm-routed --algorithm=MLD --threads=1 --port=5002 noord-holland-latest_foot.osrm

## Contraction Hierarchies (CH) which best fits use-cases where query performance is key, especially for large distance matrices
cd C:\Users\Tabea\Documents\GitHub\osrm-backend
osrm-extract  noord-holland-latest_car.osm.pbf -p profiles/car.lua
osrm-extract  noord-holland-latest_bike.osm.pbf -p profiles/bicycle.lua
osrm-extract  noord-holland-latest_foot.osm.pbf -p profiles/foot.lua

osrm- contract noord-holland-latest_car.osrm
osrm- contract noord-holland-latest_bike.osrm
osrm- contract noord-holland-latest_foot.osrm

osrm-routed --threads=1 --port=5000 noord-holland-latest_car.osrm
osrm-routed --threads=1 --port=5001 noord-holland-latest_bike.osrm
osrm-routed --threads=1 --port=5002 noord-holland-latest_foot.osrm

==========================================================
# STARTING MULTIPLE SERVERS AFTER HAVING PREPARED DATASETS (needed every time when using OSRM)
==========================================================

There are multiple ways to do this. 
(1) One can paste these commands in three different Command Prompts.  Handy software for managing multiple CMP’s: https://conemu.github.io/index.html

1.	
cd C:\Users\Tabea\Documents\GitHub\osrm-backend
osrm-routed --algorithm=MLD --threads=1 --port=5000 noord-holland-latest_car.osrm

2.	
cd C:\Users\Tabea\Documents\GitHub\osrm-backend
osrm-routed --algorithm=MLD --threads=1 --port=5001 noord-holland-latest_bike.osrm

3.	
cd C:\Users\Tabea\Documents\GitHub\osrm-backend
osrm-routed --algorithm=MLD --threads=1 --port=5002 noord-holland-latest_foot.osrm

or (2) one can create a batch file which starts the three servers on different command prompts. One example batch file can be found on GitHub (filename: start_OSRM_Servers.bat). 
It is the most elegant way to do it. You need to change the directory of your OSRM backend  folder and potentially the name of the prepared osrm files.
The script looks as follows:

start cmd /c "cd C:\Users\Tabea\Documents\GitHub\osrm-backend & osrm-routed --algorithm=MLD --threads=1 --port=5000 noord-holland-latest_car.osrm  & pause"
start cmd /c "cd C:\Users\Tabea\Documents\GitHub\osrm-backend & osrm-routed --algorithm=MLD --threads=1 --port=5001 noord-holland-latest_bike.osrm & pause"
start cmd /c "cd C:\Users\Tabea\Documents\GitHub\osrm-backend & osrm-routed --algorithm=MLD --threads=1 --port=5002 noord-holland-latest_foot.osrm & pause"


==================================================
# AUTOMATICALLY RUNNING THE BATCH FILE WHEN STARTING GAMA
==================================================

Having the batch file for starting the OSRM servers, it is now possible to start this batch file automatically every time when GAMA is started
1.	Run secpol.msc and navigate to Advanced Audit... => System Audit... => Detailed Tracking. Enable "Audit Process Creation" for "Success". This will add a Process Creation event (ID 4688) to the Security log whenever a new process is created. Close secpol.msc.
2.	Open Task Scheduler: Open Start and Search for Task Scheduler and click the top result to open the app.
3.	Right-click the "Task Scheduler Library" branch and select the New Folder option.
4.	Confirm a name for the folder — for example, MyScripts.
5.	Expand the "Task Scheduler Library" branch and Right-click the MyScripts folder.
6.	Click on “Create a New Task”
7.	Give the script a name (e.g.): StartOSRMServerBatchfileWhenOpeningGAMA
8.	Click on Triggers and New…
9.	Click on the drop down menu for Begin the task: and click on “On and event”
10.	In the Settings click on Costum and then New Event Filter
11.	In the XML tab paste 

	<QueryList>
		<Query Id="0" Path="Security">
			<Select Path="Security">*[System[Provider[@Name='Microsoft-Windows-Security-Auditing'] and EventID=4688] and EventData[Data[@Name='NewProcessName']='C:\Users\Tabea\Documents\GAMA\Gama.exe']]</Select>
		</Query>
	</QueryList>
	
Modify this with the actual path of the executable of your GAMA.
12.	Click on OK and OK to close the Trigger Window
13.	Then click on the Actions Tab > New…
14.	With the new window, click on Action: Start a Program
15.	Then browse the script of your batch file.
16.	Click on OK and OK to close the new Task that was scheduled.
17.	Try opening GAMA and see if it works.


### FURTHER DOCUMENTATION AND LINKS 
* https://github.com/Project-OSRM/osrm-backend/wiki/Running-OSRM
* https://www.r-bloggers.com/2017/09/building-a-local-osrm-instance/
* https://github.com/Project-OSRM/osrm-backend/wiki
* https://github.com/fossgis-routing-server/cbf-routing-profiles


* https://www.windowscentral.com/how-create-and-run-batch-file-windows-10
* https://forums.tomsguide.com/threads/open-batch-file-when-a-specific-program-starts.180965/


There you go! :stars: :rainbow: :rocket:
☜(ﾟヮﾟ☜)
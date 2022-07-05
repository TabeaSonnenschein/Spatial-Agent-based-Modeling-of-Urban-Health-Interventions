# Spatial-Agent-based-Modeling-of-Urban-Health-Interventions
by Tabea Sonnenschein

All the work done for this repository is part of the EXPANSE project: http://expanseproject.eu/, and embodies a core part of my PhD work.


The GitHub repository contains a set of methods and models.

1) the folder **GenSynthPop** contains a fully documented R-package to generate a representative, spatial synthetic agent population combining neighborhood marginal distributions and stratified distributions. This encompasses functions for data preparation and harmonization, for calculating conditional propensities and populating the agent dataframe according to the propensities and neighborhood marginal distributions, and finally, to validate that the resulting agent dataframe distributions correspond to the neighborhood and stratified distributions.

2) the folder **Routing** contains complete instructions of setting up a local instance of the Open Source Routing Machine (OSRM) and scripts that can be used to access the routing machine from GAMA.

3) the folder **Environmental Spatial Layers** contains a set of scripts to (1)fetch point of interest data from Foursquare, (2)extract relevant data on the location of destinations from OSM, (3)fetch and process weather data, (4)extract all vector polygons that have Green space related keys of OSM, and more.

4) the folder **NLP Knowledge Extraction and Synthesis** contains a sequence of scripts and documentation to automatically extract knowledge on significant variable from scientific articles using NLP and deep learning. The extracted knowledge is further synthesized and used to populate an ontology. It is a proof of concept method as a first step to attemp structural model validation.

5) the folder **GAMA_Models** contains simulation scripts for agent based models of urban health interventions. For now it contains a transport intervention simulation of Amsterdam.
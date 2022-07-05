## **Instructions for R-package: GenSynthPop**
#### *Author: Tabea Sonnenschein, Utrecht University*

This package contains a set of functions that help prepare stratified census datasets to generate conditional propensities, combines the conditional propensities with spatial marginal distributions to generate a representative population and validates that the produced agents have a similar distribution as the initial spatial marginal datasets and the stratified datasets. The generated population is  representative for a city or the spatial extent that is fed into the algorithms and can be used for simulation purposes, such as an agent-based model. The smaller the spatial units of the spatial marginal distributions, the more spatially resolved the agents will be too.

### Overview of functions

#### *For Data Preparation*
* **crosstabular_to_singleside_df:** Crosstabular Stratified Table to Single Sided Variable Combination - Counts Table
* **restructure_one_var_marginal:** Restructures a single-sided stratified dataframe so that the classes of one column/variable of interest are seperate columns

#### *For Initiating the Agent Dataframe*
* **gen_agent_df:** Generating an agent dataframe of the population size and assigning a unique ID
* **distr_agent_neigh_age_group:** Populating the agent_df with age_group and neigh_ID attributes distributed like a given neighborhood marginal distribution

#### *For Conditional Propensity calculation*
* **calc_propens_agents:** Calculating the conditional propensity to have an attribute based on conditional variables
* **strat_prop_from_sep_cond_var:** Creates a stratified propensity table from separate conditional variable joint distributions

#### *For Attribute Assignment based on conditional and marginal distributions*
* **distr_attr_strat_neigh_stats_binary:** Distributing attributes across agent population based on conditional proabilities and neighborhood totals for binary attributes
* **distr_attr_strat_neigh_stats_3plus:** Distributing attributes across agent population based on conditional proabilities and neighborhood totals for attributes with 3 or more classes
* **distr_attr_cond_prop:** Assigning Attributes purely based on conditional probabilities

#### *For Validation*
* **crossvalid:** Cross validation with the neighborhood and stratified marginal distributions


### Installing package in R
	install.packages("devtools")
	library(devtools)
	install_github("TabeaSonnenschein/Spatial-Agent-based-Modeling-of-Urban-Health-Interventions/GenSynthPop")
	library(GenSynthPop)

### Looking up documentation for a function
#### There is extensive documentation for the functions within R

Example:

	?crosstabular_to_singleside_df
	help(crosstabular_to_singleside_df)

Should there be remaining questions, shoot me an email: t.s.sonnenschein@uu.nl

### Instructions

1. Start by collecting neighborhood marginal distributions of age_groups. It is recommended to go as spatially resolved as you can (smallest spatial unit) but it depends on what you want to use the synthetic agent population for. You theoretically can even use provincial or national administrative areas, if this is your project scope and goal. We go for neighborhoods because we want to  create an urban ABM.

2. apply **gen_agent_df** for the sum of all age groups in all neighborhoods. This will be the population size.

3. use this new agent_df and the neighborhood marginal distribution dataframe in the **distr_agent_neigh_age_group** code to distribute the agents across neighborhoods and age groups.

4. 

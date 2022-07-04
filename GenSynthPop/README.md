## **Instructions for R-package: GenSynthPop**
#### *Author: Tabea Sonnenschein, Utrecht University*

This package contains a set of functions that help prepare stratified census datasets to generate conditional propensities, combines the conditional propensities with spatial marginal distributions to generate a representative population and validates that the produced agents have a similar distribution as the initial spatial marginal datasets and the stratified datasets. The generated population is  representative for a city or the spatial extent that is fed into the algorithms and can be used for simulation purposes, such as an agent-based model. The smaller the spatial units of the spatial marginal distributions, the more spatially resolved the agents will be too.

### Overview of functions

###### For Data Preparation
* **crosstabular_to_singleside_df:** Crosstabular Stratified Table to Single Sided Variable Combination - Counts Table
* **restructure_one_var_marginal:** Restructures a single-sided stratified dataframe so that the classes of one column/variable of interest are seperate columns

###### For Initiating the Agent Dataframe
* **gen_agent_df:** Generating an agent dataframe of the population size and assigning a unique ID

###### For Conditional Propensity calculation
* **calc_propens_agents:** Calculating the conditional propensity to have an attribute based on conditional variables
* **strat_prop_from_sep_cond_var:** Creates a stratified propensity table from separate conditional variable joint distributions

###### For Attribute Assignment based on conditional and marginal distributions
* **distr_attr_cond_prop:** Assigning Attributes purely based on conditional probabilities
* **distr_attr_strat_n_neigh_stats_3plus:** Distributing attributes across agent population based on conditional proabilities and neighborhood totals for attributes with 3 or more classes
* **distr_bin_attr_strat_n_neigh_stats:** Distributing attributes across agent population based on conditional proabilities and neighborhood totals for binary attributes

###### For Validation
* **crossvalid:** Cross validation with the neighborhood and stratified marginal distributions



### Instructions
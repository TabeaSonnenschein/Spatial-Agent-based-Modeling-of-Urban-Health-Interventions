## **Instructions for R-package: GenSynthPop**
#### *Author: Tabea Sonnenschein, Utrecht University*

This package contains a set of functions that help prepare stratified census datasets to generate conditional propensities, combines the conditional propensities with spatial marginal distributions to generate a representative population and validates that the produced agents have a similar distribution as the initial spatial marginal datasets and the stratified datasets. The generated population is  representative for a city or the spatial extent that is fed into the algorithms and can be used for simulation purposes, such as an agent-based model. The smaller the spatial units of the spatial marginal distributions, the more spatially resolved the agents will be too.

### Overview of functions
* calc_propens_agents
* crosstabular_to_singleside_df
* crossvalid
* distr_attr_cond_prop
* distr_attr_strat_n_neigh_stats_3plus
* distr_bin_attr_strat_n_neigh_stats
* gen_agent_df
* restructure_one_var_marginal
* strat_prop_from_sep_cond_var
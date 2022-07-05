install.packages("devtools")
library(devtools)
install_github("TabeaSonnenschein/Spatial-Agent-based-Modeling-of-Urban-Health-Interventions/GenSynthPop")
library(GenSynthPop)

# set the directory to your data folder for the population data
setwd()

# read the neighborhood marginal distributions across age_groups
neigh_df = read.csv()
colnames(neigh_df) # identify the columnnames corresponding to the age groups

# we generate the agent_df dataframe
agent_df = gen_agent_df(sum(neigh_df[, c("A1", "A2", "A3")]))

# we distribute the agents across the age groups and neighborhoods
agent_df = distr_agent_neigh_age_group(neigh_df = neigh_df, agent_df = agent_df, neigh_id = "neigh_ID", age_colnames = c("A1", "A2", "A3"))
print(agent_df)


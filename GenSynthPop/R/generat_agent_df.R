
####### Generating an agent dataframe of the population size and assigning a unique ID

#' @title Generating an agent dataframe of the population size and assigning a unique ID
#' @description The function creates a new agent dataframe of an indicated population size to start the building of the synthetic agent population.  Each row in the dataframe represents an individual and is assigned a unique ID. This is basically the agent dataframe scelaton that will be iteratively extended with attribute data based on conditional and marginal distributions of demographics.
#' @param pop_size The size of the population for the are for which a synthetic agent population should be created.
#'
#' @return Returns a new dataframe of len(pop_size) with unique agent_ids.
#' @export
#'
#' @examples
gen_agent_df = function(pop_size){
  agent_ID = paste("Agent_",1:pop_size, sep="")
  agent_df = as.data.frame(agent_ID)
  return(agent_df)
}

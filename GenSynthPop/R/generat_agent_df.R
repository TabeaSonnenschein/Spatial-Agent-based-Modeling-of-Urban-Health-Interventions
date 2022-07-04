
####### Generating an agent dataframe of the population size and assigning a unique ID

#' @title Generating an agent dataframe of the population size and assigning a unique ID
#' @description The function creates a new agent dataframe of an indicated population size to start the building of the synthetic agent population.  Each row in the dataframe represents an individual and is assigned a unique ID. This is basically the agent dataframe scelaton that will be iteratively extended with attribute data based on conditional and marginal distributions of demographics.
#' @param pop_size The size of the population for the are for which a synthetic agent population should be created.
#'
#' @return Returns a new dataframe of len(pop_size) with unique agent_ids.
#' @export
#' @details
#' # Example output table
#' | agent_ID |
#' |:---:|
#' | Agent_1 |
#' | Agent_2 |
#' | Agent_3 |
#' | Agent_4 |
#' | Agent_5 |
#' | Agent_6 |
#' (...)
#'
#' ### continues until population size. It is just the initiation of the agent_df, as a scelaton to be filled with representative attributes.
#' @md
#' @examples
#' ## Let us say we want to initiate a synthetic population of Amsterdam,
#' ## which has a population size of 910 146 as of 2022
#'
#' agent_df = gen_agent_df(910146)
#' print(agent_df)
#'
#' ## Because sometimes the sum of total census counts differs to the official overall city population count,
#' ## it makes sense to use the sum of the population of the first attribute you will add (for example age).
#'
gen_agent_df = function(pop_size){
  agent_ID = paste("Agent_",1:pop_size, sep="")
  agent_df = as.data.frame(agent_ID)
  return(agent_df)
}

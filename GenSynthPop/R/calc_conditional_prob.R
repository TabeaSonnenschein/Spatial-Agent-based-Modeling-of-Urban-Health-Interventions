
####### Calculating the conditional probabilities to have an attribute

### EXPLANATION
# This is a function to calculate the probability/propensity to have a specific class of a variable conditional on other variables.
# It requires a stratified dataframe (@dataframe) which includes all combinations of the conditional variables (the ones based on which we want to calculate the propensity), 
# the number of people with the variable class (@variable) for which we want to calculate the propensity, 
# and the total number of people within the combination of conditional variables (@total_population).
# The function calculates the propensity to have a specific class based on the conditional variables, 
# by dividing the number of people with the class if interest by the total number of people within the combination of conditional variables.
# Further, the function joins these probabilities with the agent dataset (@agent_df) 
# based on the list of conditional variables (@list_conditional_var).
# This requires the variable/column names of the conditional variables to be equal for the stratified and the agent dataframe.
# Finally, it shuffles the agent dataset to avoid biases due to a non random order in the next steps.

calc_propens_agents = function(dataframe, variable, total_population, agent_df, list_conditional_var){
  if(!missing(total_population)){
    dataframe[,c(paste("prop_",variable, sep = ""))] = dataframe[,c(variable)]/dataframe[, c(total_population)]
  }
  order_agent_df = colnames(agent_df)
  if(paste("prop_",variable, sep = "") %in% order_agent_df){
    x = which(order_agent_df == paste("prop_",variable, sep = ""))
    agent_df = subset(agent_df, select = -c(x))
  }
  agent_df = merge(agent_df, dataframe[,c(list_conditional_var, paste("prop_",variable, sep = ""))], all.x = T, all.y= F, by = list_conditional_var)
  agent_df = agent_df[,c(order_agent_df, paste("prop_",variable, sep = ""))]
  random_seq = sample(nrow(agent_df))
  agent_df = agent_df[random_seq,]
  return(agent_df)
}


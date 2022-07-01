
####### distributing attributes across agent population based on conditional proabilities and neighborhood totals 

### EXPLANATION
# This function distributes attribute classes in the agent population based on the conditional propensities and the neighborhood statistics
# agent_df = Dataframe of the unique agents with their attributes
# neigh_df = Dataframe of aggregate statistical data per neighborhood, specifically the total population 
# per neighborhood and the counts per variable class.
# variable = the new variable that we want to add based on the stratified and neighborhood marginal distributions
# list_var_classes_neigh_df = a list of the column names in the Neighborhood dataset with 
# the classes of the variable that will be modeled (e.g. c("Men", "Women", "Non-Binary"), which are the classes of sex). 
# list_agent_propens = A list of the columns in the agent dataset that contain the propensities for the classes of the variable based on the other agents conditional attributes.
# This list has to be in the same order as the list_var_classes_neigh_df, but can leave out the last propensity as it is 1 minus the other propensities.
# The list_class_names is optional and contains the values that the new created agent variable should have for the different variable classes.
# It has to be in the same order and of the same length as the list_var_classes_neigh_df. If left empty, the list_var_classes_neigh_df will become the default values for the classes.
# agent_exclude = an optional variable containing one or multiple variable names of the agent dataset on which basis agents should be excluded from the attribute assignment
# if that variable(s) is/are 1, then the agents will be excluded

## distr_bin_attr_strat_n_neigh_stats is for binary attributes

distr_bin_attr_strat_n_neigh_stats = function(agent_df, neigh_df, neigh_ID, variable, list_var_classes_neigh_df, list_agent_propens, list_class_names, agent_exclude){
  print(Sys.time())
  agent_df[, c(variable, "random_scores")] = 0
  if(missing(list_class_names)){
    list_class_names = list_var_classes_neigh_df
  }
  if(!missing(agent_exclude)){
    agent_df[, c("excluded")] = 0
    for(i in 1:length(agent_exclude)){
      agent_df[which(agent_df[, c(agent_exclude[i])] == 1) , c("excluded")] =  1
    }
  }
  for (i in 1:nrow(neigh_df)){
    if(!missing(agent_exclude)){
      x = which(agent_df[, c(neigh_ID)] == neigh_df[i, c(neigh_ID)] & agent_df[, c("excluded")] != 1)
    }
    else{
      x = which(agent_df[, c(neigh_ID)] == neigh_df[i, c(neigh_ID)])
    }
    tot__var_class_neigh = neigh_df[i, list_var_classes_neigh_df]
    agent_df[x, c("random_scores")] = sample(x= seq(from= 0, to = 1, by= 0.01), size = length(x), replace = T)
    fitness = 0
    if(length(x) != 0){
      while(fitness == 0){
        if(length(list_var_classes_neigh_df)== 2){
          agent_df[x[which(agent_df[x, c(list_agent_propens[1])] >= agent_df[x,c("random_scores")])], c(variable)] = list_class_names[1]
          agent_df[x[which(agent_df[x, c(list_agent_propens[1])] < agent_df[x,c("random_scores")])], c(variable)] = list_class_names[2]
          if(length(which(agent_df[x, c(variable)] == list_class_names[1])) >= tot__var_class_neigh[1] & length(which(agent_df[x, c(variable)] == list_class_names[2])) >= tot__var_class_neigh[2]){
            fitness = 1
          }
          else if(sum(tot__var_class_neigh) <= length(x)){
            agent_df[x, c("random_scores")] = sample(x= seq(from= 0, to = 1, by= 0.01), size = length(x), replace = T)
            agent_df[x[which(agent_df[x, c(list_agent_propens[1])] >= agent_df[x,c("random_scores")])], c(variable)] = list_class_names[1]
            agent_df[x[which(agent_df[x, c(list_agent_propens[1])] < agent_df[x,c("random_scores")])], c(variable)] = list_class_names[2]
            if(length(which(agent_df[x, c(variable)] == list_class_names[1])) >= tot__var_class_neigh[1] & length(which(agent_df[x, c(variable)] == list_class_names[2])) >= tot__var_class_neigh[2]){
              fitness = 1
            }
            else if(length(which(agent_df[x, c(variable)] == list_class_names[1])) < tot__var_class_neigh[1]){
              abs_diff = as.integer(as.numeric(tot__var_class_neigh[1]) - length(which(agent_df[x, c(variable)] == list_class_names[1])))
              if(abs_diff <= 1|is.na(abs_diff)){
                fitness = 1
              }
              else{
                class = which(agent_df[x, c(variable)] == list_class_names[2])[1:as.numeric(abs_diff)]
                class = class[!is.na(class)]
                if(length(class) == 0){
                  fitness = 1
                }
                agent_df[x[class], c(list_agent_propens[1])] = agent_df[x[class], c(list_agent_propens[1])] + 0.5
              }
            }
            else if(length(which(agent_df[x, c(variable)] == list_class_names[2])) < tot__var_class_neigh[2]){
              abs_diff = as.integer(as.numeric(tot__var_class_neigh[2]) - length(which(agent_df[x, c(variable)] == list_class_names[2])))
              if(abs_diff <= 1|is.na(abs_diff)){
                fitness = 1
              }
              else{
                class = which(agent_df[x, c(variable)] == list_class_names[1])[1:as.numeric(abs_diff)]
                class = class[!is.na(class)]
                if(length(class) == 0){
                  fitness = 1
                }
                agent_df[x[class], c(list_agent_propens[1])] = agent_df[x[class], c(list_agent_propens[1])] - 0.5
              }
            }
          }
          else if(length(x) < 10){
            fitness = 1
          }
          else if(sum(tot__var_class_neigh) > length(x)){
            percent_diff1 = length(which(agent_df[x, c(variable)] == list_class_names[1]))/as.numeric(tot__var_class_neigh[1])
            percent_diff2 = length(which(agent_df[x, c(variable)] == list_class_names[2]))/as.numeric(tot__var_class_neigh[2])
            percent_diff_diff = percent_diff1 - percent_diff2
            if(abs(percent_diff_diff) < 0.02|is.na(percent_diff_diff)){
              fitness = 1
            }
            else{
              if( percent_diff_diff < 0){
                abs_diff = as.integer((((as.numeric(abs(percent_diff_diff)))/2) * as.numeric(tot__var_class_neigh[1]))/3)
                if(abs_diff <= 1|is.na(abs_diff)){
                  fitness = 1
                }
                else{
                  class = which(agent_df[x, c(variable)] == list_class_names[2])[1:abs_diff]
                  class = class[!is.na(class)]
                  if(length(class) == 0){
                    fitness = 1
                  }
                  agent_df[x[class], c(list_agent_propens[1])] = agent_df[x[class], c(list_agent_propens[1])] + 0.3
                }
              }
              else{
                abs_diff = as.integer((((as.numeric(abs(percent_diff_diff)))/2) * as.numeric(tot__var_class_neigh[2]))/3)
                if(abs_diff <= 1|is.na(abs_diff)){
                  fitness = 1
                }
                else{
                  class = which(agent_df[x, c(variable)] == list_class_names[1])[1:abs_diff]
                  class = class[!is.na(class)]
                  if(length(class) == 0){
                    fitness = 1
                  }
                  agent_df[x[class], c(list_agent_propens[1])] = agent_df[x[class], c(list_agent_propens[1])] - 0.3
                }
              }
            }
          }
        }
      }
    } 
    print(paste("neighborhood:", i))
  }
  random_seq = sample(nrow(agent_df))
  agent_df = agent_df[random_seq,]
  print(Sys.time())
  return(agent_df)
}

## distr_attr_strat_n_neigh_statsis for attributes with three or more values
distr_attr_strat_n_neigh_stats_3plus = function(agent_df, neigh_df, neigh_ID, variable, list_var_classes_neigh_df, list_agent_propens, list_class_names, agent_exclude){
  print(Sys.time())
  agent_df[, c(variable, "random_scores")] = 0
  if(missing(list_class_names)){
    list_class_names = list_var_classes_neigh_df
  }
  if(!missing(agent_exclude)){
    agent_df[, c("excluded")] = 0
    for(i in 1:length(agent_exclude)){
      agent_df[which(agent_df[, c(agent_exclude[i])] == 1) , c("excluded")] =  1
    }
  }
  lvar = length(list_var_classes_neigh_df)
  for (i in 1:nrow(neigh_df)){
    if(!missing(agent_exclude)){
      x = which(agent_df[, c(neigh_ID)] == neigh_df[i, c(neigh_ID)] & agent_df[, c("excluded")] != 1)
    }
    else{
      x = which(agent_df[, c(neigh_ID)] == neigh_df[i, c(neigh_ID)])
    }
    tot__var_class_neigh = neigh_df[i, list_var_classes_neigh_df]
    agent_df[x, c("random_scores")] = sample(x= seq(from= 0, to = 1, by= 0.01), size = length(x), replace = T)
    fitness = 0
    if(length(x) != 0){
      while(fitness == 0){
        if(lvar > 2){
          agent_df[x[which(agent_df[x, c(list_agent_propens[1])] >= agent_df[x,c("random_scores")])], c(variable)] = list_class_names[1]
          agent_df[x[which(agent_df[x, c(list_agent_propens[1])] < agent_df[x,c("random_scores")] & rowSums(agent_df[x, c(list_agent_propens[1:2])]) >= agent_df[x,c("random_scores")])], c(variable)] = list_class_names[2]
          if(lvar >3){
            for(n in 3:(lvar -1)){
              agent_df[x[which(rowSums(agent_df[x, c(list_agent_propens[1:(n-1)])]) < agent_df[x,c("random_scores")] & rowSums(agent_df[x, c(list_agent_propens[1:n])]) >= agent_df[x,c("random_scores")])], c(variable)] = list_class_names[n]
            }
          }
          agent_df[x[which(rowSums(agent_df[x, c(list_agent_propens[1:(lvar -1)])]) < agent_df[x,c("random_scores")])], c(variable)] = list_class_names[lvar]
          if((length(which(agent_df[x, c(variable)] == list_class_names[1])) >= tot__var_class_neigh[1] & length(which(agent_df[x, c(variable)] == list_class_names[2])) >= tot__var_class_neigh[2] & length(which(agent_df[x, c(variable)] == list_class_names[3])) >= tot__var_class_neigh[3]) | sum(tot__var_class_neigh) == 0 | is.na(sum(tot__var_class_neigh))){
            fitness = 1
          }
          else if(sum(tot__var_class_neigh) <= length(x)){
            agent_df[x, c("random_scores")] = sample(x= seq(from= 0, to = 1, by= 0.01), size = length(x), replace = T)
            agent_df[x[which(agent_df[x, c(list_agent_propens[1])] >= agent_df[x,c("random_scores")])], c(variable)] = list_class_names[1]
            agent_df[x[which(agent_df[x, c(list_agent_propens[1])] < agent_df[x,c("random_scores")] & rowSums(agent_df[x, c(list_agent_propens[1:2])]) >= agent_df[x,c("random_scores")])], c(variable)] = list_class_names[2]
            if(lvar>3){
              for(n in 3:(lvar-1)){
                agent_df[x[which(rowSums(agent_df[x, c(list_agent_propens[1:(n-1)])]) < agent_df[x,c("random_scores")] & rowSums(agent_df[x, c(list_agent_propens[1:n])]) >= agent_df[x,c("random_scores")])], c(variable)] = list_class_names[n]
              }
            }
            agent_df[x[which(rowSums(agent_df[x, c(list_agent_propens[1:(lvar -1)])]) < agent_df[x,c("random_scores")])], c(variable)] = list_class_names[lvar]
            if(length(which(agent_df[x, c(variable)] == list_class_names[1])) >= tot__var_class_neigh[1] & length(which(agent_df[x, c(variable)] == list_class_names[2])) >= tot__var_class_neigh[2] & length(which(agent_df[x, c(variable)] == list_class_names[3])) >= tot__var_class_neigh[3]){
              fitness = 1
            }
            else{
              underrepresented = c()
              for(n in 1:(lvar)){
                if(length(which(agent_df[x, c(variable)] == list_class_names[n])) < tot__var_class_neigh[n]){
                  underrepresented = append(underrepresented, 1)
                }
                else{
                  underrepresented = append(underrepresented, 0)
                }
              }
              for(n in 1:(lvar)){
                if(underrepresented[n] == 1){
                  abs_diff = (tot__var_class_neigh[n] - length(which(agent_df[x, c(variable)] == list_class_names[n])))
                  class = which(agent_df[x, c(variable)] %in% list_class_names[which(underrepresented == 0)])[1:as.numeric(abs_diff)]
                  class = class[!is.na(class)]
                  agent_df[x[class], c(variable)] = list_class_names[n]
                  agent_df[x[class], c(list_agent_propens[n])] = agent_df[x[class], c(list_agent_propens[n])] + 0.5
                  agent_df[x[class], c(list_agent_propens[which(underrepresented == 0)])] = agent_df[x[class], c(list_agent_propens[which(underrepresented == 0)])] - (0.5/length(which(underrepresented == 0)))
                }
              }
              if(length(which(agent_df[x, c(variable)] == list_class_names[1])) >= tot__var_class_neigh[1] & length(which(agent_df[x, c(variable)] == list_class_names[2])) >= tot__var_class_neigh[2] & length(which(agent_df[x, c(variable)] == list_class_names[3])) >= tot__var_class_neigh[3]){
                fitness = 1
              }
            }  
          }
          else if(sum(tot__var_class_neigh) > length(x)){
            percent_diff = c()
            for(n in 1:(lvar)){
              if(tot__var_class_neigh[n] != 0){
                percent_diff = append(percent_diff, length(which(agent_df[x, c(variable)] == list_class_names[n]))/as.numeric(tot__var_class_neigh[n]))
              }
              else{
                percent_diff = append(percent_diff, NA)
              }
            }
            print(percent_diff)
            percent_diff_diff = as.data.frame(matrix(data = NA, nrow = length(list_var_classes_neigh_df), ncol = length(list_var_classes_neigh_df)))
            for(n in 1:(lvar)){
              for(k in 1:(lvar)){
                percent_diff_diff[n, k] = percent_diff[n] - percent_diff[k]
              }
            }
            if(all(abs(na.omit(percent_diff_diff)) < 0.03)){
              fitness = 1
            }
            else{
              tot_abs_diff = c()
              for(n in 1:(lvar)){
                m = which(percent_diff_diff[n,] < (-0.03))
                if(length(m)> 0){
                  abs_diff = as.numeric(((sum(as.numeric(abs(percent_diff_diff[n, m])))/length(m)) * as.numeric(tot__var_class_neigh[n])))
                  tot_abs_diff = append(tot_abs_diff, abs_diff )
                  for(l in m){
                    class = which(agent_df[x, c(variable)] %in% list_class_names[l])[1:as.integer((abs_diff/3)*(as.numeric(tot__var_class_neigh[l])/sum(as.numeric(tot__var_class_neigh[m]))))]
                    class = class[!is.na(class)]
                    agent_df[x[class], c(variable)] = list_class_names[n]
                    agent_df[x[class], c(list_agent_propens[n])] = agent_df[x[class], c(list_agent_propens[n])] + 0.3
                    agent_df[x[class], c(list_agent_propens[m])] = agent_df[x[class], c(list_agent_propens[m])] - (0.3/length(m))
                  }
                }
              }
              if(all(abs(tot_abs_diff) < 3)){
                fitness = 1
              }
              else{
                percent_diff = c()
                for(n in 1:(lvar)){
                  if(tot__var_class_neigh[n] != 0){
                    percent_diff = append(percent_diff, length(which(agent_df[x, c(variable)] == list_class_names[n]))/as.numeric(tot__var_class_neigh[n]))
                  }
                  else{
                    percent_diff = append(percent_diff, NA)
                  }                }
                print(percent_diff)
                percent_diff_diff = as.data.frame(matrix(data = NA, nrow = length(list_var_classes_neigh_df), ncol = length(list_var_classes_neigh_df)))
                for(n in 1:(lvar)){
                  for(k in 1:(lvar)){
                    percent_diff_diff[n, k] = percent_diff[n] - percent_diff[k]
                  }
                }
                if(all(abs(na.omit(percent_diff_diff)) < 0.05)){
                  fitness = 1
                }
                # else{
                #   agent_df[x, c("random_scores")] = sample(x= seq(from= 0, to = 1, by= 0.01), size = length(x), replace = T)
                # } 
              }
            }
          }
        }
        else if(lvar == 2){
          print("use binary attribute function: distr_bin_attr_strat_n_neigh_stats() ")
        }
      }
    } 
    print(paste("neighborhood:", i))
  }
  random_seq = sample(nrow(agent_df))
  agent_df = agent_df[random_seq,]
  print(Sys.time())
  return(agent_df)
}




#### assigning attributes purely based on conditional probabilities

distr_attr_cond_prop = function(agent_df, variable, list_agent_propens, list_class_names, agent_exclude){
  print(Sys.time())
  agent_df[, c(variable, "random_scores")] = 0
  if(!missing(agent_exclude)){
    agent_df[, c("excluded")] = 0
    for(i in 1:length(agent_exclude)){
      agent_df[which(agent_df[, c(agent_exclude[i])] == 1) , c("excluded")] =  1
    }
    x = which(agent_df[, c("excluded")] != 1)
  }
  else{
    x = which(agent_df[, c(variable)] == 0)
  }
  lvar = length(list_class_names)
  agent_df[x, c("random_scores")] = sample(x= seq(from= 0, to = 1, by= 0.01), size = length(x), replace = T)
  if(lvar == 2){
    agent_df[x[which(agent_df[x, c(list_agent_propens[1])] >= agent_df[x,c("random_scores")])], c(variable)] = list_class_names[1]
    agent_df[x[which(agent_df[x, c(list_agent_propens[1])] < agent_df[x,c("random_scores")])], c(variable)] = list_class_names[2]
  }
  else if(lvar > 2){
    agent_df[x[which(agent_df[x, c(list_agent_propens[1])] >= agent_df[x,c("random_scores")])], c(variable)] = list_class_names[1]
    agent_df[x[which(agent_df[x, c(list_agent_propens[1])] < agent_df[x,c("random_scores")] & rowSums(agent_df[x, c(list_agent_propens[1:2])]) >= agent_df[x,c("random_scores")])], c(variable)] = list_class_names[2]
    if(lvar >3){
      for(n in 3:(lvar -1)){
        agent_df[x[which(rowSums(agent_df[x, c(list_agent_propens[1:(n-1)])]) < agent_df[x,c("random_scores")] & rowSums(agent_df[x, c(list_agent_propens[1:n])]) >= agent_df[x,c("random_scores")])], c(variable)] = list_class_names[n]
      }
    }
    agent_df[x[which(rowSums(agent_df[x, c(list_agent_propens[1:(lvar -1)])]) < agent_df[x,c("random_scores")])], c(variable)] = list_class_names[lvar]
  }
  random_seq = sample(nrow(agent_df))
  agent_df = agent_df[random_seq,]
  print(Sys.time())
  return(agent_df)
}



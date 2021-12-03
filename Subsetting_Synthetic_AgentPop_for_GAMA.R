Agent_pop = read.csv(paste("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Population/", filename, sep = ""), header = T)
Agent_pop = Agent_pop[sample(nrow(Agent_pop)),]
Agent_pop = Agent_pop[0:nb_humans,]
write.csv2(Agent_pop, "C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Population/Agent_pop_GAMA.csv", row.names = F ,  quote=FALSE)
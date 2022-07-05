#path_data <- "C:/Users/Marco/Documents/ABM_thesis/Data/"
#path_ODiN_pop <- paste(path_data,"Amsterdam/Calibration/AMS-pop.csv", sep="")
#path_ODiN_sub <- paste(path_data,"Amsterdam/Calibration/Subset_AMS-pop.csv", sep="")
#path_schedule <- paste(path_data,"Amsterdam/Calibration/AMS-schedule_postcodes.csv", sep="")
#path_modal_choices <- paste(path_data,"Amsterdam/Calibration/AMS-modal_choices.csv", sep="")
#nb_humans = 10

Agent_pop = read.csv(path_ODiN_pop, header = T)
Agent_pop = Agent_pop[sample(nrow(Agent_pop)),]
Agent_pop = Agent_pop[0:nb_humans,]

Schedule_pop = read.csv(path_schedule, header = T)
ModalChoices_pop = read.csv(path_modal_choices, header = T)

df = merge(Schedule_pop, Agent_pop, by='agent_ID')
result = merge(ModalChoices_pop, df, by='agent_ID')

write.csv2(result, path_ODiN_sub, row.names = F, quote=FALSE)
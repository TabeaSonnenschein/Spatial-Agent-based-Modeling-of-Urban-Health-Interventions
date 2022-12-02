library(ggplot2)
setwd("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/ModelRuns")
PreInter = read.csv("exposure.csv")
PreInter = PreInter[PreInter$hourly_mean_NO2 != 0,]

PostInter = read.csv("exposure_intervention_scenario.csv")
PostInter = PostInter[PostInter$hourly_mean_NO2 != 0,]

PreInter$sex <- as.factor(PreInter$sex )
ggplot(PreInter, aes(x=sex, y=hourly_mean_NO2)) + 
  geom_violin()+
  stat_summary(fun=mean, geom="point", size=2, color="red")

PreInter$current_date.hour <- as.factor(PreInter$current_date.hour )
ggplot(PreInter, aes(x=current_date.hour, y=hourly_mean_NO2)) + 
  geom_violin() +  
  stat_summary(fun=mean, geom="point", size=2, color="red")

### hourly difference
hours = as.data.frame(0:23)
colnames(hours)= "hours"
hours$mean_pre_inter = 0
hours$mean_post_inter = 0

for(i in hours$hours){
  hours$mean_pre_inter[i+1] = mean(PreInter[which(PreInter$current_date.hour == i), "hourly_mean_NO2"])
  hours$mean_post_inter[i+1] = mean(PostInter[which(PostInter$current_date.hour == i), "hourly_mean_NO2"])
}

hours$Interventiondifference = hours$mean_pre_inter - hours$mean_post_inter
plot( hours$hours , hours$Interventiondifference)


## age difference
setwd("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Population")
agent_df = read.csv("Agent_pop.csv")
PreInter = merge(PreInter, agent_df, all.x = T, all.y = F, by.x = "Agent_ID", by.y = "agent_ID")
PostInter = merge(PostInter, agent_df, all.x = T, all.y = F, by.x = "Agent_ID", by.y = "agent_ID")

PreInter$migrationbackground <- as.factor(PreInter$migrationbackground )
ggplot(PreInter, aes(x=migrationbackground, y=hourly_mean_NO2)) + 
  geom_violin()+
  stat_summary(fun=mean, geom="point", size=2, color="red")


PreInter$age_group_20 <- as.factor(PreInter$age_group_20 )
ggplot(PreInter, aes(x=age_group_20, y=hourly_mean_NO2)) + 
  geom_violin()+
  stat_summary(fun=mean, geom="point", size=2, color="red")



agegroup_analysis = as.data.frame(unique(PreInter$age_group_20)[order(unique(PreInter$age_group_20))])
colnames(agegroup_analysis) = "age_groups"
agegroup_analysis$mean_pre_inter = 0
agegroup_analysis$mean_post_inter = 0

x = 1
for(i in agegroup_analysis$age_groups){
  agegroup_analysis$mean_pre_inter[x] = mean(PreInter[which(PreInter$age_group_20 == i), "hourly_mean_NO2"])
  agegroup_analysis$mean_post_inter[x] = mean(PostInter[which(PostInter$age_group_20 == i), "hourly_mean_NO2"])
  x = x +1
}

agegroup_analysis$Interventiondifference = agegroup_analysis$mean_post_inter  - agegroup_analysis$mean_pre_inter

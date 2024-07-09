import pandas as pd
import os
import numpy as np
import itertools as it

path_data = "D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/"

####################################################################################
### correcting scheduling IDs for children and babies in the synthetic population
####################################################################################
agentfiles = os.listdir(path=path_data + "Population")
agentfiles.remove("Agent_pop_clean.csv")

finaldf = pd.read_csv(path_data+"Population/Agent_pop_clean.csv")
# finaldf["randomnumber"] = np.random.uniform(0,1,len(finaldf))
# # 45% babies in childcare https://www.cbs.nl/en-gb/news/2016/34/dutch-use-childcare-more-than-other-eu-countries#:~:text=In%20the%20Netherlands%2C%2045%20percent,child%2Dminders%20or%20a%20nanny.
# finaldf.loc[(finaldf["age"].between(0,3)) & (finaldf["randomnumber"]>0.45), "SchedID"] = "SchedBaby_0"
# finaldf.loc[(finaldf["age"].between(0,3)) & (finaldf["randomnumber"]<0.45), "SchedID"] = "SchedBaby_1" #with childcare
# finaldf.loc[(finaldf["age"].between(4,9)) & (finaldf["randomnumber"]>0.5), "SchedID"] = "SchedChild_0"
# finaldf.loc[(finaldf["age"].between(4,9)) & (finaldf["randomnumber"]<=0.5), "SchedID"] = "SchedChild_1"
# finaldf.drop(columns=["randomnumber"], inplace=True)
# finaldf.to_csv(path_data+"Population/"+ finaldf, index=False)

for agentfile in agentfiles:
    print(agentfile)
    agentpop = pd.read_csv(path_data+"Population/"+ agentfile)
    agentpop.drop(columns=["randomnumber"], inplace=True)
    agentpop.loc[agentpop["age"].between(0,9), "SchedID"] = [finaldf.loc[finaldf["agent_ID"] ==id, "SchedID"].values[0] for id in agentpop.loc[agentpop["age"].between(0,9),"agent_ID"]]
    agentpop.to_csv(path_data+"Population/"+ agentfile, index=False)
    print(agentpop.loc[agentpop["age"].between(0,9),["agent_ID", "SchedID"]].head(20))

# ############################################################
# ### Schedules for children and babies
# ############################################################
# # children start school at age 4
# # 10min timesteps
# SchedChild_weekday = list(it.chain(*[it.repeat(1, times = ((6*7)+1)), # sleep till 7:10 ( = 7h 10min)
#                 it.repeat(5, times = 6), # at home till 8:10 (1h)
#                 it.repeat(4, times = ((6*3)+5) ), # school 8:10-12:00 (= 3h 50min)
#                 it.repeat(2, times = 3), # eating 12:00-12:30 (= 0.5h)
#                 it.repeat(4, times = ((6*2)+3) ), # school 12:30-15:00 (= 2h 30min)
#                 it.repeat(5, times = (6*5)), # at home 15:00-20:00 (= 5h)
#                 it.repeat(1, times=(6*4)) #sleep from 8pm till 00:00 (=4h)
#                 ]))

# SchedChild_weekdaysocial = list(it.chain(*[it.repeat(1, times = ((6*7)+1)), # sleep till 7:10 ( = 7h 10min)
#                 it.repeat(5, times = 6), # at home till 8:10 (1h)
#                 it.repeat(4, times = ((6*3)+5) ), # school 8:10-12:00 (= 3h 50min)
#                 it.repeat(2, times = 3), # eating 12:00-12:30 (= 0.5h)
#                 it.repeat(4, times = ((6*2)+3) ), # school 12:30-15:00 (= 2h 30min)
#                 it.repeat(5, times = 6), # at home 15:00-16:00 (= 1h)
#                 it.repeat(8, times = (6*2)), # sports/ outdoor activity 16:00-18:00 (= 2h)
#                 it.repeat(5, times = (6*2)), # at home 18:00-20:00 (= 2h)
#                 it.repeat(1, times=(6*4)) #sleep from 8pm till 00:00 (=4h)
#                 ]))

# SchedChild_weekend = list(it.chain(*[it.repeat(1, times = ((6*8)+3)), # sleep till 8:30 ( = 8h 30min)
#                 it.repeat(5, times = 6), # at home till 9:30 (1h)
#                 it.repeat(8, times = (6*2) ), # sports/ outdoor activity 9:30-11:30 (= 2h)
#                 it.repeat(5, times = 3), # at home 11:30-12:00 (= 0.5h)
#                 it.repeat(2, times = 6), # eating 12:00-13:00 (= 1h)
#                 it.repeat(10, times = (6*3)), # social life 13:00-16:00 (= 3h)
#                 it.repeat(5, times = (6*4)), # at home 16:00-20:00 (= 4h)
#                 it.repeat(1, times=(6*4)) #sleep from 8pm till 00:00 (=4h)
#                 ]))


# childsched1 = [SchedChild_weekday, # Monday
#                SchedChild_weekdaysocial, # Tuesday
#                SchedChild_weekday, # Wednesday
#                SchedChild_weekdaysocial, # Thursday
#                SchedChild_weekday, # Friday
#                SchedChild_weekend, # Saturday
#                SchedChild_weekend] # Sunday

# childsched2 = [SchedChild_weekdaysocial, # Monday
#                SchedChild_weekday, # Tuesday
#                SchedChild_weekdaysocial, # Wednesday
#                SchedChild_weekday, # Thursday
#                SchedChild_weekdaysocial, # Friday
#                SchedChild_weekend, # Saturday
#                SchedChild_weekend] # Sunday


# WeekLocations1 = [list(it.chain(*[it.repeat(0, times = 144)])), # Monday
#                 list(it.chain(*[it.repeat(0, times = 144)])), # Tuesday
#                 list(it.chain(*[it.repeat(0, times = 144)])), # Wednesday
#                 list(it.chain(*[it.repeat(0, times = 144)])), # Thursday
#                 list(it.chain(*[it.repeat(0, times = 144)])), # Friday
#                 list(it.chain(*[it.repeat(0, times = (13*6)), 
#                                 it.repeat(1, times=(6*3)), 
#                                 it.repeat(0,times= (6*8) )])), # Saturday social activity is elsewhere than home
#                 list(it.chain(*[it.repeat(0, times = 144)])) # Sunday
#                 ]

# WeekLocations2 = [list(it.chain(*[it.repeat(0, times = 144)])), # Monday
#                 list(it.chain(*[it.repeat(0, times = 144)])), # Tuesday
#                 list(it.chain(*[it.repeat(0, times = 144)])), # Wednesday
#                 list(it.chain(*[it.repeat(0, times = 144)])), # Thursday
#                 list(it.chain(*[it.repeat(0, times = 144)])), # Friday
#                 list(it.chain(*[it.repeat(0, times = 144)])), # Saturday
#                 list(it.chain(*[it.repeat(0, times = (13*6)), 
#                                 it.repeat(1, times=(6*3)), 
#                                 it.repeat(0,times= (6*8) )])) # Sunday social activity is elsewhere than home
#                 ]


# # preschool 2-4
# # daycare 0-4  7.30 or 8am to 6pm on weekdays 
# SchedBaby_weekday_home = list(it.chain(*[it.repeat(1, times = (6*9)), # sleep/rest till 9:00 (= 9h)
#                 it.repeat(5, times = (6*9)), # at home till 18:00 (9h)
#                 it.repeat(1, times=(6*6)) #sleep from 18pm till 00:00 (=6h)
#                 ]))

# SchedBaby_weekday_childcare = list(it.chain(*[it.repeat(1, times = (6*8)), # sleep till 8:00 ( = 8h min)
#                 it.repeat(13, times = (6*7)), # at daycare 8:00 till 15:00 (7h)
#                 it.repeat(5, times = (6*5)), # at home 15:00-20:00 (= 5h)
#                 it.repeat(1, times=(6*4)) #sleep from 8pm till 00:00 (=4h)
#                 ]))

# SchedBaby_outing = list(it.chain(*[it.repeat(1, times = (6*9)), # sleep/rest till 9:00 (= 9h)
#                 it.repeat(5, times = (6*3)), # at home till 12:00 (3h)
#                 it.repeat(8, times = (6*2)), # sports/ outdoor activity 12:00-14:00 (= 2h)
#                 it.repeat(5, times = (6*4)), # at home 14:00-18:00 (= 4h)
#                 it.repeat(1, times=(6*6)) #sleep from 18pm till 00:00 (=6h)
#                 ]))

# WeekLocationsbaby = [list(it.chain(*[it.repeat(0, times = 144)])), # Monday
#                 list(it.chain(*[it.repeat(0, times = 144)])), # Tuesday
#                 list(it.chain(*[it.repeat(0, times = 144)])), # Wednesday
#                 list(it.chain(*[it.repeat(0, times = 144)])), # Thursday
#                 list(it.chain(*[it.repeat(0, times = 144)])), # Friday
#                 list(it.chain(*[it.repeat(0, times = 144)])), # Saturday
#                 list(it.chain(*[it.repeat(0, times = 144)])) # Sunday
#                 ]

# print(len(SchedBaby_weekday_home), len(SchedBaby_weekday_childcare), len(SchedBaby_outing))

# babysched1 = [SchedBaby_weekday_home, # Monday
#                 SchedBaby_outing, # Tuesday
#                 SchedBaby_weekday_home, # Wednesday
#                 SchedBaby_outing, # Thursday
#                 SchedBaby_weekday_home, # Friday
#                 SchedBaby_outing, # Saturday
#                 SchedBaby_outing] # Sunday

# babysched2 = [SchedBaby_weekday_childcare, # Monday
#                 SchedBaby_weekday_childcare, # Tuesday
#                 SchedBaby_weekday_childcare, # Wednesday
#                 SchedBaby_weekday_childcare, # Thursday
#                 SchedBaby_weekday_home, # Friday
#                 SchedBaby_outing, # Saturday
#                 SchedBaby_outing] # Sunday


# ######################################################
# #### Joining the new schedules with the schedulefiles
# ######################################################
# weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# for weekday in weekdays:
#     schedule = pd.read_csv(path_data+"ActivitySchedules/HETUS2010_Synthpop_schedulesclean_"+weekday+".csv")
#     activitycolumns = schedule.columns[1:145]
#     locationcolumns = schedule.columns[145:]
#     print(activitycolumns)
#     print(locationcolumns)
#     schedule.loc[schedule["SchedID"] == "SchedChild_0", activitycolumns] = childsched1[weekdays.index(weekday)]
#     schedule.loc[schedule["SchedID"] == "SchedChild_0", locationcolumns] = WeekLocations1[weekdays.index(weekday)]
#     schedule.loc[schedule["SchedID"] == "SchedBaby_0", activitycolumns] = babysched1[weekdays.index(weekday)]
#     schedule.loc[schedule["SchedID"] == "SchedBaby_0", locationcolumns] = WeekLocationsbaby[weekdays.index(weekday)]
#     schedule.loc[schedule["SchedID"] == "SchedChild_1", activitycolumns] = childsched2[weekdays.index(weekday)]
#     schedule.loc[schedule["SchedID"] == "SchedChild_1", locationcolumns] = WeekLocations2[weekdays.index(weekday)]
#     schedule.loc[schedule["SchedID"] == "SchedBaby_1", activitycolumns] = babysched2[weekdays.index(weekday)]
#     schedule.loc[schedule["SchedID"] == "SchedBaby_1", locationcolumns] = WeekLocationsbaby[weekdays.index(weekday)]
    
# #     schedule.loc[len(schedule.index)] = ["SchedChild_1"] + childsched2[weekdays.index(weekday)] + WeekLocations2[weekdays.index(weekday)]
# #     schedule.loc[len(schedule.index)] = ["SchedBaby_1"] + babysched2[weekdays.index(weekday)] + WeekLocationsbaby[weekdays.index(weekday)]
    
#     schedule.to_csv(path_data+"ActivitySchedules/HETUS2010_Synthpop_schedulesclean_"+weekday+".csv", index=False)
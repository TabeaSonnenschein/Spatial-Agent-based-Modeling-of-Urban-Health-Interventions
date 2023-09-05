import pandas as pd
import itertools
import numpy as np

ActivityVars = ["Mact" + str(i) for i in range(1,145)] #Originally starts at 4:00 am but we want it to start at 0:00
LocationVars = ["Wherep" + str(i) for i in range(1,145)] #Originally starts at 4:00 am but we want it to start at 0:00

ActivityVarsOrder = ["Mact" + str(i) for i in (list(range(120,145)) + list(range(1,120)))] # 120 is 0:00
LocationVarsOrder = ["Wherep" + str(i) for i in (list(range(120,145)) + list(range(1,120)))] # 120 is 0:00

for day in range(1,8):
    Schedules = pd.read_csv(f"D:\PhD EXPANSE\Data\EU microdata access\HETUS2010_Synthpop_schedulesUniqueWeekOrder_day{day}.csv")
    Schedules["SchedID"] = [Schedules["ScheduleID"].iloc[x] + "_" + str(Schedules["OrderID"].iloc[x]) for x in range(len(Schedules.index))]
    Schedules = Schedules[["SchedID"]+ ActivityVarsOrder + LocationVarsOrder]
    Schedules = Schedules.rename(columns=dict(zip(ActivityVarsOrder + LocationVarsOrder, ActivityVars + LocationVars)))                                 
    Schedules.to_csv(f"D:\PhD EXPANSE\Data\EU microdata access\HETUS2010_Synthpop_schedulesclean_day{day}.csv", index=False)

import os
import pandas as pd

path_data = "D:\PhD EXPANSE\Data\Amsterdam\ABMRessources\ABMData\ModelRuns"
os.chdir(path_data)
Experiments = os.listdir(path=path_data)

exp, nb_agents, modelruns, minmonth, maxmonth, minday, maxday, minhour, maxhour = [], [], [], [], [], [], [], [], []

for experiment in Experiments:
    NumberAgents = os.listdir(path=os.path.join(path_data, experiment))
    for numberagents in NumberAgents:
        ModelRuns = os.listdir(path=os.path.join(path_data, experiment, numberagents, "AgentExposure"))
        for modelrun in ModelRuns:
            exp.append(experiment)
            nb_agents.append(numberagents)
            modelruns.append(modelrun)
            recordedTimes = os.listdir(path=os.path.join(path_data, experiment, numberagents, "AgentExposure", modelrun))
            if len(recordedTimes) == 0:
                minmonth.append(None)
                minday.append(None)
                minhour.append(None)
                maxmonth.append(None)
                maxday.append(None)
                maxhour.append(None)
            else:
                dates = [[int(x.split("_")[3][1:]), int(x.split("_")[4][1:]), int(x.split("_")[5][1:])] for x in recordedTimes]
                minmonth.append(min(dates)[0])
                minday.append(min(dates)[1])
                minhour.append(min(dates)[2])
                maxmonth.append(max(dates)[0])
                maxday.append(max(dates)[1])
                maxhour.append(max(dates)[2])

ExperimentOverview_df = pd.DataFrame({"Experiment": exp, 
              "Number of Agents": nb_agents, 
              "Model Run": modelruns,
              "Start Month": minmonth,
              "Start Day": minday,
              "Start Hour": minhour,
              "End Month": maxmonth,
              "End Day": maxday,
              "End Hour": maxhour
              })

ExperimentOverview_df["fullrun"] = ((ExperimentOverview_df["Start Day"]==1) & (ExperimentOverview_df["Start Hour"]==0) & (ExperimentOverview_df["End Day"]==7) & (ExperimentOverview_df["End Hour"]==23) & (ExperimentOverview_df["End Month"] >= 10))
print(ExperimentOverview_df)

ExperimentOverview_df.to_csv("D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/ExperimentOverview.csv", index=False)
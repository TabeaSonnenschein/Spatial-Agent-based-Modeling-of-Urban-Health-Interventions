import os
import pandas as pd
import  numpy as np
import matplotlib.pyplot as plt

nb_agents = 21750  #87000 = 10%, 43500 = 5%, 21750 = 2.5%, 8700 = 1%
path_data = "D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/RunSpecs"
os.chdir(path_data)
crs = "epsg:28992"

jobs = os.listdir(path=path_data)
jobs = [job for job in jobs if "seff" in job]
print(jobs)

ABMrun, Popsample, ABMthreads, OSRMthreads, Experiment = [], [], [], [], []

for count, job in enumerate(jobs):
    print(job)
    with open(job, "r") as f:
        content = f.readlines()
    content = [content.replace("\n", "").split(":") for content in content]
    print(content)
    if count == 0:
        jobeff = pd.DataFrame({specs[0]: [(":").join(specs[1:])] for specs in content})
    else:
        jobeff = pd.concat([jobeff, pd.DataFrame({specs[0]: [(":").join(specs[1:])] for specs in content})], ignore_index=True)
    id  = content[0][1]
    with open(f"slurm-{id[1:]}.out", "r") as f:
        ABMoutput = f.readlines()
    ABMoutput = [op.replace("\n", "") for op in ABMoutput]
    print(ABMoutput[:10])
    # find substring --threads in ABMoutput[2]
    try:
        OSRMthread = ABMoutput[2].split("--threads ")[1][0]
        print(OSRMthread)
        OSRMthreads.append(OSRMthread)
    except:
        OSRMthreads.append("1")
    ABmscripstart = ABMoutput.index("Starting Python ABM script")
    ABMthreads.append(ABMoutput[ABmscripstart+2].replace("Nr of assigned processes ", ""))
    expid = ABMoutput[ABmscripstart+3].split(" ")
    Experiment.append(expid[0])
    ABMrun.append(expid[1])
    Popsample.append(ABMoutput[ABmscripstart+4].split(" ")[-1])
    

jobeff["ABMrun"] = ABMrun
jobeff["Experiment"] = Experiment
jobeff["ABMthreads"] = ABMthreads
jobeff["OSRMthreads"] = OSRMthreads
jobeff["Popsample"] = Popsample

jobeff.to_csv("JobEfficiency.csv", index=False)
import numpy as np


def init_worker_init(schedules, Resid, univers, Scho, Prof):
    # declare scope of a new global variable
    global schedulelist, Residences, Universities, Schools, Profess, Entertainment, Restaurants
    # store argument in the global variable for this process
    schedulelist = schedules
    Residences = Resid
    Universities = univers
    Schools = Scho
    Profess = Prof



    # initialize worker processes
def init_worker_simul(Resid, Entertain, Restaur, envdeters, modalchoice, ordprevars, cols, projectWSG84, projcrs, crs_string, routevars, originvars, destinvars, Grid):
    # declare scope of a new global variable
    global Residences, Entertainment, Restaurants, EnvBehavDeterms, ModalChoiceModel, OrderPredVars, colvars, project_to_WSG84, projecy_to_crs, crs, routevariables, originvariables, destinvariables, EnvStressGrid
    # store argument in the global variable for this process
    Residences = Resid
    Entertainment = Entertain
    Restaurants = Restaur
    EnvBehavDeterms = envdeters
    ModalChoiceModel = modalchoice
    OrderPredVars = ordprevars
    colvars = cols
    project_to_WSG84 = projectWSG84
    projecy_to_crs = projcrs
    crs = crs_string
    routevariables = routevars
    originvariables = originvars
    destinvariables = destinvars
    EnvStressGrid = Grid
    

def worker_process( agents, current_datetime):
    global Residences, Entertainment, Restaurants, EnvBehavDeterms, ModalChoiceModel, OrderPredVars, colvars, project_to_WSG84, projecy_to_crs, crs, routevariables, originvariables, destinvariables
    for agent in agents:
        agent.step(current_datetime)
    return agents

def hourly_worker_process( agents, current_datetime, NO2):
    global Residences, Entertainment, Restaurants, EnvBehavDeterms, ModalChoiceModel, OrderPredVars, colvars, project_to_WSG84, projecy_to_crs, crs, routevariables, originvariables, destinvariables, EnvStressGrid
    EnvStressGrid[:] = np.array(NO2).reshape(EnvStressGrid.shape)
    for agent in agents:
        agent.Exposure()
        agent.step(current_datetime)
    return agents

def RetrieveRoutes(thishourmode, thishourtrack):
   if "drive" in thishourmode:
      return([thishourtrack[count] for count, value in enumerate(thishourmode) if value == "drive"])

def RetrieveExposure(agents, dum):
    return [[agent.unique_id, agent.hourlyNO2, agent.hourlyMET]  for agent in agents]
  
def RetrieveModalSplitStep(agents, dum):
    return [[agent.unique_id, agent.modalchoice, agent.track_duration, agent.trip_distance]  for agent in agents]

def RetrieveModalSplitHour(agents, dum):
    return [agent.thishourmode  for agent in agents]
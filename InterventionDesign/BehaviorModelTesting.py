from sklearn_pmml_model.tree import PMMLTreeClassifier
import pandas as pd
import geopandas as gpd
from shapely import LineString, Point
import numpy as np
from collections import Counter
import random
from shapely.ops import nearest_points, unary_union
from statistics import mean

def add_suffix(lst,  suffix): 
    return  list(map(lambda x: x + suffix, lst))

crs = "epsg:28992"
path_data = "C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/"

# Read static data
nb_humans = 21750     #87000 = 10%, 43500 = 5%, 21750 = 2.5%, 8700 = 1%
random_subset = pd.read_csv(path_data+f"Population/Amsterdam_population_subset{nb_humans}.csv")
random_subset["student"] = 0
random_subset.loc[random_subset["current_education"] == "high", "student"] = 1
Residences = gpd.read_feather(path_data+"FeatherDataABM/Residences.feather")
Schools = gpd.read_feather(path_data+"FeatherDataABM/Schools.feather")
EnvBehavDeterms = gpd.read_feather(path_data+"FeatherDataABM/EnvBehavDeterminants.feather")
EnvBehavDeterms = EnvBehavDeterms.fillna(0)
monthly_weather_df = pd.read_csv(path_data+"Weather/monthlyWeather2019TempDiff.csv") 
WeatherVars = list(monthly_weather_df.loc[1,["Rain", "Temperature", "Winddirection", "Windspeed"]])



def PredModForScenario(EnvBehavDeterms, TripVars, modelvars, PCstat, trip_distance, IndModalPreds, route_eucl_line, orig, dest, routevariables, originvariables, destinvariables,colvars, OrderPredVars, FactorLoadings, ModalChoiceModel ):
    # Predicting modechoice for status quo
    RouteVars = gpd.GeoDataFrame(data = {'id': ['1'], 'geometry': [route_eucl_line]}, geometry="geometry", crs=crs).sjoin(EnvBehavDeterms, how="left")[routevariables].mean(axis=0).values
    OrigVars = gpd.GeoDataFrame(data = {'id': ['1'], 'geometry': [orig]}, geometry="geometry", crs=crs).sjoin(EnvBehavDeterms, how="left")[originvariables].values[0]
    DestVars = gpd.GeoDataFrame(data = {'id': ['1'], 'geometry': [dest]}, geometry="geometry",crs=crs).sjoin(EnvBehavDeterms, how="left")[destinvariables].values[0]
    if modelvars == "allvars_strict":
        pred_df = pd.DataFrame(np.concatenate((RouteVars, OrigVars, DestVars, IndModalPreds, [trip_distance]), axis=None).reshape(1, -1), 
                                columns=colvars).fillna(0)
    else:
        pred_df = pd.DataFrame(np.concatenate((RouteVars, OrigVars, DestVars, IndModalPreds, [trip_distance],TripVars, WeatherVars), axis=None).reshape(1, -1), 
                                columns=colvars).fillna(0)
    if PCstat == "PCA":
        PCValues = [mean(np.asarray(pred_df.loc[0,FactorLoadings["Vars"]]) * np.asarray(FactorLoadings.iloc[:,i])) for i in range(1, FactorLoadings.shape[1])]
        pred_df[FactorLoadings.columns[1:]] = PCValues
    mode = ModalChoiceModel.predict(pred_df[OrderPredVars].values)[0].replace("1", "bike").replace("2", "drive").replace("3", "transit").replace("4", "walk")
    return mode


def RunMonteCarloSaveData(MonteCarloCount, pop_size, modelvars, PCstat, InterventionName, EnvBehavDeterms_Intervention, tripvariables, routevariables, originvariables, destinvariables,colvars, OrderPredVars, FactorLoadings, ModalChoiceModel):
    print(f"Predicting Mode of Transport Choice with {MonteCarloCount} Monte Carlo Iterations")
    ModeCounter_StatusQuo = []
    ModeCounter_Intervention = []
    for x in range(MonteCarloCount):
        print("Monte Carlo Iteration: ", x+1)
        pop = pd.DataFrame(random_subset.sample(n=pop_size))
        pop = pop.reset_index(drop=True)
        modechoice_StatQuo = []
        modechoice_Intervention = []
        for agent in range(len(pop)):
            if modelvars == "allvars_strict":
                IndModalPreds = [pop.iloc[agent,i] for i in [19,2,13,20,21,22,17,11,12,23,24,15,14,16]]    # individual modal choice predictions: ["sex_male", "age", "car_access", "Western", 
                                                                    # "Non_Western", "Dutch", 'income','employed',
                                                                    # 'edu_3_levels','HH_size', 'Nrchildren', 'driving_habit','biking_habit','transit_habit']
            else:
                IndModalPreds = [pop.iloc[agent,i] for i in [19,2,13,20,21,22,17,11,12,23,24,25,15,14,16]] # "sex_male", "age", "car_access", 
                                                                    # "Western", "Non_Western", "Dutch", 'income','employed',
                                                                    #'edu_3_levels','HH_size', 'Nrchildren', 'student', 'driving_habit','biking_habit',
                                                                    # 'transit_habit']
            TripVars = [random.randint(0, 1) for _ in range(len(tripvariables)-1)]
            orig = Residences.sample(1)["geometry"].values[0]
            if bool(random.getrandbits(1)):
                dest = Residences.sample(1)["geometry"].values[0]
            else:
                dest = nearest_points(orig, Schools["geometry"].unary_union)[1]
            route_eucl_line = LineString([orig, dest])
            trip_distance = route_eucl_line.length
            
            modechoice_StatQuo.append(PredModForScenario(EnvBehavDeterms, TripVars, modelvars, PCstat, trip_distance, IndModalPreds, route_eucl_line, orig, dest, routevariables, originvariables, destinvariables,colvars, OrderPredVars, FactorLoadings, ModalChoiceModel ))
            modechoice_Intervention.append(PredModForScenario(EnvBehavDeterms_Intervention, TripVars, modelvars, PCstat, trip_distance, IndModalPreds, route_eucl_line, orig, dest, routevariables, originvariables, destinvariables,colvars, OrderPredVars, FactorLoadings, ModalChoiceModel ))

        print("StatusQuo Modal Split: ", Counter(modechoice_StatQuo))
        print(f"{InterventionName} Intervention Modal Split:", Counter(modechoice_Intervention))
        ModeCounter_StatusQuo.append(Counter(modechoice_StatQuo))
        ModeCounter_Intervention.append(Counter(modechoice_Intervention))
    
    # Tranform to dataframe
    ModeCounter_StatusQuo_df = pd.DataFrame.from_dict(ModeCounter_StatusQuo).reset_index(drop=True)
    ModeCounter_Intervention_df = pd.DataFrame.from_dict(ModeCounter_Intervention).reset_index(drop=True)
    ModeCounter_StatusQuo_df["MonteCarloRun"] = list(range(1, MonteCarloCount+1))
    ModeCounter_Intervention_df["MonteCarloRun"] = list(range(1, MonteCarloCount+1))
    ModeCounter_Intervention = pd.merge(ModeCounter_StatusQuo_df, ModeCounter_Intervention_df, on="MonteCarloRun", suffixes=('_StatusQuo', f'_{InterventionName}'))

    # calculate relative change
    ModeCounter_Intervention["bike_rel_change"] = (ModeCounter_Intervention["bike_"+InterventionName] - ModeCounter_Intervention["bike_StatusQuo"])/ModeCounter_Intervention["bike_StatusQuo"]
    ModeCounter_Intervention["drive_rel_change"] = (ModeCounter_Intervention["drive_"+InterventionName] - ModeCounter_Intervention["drive_StatusQuo"])/ModeCounter_Intervention["drive_StatusQuo"]
    ModeCounter_Intervention["transit_rel_change"] = (ModeCounter_Intervention["transit_"+InterventionName] - ModeCounter_Intervention["transit_StatusQuo"])/ModeCounter_Intervention["transit_StatusQuo"]
    ModeCounter_Intervention["walk_rel_change"] = (ModeCounter_Intervention["walk_"+InterventionName] - ModeCounter_Intervention["walk_StatusQuo"])/ModeCounter_Intervention["walk_StatusQuo"]

    print(ModeCounter_Intervention[["bike_rel_change", "drive_rel_change", "transit_rel_change", "walk_rel_change"]])
    ModeCounter_Intervention.to_csv(path_data+f"ModalSplit{InterventionName}_{modelvars}{PCstat}.csv", index=False)

def RunForModelVarsPCstatInterventions(modelvariables, PCstats, Interventions):
    for modelvars in modelvariables:
        for PCstat in PCstats:
            if modelvars == "allvars":
                routevariables = ["popDns", "retaiDns","greenCovr", "RdIntrsDns", "TrafAccid", "NrTrees", "MeanTraffV", "HighwLen", "AccidPedes",
                                "PedStrWidt", "PedStrLen", "LenBikRout", "DistCBD", "retailDiv", "MeanSpeed", "MaxSpeed", "NrStrLight", "CrimeIncid",
                                "MaxNoisDay", "OpenSpace", "PNonWester", "PWelfarDep", "SumTraffVo", "pubTraDns", "MxNoisNigh", "MinSpeed", "PrkPricPre", "PrkPricPos" ]
                personalvariables = ["sex_male", "age", "car_access", "Western", "Non_Western", "Dutch", 'income','employed',
                                        'edu_3_levels','HH_size', 'Nrchildren', 'student', 'driving_habit','biking_habit','transit_habit']
                tripvariables = ["trip_distance", "purpose_commute", 'purpose_leisure','purpose_groceries_shopping',
                                        'purpose_education', 'purpose_bring_person']
                weathervariables = ['Rain', 'Temperature', 'Winddirection', 'Windspeed']
                originvariables = ["pubTraDns", "DistCBD"]
                destinvariables = ["pubTraDns", "DistCBD", "NrParkSpac", "PrkPricPre", "PrkPricPos"]
                
            elif modelvars == "allvars_strict":
                routevariables = ["popDns", "retaiDns","greenCovr", "RdIntrsDns", "TrafAccid", "NrTrees", "MeanTraffV", "HighwLen", "AccidPedes",
                                "PedStrWidt", "PedStrLen", "LenBikRout", "DistCBD", "retailDiv", "MeanSpeed", "MaxSpeed", "MinSpeed", "NrStrLight", "CrimeIncid",
                                "MaxNoisDay", "MxNoisNigh", "OpenSpace", "PNonWester", "PWelfarDep", "pubTraDns", "SumTraffVo"]
                personalvariables = ["sex_male", "age", "car_access", "Western", "Non_Western", "Dutch", 'income','employed',
                                        'edu_3_levels','HH_size', 'Nrchildren', 'driving_habit','biking_habit','transit_habit']
                tripvariables = ["trip_distance"]
                originvariables = ["pubTraDns", "DistCBD"]
                destinvariables = ["pubTraDns", "DistCBD"]

            routevariables_suff = add_suffix(routevariables, ".route")
            originvariables_suff = add_suffix(originvariables, ".orig")
            destinvariables_suff = add_suffix(destinvariables, ".dest")

            if modelvars == "allvars_strict":  
                colvars = routevariables_suff + originvariables_suff + destinvariables_suff + personalvariables + tripvariables
            elif modelvars == "allvars":
                colvars = routevariables_suff + originvariables_suff + destinvariables_suff + personalvariables + tripvariables + weathervariables

            print("Reading Mode of Transport Choice Model")
            ModalChoiceModel = PMMLTreeClassifier(pmml=path_data+f"ModalChoiceModel/modalChoice_{modelvars}{PCstat}.pmml")
            ModalChoiceModel.splitter = "random"
            OrderPredVars = [x for x in ModalChoiceModel.fields][1:]
            print(OrderPredVars)

            if PCstat == "PCA":
                FactorLoadings = pd.read_csv(path_data+f"ModalChoiceModel/{modelvars}_PCLoadings.csv")
                print(FactorLoadings)
            else:
                FactorLoadings = None

            for InterventionName in Interventions:
                EnvBehavDeterms_Intervention = gpd.read_feather(path_data+f"FeatherDataABM/EnvBehavDeterminants{InterventionName}.feather")
                EnvBehavDeterms_Intervention = EnvBehavDeterms_Intervention.fillna(0)

                RunMonteCarloSaveData(MonteCarloCount = 5, pop_size = 300, 
                                                                                        modelvars= modelvars, PCstat=PCstat, 
                                                                                        InterventionName=InterventionName, 
                                                                                        EnvBehavDeterms_Intervention = EnvBehavDeterms_Intervention,
                                                                                        tripvariables = tripvariables, routevariables = routevariables,
                                                                                        originvariables= originvariables, destinvariables= destinvariables,
                                                                                        colvars = colvars, OrderPredVars = OrderPredVars, 
                                                                                        FactorLoadings= FactorLoadings, ModalChoiceModel= ModalChoiceModel)


# RunForModelVarsPCstatInterventions(modelvariables= ["allvars_strict", "allvars"], 
#                                    PCstats = ["PCA", "NOPCA"], 
#                                    Interventions = ["SpeedInterv", "PedStrWidth", "SpeedInterv", "RetaiDns", "RetaiDnsDiv", "GreenCovr", "ParkSpace", "ParkPrice", "NrTrees"])

# RunForModelVarsPCstatInterventions(modelvariables= ["allvars_strict", "allvars"], 
#                                    PCstats = ["PCA", "NOPCA"], 
#                                    Interventions = ["LenBikRout", "HighwLen", "PedStrLen"])

# RunForModelVarsPCstatInterventions(modelvariables= ["allvars_strict", "allvars"],
#                                       PCstats = ["PCA", "NOPCA"], 
#                                       Interventions = ["PedStrWidthOutskirt", "PedStrWidthCenter", "RdIntrsDnsIncr", "RdIntrsDnsDcr", "LenBikRout", "HighwLen", "PedStrLen"])

RunForModelVarsPCstatInterventions(modelvariables= ["allvars_strict", "allvars"], 
                                   PCstats = ["PCA", "NOPCA"], 
                                   Interventions = [ "PedStrLen"])
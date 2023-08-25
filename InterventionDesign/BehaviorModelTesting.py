from sklearn_pmml_model.tree import PMMLTreeClassifier
import pandas as pd
import geopandas as gpd
from shapely import LineString, Point
import numpy as np
from collections import Counter

def add_suffix(lst,  suffix): 
    return  list(map(lambda x: x + suffix, lst))

crs = "epsg:28992"
path_data = "C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/"

print("Reading Mode of Transport Choice Model")
ModalChoiceModel = PMMLTreeClassifier(pmml=path_data+"ModalChoiceModel/modalChoice.pmml")
ModalChoiceModel.splitter = "random"
OrderPredVars = [x for x in ModalChoiceModel.fields][1:]


# modelvars = "allvars"
modelvars = "allvars_strict"
if modelvars == "allvars":
    routevariables = ["popDns", "retaiDns","greenCovr", "RdIntrsDns", "TrafAccid", "NrTrees", "MeanTraffV", "HighwLen", "AccidPedes",
                    "PedStrWidt", "PedStrLen", "LenBikRout", "DistCBD", "retailDiv", "MeanSpeed", "MaxSpeed", "NrStrLight", "CrimeIncid",
                    "MaxNoisDay", "OpenSpace", "PNonWester", "PWelfarDep"]
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

colvars = routevariables_suff + originvariables_suff + destinvariables_suff + personalvariables + tripvariables




random_subset = pd.read_csv(path_data+"Population/Amsterdam_population_subset.csv")
random_subset = random_subset.iloc[:200]

EnvBehavDeterms = gpd.read_feather(path_data+"FeatherDataABM/EnvBehavDeterminants.feather")
EnvBehavDetermsSpeedInterv = gpd.read_feather(path_data+"FeatherDataABM/EnvBehavDeterminantsSpeedInterv.feather")

Residences = gpd.read_feather(path_data+"FeatherDataABM/Residences.feather")


modechoice_StatQuo = []
modechoice_Intervention = []
for agent in random_subset:
    IndModalPreds = [random_subset[i] for i in [19,2,13,20,21,22,17,11,12,5,7,15,14,16]]    # individual modal choice predictions: ["sex_male", "age", "car_access", 
                                                             # "Western", "Non_Western", "Dutch", 'income','employed',
                                                             #'edu_3_levels','HH_size', 'Nrchildren', 'driving_habit','biking_habit',
                                                             # 'transit_habit']
    orig = Residences.sample(1)
    dest = Residences.sample(1)
    route_eucl_line = LineString([Point(tuple(orig)), Point(tuple(dest))])
    trip_distance = route_eucl_line.length
    # Predicting modechoice for status quo
    RouteVars = gpd.GeoDataFrame(data = {'id': ['1'], 'geometry': [route_eucl_line]}, geometry="geometry", crs=crs).sjoin(EnvBehavDeterms, how="left")[routevariables].mean(axis=0).values
    OrigVars = gpd.GeoDataFrame(data = {'id': ['1'], 'geometry': [Point(tuple(orig))]}, geometry="geometry", crs=crs).sjoin(EnvBehavDeterms, how="left")[originvariables].values[0]
    DestVars = gpd.GeoDataFrame(data = {'id': ['1'], 'geometry': [Point(tuple(dest))]}, geometry="geometry",crs=crs).sjoin(EnvBehavDeterms, how="left")[destinvariables].values[0]
    pred_df = pd.DataFrame(np.concatenate((RouteVars, OrigVars, DestVars, IndModalPreds, [trip_distance]), axis=None).reshape(1, -1), 
                                  columns=colvars).fillna(0)
    modechoice_StatQuo.append(ModalChoiceModel.predict(pred_df[OrderPredVars].values)[0].replace("1", "bike").replace("2", "drive").replace("3", "transit").replace("4", "walk"))

    # Predicting modechoice for intervention   
    RouteVars = gpd.GeoDataFrame(data = {'id': ['1'], 'geometry': [route_eucl_line]}, geometry="geometry", crs=crs).sjoin(EnvBehavDetermsSpeedInterv, how="left")[routevariables].mean(axis=0).values
    OrigVars = gpd.GeoDataFrame(data = {'id': ['1'], 'geometry': [Point(tuple(orig))]}, geometry="geometry", crs=crs).sjoin(EnvBehavDetermsSpeedInterv, how="left")[originvariables].values[0]
    DestVars = gpd.GeoDataFrame(data = {'id': ['1'], 'geometry': [Point(tuple(dest))]}, geometry="geometry",crs=crs).sjoin(EnvBehavDetermsSpeedInterv, how="left")[destinvariables].values[0]
    pred_df = pd.DataFrame(np.concatenate((RouteVars, OrigVars, DestVars, IndModalPreds, [trip_distance]), axis=None).reshape(1, -1), 
                                  columns=colvars).fillna(0)
    modechoice_Intervention.append(ModalChoiceModel.predict(pred_df[OrderPredVars].values)[0].replace("1", "bike").replace("2", "drive").replace("3", "transit").replace("4", "walk"))


print("StatusQuo Modal Split: ", Counter(modechoice_StatQuo))
print("Intervention Modal Split", Counter(modechoice_Intervention))

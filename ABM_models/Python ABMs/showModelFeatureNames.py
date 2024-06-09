import joblib as jl
import pandas as pd
import sklearn as sk
# from sklearn2pmml.pipeline import PMMLPipeline
# from  sklearn2pmml import sklearn2pmml
from sklearn_pmml_model.ensemble import PMMLForestClassifier
# from sklearn_pmml_model import PMMLPipeline



path_data = "C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/"
# ModalChoiceModel = jl.load(path_data+f"ModalChoiceModel/01Models/RandomForest.joblib")
# print(ModalChoiceModel.feature_names_in_)
# Features = ModalChoiceModel.feature_names_in_
# with open(path_data+f"ModalChoiceModel/01Models/RFfeatures.txt", 'w') as file:
#     for feature in Features:
#         file.write(feature + '\n')
# sklearn2pmml(PMMLPipeline([("classifier", ModalChoiceModel)]), path_data+f"ModalChoiceModel/01Models/RandomForest.pmml",  with_repr = True)

ModalChoiceModel = PMMLForestClassifier(pmml=path_data+f"ModalChoiceModel/01Models/RandomForest.pmml")
print(dir(ModalChoiceModel))
print(ModalChoiceModel.n_features_)

columns = ['RdIntrsDns.route', 'retaiDns.route', 'greenCovr.route', 'popDns.route', 
 'OpenSpace.route', 'sex_male', 'pubTraDns.orig', 'pubTraDns.route', 'retailDiv.route', 
 'age', 'car_access', 'CrimeIncid.route', 'TrafAccid.route', 'AccidPedes.route', 
 'PedStrWidt.route', 'PedStrLen.route', 'LenBikRout.route', 'Western', 'Non_Western', 'Dutch', 'HighwLen.route', 'MeanSpeed.route', 'DistCBD.orig', 
 'DistCBD.dest', 'MeanTraffV.route', 'SumTraffVo.route', 'income', 'employed', 'edu_3_levels', 'HH_size', 'Nrchildren', 'NrParkSpac.dest', 'NrTrees.route', 
 'MaxSpeed.route', 'MinSpeed.route', 'NrStrLight.route', 'MaxNoisDay.route', 'MxNoisNigh.route', 'PNonWester.route', 'PWelfarDep.route', 'trip_distance', 
 'PrkPricPre.dest',
 'pubTraDns.dest', 'Rain', 'Temperature', 'Winddirection', 
 'Windspeed', 'purpose_commute', 
 'purpose_leisure', 'purpose_groceries_shopping', 'purpose_education',  'purpose_bring_person', 
 'student', 'driving_habit', 'biking_habit', 'transit_habit']

data = [27.545455,10.363636,0.073718 ,307.918784 ,0.307206,
 1,0, 3,1, 34, 1, 30,2,1,4,45,32,1,0,0,2,20,569, 290, 400, 10200, 4, 1,3,2,0,60,39,
 50, 20, 50,25,34,0.7,0.2,1579, 7.5, 5, 30,9, 180, 46, 0,0,1,1,
 0.0,0.0,0.0,0.0,1.0]


#make a dataframe out of the data and the columns
df = pd.DataFrame([data], columns=columns)

print(ModalChoiceModel.predict(df))
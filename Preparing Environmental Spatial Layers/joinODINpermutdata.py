import pandas as pd
import os
import numpy as np
from itertools import chain
from operator import itemgetter
pd.options.mode.chained_assignment = None  # default='warn'

os.chdir(r"D:")
listOfFiles = os.listdir(path='D:')
listOfFiles = [filename for filename in listOfFiles if ".csv" in filename]

#
# numberlist = [int(el.replace("ODIN2018_Studyarea_PC6_data1_", "").replace(".csv", "")) for el in listOfFiles ]
# numberlist = [int(el.replace("ODIN2018_Studyarea_PC6_joineddata_", "").replace(".csv", "")) for el in listOfFiles ]
# listOfFiles = [listOfFiles[indx] for indx in np.argsort(numberlist)]
print(listOfFiles)

envdata = pd.read_csv("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Built Environment/Transport Infrastructure/PC6_env_behav_determ.csv")
print(list(envdata.columns))
origjoin = envdata[["PC6", "PrkPricPre", "PrkPricPos", "NrParkSpac"]]
destjoin = envdata[["PC6", "DistCBD", "pubTraDns"]]
origjoin.rename(columns = { "PC6": "orig_PC6" , 'PrkPricPre':'PrkPricPre.orig', 'PrkPricPos':'PrkPricPos.orig', 'NrParkSpac':'NrParkSpac.orig'}, inplace = True)
destjoin.rename(columns = {"PC6": "dest_PC6" , 'DistCBD':'DistCBD.dest', 'pubTraDns':'pubTraDns.dest'}, inplace = True)
print(list(origjoin.columns))
print(list(destjoin.columns))
origjoin.fillna(0, inplace= True)
destjoin.fillna(0, inplace= True)
print(origjoin.head())
print(destjoin.head())
del envdata

# for file in listOfFiles:
#     print("reading: ", file)
#     df = pd.read_csv(os.path.join(os.getcwd(), file))
#     columnnames = [el for el in list(df.columns) if not(el in ["PC6.orig", "coords.x1.orig",	"coords.x2.orig", "PC6.dest", "coords.x1.dest",	"coords.x2.dest"])]
#     print(list(df.columns))
#     print(columnnames)
#     df = df[columnnames]
#     columnnames.extend(['PrkPricPre.dest','PrkPricPos.dest'])
#     print(columnnames)
#     print("merging: ", file)
#     df = pd.merge(df, parkingprice, left_on="dest_PC6", right_on="PC6", how="left")
#     print(list(df.columns))
#     # columnnames.extend(['PrkPricPre.dest','PrkPricPos.dest'])
#     # print(columnnames)
#     df = df[columnnames]
#     print("writing: ", file)
#     df.to_csv(file, index = False)

for file in listOfFiles:
    print("reading: ", file)
    df = pd.read_csv(os.path.join(os.getcwd(), file))
    columnnames = list(df.columns)
    df1 = df.iloc[:int(len(df.index)/2)]
    df2 = df.iloc[int(len(df.index)/2):]
    del df
    print(columnnames)
    columnnames.extend(["PrkPricPre.orig","PrkPricPos.orig", "NrParkSpac.orig", "DistCBD.dest","pubTraDns.dest"])
    print(columnnames)
    print("merging: NR1 ", file)
    df1 = pd.merge(df1, origjoin, on="orig_PC6", how="left")
    df1 = pd.merge(df1, destjoin, on="dest_PC6", how="left")
    print("merging: NR2 ", file)
    df2 = pd.merge(df2, origjoin, on="orig_PC6", how="left")
    df2 = pd.merge(df2, destjoin, on="dest_PC6", how="left")
    print(list(df1.columns))
    df1 = pd.concat([df1, df2])
    del df2
    df1 = df1[columnnames]
    len(df1.index)
    print("writing: ", file)
    df1.to_csv(file, index = False)


# for file in listOfFiles:
#     print("reading: ", file)
#     df = pd.read_csv(os.path.join(os.getcwd(), file))
#     print(list(df.columns))
#     df = df.iloc[:,1:]
#     print("writing: ", file)
#     df.to_csv(file, index = False)
#
# redundant = pd.read_csv(os.path.join("D:/restdata", "redundantPC6combinations.csv"))
#
# def del_list_numpy(l, id_to_del):
#     arr = np.array(l, dtype='int32')
#     return list(np.delete(arr, id_to_del))
#
# print("reading file 1")
# files = pd.read_csv(os.path.join(os.getcwd(), listOfFiles[3]))
# print(len(files.index))
# redundant_idx = []
# for count in range(0, len(redundant.index)):
#     redundant_idx.extend(list(np.where((files["orig_postcode"] == redundant["orig_postcode"].iloc[count]) & (files["dest_postcode"] == redundant["dest_postcode"].iloc[count]))[0].tolist()))
#
# print(len(redundant_idx))
# print(redundant_idx[0:1000])
#
# print(files.iloc[redundant_idx].head())
# keep_idx = list(files.index)
# print([keep_idx[x] for x in redundant_idx[0:1000]])
# keep_idx = del_list_numpy(keep_idx,redundant_idx)
# print(keep_idx[0:2000])
# print(len(keep_idx))
# files = files.iloc[keep_idx]
# print(len(files.index))
#
# print("reading file 2")
# files2 = pd.read_csv(os.path.join(os.getcwd(), listOfFiles[4]))
# redundant_idx = []
# for count in range(0, len(redundant.index)):
#     redundant_idx.extend(list(np.where((files2["orig_postcode"] == redundant["orig_postcode"].iloc[count]) & (files2["dest_postcode"] == redundant["dest_postcode"].iloc[count]))[0].tolist()))
#
# print(len(redundant_idx))
# print(redundant_idx[0:1000])
#
# print(files2.iloc[redundant_idx].head())
# keep_idx = list(files2.index)
# print([keep_idx[x] for x in redundant_idx[0:1000]])
# keep_idx = del_list_numpy(keep_idx,redundant_idx)
# print(keep_idx[0:2000])
# print(len(keep_idx))
# files2 = files2.iloc[keep_idx]
# print(len(files2.index))
#
# print("reading file 3")
# files3 = pd.read_csv(os.path.join(os.getcwd(), listOfFiles[5]))
#
# redundant_idx = []
# for count in range(0, len(redundant.index)):
#     redundant_idx.extend(list(np.where((files3["orig_postcode"] == redundant["orig_postcode"].iloc[count]) & (files3["dest_postcode"] == redundant["dest_postcode"].iloc[count]))[0].tolist()))
#
# print(len(redundant_idx))
# print(redundant_idx[0:1000])
#
# print(files3.iloc[redundant_idx].head())
# keep_idx = list(files3.index)
# print([keep_idx[x] for x in redundant_idx[0:1000]])
# keep_idx = del_list_numpy(keep_idx,redundant_idx)
# print(keep_idx[0:2000])
# print(len(keep_idx))
# files3 = files3.iloc[keep_idx]
# print(len(files3.index))
#
#
# print("reading file 4")
# files4 = pd.read_csv(os.path.join(os.getcwd(), listOfFiles[6]))
#
# redundant_idx = []
# for count in range(0, len(redundant.index)):
#     redundant_idx.extend(list(np.where((files4["orig_postcode"] == redundant["orig_postcode"].iloc[count]) & (files4["dest_postcode"] == redundant["dest_postcode"].iloc[count]))[0].tolist()))
#
# print(len(redundant_idx))
# print(redundant_idx[0:1000])
#
# print(files4.iloc[redundant_idx].head())
# keep_idx = list(files4.index)
# print([keep_idx[x] for x in redundant_idx[0:1000]])
# keep_idx = del_list_numpy(keep_idx,redundant_idx)
# print(keep_idx[0:2000])
# print(len(keep_idx))
# files4 = files4.iloc[keep_idx]
# print(len(files4.index))
#
# print("reading file 5")
# files5 = pd.read_csv(os.path.join(os.getcwd(), listOfFiles[7]))
#
# redundant_idx = []
# for count in range(0, len(redundant.index)):
#     redundant_idx.extend(list(np.where((files5["orig_postcode"] == redundant["orig_postcode"].iloc[count]) & (files5["dest_postcode"] == redundant["dest_postcode"].iloc[count]))[0].tolist()))
#
# print(len(redundant_idx))
# print(redundant_idx[0:1000])
#
# print(files5.iloc[redundant_idx].head())
# keep_idx = list(files5.index)
# print([keep_idx[x] for x in redundant_idx[0:1000]])
# keep_idx = del_list_numpy(keep_idx,redundant_idx)
# print(keep_idx[0:2000])
# print(len(keep_idx))
# files5 = files5.iloc[keep_idx]
# print(len(files5.index))
#
# print("reading file 6")
# files6 = pd.read_csv(os.path.join(os.getcwd(), listOfFiles[8]))
#
# redundant_idx = []
# for count in range(0, len(redundant.index)):
#     redundant_idx.extend(list(np.where((files6["orig_postcode"] == redundant["orig_postcode"].iloc[count]) & (files6["dest_postcode"] == redundant["dest_postcode"].iloc[count]))[0].tolist()))
#
# print(len(redundant_idx))
# print(redundant_idx[0:1000])
#
# print(files6.iloc[redundant_idx].head())
# keep_idx = list(files6.index)
# print([keep_idx[x] for x in redundant_idx[0:1000]])
# keep_idx = del_list_numpy(keep_idx,redundant_idx)
# print(keep_idx[0:2000])
# print(len(keep_idx))
# files6 = files6.iloc[keep_idx]
# print(len(files6.index))
#
# print("concatinating")
# files = pd.concat([files, files2, files3,files4, files5, files6])
# print("writing data")
# files.to_csv(("ODIN2018_Studyarea_PC6_joineddata_2.csv"), index=False)


#
# print("reading file 1")
# file1 = pd.read_csv(os.path.join("D:\Orig_Dest_TrackProperties_PC6Combinations", "ODIN2018_Studyarea_PC6_joineddata_1.csv"))
# print("reading file 2")
# file2 = pd.read_csv(os.path.join("D:\Orig_Dest_TrackProperties_PC6Combinations", "ODIN2018_Studyarea_PC6_joineddata_2.csv"))
# print("concatinating")
# files = pd.concat([file1, file2])
# print("writing data")
# files.to_csv(("ODIN2018_Studyarea_PC6_joineddata.csv"), index=False)

# print("reading")
# files = pd.read_csv(os.path.join("D:/restdata", "ODIN2018_Studyarea_origPC6.csv"))
# print("subselecting")
# files = files[["orig_postcode", "dest_postcode"]]
# print("writing")
# files.to_csv("D:/restdata/purePC4.csv", index=False)

#
# files = pd.read_csv(os.path.join(os.getcwd(), listOfFiles[40]))
# for count in range(41,60):
#     file = pd.read_csv(os.path.join(os.getcwd(), listOfFiles[count]))
#     files = pd.concat([files, file])
#     print(len(files.index))
#     if (len(files.index) == 20000000) and (count < ((len(listOfFiles) // 20)*20)) :
#         files.to_csv(("ODIN2018_Studyarea_PC6_joineddata_" +str(count)+ ".csv"), index=False)
#         files = files.iloc[0]
#     elif count == (len(listOfFiles)-1) :
#         files.to_csv(("ODIN2018_Studyarea_PC6_joineddata_" +str(count)+ ".csv"), index=False)
#
# files = pd.read_csv(os.path.join(os.getcwd(), listOfFiles[60]))
# for count in range(61,80):
#     file = pd.read_csv(os.path.join(os.getcwd(), listOfFiles[count]))
#     files = pd.concat([files, file])
#     print(len(files.index))
#     if (len(files.index) == 20000000) and (count < ((len(listOfFiles) // 20)*20)) :
#         files.to_csv(("ODIN2018_Studyarea_PC6_joineddata_" +str(count)+ ".csv"), index=False)
#         files = files.iloc[0]
#     elif count == (len(listOfFiles)-1) :
#         files.to_csv(("ODIN2018_Studyarea_PC6_joineddata_" +str(count)+ ".csv"), index=False)
#
# files = pd.read_csv(os.path.join(os.getcwd(), listOfFiles[80]))
# for count in range(81,100):
#     file = pd.read_csv(os.path.join(os.getcwd(), listOfFiles[count]))
#     files = pd.concat([files, file])
#     print(len(files.index))
#     if (len(files.index) == 20000000) and (count < ((len(listOfFiles) // 20)*20)) :
#         files.to_csv(("ODIN2018_Studyarea_PC6_joineddata_" +str(count)+ ".csv"), index=False)
#         files = files.iloc[0]
#     elif count == (len(listOfFiles)-1) :
#         files.to_csv(("ODIN2018_Studyarea_PC6_joineddata_" +str(count)+ ".csv"), index=False)
#
#
# files = pd.read_csv(os.path.join(os.getcwd(), listOfFiles[100]))
# for count in range(101,120):
#     file = pd.read_csv(os.path.join(os.getcwd(), listOfFiles[count]))
#     files = pd.concat([files, file])
#     print(len(files.index))
#     if (len(files.index) == 20000000) and (count < ((len(listOfFiles) // 20)*20)) :
#         files.to_csv(("ODIN2018_Studyarea_PC6_joineddata_" +str(count)+ ".csv"), index=False)
#         files = files.iloc[0]
#     elif count == (len(listOfFiles)-1) :
#         files.to_csv(("ODIN2018_Studyarea_PC6_joineddata_" +str(count)+ ".csv"), index=False)
#
#
# files = pd.read_csv(os.path.join(os.getcwd(), listOfFiles[120]))
# for count in range(121,140):
#     file = pd.read_csv(os.path.join(os.getcwd(), listOfFiles[count]))
#     files = pd.concat([files, file])
#     print(len(files.index))
#     if (len(files.index) == 20000000) and (count < ((len(listOfFiles) // 20)*20)) :
#         files.to_csv(("ODIN2018_Studyarea_PC6_joineddata_" +str(count)+ ".csv"), index=False)
#         files = files.iloc[0]
#     elif count == (len(listOfFiles)-1) :
#         files.to_csv(("ODIN2018_Studyarea_PC6_joineddata_" +str(count)+ ".csv"), index=False)
#
# files = pd.read_csv(os.path.join(os.getcwd(), listOfFiles[140]))
# for count in range(141,160):
#     file = pd.read_csv(os.path.join(os.getcwd(), listOfFiles[count]))
#     files = pd.concat([files, file])
#     print(len(files.index))
#     if (len(files.index) == 20000000) and (count < ((len(listOfFiles) // 20)*20)) :
#         files.to_csv(("ODIN2018_Studyarea_PC6_joineddata_" +str(count)+ ".csv"), index=False)
#         files = files.iloc[0]
#     elif count == (len(listOfFiles)-1) :
#         files.to_csv(("ODIN2018_Studyarea_PC6_joineddata_" +str(count)+ ".csv"), index=False)
# files = pd.read_csv(os.path.join(os.getcwd(), listOfFiles[160]))
# for count in range(161,168):
#     file = pd.read_csv(os.path.join(os.getcwd(), listOfFiles[count]))
#     files = pd.concat([files, file])
#     print(len(files.index))
#     if (len(files.index) == 20000000) and (count < ((len(listOfFiles) // 20)*20)) :
#         files.to_csv(("ODIN2018_Studyarea_PC6_joineddata_" +str(count)+ ".csv"), index=False)
#         files = files.iloc[0]
#     elif count == (len(listOfFiles)-1) :
#         files.to_csv(("ODIN2018_Studyarea_PC6_joineddata_" +str(count)+ ".csv"), index=False)



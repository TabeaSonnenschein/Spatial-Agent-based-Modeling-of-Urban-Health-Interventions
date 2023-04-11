import os
import pandas as pd
import numpy as np
import re
from math import floor, ceil
import nltk
nltk.download('wordnet')
from nltk.corpus import wordnet
pd.options.mode.chained_assignment = None  # default='warn'
from itertools import chain

############################################################################################################
## This script harmonizes synonymous variable names based on string similarity (using shared subword analysis and Jaro-Winkler distance)
## and semantic similarity (using the synonym function of nltk's wordnet package).
## Consequently, the variable name for the synonym cluster is identified based on which variable
## was mentioned most frequently (maximization) and in case of no single variable on top, based on string length (minimization)
## ATTENTION:
## This script has two modes. First a "manualCheck" mode, where the automatically harmonised variable name clusters
## are saved and can be manually checked/corrected.
## The second mode "readAndJoinControl" then reads the checked/corrected variable name clusters and joins it to
## the evidence dataframe, which is then saved with the replaced harmonised variable names.
#############################################################################################################

## Functions
def UniqueLabelsFreq(phraselist, variable_type):
    """Find unique Labels and count their frequency"""
    Labels, freq_Labels = [], []
    for instance in phraselist:
        Labels.extend(instance.split(" ; "))
    unique_Labels = list(dict.fromkeys(Labels))
    for Label in unique_Labels:
        freq_Labels.append(Labels.count(Label))
    return pd.DataFrame({variable_type: unique_Labels, 'Freq': freq_Labels})


# https://www.geeksforgeeks.org/jaro-and-jaro-winkler-similarity/
# Function to calculate the
# Jaro Similarity of two s
def jaro_distance(s1, s2):
    # If the s are equal
    if (s1 == s2):
        return 1.0

    # Length of two s
    len1 = len(s1)
    len2 = len(s2)

    # Maximum distance upto which matching
    # is allowed
    max_dist = floor(max(len1, len2) / 2) - 1

    # Count of matches
    match = 0

    # Hash for matches
    hash_s1 = [0] * len(s1)
    hash_s2 = [0] * len(s2)

    # Traverse through the first
    for i in range(len1):

        # Check if there is any matches
        for j in range(max(0, i - max_dist),
                       min(len2, i + max_dist + 1)):

            # If there is a match
            if (s1[i] == s2[j] and hash_s2[j] == 0):
                hash_s1[i] = 1
                hash_s2[j] = 1
                match += 1
                break

    # If there is no match
    if (match == 0):
        return 0.0

    # Number of transpositions
    t = 0
    point = 0

    # Count number of occurrences
    # where two characters match but
    # there is a third matched character
    # in between the indices
    for i in range(len1):
        if (hash_s1[i]):

            # Find the next matched character
            # in second
            while (hash_s2[point] == 0):
                point += 1

            if (s1[i] != s2[point]):
                t += 1
            point += 1
    t = t // 2

    # Return the Jaro Similarity
    return (match / len1 + match / len2 +
            (match - t) / match) / 3.0

# This code is contributed by mohit kumar 29


def StringSimilarityMatrixAcrossList_JaroWinkler(variable_names):
    '''This function takes a list of strings and computes the string similarity pairwise.
       The output is a matrix in which x and y axis represent the strings of the list,
       and the values their Jaro Winkler string similarity.'''
    variable_similarity = []
    for variable in variable_names:
        variable_data = []
        for compare_variable in variable_names:
            variable_data.append(jaro_distance(variable, compare_variable))
        variable_similarity.append(variable_data)
    variable_similarity_df = pd.DataFrame(data=variable_similarity, columns=variable_names)
    print(variable_similarity_df.head())
    return variable_similarity_df

def FindNounsInSubwords(subword_list_var):
    '''Identify Nouns in the Subwords and return their indices'''
    PosList = nltk.pos_tag(subword_list_var)
    Noun_idx = [index for index, item in enumerate(PosList) if item in ["NN", "NNP"]]
    return Noun_idx

def FindOtherVariablesWithSharedSubwords( subword_list_var, variable_names, self_index):
    '''This function finds other words that share subwords and ranks them based on how many subwords they share.
       Additionally, if there are words that only miss one word of the variable the variable is casted as eligible (for synonymity),
       and if there are words that contain all subwords of the word of analysis, it is casted as certain.'''
    shar_subword_varname, shar_subword_ID = [], []
    for word in subword_list_var:
        for count, value in enumerate(variable_names):
            if (word in value) and (count != self_index):
                shar_subword_varname.append(variable_names[count])
                shar_subword_ID.append(variables_df['orig_name_ID'].iloc[count])
    Ranking_most_similar_ID, Ranking_Nr_shared_words, Ranking_variable_name, Eligible, Certain = [], [], [], 0, 0
    Freq_table = pd.DataFrame(pd.Series(shar_subword_ID).value_counts())
    Ranking_most_similar_ID = "; ".join(Freq_table.index.values)
    Ranking_Nr_shared_words = "; ".join([str(el) for el in Freq_table.iloc[:,0]])
    Freq_table = pd.DataFrame(pd.Series(shar_subword_varname).value_counts())
    Ranking_variable_name = "; ".join(Freq_table.index.values)
    if len(Freq_table)>0 and (len(subword_list_var) - max(Freq_table.iloc[:,0])) <= 1:
        Eligible = 1
    if len(Freq_table)>0 and (len(subword_list_var) == max(Freq_table.iloc[:,0])):
        Certain = 1
    return Ranking_most_similar_ID, Ranking_Nr_shared_words, Ranking_variable_name, Eligible, Certain

def AddSharedSubwordsToAllVarOfDf(variables_df, variable_names):
    '''This functions adds shared subwords ranking variables to a complete dataframe.'''
    subword_list = [variable.split() for variable in variable_names]
    eligibility, certainty = [], []
    variables_df[['Nr_subwords','Ranking_most_similar_ID', 'Ranking_Nr_shared_words', 'Ranking_variable_name']] = ''
    for i in range(0,nr_variables):
        variables_df['Nr_subwords'].iloc[i] = len(subword_list[i])
        Ranking_most_similar_ID, Ranking_Nr_shared_words, Ranking_variable_name, Eligible, Certain = FindOtherVariablesWithSharedSubwords(subword_list[i], variable_names, self_index = i)
        variables_df['Ranking_most_similar_ID'].iloc[i] = Ranking_most_similar_ID
        variables_df['Ranking_Nr_shared_words'].iloc[i] = Ranking_Nr_shared_words
        variables_df['Ranking_variable_name'].iloc[i] = Ranking_variable_name
        eligibility.append(Eligible)
        certainty.append(Certain)
    variables_df = variables_df.assign(Eligible = eligibility, Certainty = certainty)
    print(variables_df)
    return variables_df

def GetIndicesOfValuesOverValue(df, column, value):
    ''' Retrieves the indices of cells in a column above a certain value.'''
    indices = list(df[df.iloc[:,column] > value].index.values)
    indices.remove(column)
    return indices

def RemoveRedundantCluster(variable_clusters):
    '''remove redudant clusters that are contained in other clusters'''
    for count, cluster in enumerate(variable_clusters):
        for otherclusters in (variable_clusters[:count] + variable_clusters[count + 1:]):
            if all(item in otherclusters for item in cluster):
                del variable_clusters[count]
    return variable_clusters

def ReturnClustersWithUniqueElements(variable_clusters):
    '''Reduces the clusters to its unique elements'''
    for count, cluster in enumerate(variable_clusters):
        variable_clusters[count] = list(dict.fromkeys(cluster))
    return variable_clusters

def GenerateVarClustersFromSynonymityMatrix(synonymity_matrix, variable_IDs):
    ''' This function takes a matrix of Xvariables times the same XVariables whereby 1 mean they are synonymous or not.
        Consequently the function returns a list of lists, with sublists representing the clusters.'''
    variable_clusters = []
    for count, value in enumerate(variable_IDs):
        indices = list(np.where(synonymity_matrix.iloc[:, count] == 1)[0])
        variables = [value] + [variable_IDs[el] for el in indices]
        if any(True for var in variables for cluster in variable_clusters if var in cluster):
            cluster_idx = [cluster_idx for cluster_idx, cluster in enumerate(variable_clusters) for var in variables if var in cluster]
            variable_clusters[cluster_idx[0]].extend(variables)
        else:
            variable_clusters.append(variables)
    return ReturnClustersWithUniqueElements(variable_clusters)


def IdentifyClusterVariableName(Var_df, ClusterID, VarColName):
    '''Identifying the best variable name for the synonym cluster based on the frequency
       that it was mentioned in the evidence across studies (maximization)
       and the length of the string (minization).'''
    subset = Cluster_df[Var_df['ClusterID'] == ClusterID]
    if len(subset.index) > 1:
        VarHarmon_df['Synonyms'].iloc[count] = "; ".join(subset[VarColName])
        if max(subset['Freq']) > 3:
            maxFreq_idx = [index for index, item in enumerate(subset['Freq']) if item == max(subset['Freq'])]
            if len(maxFreq_idx) > 1:
                maxQuota_idx = [index for index, item in enumerate(subset['AssignedWords_NrWords_freq_Quota'].iloc[maxFreq_idx]) if
                              item == max(subset['AssignedWords_NrWords_freq_Quota'].iloc[maxFreq_idx])]
                VarID = subset['orig_name_ID'].iloc[maxFreq_idx[maxQuota_idx[0]]]
                VarName = subset[VarColName].iloc[maxFreq_idx[maxQuota_idx[0]]]
            else:
                VarID = subset['orig_name_ID'].iloc[maxFreq_idx[0]]
                VarName = subset[VarColName].iloc[maxFreq_idx[0]]
        else:
            maxFreq_idx = [index for index, item in enumerate(subset['AssignedWords_NrWords_freq_Quota']) if
                           item == max(subset['AssignedWords_NrWords_freq_Quota'])]
            if len(maxFreq_idx) > 1:
                minLen_idx = [index for index, item in enumerate(subset['Str_Length'].iloc[maxFreq_idx]) if
                              item == min(subset['Str_Length'].iloc[maxFreq_idx])]
                VarID = subset['orig_name_ID'].iloc[maxFreq_idx[minLen_idx[0]]]
                VarName = subset[VarColName].iloc[maxFreq_idx[minLen_idx[0]]]
            else:
                VarID = subset['orig_name_ID'].iloc[maxFreq_idx[0]]
                VarName = subset[VarColName].iloc[maxFreq_idx[0]]
    else:
        VarID = subset['orig_name_ID'].iloc[0]
        VarName = subset[VarColName].iloc[0]
    return VarID, VarName

############################################################
##### Execution ############################################
############################################################
os.chdir(r"D:\PhD EXPANSE\Written Paper\02- Behavioural Model paper")
# filename = "unique_evidence_instances_clean2_harmonised_BO_manualclean"
filename = "unique_evidence_instances_clean2_harmonised_BO_manualclean_BD_unique"
evidence_instances_full = pd.read_csv(filename + ".csv")

##################################################################################################
# mode = "manualCheck"   # uncomment this when at the stage of checking the variable harmonisation
mode = "readAndJoinControl"  # uncomment this when having controled the results to join to df
##################################################################################################

# variable_type = "BehaviorDeterminant"
# TypeAbbrev = "BD"

variable_type = "Studygroup"
TypeAbbrev = "SG"
evidence_instances_full[variable_type] = [el.lower() for el in evidence_instances_full[variable_type]]

if mode == "manualCheck":
    if variable_type == "Studygroup":
        origvarlist = list(chain.from_iterable([el.replace("['", ""). replace("']", "").split("', '") for el in evidence_instances_full[variable_type] if el != "-100"]))
        print(origvarlist)
    else:
        origvarlist = evidence_instances_full[variable_type]
    variables_df = UniqueLabelsFreq(origvarlist, variable_type)

    variables_df.insert(0, 'orig_name_ID',  ['ON_'+ str(i) for i in range(1,len(variables_df.iloc[:,0])+1)])
    variable_names = list(variables_df.iloc[:, 1])
    variable_names = [x.lower() for x in variable_names]
    nr_variables = len(variable_names)
    variable_IDs = variables_df.iloc[:,0]
    variables_df['subwords'] = ["; ".join(variable.split()) for variable in variable_names]
    print(variables_df.head())

    variables_df = AddSharedSubwordsToAllVarOfDf(variables_df, variable_names)
    variable_similarity_df = StringSimilarityMatrixAcrossList_JaroWinkler(variable_names)

    JWsim_80plus_names,JWsim_80plus_IDs, JWsim_85plus_names, JWsim_85plus_IDs, JWsim_90plus_names, JWsim_90plus_IDs, dominant = [], [], [], [], [], [], []
    for count, value in enumerate(variable_names):
        indices = GetIndicesOfValuesOverValue(variable_similarity_df, count, 0.8)
        JWsim_80plus_names.append("; ".join([variable_names[index] for index in indices]))
        JWsim_80plus_IDs.append("; ".join([variable_IDs[index] for index in indices]))
        indices = GetIndicesOfValuesOverValue(variable_similarity_df, count, 0.85)
        JWsim_85plus_names.append("; ".join([variable_names[index] for index in indices]))
        JWsim_85plus_IDs.append("; ".join([variable_IDs[index] for index in indices]))
        indices = GetIndicesOfValuesOverValue(variable_similarity_df, count, 0.9)
        JWsim_90plus_names.append("; ".join([variable_names[index] for index in indices]))
        JWsim_90plus_IDs.append("; ".join([variable_IDs[index] for index in indices]))

    variables_df = variables_df.assign(JWsim_80plus_names = JWsim_80plus_names,
                        JWsim_80plus_IDs = JWsim_80plus_IDs,
                        JWsim_85plus_names = JWsim_85plus_names,
                        JWsim_85plus_IDs = JWsim_85plus_IDs,
                        JWsim_90plus_names = JWsim_90plus_names,
                        JWsim_90plus_IDs = JWsim_90plus_IDs)



    ## Assigning Synonymity
    synonymity_df =  pd.DataFrame(data = 0, columns= variable_IDs,
                      index=variable_IDs)

    for count, value in enumerate(variable_IDs):
        if variables_df["Certainty"].iloc[count] == 1:
            candidates = variables_df["Ranking_most_similar_ID"].iloc[count].split("; ")
            candidates_freq = [int(el) for el in variables_df["Ranking_Nr_shared_words"].iloc[count].split("; ")]
            Nr = [index for index, item in enumerate(candidates_freq) if item == max(candidates_freq)]
            winners = [candidates[el] for el in Nr]
            if variables_df["Nr_subwords"].iloc[count] > 1: #if more than one word is shared
                synonymity_df.loc[value, winners] = 1
            elif len(winners) <= 5 : # if only one word is shared (substring) but both words are one  or two words long
                NrSubwords = [variables_df.loc[variables_df[variables_df['orig_name_ID'] == el].index, "Nr_subwords"].values[0] for el in winners]
                singleWordVar = [candidates[el] for el in [index for index, item in enumerate(NrSubwords) if item < 3]]
                synonymity_df.loc[value, singleWordVar] = 1

        elif variables_df["Eligible"].iloc[count] == 1:
            candidates = variables_df["Ranking_most_similar_ID"].iloc[count].split("; ")
            candidates_freq = [int(el) for el in variables_df["Ranking_Nr_shared_words"].iloc[count].split("; ")]
            Nr = [index for index, item in enumerate(candidates_freq) if item == max(candidates_freq)]
            winners = [candidates[el] for el in Nr]
            # check if the word that is different is a synonym
            candidate_subwords = [str(variables_df.loc[variables_df[variables_df['orig_name_ID'] == el].index, "subwords"].values[0]).split("; ") for el in winners]
            own_subwords = str(variables_df[variable_type].iloc[count]).split(" ")
            for number, subwordlist in enumerate(candidate_subwords):
                for word in own_subwords:
                    if not(word in subwordlist) and not(any(True for subword in subwordlist if word in subword)):
                        syno_antonyms = []
                        for syn in wordnet.synsets(word):
                            for i in syn.lemmas():
                                syno_antonyms.append(i.name())
                                if i.antonyms():
                                    syno_antonyms.append(i.antonyms()[0].name())
                        if any(True for synonym in syno_antonyms if synonym in subwordlist) :
                            synonymity_df.loc[value, winners[number]] = 1
                            print("orig", own_subwords, "candit", subwordlist, "contains one of:", syno_antonyms)

            if variables_df["Nr_subwords"].iloc[count] >= 3:     ### For long words two word synonymity matching
                Nr = [index for index, item in enumerate(candidates_freq) if item == (variables_df["Nr_subwords"].iloc[count] - 2)]
                winners = [candidates[el] for el in Nr]
                # check if the 2 words that are different are synonyms
                candidate_subwords = [str(variables_df.loc[variables_df[variables_df['orig_name_ID'] == el].index, "subwords"].values[0]).split("; ") for el in winners]
                own_subwords = str(variables_df[variable_type].iloc[count]).split(" ")
                for number, subwordlist in enumerate(candidate_subwords):
                    synonym_number = 0
                    excess_subwords = [word for word in subwordlist if (not(word in own_subwords) and not(any(True for ownword in own_subwords if ownword in word)))]
                    for word in own_subwords:
                        if not(word in subwordlist) and not(any(True for subword in subwordlist if word in subword)):
                            if word in ["of", "to", "in"]:
                                synonym_number = synonym_number + 1
                            else:
                                syno_antonyms = []
                                for syn in wordnet.synsets(word):
                                    for i in syn.lemmas():
                                        syno_antonyms.append(i.name())
                                        if i.antonyms():
                                            syno_antonyms.append(i.antonyms()[0].name())
                                # if any(True for synonym in syno_antonyms if synonym in excess_subwords) or any(True for synonym in syno_antonyms for subword in excess_subwords if ((subword in synonym) and (len(subword) > 3))):
                                if any(True for synonym in syno_antonyms if synonym in excess_subwords):
                                    synonym_number = synonym_number + 1
                            if synonym_number == 2:
                                synonymity_df.loc[value, winners[number]] = 1
                                print("orig", own_subwords, "candit", subwordlist, excess_subwords, "contains one of:", syno_antonyms)

        if variables_df['JWsim_90plus_IDs'].iloc[count] and (variables_df['Nr_subwords'].iloc[count] > 1):
            winners = variables_df['JWsim_90plus_IDs'].iloc[count].split("; ")
            synonymity_df.loc[value, winners] = 1

        if variables_df["Nr_subwords"].iloc[count] == 1: #direct synonyms of single word variables
            synonyms = []
            for syn in wordnet.synsets(str(variables_df[variable_type].iloc[count])):
                for i in syn.lemmas():
                    synonyms.append(i.name())
            winners = [number for number, var in enumerate(variable_names) if var in synonyms and var != variables_df[variable_type].iloc[count]]
            if len(winners) > 0:
                synonymity_df.loc[value, [variable_IDs[el] for el in winners]] = 1


    csv = os.path.join(os.getcwd(), (variable_type + "_synonymity_NEW.csv"))
    synonymity_df.to_csv(csv, index=False)

    variables_df["NrAssignedSynonyms"] = list(synonymity_df.sum(axis = 1))
    variables_df["NrAssignedSynonyms"] = list(synonymity_df.sum(axis = 1))

    ## Identifying Clusters
    variable_clusters = GenerateVarClustersFromSynonymityMatrix(synonymity_df, variable_IDs)
    variable_clusters = RemoveRedundantCluster(variable_clusters)

    variables_df["ClusterID"] = "NaN"
    variables_df.index = variables_df["orig_name_ID"]
    variable_clusters_names = []
    for count, cluster in enumerate(variable_clusters):
        variable_clusters_names.append(list(variables_df.loc[cluster, variable_type]))
        variables_df.loc[cluster, "ClusterID"] = count

    print(variable_clusters_names)

    variables_df = variables_df.sort_values(by=['ClusterID'])
    variables_df['AssignedWords_NrWords_freq_Quota'] = (variables_df['NrAssignedSynonyms']*variables_df['Nr_subwords']) + variables_df['Freq']
    variables_df.to_csv(os.path.join(os.getcwd(), (variable_type + "_clusters.csv")), index=False)

    Cluster_df = variables_df[['ClusterID', 'orig_name_ID', variable_type, 'Freq', 'NrAssignedSynonyms', 'Nr_subwords', 'AssignedWords_NrWords_freq_Quota']]
    Cluster_df['Str_Length'] = Cluster_df[variable_type].str.len()


    ## Identify the variable name for synonymous cluster based on frequency of mentions and stringlength
    VarHarmon_df = pd.DataFrame(Cluster_df['ClusterID'])
    VarHarmon_df.drop_duplicates(inplace=True)
    VarHarmon_df = VarHarmon_df.assign(VarID = '', VarName = '', Synonyms = '')
    for count, value in enumerate(VarHarmon_df['ClusterID']):
        VarHarmon_df['VarID'].iloc[count], VarHarmon_df['VarName'].iloc[count] = IdentifyClusterVariableName(Cluster_df, value, variable_type)

    ## write the data
    VarHarmon_df.to_csv(os.path.join(os.getcwd(), (variable_type + "_HarmonVar.csv")), index=False)

    Cluster_df = pd.merge(Cluster_df, VarHarmon_df[['ClusterID', 'VarID', 'VarName']], on="ClusterID")
    Cluster_df.to_csv(os.path.join(os.getcwd(), (variable_type + "_clusters_clean.csv")), index=False)

elif mode == "readAndJoinControl":
    ## read the controlled/corrected harmonised variables
    Cluster_df = pd.read_csv(os.path.join(os.getcwd(), (variable_type + "_clusters_clean.csv")))
    if variable_type == "Studygroup":
        evidence_instances_full = pd.merge(evidence_instances_full, Cluster_df[[variable_type, 'VarName']], how= "left",
                                           on=variable_type)
        listSGs = [idx for idx, value in enumerate(evidence_instances_full[variable_type]) if "[" in value]
        for idx in listSGs:
            subwords = evidence_instances_full[variable_type].iloc[idx].replace("['", ""). replace("']", "").split("', '")
            evidence_instances_full['VarName'].iloc[idx]  = "['" + "', '".join(Cluster_df['VarName'].loc[Cluster_df[variable_type].isin(subwords)]) + "']"
        evidence_instances_full['VarName'] = evidence_instances_full['VarName'].fillna("-100")
    else:
        evidence_instances_full = pd.merge(evidence_instances_full, Cluster_df[[variable_type,'VarName' ]], on= variable_type)
    evidence_instances_full["Sentence_int"] =[int(el.replace("Sentence: ", "")) for el in evidence_instances_full["Sentence"]]
    evidence_instances_full.sort_values(by = ["DOI", "Sentence_int"]).to_csv(os.path.join(os.getcwd(), (filename + "_" + TypeAbbrev + ".csv")), index=False)

    ## save unique instances with harmon names
    col = list(evidence_instances_full.columns.values)
    print(col)
    col.remove(variable_type)

    evidence_instances_full = evidence_instances_full[col]
    evidence_instances_full.columns = list(map(lambda x: x.replace('VarName', variable_type), col))
    evidence_instances_full.drop_duplicates(inplace=True)
    evidence_instances_full.to_csv(os.path.join(os.getcwd(), (filename + "_" + TypeAbbrev + "_unique.csv")), index=False)

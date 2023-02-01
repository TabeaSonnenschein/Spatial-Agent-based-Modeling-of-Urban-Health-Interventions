import os
import pandas as pd
import numpy as np
import re
from math import floor, ceil

## reading the significant variable names extracted from all papers
## applying string similarity measures (levensthein distance... johan winkler...)
## apply network distance measures using open source wordnet network

os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Written Paper\02- Behavioural Model paper")
variable_type = "BehaviorDeterminants"
variables_df = pd.read_csv("unique_" + variable_type + ".csv")
variables_df.insert(0, 'orig_name_ID',  ['ON_'+ str(i) for i in range(1,len(variables_df.iloc[:,0])+1)])
print(variables_df.head())

variable_names = list(variables_df.iloc[:, 1])
variable_names = [x.lower() for x in variable_names]
print(variable_names)
nr_variables = len(variable_names)

variables_df['subwords'] = ["; ".join(variable.split()) for variable in variable_names]
print(variables_df.head())
subword_list = [variable.split() for variable in variable_names]
print(subword_list)

variables_df[['shared_subwords_VarN', 'shared_subwords_VarID']] = ''
for i in range(0,nr_variables):
    shar_subword_varname, shar_subword_ID = [], []
    for word in subword_list[i]:
        for count, value in enumerate(subword_list):
            if (word in value) and (count != i):
                shar_subword_varname.append(variable_names[count])
                shar_subword_ID.append(variables_df['orig_name_ID'].iloc[count])
    variables_df['shared_subwords_VarN'].iloc[i] = "; ".join(shar_subword_varname)
    variables_df['shared_subwords_VarID'].iloc[i] = "; ".join(shar_subword_ID)

print(variables_df)


# https://www.datacamp.com/community/tutorials/fuzzy-string-python
def levenshtein_ratio_and_distance(s, t, ratio_calc = False):
    """ levenshtein_ratio_and_distance:
        Calculates levenshtein distance between two strings.
        If ratio_calc = True, the function computes the
        levenshtein distance ratio of similarity between two strings
        For all i and j, distance[i,j] will contain the Levenshtein
        distance between the first i characters of s and the
        first j characters of t
    """
    # Initialize matrix of zeros
    rows = len(s)+1
    cols = len(t)+1
    distance = np.zeros((rows,cols),dtype = int)

    # Populate matrix of zeros with the indeces of each character of both strings
    for i in range(1, rows):
        for k in range(1,cols):
            distance[i][0] = i
            distance[0][k] = k

    # Iterate over the matrix to compute the cost of deletions,insertions and/or substitutions
    for col in range(1, cols):
        for row in range(1, rows):
            if s[row-1] == t[col-1]:
                cost = 0 # If the characters are the same in the two strings in a given position [i,j] then the cost is 0
            else:
                # In order to align the results with those of the Python Levenshtein package, if we choose to calculate the ratio
                # the cost of a substitution is 2. If we calculate just distance, then the cost of a substitution is 1.
                if ratio_calc == True:
                    cost = 2
                else:
                    cost = 1
            distance[row][col] = min(distance[row-1][col] + 1,      # Cost of deletions
                                 distance[row][col-1] + 1,          # Cost of insertions
                                 distance[row-1][col-1] + cost)     # Cost of substitutions
    if ratio_calc == True:
        # Computation of the Levenshtein Distance Ratio
        Ratio = ((len(s)+len(t)) - distance[row][col]) / (len(s)+len(t))
        return Ratio
    else:
        # print(distance) # Uncomment if you want to see the matrix showing how the algorithm computes the cost of deletions,
        # insertions and/or substitutions
        # This is the minimum number of edits needed to convert string a to string b
        return distance[row][col]



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


variable_similarity = []
for variable in variable_names:
    variable_data = []
    for compare_variable in variable_names:
        variable_data.append(levenshtein_ratio_and_distance(variable, compare_variable))
    variable_similarity.append(variable_data)

# print(variable_similarity)

variable_similarity_Levenshtein_df = pd.DataFrame(data=variable_similarity, columns=variable_names)
variable_similarity_Levenshtein_df.insert(0, "variablename", variable_names)
print(variable_similarity_Levenshtein_df.head())
csv = os.path.join(os.getcwd(), (variable_type + "_LevenshteinDST.csv"))
variable_similarity_Levenshtein_df.to_csv(csv, index=False)



variables_df[['similar_VarN_LS', 'similar_VarID_LS','similar_VarIndx_LS', 'similar_Var_LSD']] = ''

for i in range(0,nr_variables):
    sim_varN, sim_varId, sim_varindx, sim_var_LSD = [], [], [], []
    if len(variable_similarity_Levenshtein_df.iloc[i, 0]) > 6:
        max_LSD = 3
    else:
        max_LSD = 1
    for n in range(1, nr_variables+1):
        if (n != i+1) and variable_similarity_Levenshtein_df.iloc[i,n] <= max_LSD and len(variable_similarity_Levenshtein_df.iloc[i,0])>5:
            sim_varindx.append(str(n-1))
            sim_varN.append(variable_names[n-1])
            sim_varId.append(variables_df['orig_name_ID'].iloc[n-1])
            sim_var_LSD.append(str(variable_similarity_Levenshtein_df.iloc[i,n]))
    variables_df['similar_VarN_LS'].iloc[i] = "; ".join(sim_varN)
    variables_df['similar_VarID_LS'].iloc[i] = "; ".join(sim_varId)
    variables_df['similar_VarIndx_LS'].iloc[i] = "; ".join(sim_varindx)
    variables_df['similar_Var_LSD'].iloc[i] = "; ".join(sim_var_LSD)


csv = os.path.join(os.getcwd(), (variable_type + "_similarwords_LSD.csv"))
variables_df.to_csv(csv, index=False)

#
# variable_similarity = []
# for variable in variable_names:
#     variable_data = []
#     for compare_variable in variable_names:
#         variable_data.append(jaro_distance(variable, compare_variable))
#     variable_similarity.append(variable_data)
#
# variable_similarity_Jaro_df = pd.DataFrame(data=variable_similarity, columns=variable_names)
# #variable_similarity_df.index.values = variable_names
# print(variable_similarity_Jaro_df.head())
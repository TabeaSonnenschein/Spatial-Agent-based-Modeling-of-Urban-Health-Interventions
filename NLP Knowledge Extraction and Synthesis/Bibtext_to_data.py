import pandas as pd
import re

# set working directory
import os
os.chdir("C:/Users/Tabea/Documents/PhD EXPANSE/Written Paper/02- Behavioural Model paper/modalchoice literature search")

# read in csv file
ref_data = pd.read_csv("search5_reference_data.csv")

# find the number of rows where the "file" column starts with "file"
len = len(ref_data.loc[ref_data['file'].str.startswith("file", na=False)])

# create a new dataframe with 14 columns and len rows
ref_data_clean = pd.DataFrame(index=range(len), columns=["article_id", "doc_type", "title", "abstract", "author", "doi", "file", "issn", "journal", "keywords", "number", "pages", "volume", "year"])

# find the rows where the "file" column starts with "}"
endings = ref_data.loc[ref_data['file'].str.startswith("}", na=False)].index.tolist()

# assign the article_id column of ref_data_clean to the first row of ref_data and every row after an ending
ref_data_clean['article_id'] = ref_data.iloc[[0]+endings[:-1]+1]['file']

# find the rows in article_id where the value starts with "@article"
ref_data_clean.loc[ref_data_clean['article_id'].str.startswith("@article", na=False), 'doc_type'] = "article"
# find the rows in article_id where the value starts with "@book"
ref_data_clean.loc[ref_data_clean['article_id'].str.startswith("@book", na=False), 'doc_type'] = "book"

# remove "@article{" and "@book{" from the article_id column
ref_data_clean['article_id'] = ref_data_clean['article_id'].str.replace("@article{","").str.replace("@book{","")

for i in range(len(ref_data_clean)):
    # assign the current_p and next_p variables
    current_p = [0]+endings[:-1]+1)[i]
    next_p = [0]+endings[:-1]+1)[i+1]
    paper_info = ref_data.iloc[current_p:next_p]['file']
    ref_data_clean.loc[i,'file'] = paper_info[paper_info.str.startswith("file", na=False)].iloc[0]
    ref_data_clean.loc[i,'title'] = paper_info[paper_info.str.startswith("title", na=False)].iloc[0]
    if paper_info.str.startswith("abstract", na=False).any():
        ref_data



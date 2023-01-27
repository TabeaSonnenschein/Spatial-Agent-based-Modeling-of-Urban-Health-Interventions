import pandas as pd
import os

# set working directory
os.chdir("D:/PhD EXPANSE/Written Paper/02- Behavioural Model paper/modalchoice literature search")

# read in csv file
ref_data = pd.read_csv("search5_reference_data.csv")

# find the number of rows where the "file" column starts with "file"
len = len(ref_data.loc[ref_data['input'].str.startswith("file", na=False)])

# create a new dataframe with 14 columns and len rows
ref_data_clean = pd.DataFrame(index=range(len), columns=["article_id", "doc_type", "title", "abstract", "author", "doi", "file", "issn", "journal", "keywords", "number", "pages", "volume", "year"])

# find the rows where the "file" column starts with "}"
endings = ref_data.loc[ref_data['input'].str.startswith("}", na=False)].index.tolist()
endings.insert(0, -1)
print(endings)

# assign the article_id column of ref_data_clean to the first row of ref_data and every row after an ending
ref_data_clean['article_id'] = list(ref_data['input'].iloc[[i+1 for i in endings[:-1]]])

# find the rows in article_id where the value starts with "@article"
ref_data_clean.loc[ref_data_clean['article_id'].str.startswith("@article", na=False), 'doc_type'] = "article"

# find the rows in article_id where the value starts with "@book"
ref_data_clean.loc[ref_data_clean['article_id'].str.startswith("@book", na=False), 'doc_type'] = "book"
print(ref_data_clean['doc_type'])

# remove "@article{" and "@book{" from the article_id column
ref_data_clean['article_id'] = ref_data_clean['article_id'].str.replace("@article{","").str.replace("@book{","")

print(ref_data_clean)

for i in range(len):
    print(i)
    # assign the current_p and next_p variables
    current_p = endings[i]
    print(current_p)
    next_p = endings[i+1]
    paper_info = ref_data['input'].iloc[(current_p+1):(next_p+1)]
    print(paper_info)
    ref_data_clean.loc[i,'file'] = paper_info[paper_info.str.startswith("file", na=False)].iloc[0]
    ref_data_clean.loc[i,'title'] = paper_info[paper_info.str.startswith("title", na=False)].iloc[0]
    if paper_info.str.startswith("abstract", na=False).any():
        ref_data_clean.loc[i,'abstract']  = paper_info[paper_info.str.startswith("abstract", na=False)].iloc[0]
    if paper_info.str.startswith("journal", na=False).any():
        ref_data_clean.loc[i,'journal']  = paper_info[paper_info.str.startswith("journal", na=False)].iloc[0]
    if paper_info.str.startswith("keywords", na=False).any():
        ref_data_clean.loc[i,'keywords']  = paper_info[paper_info.str.startswith("keywords", na=False)].iloc[0]
    if paper_info.str.startswith("doi", na=False).any():
        ref_data_clean.loc[i,'doi']  = paper_info[paper_info.str.startswith("doi", na=False)].iloc[0]
    if paper_info.str.startswith("author", na=False).any():
        ref_data_clean.loc[i,'author']  = paper_info[paper_info.str.startswith("author", na=False)].iloc[0]
    if paper_info.str.startswith("issn", na=False).any():
        ref_data_clean.loc[i,'issn']  = paper_info[paper_info.str.startswith("issn", na=False)].iloc[0]
    if paper_info.str.startswith("number", na=False).any():
        ref_data_clean.loc[i,'number']  = paper_info[paper_info.str.startswith("number", na=False)].iloc[0]
    if paper_info.str.startswith("pages", na=False).any():
        ref_data_clean.loc[i,'pages']  = paper_info[paper_info.str.startswith("pages", na=False)].iloc[0]
    if paper_info.str.startswith("volume", na=False).any():
        ref_data_clean.loc[i,'volume']  = paper_info[paper_info.str.startswith("volume", na=False)].iloc[0]
    if paper_info.str.startswith("year", na=False).any():
        ref_data_clean.loc[i,'year']  = paper_info[paper_info.str.startswith("year", na=False)].iloc[0]

print(ref_data_clean)

ref_data_clean['title'] = ref_data_clean['title'].apply(lambda x: x.replace("title = {{", "").replace("}},", ""))
ref_data_clean['abstract'] = ref_data_clean['abstract'].apply(lambda x: x.replace("abstract = {", "").replace("},", ""))
ref_data_clean['title'] = ref_data_clean['title'].apply(lambda x: x.replace('title = {{', '').replace('}}', ''))
ref_data_clean['abstract'] = ref_data_clean['abstract'].apply(lambda x: x.replace('abstract = {', '').replace('},', ''))
ref_data_clean['file'] = ref_data_clean['file'].apply(lambda x: x.replace('file = {:', '').replace(':pdf},', ''))
ref_data_clean['file_name'] = ref_data_clean['file'].apply(lambda x: x.replace('C\:/Users/Tabea/Documents/PhD EXPANSE/Literature/WOS_ModalChoice_Ref/CrossrefResults/pdf/', ''))
ref_data_clean['author'] = ref_data_clean['author'].apply(lambda x: str(x).replace('author = {', '').replace('},', ''))
ref_data_clean['doi'] = ref_data_clean['doi'].apply(lambda x: str(x).replace('doi = {', '').replace('},', ''))
ref_data_clean['issn'] = ref_data_clean['issn'].apply(lambda x: str(x).replace('issn = {', '').replace('},', ''))
ref_data_clean['journal'] = ref_data_clean['journal'].apply(lambda x: str(x).replace('journal = {', '').replace('},', ''))
ref_data_clean['volume'] = ref_data_clean['volume'].apply(lambda x: str(x).replace('volume = {', '').replace('},', ''))
ref_data_clean['number'] = ref_data_clean['number'].apply(lambda x: str(x).replace('number = {', '').replace('},', ''))
ref_data_clean['keywords'] = ref_data_clean['keywords'].apply(lambda x: str(x).replace('keywords = {', '').replace('},', ''))
ref_data_clean['year'] = ref_data_clean['year'].apply(lambda x: str(x).replace('year = {', '').replace('}', ''))
ref_data_clean['pages'] = ref_data_clean['pages'].apply(lambda x: str(x).replace('pages = {', '').replace('},', ''))

print(ref_data_clean)

# Write to CSV file
ref_data_clean.to_csv("ref_data5_cleanNEW.csv", index=False)


# join with Web of Science Bibliometric Data
WOS_details = pd.read_csv("WOS_references_search5_metareviews.csv")
WOS_details.rename(columns={'DOI': 'doi'}, inplace=True)
reference_details = pd.merge(WOS_details, ref_data_clean, on='doi')
reference_details.to_csv("metareview_details2.csv", index=False)
print(reference_details)

reference_details_short = WOS_details[["doi", "citation", "Publication Year", "Source Title", "Article Title"]]
reference_details_short.to_csv("metareview_details_short.csv", index=False)

ref_ids = ref_data_clean[["article_id", "doi", "file_name"]]
ref_ids.to_csv("ref_ids.csv", index=False)

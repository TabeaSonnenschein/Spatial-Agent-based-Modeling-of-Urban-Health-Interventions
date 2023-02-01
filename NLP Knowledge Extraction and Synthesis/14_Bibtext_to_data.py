import pandas as pd
import os

###########################################################################
## Translate a bibtex copy to a csv file into a bibliometric dataframe.
## Join it with the Web of Science bibliometric file.
## The output file can be used for populating the ontology with bibliometric data
###############################################################################

## Functions
def findNrArticlesAndEndings(ref_data):
    """find the number of rows where the "file" column starts with file.
       find the rows where the "file" column starts with }"""
    length = len(ref_data.loc[ref_data['input'].str.startswith("file", na=False)])
    endings = ref_data.loc[ref_data['input'].str.startswith("}", na=False)].index.tolist()
    endings.insert(0, -1)
    return length, endings

def CreateDfOfArticles(ref_data, len, endings):
    """Create a dataframe of the articles and all the columns for the bibtex info.
       Assign the article id and doctype. Remove "@article{" and @book{ from the article_id column"""
    df = pd.DataFrame(index=range(len),columns=["article_id", "doc_type", "title", "abstract", "author", "doi", "file",
                                           "issn", "journal", "keywords", "number", "pages", "volume", "year"])
    df['article_id'] = list(ref_data['input'].iloc[[i+1 for i in endings[:-1]]])
    df.loc[df['article_id'].str.startswith("@article", na=False), 'doc_type'] = "article"
    df.loc[df['article_id'].str.startswith("@book", na=False), 'doc_type'] = "book"
    df['article_id'] = df['article_id'].str.replace("@article{", "").str.replace("@book{", "").str.replace(",", "").str.replace("{", "")
    return df


def extractInfoperPaper(target_df,len, endings):
    """Extracts the information from the bibtex string for each paper based
       on the variable keys."""
    for i in range(len):
        # assign the current_p and next_p variables
        current_p = endings[i]
        next_p = endings[i + 1]
        paper_info = ref_data['input'].iloc[(current_p + 1):(next_p + 1)]
        print(paper_info)
        target_df.loc[i, 'file'] = paper_info[paper_info.str.startswith("file", na=False)].iloc[0]
        target_df.loc[i, 'title'] = paper_info[paper_info.str.startswith("title", na=False)].iloc[0]
        if paper_info.str.startswith("abstract", na=False).any():
            target_df.loc[i, 'abstract'] = paper_info[paper_info.str.startswith("abstract", na=False)].iloc[0]
        if paper_info.str.startswith("journal", na=False).any():
            target_df.loc[i, 'journal'] = paper_info[paper_info.str.startswith("journal", na=False)].iloc[0]
        if paper_info.str.startswith("keywords", na=False).any():
            target_df.loc[i, 'keywords'] = paper_info[paper_info.str.startswith("keywords", na=False)].iloc[0]
        if paper_info.str.startswith("doi", na=False).any():
            target_df.loc[i, 'doi'] = paper_info[paper_info.str.startswith("doi", na=False)].iloc[0]
        if paper_info.str.startswith("author", na=False).any():
            target_df.loc[i, 'author'] = paper_info[paper_info.str.startswith("author", na=False)].iloc[0]
        if paper_info.str.startswith("issn", na=False).any():
            target_df.loc[i, 'issn'] = paper_info[paper_info.str.startswith("issn", na=False)].iloc[0]
        if paper_info.str.startswith("number", na=False).any():
            target_df.loc[i, 'number'] = paper_info[paper_info.str.startswith("number", na=False)].iloc[0]
        if paper_info.str.startswith("pages", na=False).any():
            target_df.loc[i, 'pages'] = paper_info[paper_info.str.startswith("pages", na=False)].iloc[0]
        if paper_info.str.startswith("volume", na=False).any():
            target_df.loc[i, 'volume'] = paper_info[paper_info.str.startswith("volume", na=False)].iloc[0]
        if paper_info.str.startswith("year", na=False).any():
            target_df.loc[i, 'year'] = paper_info[paper_info.str.startswith("year", na=False)].iloc[0]
    return target_df

def cleanBibtexNoise(df):
    """Removes the variable definitions in the Bibtex strings."""
    df['title'] = df['title'].apply(lambda x: x.replace("title = {{", "").replace("}},", ""))
    df['abstract'] = df['abstract'].apply(lambda x: x.replace("abstract = {", "").replace("},", ""))
    df['title'] = df['title'].apply(lambda x: x.replace('title = {{', '').replace('}}', ''))
    df['abstract'] = df['abstract'].apply(lambda x: x.replace('abstract = {', '').replace('},', ''))
    df['file'] = df['file'].apply(lambda x: x.replace('file = {:', '').replace(':pdf},', ''))
    df['file_name'] = df['file'].apply(lambda x: x.replace('C\:/Users/Tabea/Documents/PhD EXPANSE/Literature/WOS_ModalChoice_Ref/CrossrefResults/pdf/',''))
    df['author'] = df['author'].apply(lambda x: str(x).replace('author = {', '').replace('},', ''))
    df['doi'] = df['doi'].apply(lambda x: str(x).replace('doi = {', '').replace('},', ''))
    df['issn'] = df['issn'].apply(lambda x: str(x).replace('issn = {', '').replace('},', ''))
    df['journal'] = df['journal'].apply(lambda x: str(x).replace('journal = {', '').replace('},', ''))
    df['volume'] = df['volume'].apply(lambda x: str(x).replace('volume = {', '').replace('},', ''))
    df['number'] = df['number'].apply(lambda x: str(x).replace('number = {', '').replace('},', ''))
    df['keywords'] = df['keywords'].apply(lambda x: str(x).replace('keywords = {', '').replace('},', ''))
    df['year'] = df['year'].apply(lambda x: str(x).replace('year = {', '').replace('}', ''))
    df['pages'] = df['pages'].apply(lambda x: str(x).replace('pages = {', '').replace('},', ''))
    return df


## Execution
# read in csv file
os.chdir("D:/PhD EXPANSE/Written Paper/02- Behavioural Model paper/modalchoice literature search")
ref_data = pd.read_csv("search5_reference_data.csv")

length, endings = findNrArticlesAndEndings(ref_data)
ref_data_clean = CreateDfOfArticles(ref_data, length, endings)
print(ref_data_clean)
ref_data_clean = extractInfoperPaper(target_df=ref_data_clean,len=length, endings=endings)
ref_data_clean= cleanBibtexNoise(ref_data_clean)
# print(ref_data_clean)
# Write to CSV file
ref_data_clean.to_csv("ref_data5_clean.csv", index=False)

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

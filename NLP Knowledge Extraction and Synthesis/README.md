### Instructions

The purpose of the method is to **extract and synthesise knowledge** about behavior determinants and their statistical associations to behavior choice options from a body of scientific literature automatically and feed the resulting knowledge into a **"Behavior Choice Determinants Ontology"**. This document walks the user through the order and purpose of the scripts. 

*Author: Tabea Sonnenschein*
*Date: 16/06/2022*

---
---

#### Steps

1) download bibliometrics of articles identified by the querying of the scientific database (e.g. Web of Science)

2) use script ["02_CrossRef_XML_mining.py"](https://github.com/TabeaSonnenschein/Spatial-Agent-based-Modeling-of-Urban-Health-Interventions/blob/main/NLP%20Knowledge%20Extraction%20and%20Synthesis/02_CrossRef_XML_mining.py) to apply the Crossref and Elsevier API to download XML of articles that have it and Pdf links for the rest. 

3) after downloading all pdf's, use ["03_PdfToText.py"](https://github.com/TabeaSonnenschein/Spatial-Agent-based-Modeling-of-Urban-Health-Interventions/blob/main/NLP%20Knowledge%20Extraction%20and%20Synthesis/03_PdfToText.py) to extract the text from the Pdf documents and substitute bbreviations with the full names of what they represents.

4) use ["04_ExtractMainBodyText.py"](https://github.com/TabeaSonnenschein/Spatial-Agent-based-Modeling-of-Urban-Health-Interventions/blob/main/NLP%20Knowledge%20Extraction%20and%20Synthesis/04_ExtractMainBodyText.py) to cut out references and other type of text that is not the main body text that contains the information we are looking for. The Pdf extracted text is ready now.

5) use ["05_XMLToCleanText.py"](https://github.com/TabeaSonnenschein/Spatial-Agent-based-Modeling-of-Urban-Health-Interventions/blob/main/NLP%20Knowledge%20Extraction%20and%20Synthesis/05_XMLToCleanText.py) to extract the text out of the XML documents and replace the abbreviations with the full names of what they represents. The XML extracted text is ready  now.

6) use ["06_BERTDataPreparation.py"](https://github.com/TabeaSonnenschein/Spatial-Agent-based-Modeling-of-Urban-Health-Interventions/blob/main/NLP%20Knowledge%20Extraction%20and%20Synthesis/06_BERTDataPreparation.py) to read the prepared text data for all unique articles, whereby a XML extracted text of a document is prioritized over a Pdf extracted text (as it has higher quality). The text is then transformed into a dataframe of ordered words with a doi (document id) column and a sentence id (column). Additionally a Part of Speech tagger is applied to classify the words into grammatical functions. A Tag column is added with the default value of "O" (outside). This column can be used to tag a set of articles for training the Named entity recognition model on.  Apply this script first to the XML produced text documents and then to the Pdf extracted text documents.

7) after having labeled a set of articles, use ["07_BERTDeepLearningKnowledgeExtraction.py"](https://github.com/TabeaSonnenschein/Spatial-Agent-based-Modeling-of-Urban-Health-Interventions/blob/main/NLP%20Knowledge%20Extraction%20and%20Synthesis/07_BERTDeepLearningKnowledgeExtraction.py) to train the BERT named entity recognition model with the labeled variables and predict the labels for the remaining yet unlabeled articles (the majority). The script also will produce a model performance graph and a weighted F1 score, as well as F1 scores for all labels seperately, to assess the quality of the prediction.

8) use ["08_PredictLabelsRestArticles.py"](https://github.com/TabeaSonnenschein/Spatial-Agent-based-Modeling-of-Urban-Health-Interventions/blob/main/NLP%20Knowledge%20Extraction%20and%20Synthesis/08_PredictLabelsRestArticles.py) to predict the labels for the remaining yet unlabeled articles (the majority) using the saved model.

9) use ["09_TokenizedTextToRelationalData.py"](https://github.com/TabeaSonnenschein/Spatial-Agent-based-Modeling-of-Urban-Health-Interventions/blob/main/NLP%20Knowledge%20Extraction%20and%20Synthesis/09_TokenizedTextToRelationalData.py) to restructure the predicted labels in a dataframe of lists of association types, behavior options, behavior determinants, studygroups and moderators per sentence. Hereby the words that are labeled with the same label consequtively become one variable/entity/phrase. Information on the DOI, fullstence and sentence id are maintained.

10) use ["10_syntactical_relation_learning_preparation.py"](https://github.com/TabeaSonnenschein/Spatial-Agent-based-Modeling-of-Urban-Health-Interventions/blob/main/NLP%20Knowledge%20Extraction%20and%20Synthesis/10_syntactical_relation_learning_preparation.py) to read the sentence aggregated lists of labels per class and create a dataset of every combination of association types, behavior options, behavior determinants, studygroups and moderators within a sentence. This new dataframe is the total set of all possible evidence relations within the labeled sentences, but only some of them are true. The script adds syntactical feautures of the sentence that will be the basis for predicting in step 10 whether the variable combination has a true evidence relation or not. The step also adds a Tag column that will be set to the default 0 (no true evidence relation). Use this column to put a 1 in the rows where the variable combination is actually a true evidence relationship.

11) use ["11_syntactical_relation_learning_model.py"](https://github.com/TabeaSonnenschein/Spatial-Agent-based-Modeling-of-Urban-Health-Interventions/blob/main/NLP%20Knowledge%20Extraction%20and%20Synthesis/11_syntactical_relation_learning_model.py) to apply a machine learning model to the syntactical feauture created in the previous step and infer the evidence relation truthfulness of the variable combinations. The script uses Random Forest as a default since it produced the best results but it can also use other classification models from the package sklearn. A F1 score and accuracy value will be also calculated. As an output the total dataset of possible evidence relations with the predicted truthfullness will be saved, but also a dataset with only the true evidence relations. The latter is what we will use for the last steps of the method. This is the extracted knowledge of the literature.

12) use ["12_classify_association_types.py"](https://github.com/TabeaSonnenschein/Spatial-Agent-based-Modeling-of-Urban-Health-Interventions/blob/main/NLP%20Knowledge%20Extraction%20and%20Synthesis/12_classify_association_types.py) to classify the association type phrases into significant, insignificant, consistent, inconsistent, postive, negative, correlated. Then drop the dublicate association types.

13)  use ["13_ExtractingInfoOfTitleAbstract.py"](https://github.com/TabeaSonnenschein/Spatial-Agent-based-Modeling-of-Urban-Health-Interventions/blob/main/NLP%20Knowledge%20Extraction%20and%20Synthesis/13_ExtractingInfoOfTitleAbstract.py) to impute the missing behavior options from the title of the article or the last mentioned behavior option. Moreover, studygroups that are mentioned in the title are assigned to all findings.

14) use ["14_Bibtext_to_data.py"](https://github.com/TabeaSonnenschein/Spatial-Agent-based-Modeling-of-Urban-Health-Interventions/blob/main/NLP%20Knowledge%20Extraction%20and%20Synthesis/14_Bibtext_to_data.py) to use the bibtex extractions from Mendeley of all articles to compose a dataframe of bibliometric data that can be used to feed the study information into the ontology. The script moreover joins the Bibtex Info with the Web of Science bibliometric data.

15) use ["15_PopulatingTheOntology.py"](https://github.com/TabeaSonnenschein/Spatial-Agent-based-Modeling-of-Urban-Health-Interventions/blob/main/NLP%20Knowledge%20Extraction%20and%20Synthesis/15_PopulatingTheOntology.py) to populate the Behavior Choice Determinants Ontology with the evidence instances extracted and the study information.

16) use ["16_QueryingTheOntology.py"](https://github.com/TabeaSonnenschein/Spatial-Agent-based-Modeling-of-Urban-Health-Interventions/blob/main/NLP%20Knowledge%20Extraction%20and%20Synthesis/16_QueryingTheOntology.py) to query the ontology using SPARQL queries. The script contains the queries presented in the paper.

17) use ["17_Visualization.py"](https://github.com/TabeaSonnenschein/Spatial-Agent-based-Modeling-of-Urban-Health-Interventions/blob/main/NLP%20Knowledge%20Extraction%20and%20Synthesis/17_Visualization.py) to produce edge and nodelists for subgraphs of the knowledge graph and add unique IDs for each node. These tables can then be imported as such in Gephi to facilitate the visualization of the knowledge graph.

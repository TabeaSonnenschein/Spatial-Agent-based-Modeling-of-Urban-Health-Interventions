from sys import platform
from owlready2 import *
from numpy import *
import pandas as pd

# Load the ontology
os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Ontology")
onto = get_ontology(os.path.join(os.getcwd(),"BehaviouralModelOntology.owl")).load()

# Set the correct java binary
if platform == 'win32':
    JAVA_EXE = '../lib/jdk-17/bin/java.exe'

os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Written Paper\02- Behavioural Model paper")
meta_review_details = pd.read_csv("metareview_details_short.csv")


# Synchronise the reasoner in order to get inferences
sync_reasoner_pellet(onto, True, True, 0)
print(onto.Studies.instances())

for count, value in enumerate(meta_review_details['doi']):
    print(count, value)
    paper_doi = onto.search(iri="*" + value)
    print("ontology_paper_doi" + str(paper_doi))
    if paper_doi:
        paper_doi = paper_doi[0]
    else:
        paper_doi = onto.ReviewStudies(value)
        if "meta-analy" in str(meta_review_details['Article.Title'].iloc[count]).lower():
            paper_doi.is_a.append(onto.MetaAnalysis)
        if "systematic review" in str(meta_review_details['Article.Title'].iloc[count]).lower() or "systematic literature review" in str(meta_review_details['Article.Title'].iloc[count]).lower() :
            paper_doi.is_a.append(onto.SystematicReviewStudies)
    paper_doi.HasCitation = [str(meta_review_details['citation'].iloc[count])]
    paper_doi.HasStudyYear = [int(meta_review_details['Publication.Year'].iloc[count])]
    paper_doi.HasTitle = [str(meta_review_details['Article.Title'].iloc[count])]
    paper_doi.HasJournal = [str(meta_review_details['Source.Title'].iloc[count])]
    paper_doi.comment = [str(meta_review_details['citation'].iloc[count])]
    for prop in paper_doi.get_properties():
        for DataPropertyValue in prop[paper_doi]:
            print(".%s == %s" % (prop.python_name, DataPropertyValue))

onto.save(file = os.path.join(os.getcwd(),"extendedBehaviouralModelOntology.owl"), format = "rdfxml")


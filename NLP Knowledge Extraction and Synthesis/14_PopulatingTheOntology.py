from sys import platform
from owlready2 import *
from numpy import *
import pandas as pd
import rdflib
from rdflib.namespace import NamespaceManager
from rdflib import BNode, Namespace, Graph

# Load the ontology
os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Written Paper\02- Behavioural Model paper")
onto = get_ontology(os.path.join(os.getcwd(),"BehaviorChoiceDeterminantsOntology.owl")).load()

# Set the correct java binary
if platform == 'win32':
    JAVA_EXE = '../lib/jdk-17/bin/java.exe'

os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Written Paper\02- Behavioural Model paper\modalchoice literature search")
meta_review_details = pd.read_csv("metareview_details_short.csv")


# Synchronise the reasoner in order to get inferences
sync_reasoner_pellet(onto, True, True, 0)

## adding study details
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


## adding evidence instances
os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Written Paper\02- Behavioural Model paper")
evidence_instances_full = pd.read_csv("unique_evidence_instances.csv")
evidence_instances = evidence_instances_full[['DOI', 'Sentence', 'Fullsentence', 'BehaviorOption', 'BehaviorDeterminant', 'Studygroup',
                                              'Moderator', 'stat_significance', 'stat_consistency', 'stat_direction', 'stat_correl']]

uniqueBO = list(dict.fromkeys(evidence_instances_full['BehaviorOption']))
uniqueBD = list(dict.fromkeys(evidence_instances_full['BehaviorDeterminant']))
uniqueSG = list(dict.fromkeys(evidence_instances_full['Studygroup']))
uniqueMO = list(dict.fromkeys(evidence_instances_full['Moderator']))
uniqueBO.remove("-100")
uniqueSG.remove("-100")
uniqueMO.remove("-100")
uniqueBO = [el.replace(" ", "_") for el in uniqueBO]
uniqueSG = [el.replace(" ", "_") for el in uniqueSG]
uniqueMO = [el.replace(" ", "_") for el in uniqueMO]
uniqueBD = [el.replace(" ", "_") for el in uniqueBD]


for i in uniqueBO:
    x = onto.BehaviorChoiceOptions(i)
for i in uniqueBD:
    x = onto.BehaviorDeterminants(i)
for i in uniqueSG:
    x = onto.IndividualProperties(i)
for i in uniqueMO:
    x = onto.BehaviorModerators(i)

graph = default_world.as_rdflib_graph()
#
for count, value in enumerate(evidence_instances['DOI']):
    # bn = BNode() # blanknote
    Envid_inst = graph.BNode() # blanknote
    with onto:
        graph.add((Envid_inst, rdflib.URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
               rdflib.URIRef("http://www.w3.org/2002/07/owl#Class")))
    # Envid_inst = onto.EvidenceInstances("ev_inst_" + str(count))
    doi = value.replace(".csv", "").replace("_", "/")
    paper_doi = onto.search(iri="*" + doi)
    if paper_doi:
        paper_doi = paper_doi[0]
    else:
        paper_doi = onto.ReviewStudies(doi)
    BO = onto.search(iri="*" + evidence_instances_full['BehaviorOption'].iloc[count].replace(" ", "_"))
    BD = onto.search(iri="*" + evidence_instances_full['BehaviorDeterminant'].iloc[count].replace(" ", "_"))
    SG = onto.search(iri="*" + evidence_instances_full['Studygroup'].iloc[count].replace(" ", "_"))
    MO = onto.search(iri="*" + evidence_instances_full['Moderator'].iloc[count].replace(" ", "_"))
    paper_doi.FindsSignificant = Envid_inst
    BD[0].StudiedDeterminant.append(Envid_inst)
    Envid_inst.FullSentenceString = [str(evidence_instances_full['Fullsentence'].iloc[count])]
    Envid_inst.SentenceNumber = [str(evidence_instances_full['Sentence'].iloc[count])]
    if BO:
        BO[0].StudiedChoiceOptions.append(Envid_inst)
    for prop in Envid_inst.get_properties():
        for DataPropertyValue in prop[Envid_inst]:
            print(".%s == %s" % (prop.python_name, DataPropertyValue))

#
# for count, value in enumerate(evidence_instances['DOI']):
#     Envid_inst = onto.EvidenceInstances("ev_inst_" + str(count))
#     doi = value.replace(".csv", "").replace("_", "/")
#     paper_doi = onto.search(iri="*" + doi)
#     if paper_doi:
#         paper_doi = paper_doi[0]
#     else:
#         paper_doi = onto.ReviewStudies(doi)
#     BO = onto.search(iri="*" + evidence_instances_full['BehaviorOption'].iloc[count].replace(" ", "_"))
#     BD = onto.search(iri="*" + evidence_instances_full['BehaviorDeterminant'].iloc[count].replace(" ", "_"))
#     SG = onto.search(iri="*" + evidence_instances_full['Studygroup'].iloc[count].replace(" ", "_"))
#     MO = onto.search(iri="*" + evidence_instances_full['Moderator'].iloc[count].replace(" ", "_"))
#     paper_doi.FindsSignificant = Envid_inst
#     BD[0].StudiedDeterminant.append(Envid_inst)
#     Envid_inst.FullSentenceString = [str(evidence_instances_full['Fullsentence'].iloc[count])]
#     Envid_inst.SentenceNumber = [str(evidence_instances_full['Sentence'].iloc[count])]
#     if BO:
#         BO[0].StudiedChoiceOptions.append(Envid_inst)
#     for prop in Envid_inst.get_properties():
#         for DataPropertyValue in prop[Envid_inst]:
#             print(".%s == %s" % (prop.python_name, DataPropertyValue))

onto.save(file = os.path.join(os.getcwd(),"extendedBehaviouralModelOntology2.owl"), format = "rdfxml")


from sys import platform
from owlready2 import *
import numpy as np
import pandas as pd
import types
import rdflib
from rdflib.namespace import NamespaceManager
from rdflib import BNode, Namespace, Graph

# Load the ontology
os.chdir(r"D:\PhD EXPANSE\Written Paper\02- Behavioural Model paper")
onto = get_ontology(os.path.join(os.getcwd(),"BehaviorChoiceDeterminantsOntology.owl")).load()

# Set the correct java binary
if platform == 'win32':
    JAVA_EXE = '../lib/jdk-17/bin/java.exe'

os.chdir(r"D:\PhD EXPANSE\Written Paper\02- Behavioural Model paper\modalchoice literature search")
meta_review_details = pd.read_csv("metareview_details_short.csv")

# # Synchronise the reasoner in order to get inferences
# sync_reasoner_pellet(onto, True, True, 0)

## adding evidence instances
os.chdir(r"D:\PhD EXPANSE\Written Paper\02- Behavioural Model paper")
evidence_instances_full = pd.read_csv("unique_evidence_instances_clean2_harmonised_BO_manualclean.csv")
evidence_instances = evidence_instances_full[['DOI', 'Sentence', 'Fullsentence', 'BehaviorOption', 'BehaviorDeterminant', 'Studygroup',
                                              'Moderator', 'stat_significance', 'stat_consistency', 'stat_direction', 'stat_correl']]

uniqueBO = list(dict.fromkeys([x.lower() for x in evidence_instances_full['BehaviorOption']]))
uniqueBD = list(dict.fromkeys([x.lower() for x in evidence_instances_full['BehaviorDeterminant']]))
uniqueSG = list(dict.fromkeys([x.lower() for x in evidence_instances_full['Studygroup']]))
uniqueMO = list(dict.fromkeys([x.lower() for x in evidence_instances_full['Moderator']]))
# uniqueBO.remove("-100")
uniqueSG.remove("-100")
uniqueMO.remove("-100")
uniqueSG = list(dict.fromkeys(list(chain.from_iterable([i.replace("[", "").replace("]","").replace("'","").replace("<", "less than").strip().split(", ") for i in uniqueSG]))))
print(uniqueSG)
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

# uniqueBO_classes = list(dict.fromkeys([x.lower() for x in evidence_instances_full['BehaviorOptionHarmon']]))
# uniqueBO_classes = [el.replace(" ", "_") for el in uniqueBO_classes]
# with onto:
#     for i in uniqueBO_classes:
#         print(i)
#         my_new_class = types.new_class(str(i), (onto["BehaviorChoiceOptions"],))  # make a class
#     pass


# graph = default_world.as_rdflib_graph()

for count, value in enumerate(evidence_instances['DOI']):

    ## Create an evidence instance individual
    # Evid_inst = graph.BNode()  # blanknode
    #     with onto:
    #         graph.add((Evid_inst, rdflib.URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
    #                rdflib.URIRef("http://www.w3.org/2002/07/owl#Class")))
    Evid_inst = onto.EvidenceInstances("ev_inst_" + str(count))


    ## identify the article in ontology or add details if not yet exists
    doi = value.replace(".csv", "").replace("_", "/")
    paper_doi = onto.search(iri="*" + doi)
    if paper_doi:
        paper_doi = paper_doi[0]
    else:
        doi_idx = np.where(meta_review_details['doi'] == doi)[0]
        print(doi_idx)
        paper_doi = onto.ReviewStudies(doi)
        if len(doi_idx) > 0:
            if "meta-analy" in str(meta_review_details['Article.Title'].iloc[doi_idx[0]]).lower():
                paper_doi.is_a.append(onto.MetaAnalysis)
            if "systematic review" in str(meta_review_details['Article.Title'].iloc[doi_idx[0]]).lower() \
                    or "systematic literature review" in str(meta_review_details['Article.Title'].iloc[doi_idx[0]]).lower():
                paper_doi.is_a.append(onto.SystematicReviewStudies)
            paper_doi.HasCitation = [str(meta_review_details['citation'].iloc[doi_idx[0]])]
            paper_doi.HasStudyYear = [int(meta_review_details['Publication.Year'].iloc[doi_idx[0]])]
            paper_doi.HasTitle = [str(meta_review_details['Article.Title'].iloc[doi_idx[0]])]
            paper_doi.HasJournal = [str(meta_review_details['Source.Title'].iloc[doi_idx[0]])]
            paper_doi.comment = [str(meta_review_details['citation'].iloc[doi_idx[0]])]
        else:
            paper_doi.comment = [str("https://doi.org/" + doi)]
        for prop in paper_doi.get_properties():
            for DataPropertyValue in prop[paper_doi]:
                print(".%s == %s" % (prop.python_name, DataPropertyValue))

    ## identify the evidence info individuals in the ontology
    ## and add the object property relations
    BO = onto.search(iri="*" + evidence_instances_full['BehaviorOption'].iloc[count].replace(" ", "_").lower())
    BD = onto.search(iri="*" + evidence_instances_full['BehaviorDeterminant'].iloc[count].replace(" ", "_").lower())
    MO = onto.search(iri="*" + evidence_instances_full['Moderator'].iloc[count].replace(" ", "_").lower())
    localSGs = evidence_instances_full['Studygroup'].iloc[count].replace("[", "").replace("]","").replace("'","").replace("<", "less than").strip().split(", ")
    print(localSGs)
    if localSGs != ['-100']:
        for localSG in localSGs:
            SG = onto.search(iri="*" + localSG.replace(" ", "_").lower())
            SG[0].GroupStudiedIn.append(Evid_inst)
    # SG = onto.search(iri="*" + evidence_instances_full['Studygroup'].iloc[count].replace(" ", "_"))
    if evidence_instances['stat_significance'].iloc[count] == "significant":
        paper_doi.FindsSignificance.append(Evid_inst)
        if evidence_instances['stat_direction'].iloc[count] == "positive":
            paper_doi.FindsPositiveAssociation.append(Evid_inst)
        elif evidence_instances['stat_direction'].iloc[count] == "negative":
            paper_doi.FindsNegativeAssociation.append(Evid_inst)
    elif evidence_instances['stat_significance'].iloc[count] == "insignificant":
        paper_doi.FindsInsignificance.append(Evid_inst)
    if evidence_instances['stat_consistency'].iloc[count] == "consistent":
        paper_doi.FindsConsistency.append(Evid_inst)
    elif evidence_instances['stat_consistency'].iloc[count] == "inconsistent":
        paper_doi.FindsInconsistency.append(Evid_inst)
    if evidence_instances['stat_correl'].iloc[count] == "correlated":
        paper_doi.FindsCorrelation.append(Evid_inst)
    BD[0].StudiedDeterminant.append(Evid_inst)
    paper_doi.StudiesDeterminant.append(BD[0])
    Evid_inst.FullSentenceString = [str(evidence_instances_full['Fullsentence'].iloc[count])]
    Evid_inst.SentenceNumber = [str(evidence_instances_full['Sentence'].iloc[count])]
    if BO:
        BO[0].StudiedChoiceOptions.append(Evid_inst)
    if MO:
        MO[0].ModeratorIn.append(Evid_inst)

    ## print the evidence instance properties
    for prop in Evid_inst.get_properties():
        for DataPropertyValue in prop[Evid_inst]:
            print(".%s == %s" % (prop.python_name, DataPropertyValue))


#### want to synchronize reasoner to save inferred facts
#### despite following the instructions of the documentations, it does not work
# sync_reasoner_pellet(onto)
# sync_reasoner(onto,True, True, 0)
with onto:
    sync_reasoner_pellet(infer_property_values = True, debug=0)

onto.save(file = os.path.join(os.getcwd(),"extendedBehaviouralModelOntology3.owl"), format = "rdfxml")


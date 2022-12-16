from sys import platform
from owlready2 import *
import numpy as np
import pandas as pd
import types
import rdflib
from rdflib.namespace import NamespaceManager
from rdflib import BNode, Namespace, Graph


##### Define functions
def AddBOMetaClasses(df, BO_class_column = "BehaviorOptionHarmon"):
    uniqueBO_classes = list(dict.fromkeys([x.lower() for x in df[BO_class_column]]))
    uniqueBO_classes = [el.replace(" ", "_") for el in uniqueBO_classes]
    with onto:
        for i in uniqueBO_classes:
            print(i)
            x = types.new_class(str(i), (onto.BehaviorChoiceOptions,))  # make a class
        pass

# graph = default_world.as_rdflib_graph()
def AddEvidenceInstancesAndRelations(evidence_df, article_df, harmon_BO_classes = False):
    for count, value in enumerate(evidence_df['DOI']):

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
            doi_idx = np.where(article_df['doi'] == doi)[0]
            print(doi_idx)
            paper_doi = onto.ReviewStudies(doi)
            if len(doi_idx) > 0:
                if "meta-analy" in str(article_df['Article.Title'].iloc[doi_idx[0]]).lower():
                    paper_doi.is_a.append(onto.MetaAnalysis)
                if "systematic review" in str(article_df['Article.Title'].iloc[doi_idx[0]]).lower() \
                        or "systematic literature review" in str(article_df['Article.Title'].iloc[doi_idx[0]]).lower():
                    paper_doi.is_a.append(onto.SystematicReviewStudies)
                paper_doi.HasCitation = [str(article_df['citation'].iloc[doi_idx[0]])]
                paper_doi.HasStudyYear = [int(article_df['Publication.Year'].iloc[doi_idx[0]])]
                paper_doi.HasTitle = [str(article_df['Article.Title'].iloc[doi_idx[0]])]
                paper_doi.HasJournal = [str(article_df['Source.Title'].iloc[doi_idx[0]])]
                paper_doi.comment = [str(article_df['citation'].iloc[doi_idx[0]])]
            else:
                paper_doi.comment = [str("https://doi.org/" + doi)]
            for prop in paper_doi.get_properties():
                for DataPropertyValue in prop[paper_doi]:
                    print(".%s == %s" % (prop.python_name, DataPropertyValue))

        ## identify the evidence info individuals in the ontology
        ## and add the object property relations
        if harmon_BO_classes:
            BO_class_list = onto.search(iri = "*" + str(evidence_df['BehaviorOptionHarmon'].iloc[count].replace(" ", "_").lower()))
            if len(BO_class_list) < 1:
                with onto:
                    BO_class = types.new_class(str(evidence_df['BehaviorOptionHarmon'].iloc[count].replace(" ", "_").lower()), (onto.BehaviorChoiceOptions,))  # make a class
                    pass
            else:
                BO_class = BO_class_list[0]
            try:        ### trows an error when instance and class are called equivalently
                BO = BO_class(str(evidence_df['BehaviorOption'].iloc[count].replace(" ", "_").lower()))
            except:     ## so if that is the case we edit the string with an '_instance'
                BO = BO_class(str(evidence_df['BehaviorOption'].iloc[count].replace(" ", "_").lower()+"_instance"))
        else:
            BO = onto.BehaviorChoiceOptions(evidence_df['BehaviorOption'].iloc[count].replace(" ", "_").lower())
        BD = onto.BehaviorDeterminants(evidence_df['BehaviorDeterminant'].iloc[count].replace(" ", "_").lower())
        localMO = evidence_df['Moderator'].iloc[count].replace(" ", "_").lower()
        if localMO != '-100':
            MO = onto.BehaviorModerators(evidence_df['Moderator'].iloc[count].replace(" ", "_").lower())
            MO.ModeratorIn.append(Evid_inst)
        localSGs = evidence_df['Studygroup'].iloc[count].replace("[", "").replace("]","").replace("'","").replace("<", "less than").strip().split(", ")
        if localSGs != ['-100']:
            for localSG in localSGs:
                SG = onto.IndividualProperties(localSG.replace(" ", "_").lower())
                SG.GroupStudiedIn.append(Evid_inst)

        if evidence_df['stat_significance'].iloc[count] == "significant":
            paper_doi.FindsSignificance.append(Evid_inst)
            if evidence_df['stat_direction'].iloc[count] == "positive":
                paper_doi.FindsPositiveAssociation.append(Evid_inst)
            elif evidence_df['stat_direction'].iloc[count] == "negative":
                paper_doi.FindsNegativeAssociation.append(Evid_inst)
        elif evidence_df['stat_significance'].iloc[count] == "insignificant":
            paper_doi.FindsInsignificance.append(Evid_inst)
        if evidence_df['stat_consistency'].iloc[count] == "consistent":
            paper_doi.FindsConsistency.append(Evid_inst)
        elif evidence_df['stat_consistency'].iloc[count] == "inconsistent":
            paper_doi.FindsInconsistency.append(Evid_inst)
        if evidence_df['stat_correl'].iloc[count] == "correlated":
            paper_doi.FindsCorrelation.append(Evid_inst)
        BD.StudiedDeterminant.append(Evid_inst)
        paper_doi.StudiesDeterminant.append(BD)
        Evid_inst.FullSentenceString = [str(evidence_df['Fullsentence'].iloc[count])]
        # Evid_inst.FullSentenceString = [str(evidence_df['Fullsentence'].iloc[count].replace("&", "and").replace("<", "less than").replace(">", "more than").replace("%", "procent").replace("=","equals").replace(":", ""))]
        Evid_inst.SentenceNumber = [str(evidence_df['Sentence'].iloc[count])]
        BO.StudiedChoiceOptions.append(Evid_inst)


        ## print the evidence instance properties
        for prop in Evid_inst.get_properties():
            for DataPropertyValue in prop[Evid_inst]:
                print(".%s == %s" % (prop.python_name, DataPropertyValue))


# Load the ontology
os.chdir(r"D:\PhD EXPANSE\Written Paper\02- Behavioural Model paper")
onto = get_ontology(os.path.join(os.getcwd(),"BehaviorChoiceDeterminantsOntology.owl")).load()

# Set the correct java binary
if platform == 'win32':
    JAVA_EXE = '../lib/jdk-17/bin/java.exe'


## load data
## article details
os.chdir(r"D:\PhD EXPANSE\Written Paper\02- Behavioural Model paper\modalchoice literature search")
meta_review_details = pd.read_csv("metareview_details_short.csv")

## evidence instances
os.chdir(r"D:\PhD EXPANSE\Written Paper\02- Behavioural Model paper")
evidence_instances_full = pd.read_csv("unique_evidence_instances_clean2_harmonised_BO_manualclean.csv")
evidence_instances = evidence_instances_full[['DOI', 'Sentence', 'Fullsentence', 'BehaviorOption', 'BehaviorDeterminant', 'Studygroup',
                                              'Moderator', 'stat_significance', 'stat_consistency', 'stat_direction', 'stat_correl']]

#AddBOMetaClasses(df=evidence_instances_full)

AddEvidenceInstancesAndRelations(evidence_df = evidence_instances_full,
                                 article_df= meta_review_details,harmon_BO_classes = True)

## Change the ontology annotation to reflect the behavior choice
BehaviorChoice = "Choice of Mode of Transport"
print(onto.comment)
onto.comment.append("This is the BehaviorChoiceDeterminantsOntology populated with evidence on the " + BehaviorChoice)


#### want to synchronize reasoner to save inferred facts
#### despite following the instructions of the documentations, it does not work
with onto:
    sync_reasoner_pellet(infer_property_values = True,  debug=0)

graph = default_world.as_rdflib_graph()
graph.serialize(destination="extendedBehaviouralModelOntology.ttl")

# onto.save(file = os.path.join(os.getcwd(),"extendedBehaviouralModelOntology3.owl"), format = "rdfxml")


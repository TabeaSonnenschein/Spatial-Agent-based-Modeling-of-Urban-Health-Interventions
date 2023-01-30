from sys import platform
from owlready2 import *
import numpy as np
import pandas as pd
import types
import rdflib
from rdflib.namespace import NamespaceManager
from rdflib import BNode, Namespace, Graph

######################################################################################
## This script cam be used to populate the ontology with the extracted evidence
## as well as the bibliometrics of the studies.
######################################################################################

##### Define functions
# graph = default_world.as_rdflib_graph()
def AddEvidenceInstancesAndRelations(evidence_df, article_df, harmon_BO_classes = False):
    for count, value in enumerate(evidence_df['DOI']):

        ## Create an evidence instance individual
        # Evid_inst = graph.BNode()  # blanknode
        #     with onto:
        #         graph.add((Evid_inst, rdflib.URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
        #                rdflib.URIRef("http://www.w3.org/2002/07/owl#Class")))
        Evid_inst = onto.EvidenceInstance("ev_inst_" + str(count))


        ## identify the article in ontology or add details if not yet exists
        doi = value.replace(".csv", "").replace("_", "/")
        paper_doi = onto.search(iri="*" + doi)
        if paper_doi:
            paper_doi = paper_doi[0]
        else:
            doi_idx = np.where(article_df['doi'] == doi)[0]
            print(doi_idx)
            paper_doi = onto.ReviewStudy(doi)
            if len(doi_idx) > 0:
                if "meta-analy" in str(article_df['Article.Title'].iloc[doi_idx[0]]).lower():
                    paper_doi.is_a.append(onto.MetaAnalysis)
                if "systematic review" in str(article_df['Article.Title'].iloc[doi_idx[0]]).lower() \
                        or "systematic literature review" in str(article_df['Article.Title'].iloc[doi_idx[0]]).lower():
                    paper_doi.is_a.append(onto.SystematicReviewStudy)
                paper_doi.hasCitation = [str(article_df['citation'].iloc[doi_idx[0]])]
                paper_doi.hasStudyYear = [int(article_df['Publication.Year'].iloc[doi_idx[0]])]
                paper_doi.hasTitle = [str(article_df['Article.Title'].iloc[doi_idx[0]])]
                paper_doi.hasJournal = [str(article_df['Source.Title'].iloc[doi_idx[0]])]
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
                    BO_class = types.new_class(str(evidence_df['BehaviorOptionHarmon'].iloc[count].replace(" ", "_").lower()), (onto.BehaviorChoiceOption,))  # make a class
                    pass
            else:
                BO_class = BO_class_list[0]
            try:        ### trows an error when instance and class are called equivalently
                BO = BO_class(str(evidence_df['BehaviorOption'].iloc[count].replace(" ", "_").lower()))
            except:     ## so if that is the case we edit the string with an '_instance'
                BO = BO_class(str(evidence_df['BehaviorOption'].iloc[count].replace(" ", "_").lower()+"_instance"))
        else:
            BO = onto.BehaviorChoiceOption(evidence_df['BehaviorOption'].iloc[count].replace(" ", "_").lower())
        BD = onto.BehaviorDeterminant(evidence_df['BehaviorDeterminant'].iloc[count].replace(" ", "_").lower())
        localMO = evidence_df['Moderator'].iloc[count].replace(" ", "_").lower()
        if localMO != '-100':
            MO = onto.BehaviorModerator(evidence_df['Moderator'].iloc[count].replace(" ", "_").lower())
            MO.moderatorIn.append(Evid_inst)
        localSGs = evidence_df['Studygroup'].iloc[count].replace("[", "").replace("]","").replace("'","").replace("<", "less than").strip().split(", ")
        if localSGs != ['-100']:
            for localSG in localSGs:
                SG = onto.IndividualProperty(localSG.replace(" ", "_").lower())
                SG.groupStudiedIn.append(Evid_inst)

        if evidence_df['stat_significance'].iloc[count] == "significant":
            paper_doi.findsSignificance.append(Evid_inst)
            if evidence_df['stat_direction'].iloc[count] == "positive":
                paper_doi.findsPositiveAssociation.append(Evid_inst)
            elif evidence_df['stat_direction'].iloc[count] == "negative":
                paper_doi.findsNegativeAssociation.append(Evid_inst)
        elif evidence_df['stat_significance'].iloc[count] == "insignificant":
            paper_doi.findsInsignificance.append(Evid_inst)
        if evidence_df['stat_consistency'].iloc[count] == "consistent":
            paper_doi.findsConsistency.append(Evid_inst)
        elif evidence_df['stat_consistency'].iloc[count] == "inconsistent":
            paper_doi.findsInconsistency.append(Evid_inst)
        if evidence_df['stat_correl'].iloc[count] == "correlated":
            paper_doi.findsCorrelation.append(Evid_inst)
        BD.studiedDeterminant.append(Evid_inst)
        paper_doi.studiesDeterminant.append(BD)
        Evid_inst.fullSentenceString = [str(evidence_df['Fullsentence'].iloc[count])]
        # Evid_inst.FullSentenceString = [str(evidence_df['Fullsentence'].iloc[count].replace("&", "and").replace("<", "less than").replace(">", "more than").replace("%", "procent").replace("=","equals").replace(":", ""))]
        Evid_inst.sentenceNumber = [str(evidence_df['Sentence'].iloc[count])]
        BO.studiedChoiceOption.append(Evid_inst)


        ## print the evidence instance properties
        for prop in Evid_inst.get_properties():
            for DataPropertyValue in prop[Evid_inst]:
                print(".%s == %s" % (prop.python_name, DataPropertyValue))


# Load the ontology
os.chdir(r"C:\Users\Tabea\Documents\GitHub\TabeaSonnenschein.github.io\ontologies")

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
BehaviorChoice_short = "TranspModeChoice"
# print(onto.comment)
# onto.comment.append("This ontology has been populated with scientific evidence on the "
#                     "behavior choice of "+BehaviorChoice+". Therefore the evidence on behavior "
#                     + "choice options, determinants and statistical associations encompassed in this "
#                     + "ontology is limited to the choice of" + BehaviorChoice + ".")


#### want to synchronize reasoner to save inferred facts
#### despite following the instructions of the documentations, it does not work
with onto:
    sync_reasoner_pellet(infer_property_values = True,  debug=0)

os.chdir(r"C:\Users\Tabea\Documents\GitHub\TabeaSonnenschein.github.io\ontologies")
graph = default_world.as_rdflib_graph()
graph.serialize(destination="BehaviorChoiceDeterminantsOntology_"+BehaviorChoice_short+".ttl")

# onto.save(file = os.path.join(os.getcwd(),"extendedBehaviouralModelOntology3.owl"), format = "rdfxml")


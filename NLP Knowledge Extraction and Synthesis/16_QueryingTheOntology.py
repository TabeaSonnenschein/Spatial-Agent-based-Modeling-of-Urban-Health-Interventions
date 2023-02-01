from rdflib import *
import owlrl
from owlrl import OWLRL_Semantics
from rdflib import Namespace
from pprint import pprint
import os

################################################################################
## This script can be used to query the evidence knowledge graph.
## There are a set of example SPARQL queries, such as the ones presented in the paper.
########################################################################################


bmo= Namespace("https://tabeasonnenschein.github.io/ontologies/bcdo.html#")
def prefix(g):
    g.bind('bmo', Namespace("https://tabeasonnenschein.github.io/ontologies/bcdo.html#"))

def n_triples( g, n=None ):
    """ Prints the number of triples in graph g """
    if n is None:
        print( '  Triples: '+str(len(g)) )
    else:
        print( '  Triples: +'+str(len(g)-n) )
    return len(g)

def load_RDF( g, fn ):
    print("load_RDF: "+fn)
    g.parse( fn , format='turtle')
    n_triples(g)
    return g

testquery= """
SELECT DISTINCT ?causec ?causecl
WHERE {  
"""
queries = {}
queries['What are studies containing behavioral evidence for biking after 2015?']="""
SELECT DISTINCT ?cite
WHERE {  
?a a bmo:biking; bmo:studiedChoiceOption ?evidence.
?evidence bmo:foundCorrelatedBy ?study.
?study bmo:hasStudyYear ?year; bmo:hasCitation ?cite.
FILTER(?year >= 2015)
}
"""
queries['What are the studies with most evidences for each behavioral choice option?']="""
SELECT  ?choice ?study ?count_evidence   
WHERE {  
SELECT DISTINCT ?study ?choice (COUNT(?evidence) as ?count_evidence)  WHERE 
{
?choice rdfs:subClassOf bmo:BehaviorChoiceOption.
?a a ?choice; bmo:studiedChoiceOption ?evidence.
?evidence bmo:foundCorrelatedBy ?study.
FILTER(?choice not in (bmo:BehaviorChoiceOption))
} GROUP BY ?study ?choice 
ORDER BY ?choice DESC(?count_evidence)
}
"""
queries['Find studies with consistent significant evidence for walking']="""
SELECT DISTINCT ?study WHERE 
{
?a a bmo:walking; bmo:studiedChoiceOption ?evidence.
?evidence bmo:foundConsistentBy ?study.
?evidence bmo:foundSignificantBy ?study.
}
"""

queries['Find studies with significant evidence for walking']="""
SELECT DISTINCT ?cite WHERE 
{
?a a bmo:walking; bmo:studiedChoiceOption ?evidence.
?evidence bmo:foundSignificantBy ?study.
?study bmo:hasCitation ?cite.

}
"""
queries['Find all significant behavior determinants for walking?']="""
SELECT DISTINCT ?det WHERE 
{
?a a bmo:walking; bmo:studiedChoiceOption ?evidence.
?evidence bmo:foundSignificantBy ?study.
?evidence bmo:regardsDeterminant ?det.
}
"""

queries['Find all significant behavior determinants for biking?']="""
SELECT DISTINCT ?det WHERE 
{
?a a bmo:biking; bmo:studiedChoiceOption ?evidence.
?evidence bmo:foundSignificantBy ?study.
?evidence bmo:regardsDeterminant ?det.
}
"""
queries['What are the most relevant behavioral determinants, in terms of how many classes of behavioral choice options they significantly influence?' ]="""
SELECT  ?det (COUNT(DISTINCT ?choice) as ?count_choice) (GROUP_CONCAT(DISTINCT STR( ?choice )) AS ?choices ) 
WHERE 
{
?choice rdfs:subClassOf bmo:BehaviorChoiceOption.
?a a ?choice; bmo:studiedChoiceOption ?evidence.
?evidence bmo:foundSignificantBy ?study.
?evidence bmo:regardsDeterminant ?det.
FILTER(?choice not in (bmo:BehaviorChoiceOption))
} GROUP BY ?det
ORDER BY DESC(?count_choice)
limit 10
"""

queries['Which determinants for walking are inconsistent or insignificant?']="""
SELECT DISTINCT ?det ?study
WHERE {
    ?a a bmo:walking; bmo:studiedChoiceOption ?evidence.
    ?evidence bmo:foundInconsistentBy|bmo:foundInsignificantBy  ?study.
    ?evidence bmo:regardsDeterminant ?det.
}
"""

queries['Which determinants for walking are inconsistent?']="""
SELECT DISTINCT ?det ?study
WHERE {
    ?a a bmo:walking; bmo:studiedChoiceOption ?evidence.
    ?evidence bmo:foundInconsistentBy  ?study.
    ?evidence bmo:regardsDeterminant ?det.
}
"""


def test(g, t = testquery):
    qres = g.query(t)
    print("now testing:")
    for row in qres:
        pprint(row)

os.chdir(r"C:\Users\Tabea\Documents\GitHub\TabeaSonnenschein.github.io\ontologies")
ontology = "BehaviorChoiceDeterminantsOntology_TranspModeChoice.ttl"
g = Graph()
g = load_RDF(g, ontology)
prefix(g)
# test(g)
print("Inference")
owlrl.DeductiveClosure(OWLRL_Semantics, rdfs_closure=True).expand(g)
n_triples(g)
for question in queries:
    print(question)
    test(g,queries[question])

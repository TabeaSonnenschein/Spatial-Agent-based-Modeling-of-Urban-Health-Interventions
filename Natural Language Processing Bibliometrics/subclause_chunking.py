import spacy
import deplacy
from spacy.lang.en.examples import sentences
en = spacy.load('en_core_web_sm')
from spacy import displacy
import os
from typing import List, Any
import re
import pandas as pd
import numpy as np
from itertools import chain
import stanza
from stanza.models.common.doc import Document
#nlp = stanza.Pipeline(lang='en', processors='depparse', depparse_pretagged=True)
# nlp = stanza.Pipeline(lang='en', processors='tokenize,pos,constituency')

os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Written Paper\02- Behavioural Model paper")
# csv = os.path.join(os.getcwd(), ("Evidence_instances_df_ManualLabel.csv"))
csv = os.path.join(os.getcwd(), ("Evidence_instances_df.csv"))
Evidence_instances_df = pd.read_csv(csv)

## disaggregating evidence of within sentence colocation
## Data processing
complete_evidence_Instances = Evidence_instances_df.iloc[list(np.where((Evidence_instances_df['BehaviorDeterminant'].notnull()) & (Evidence_instances_df['AssociationType'].notnull()))[0])]
complete_evidence_Instances = complete_evidence_Instances.fillna(" ")
complete_evidence_Instances['AssociationType'] = [x.replace("; ( ", "; ").replace(" ) ;", " ;").replace(" ) ", " ; ").replace(" ( ", " ; ").replace("( ", "").replace(" )", "").replace("(", "").replace(")","").replace("  "," ") for x in complete_evidence_Instances['AssociationType']]
complete_evidence_Instances['BehaviorDeterminant'] = [x.replace("; ( ", "; ").replace(" ) ;", " ;").replace(" ) ", " ; ").replace(" ( ", " ; ").replace("( ", "").replace(" )", "").replace("(", "").replace(")","").replace("  "," ") for x in complete_evidence_Instances['BehaviorDeterminant']]

gramm_complete_sentences = [x for i in ['VB','VBG','VBD', 'VBN', 'VBP', 'VBZ'] for x,y in enumerate(complete_evidence_Instances['sentence_POS']) if i in y]
complete_evidence_Instances = complete_evidence_Instances.iloc[gramm_complete_sentences]
complete_evidence_Instances['Fullsentence'] = [x.replace("?",",") for x in complete_evidence_Instances['Fullsentence']]


## Target List Creation
BD_disagg, AT_disagg, SENT_disagg, DOI_disagg, sent_ID_disagg, BO_disagg, SG_disagg, MO_disagg  = [], [], [], [], [], [], [], []

for count, value in enumerate(complete_evidence_Instances['Fullsentence']):
    value = value.strip()
    value = re.sub(r'(\d+)( \. )(\d+)', r'\1.\3', value)
    doc = en(value)
    Nr_added_Instances = 0

    print("-" * 70)
    print("LABELED PHRASES")
    print("assoc:", complete_evidence_Instances['AssociationType'].iloc[count])
    print("behavDet:", complete_evidence_Instances['BehaviorDeterminant'].iloc[count])
    print("behavOpt:",complete_evidence_Instances['BehaviorOption'].iloc[count])
    print(value)
    # print("{:<5} | {:<15} | {:<8} | {:<15} | {:<20} | {:<25}".format('Tag', 'Token', 'Relation', 'Head', 'Children', 'All Children'))
    # AT = list(chain.from_iterable([word.split(' ') for word in complete_evidence_Instances['AssociationType'].iloc[count].split(' ; ')]))
    # BD = list(chain.from_iterable([word.split(' ') for word in complete_evidence_Instances['BehaviorDeterminant'].iloc[count].split(' ; ')]))
    # BO = list(chain.from_iterable([word.split(' ') for word in complete_evidence_Instances['BehaviorOption'].iloc[count].split(' ; ')]))
    fullAT = complete_evidence_Instances['AssociationType'].iloc[count].split(' ; ')
    fullBD = complete_evidence_Instances['BehaviorDeterminant'].iloc[count].split(' ; ')
    fullBO = complete_evidence_Instances['BehaviorOption'].iloc[count].split(' ; ')

    root = [word for word in doc if (word.dep_ in ['ROOT', 'advcl']) or ((word.head.dep_ == 'ROOT') and (word.dep_ == 'conj'))]
    rootpos = [token.pos_ for token in root]
    print("ROOT", root, rootpos)

    for token in root:
        # tokens = [el]
        # tokens.extend([word for word in el.children if word.dep_ in ['ccomp', 'xcomp']])
        print(token.text)
        clausal_complement = [word for word in token.children if word.dep_ in ['ccomp', 'xcomp']]
        clausal_complement_children = [child for cl in clausal_complement for child in cl.subtree]
        subject = [child for child in token.children if child.dep_ in ['nsubjpass', 'nsubj']]
        subject_children = [child for sub in subject for child in sub.subtree]
        preposition = [child for child in token.children if child.dep_ == 'prep']
        preposition_children = [child for prep in preposition for child in prep.subtree]
        object = [child for child in token.children if child.dep_ == 'dobj']
        object_children = [child for obj in object for child in obj.subtree]
        # print(clausal_complement, clausal_complement_children)
        # print(subject, subject_children)
        # print(preposition, preposition_children)
        # print(object, object_children)

        ## join the word lists, check if variables are inside, use this as basis for seperation
        wordlist = list(chain.from_iterable([[str(token)], clausal_complement, clausal_complement_children, subject, subject_children , preposition, preposition_children, object, object_children]))
        wordlist = [str(word) for word in wordlist]
        print(wordlist)
        wordlist_joined = (" ").join(wordlist)
        # local_ATs = [at for at in AT if at in wordlist]
        # local_BOs = [at for at in BO if at in wordlist]
        # local_BDs = [at for at in BD if at in wordlist]
        # print("local ATs", local_ATs)
        # print("local BOs", local_BOs)
        # print("local BDs", local_BDs)
        # print("local ATs full", [at for at in fullAT if at in wordlist_joined])
        # print("local BOs full", [at for at in fullBO if at in wordlist_joined])
        # print("local BDs full", [at for at in fullBD if at in wordlist_joined])
        local_ATs = (", ").join([at for at in fullAT if at in wordlist_joined])
        local_BOs = [bo for bo in fullBO if bo in wordlist_joined]
        local_BDs = [bd for bd in fullBD if bd in wordlist_joined]
        print("local ATs", [local_ATs])
        print("local BOs", local_BOs)
        print("local BDs", local_BDs)
        bd_length = len(local_BDs)
        if len(local_BOs) == 0:
            AT_disagg.extend(([local_ATs]) * bd_length)
            BD_disagg.extend(local_BDs)
            BO_disagg.extend([" "] * bd_length)
            Nr_added_Instances += bd_length
        else:
            bo_length = len(local_BOs)
            AT_disagg.extend(([local_ATs]) * bd_length * bo_length)
            BD_disagg.extend((local_BDs) * bo_length)
            for BO in local_BOs:
                BO_disagg.extend([BO] * bd_length)
            Nr_added_Instances += (bd_length * bo_length)

    SENT_disagg.extend([value] * Nr_added_Instances)
    DOI_disagg.extend([complete_evidence_Instances['DOI'].iloc[count]] * Nr_added_Instances)
    sent_ID_disagg.extend([complete_evidence_Instances['Sentence'].iloc[count]] * Nr_added_Instances)
    SG_disagg.extend([complete_evidence_Instances['Studygroup'].iloc[count]] * Nr_added_Instances)
    MO_disagg.extend([complete_evidence_Instances['Moderator'].iloc[count]] * Nr_added_Instances)
    deplacy.render(doc)

print(len(SENT_disagg), len(BD_disagg), len(AT_disagg), len(BO_disagg))
disaggregated_evidence_instances = pd.DataFrame({'DOI': DOI_disagg, 'Sentence': sent_ID_disagg, 'BehaviorOption': BO_disagg, 'BehaviorDeterminant': BD_disagg, 'AssociationType': AT_disagg, 'Studygroup': SG_disagg, 'Moderator': MO_disagg ,  'Fullsentence': SENT_disagg })
print(disaggregated_evidence_instances)
disaggregated_evidence_instances.to_csv("disaggregated_evidence_instances22.csv", index=False)

    # #Consituency Parsing --> seems to be not useful
    # doc2 = nlp(value)
    # for sentence in doc2.sentences:
    #     tree = sentence.constituency
    #     print("fulltree:", tree)
    #     nr_child = len(tree.children[0].children)
    #     print(nr_child)
    #     print()
    #     for i in range(0,nr_child):
    #         print("   child number", i, ":", tree.children[0].children[i])
    #         nr_childchild = len(tree.children[0].children[i].children)
    #         print("   has number of children:", nr_childchild)
    #         if nr_childchild > 1:
    #             for x in range(0, nr_childchild):
    #                 print("      child", i, "'s child number", x, ":", tree.children[0].children[i].children[x])
    #         print()

    # for token in doc:
        # if (token.dep_ == "prep") and (token.head.pos_ == 'VERB'):
        #     print(token.dep_, token.text,  token.tag_, token.head.text, token.pos_)
        #     print('Children:', ([child for child in token.children]))
        #     print('Child Relation:',([child.dep_ for child in token.children]))
        #     children = [child for child in token.children]
        #     subchildren = [child for child in token.subtree]
        #     print('SubChildren:', str(subchildren))
        #     print()
        # if (token.dep_ == 'ROOT'):
        #     print(token.dep_, token.text,  token.tag_, token.head.text, token.pos_)
        #     print('Children:', ([child for child in token.children if child.pos_ != 'VERB']))
        #     print('Child Relation:',([child.dep_ for child in token.children]))
        #     print('Subject:', ([child for child in token.children if child.dep_ == 'nsubjpass']))
        #     children = [child for child in token.children if child.pos_ != 'VERB']
        #     verbchildren = [child for child in token.children if child.pos_ == 'VERB']
        #     subchildren = [child for child in token.subtree if child.pos_ != 'VERB']
        #     print('SubChildren:', str(subchildren))
        #     print()
        #     for verb in verbchildren:
        #         print(verb.dep_, verb.text, verb.tag_, verb.head.text, verb.pos_)
        #         print('Children:', ([child for child in verb.children if child.pos_ != 'VERB']))
        #         print('Child Relation:', ([child.dep_ for child in verb.children]))
        #         print('Subject:', ([child for child in verb.children if child.dep_ == 'nsubjpass']))
        #         children = [child for child in verb.children if child.pos_ != 'VERB']
        #         subchildren = [child for child in token.subtree if child.pos_ != 'VERB']
        #         print('SubChildren:', str(subchildren))
        #         print()

    # for token in doc:
    #     label = ''
    #     if str(token.text) in AT:
    #         label = 'AT'
    #     elif str(token.text) in BD:
    #         label = 'BD'
    #     elif str(token.text) in BO:
    #         label = 'BO'
    #     # Print the token, dependency nature, head and all dependents of the token
    #     print("{:<5} | {:<15} | {:<8} | {:<15} | {:<20} | {:<25}"
    #           .format(label, str(token.text), str(token.dep_), str(token.head.text), str([child for child in token.children]), str([subtoken for subtoken in token.subtree])))

        # Use displayCy to visualize the dependency
    # displacy.render(doc, style='dep', jupyter=True, options={'distance': 120})
    # seen = set() # keep track of covered words
    #
    # chunks = []
    # for sent in doc.sents:
    #     heads = [cc for cc in sent.root.children if cc.dep_ == 'conj']
    #
    #     for head in heads:
    #         words = [ww for ww in head.subtree]
    #         for word in words:
    #             seen.add(word)
    #         chunk = (' '.join([ww.text for ww in words]))
    #         chunks.append( (head.i, chunk) )
    #
    #     unseen = [ww for ww in sent if ww not in seen]
    #     chunk = ' '.join([ww.text for ww in unseen])
    #     chunks.append( (sent.root.i, chunk) )
    #
    # chunks = sorted(chunks, key=lambda x: x[0])
    #
    # for ii, chunk in chunks:
    #     print("chunk", chunk)
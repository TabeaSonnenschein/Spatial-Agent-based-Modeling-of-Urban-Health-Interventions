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


os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Written Paper\02- Behavioural Model paper")
# csv = os.path.join(os.getcwd(), ("Evidence_instances_df_ManualLabel.csv"))
csv = os.path.join(os.getcwd(), ("Evidence_instances_df.csv"))
Evidence_instances_df = pd.read_csv(csv)

## disaggregating evidence of within sentence colocation
complete_evidence_Instances = Evidence_instances_df.iloc[list(np.where((Evidence_instances_df['BehaviorDeterminant'].notnull()) & (Evidence_instances_df['AssociationType'].notnull()))[0])]
complete_evidence_Instances = complete_evidence_Instances.fillna(" ")
complete_evidence_Instances['AssociationType'] = [x.replace("; ( ", "; ").replace(" ) ;", " ;").replace(" ) ", " ; ").replace(" ( ", " ; ").replace("( ", "").replace(" )", "").replace("(", "").replace(")","").replace("  "," ") for x in complete_evidence_Instances['AssociationType']]
complete_evidence_Instances['BehaviorDeterminant'] = [x.replace("; ( ", "; ").replace(" ) ;", " ;").replace(" ) ", " ; ").replace(" ( ", " ; ").replace("( ", "").replace(" )", "").replace("(", "").replace(")","").replace("  "," ") for x in complete_evidence_Instances['BehaviorDeterminant']]
# text = "This all encompassing experience wore off for a moment and in that moment, my awareness came gasping to the surface of the hallucination and I was able to consider momentarily that I had killed myself by taking an outrageous dose of an online drug and this was the most pathetic death experience of all time."
gramm_complete_sentences = [x for i in ['VB','VBG','VBD', 'VBN', 'VBP', 'VBZ'] for x,y in enumerate(complete_evidence_Instances['sentence_POS']) if i in y]
complete_evidence_Instances = complete_evidence_Instances.iloc[gramm_complete_sentences]
complete_evidence_Instances['Fullsentence'] = [x.replace("?",",") for x in complete_evidence_Instances['Fullsentence'] ]
for count, value in enumerate(complete_evidence_Instances['Fullsentence']):
    value = value.strip()
    value = re.sub(r'(\d+)( \. )(\d+)', r'\1.\3', value)
    doc = en(value)

    print("-" * 70)
    print("LABELED PHRASES")
    print("assoc:", complete_evidence_Instances['AssociationType'].iloc[count])
    print("behavDet:", complete_evidence_Instances['BehaviorDeterminant'].iloc[count])
    print("behavOpt:",complete_evidence_Instances['BehaviorOption'].iloc[count])
    print(value)
    # print("{:<5} | {:<15} | {:<8} | {:<15} | {:<20} | {:<25}".format('Tag', 'Token', 'Relation', 'Head', 'Children', 'All Children'))
    AT = list(chain.from_iterable([word.split(' ') for word in complete_evidence_Instances['AssociationType'].iloc[count].split(' ; ')]))
    BD = list(chain.from_iterable([word.split(' ') for word in complete_evidence_Instances['BehaviorDeterminant'].iloc[count].split(' ; ')]))
    BO = list(chain.from_iterable([word.split(' ') for word in complete_evidence_Instances['BehaviorOption'].iloc[count].split(' ; ')]))

    root = [word for word in doc if (word.dep_ in ['ROOT', 'advcl']) or ((word.head.dep_ == 'ROOT') and (word.dep_ == 'conj'))]
    rootpos = [token.pos_ for token in root]
    print("ROOT", root, rootpos)

    for token in root:
        # tokens = [el]
        # tokens.extend([word for word in el.children if word.dep_ in ['ccomp', 'xcomp']])
        print(token)
        clausal_complement = [word for word in token.children if word.dep_ in ['ccomp', 'xcomp']]
        clausal_complement_children = [child for cl in clausal_complement for child in cl.subtree]
        subject = [child for child in token.children if child.dep_ in ['nsubjpass', 'nsubj']]
        subject_children = [child for sub in subject for child in sub.subtree]
        preposition = [child for child in token.children if child.dep_ == 'prep']
        preposition_children = [child for prep in preposition for child in prep.subtree]
        object = [child for child in token.children if child.dep_ == 'dobj']
        object_children = [child for obj in object for child in obj.subtree]
        print(clausal_complement, clausal_complement_children)
        print(subject, subject_children)
        print(preposition, preposition_children)
        print(object, object_children)
        wordlist = list(chain.from_iterable([token.text, clausal_complement, clausal_complement_children, subject, subject_children , preposition, preposition_children, object, object_children]))
        wordlist = [str(word) for word in wordlist]
        print("local ATs", [at for at in AT if at in wordlist])
        print("local BOs", [at for at in BO if at in wordlist])
        print("local BDs", [at for at in BD if at in wordlist])
        ## join the word lists, check if variables are inside, use this as basis for seperation



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
    deplacy.render(doc)
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
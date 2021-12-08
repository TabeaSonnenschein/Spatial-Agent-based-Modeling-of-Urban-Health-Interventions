# Importing modules
import pandas as pd
import os
# Load the regular expression library
import re
import numpy as np


# Import the wordcloud library
from gensim.corpora import Dictionary
from wordcloud import WordCloud     # version 1.8.1

import gensim   # version 4.1.2
from gensim.utils import simple_preprocess
import nltk     # version 3.6.5
nltk.download('stopwords')
from nltk.corpus import stopwords
import gensim.corpora as corpora
#
from pprint import pprint

import pyLDAvis     # version 3.3.1
from pyLDAvis import gensim_models
import pickle

# os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Literature\WOS_ModalChoice_Ref\CrossrefResults")
os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Literature\WOS_ModalChoice_Ref")
# os.chdir(r"C:\Dokumente\PhD EXPANSE\Literature\WOSref\CrossrefResults\txt")

# listOfFiles = os.listdir(path=os.path.join(os.getcwd(),"txt"))
listOfFiles = os.listdir(path=os.path.join(os.getcwd(),"search3txt"))
print(listOfFiles)

text_df = pd.DataFrame(columns= ["DOI", "text"])
text_df['DOI'] = listOfFiles
print(text_df)

for textdoc in listOfFiles:
    print(listOfFiles.index(textdoc))
    text_df.iloc[listOfFiles.index(textdoc), 0] = text_df.iloc[listOfFiles.index(textdoc), 0].replace(".txt", "")
    # text_df.iloc[listOfFiles.index(textdoc), 1] = str(open(os.path.join(os.getcwd(),("txt/" + textdoc)), 'r').read())
    text_df.iloc[listOfFiles.index(textdoc), 1] = str(open(os.path.join(os.getcwd(),("search3txt/" + textdoc)), 'r').read())

print(text_df.head())
csv = os.path.join(os.getcwd(),"textcsv.csv")
pd.DataFrame(text_df).to_csv(csv)

# Remove punctuation
text_df['paper_text_processed'] = \
text_df['text'].map(lambda x: re.sub('[,\.!?]', '', x))
# Convert the titles to lowercase
text_df['paper_text_processed'] = \
text_df['paper_text_processed'].map(lambda x: x.lower())
# Print out the first rows of papers
text_df['paper_text_processed'].head()


# Join the different processed titles together.
long_string = ','.join(list((text_df.iloc[0, 2]).split()))
# print(long_string)
# Create a WordCloud object
wordcloud = WordCloud(background_color="white", max_words=5000, contour_width=3, contour_color='steelblue')
# Generate a word cloud
wordcloud.generate(long_string)
# Visualize the word cloud
wordcloud.to_image()
wordcloud.to_file("article_wordcloud.jpg")


stop_words = stopwords.words('english')
stop_words.extend(['from', 'subject', 're', 'edu', 'use', 'al', 'et', 'research',
                   'studies', 'study', 'ref', 'res', 'also', 'analysis', 'literature',
                   'review', 'en', 'journal', 'doi', 'however', 'co' 'fig'])
def sent_to_words(sentences):
    for sentence in sentences:
        # deacc=True removes punctuations
        yield(gensim.utils.simple_preprocess(str(sentence), deacc=True))
def remove_stopwords(texts):
    return [[word for word in simple_preprocess(str(doc))
             if word not in stop_words] for doc in texts]
data = text_df.paper_text_processed.values.tolist()
data_words = list(sent_to_words(data))
# remove stop words
data_words = remove_stopwords(data_words)
print(data_words[:1][0][:10])
# print(data_words)
file1 = open(os.path.join(os.getcwd(), 'Data_words.txt'), "w",
             errors="replace")
file1.writelines(str(data_words))

# Create Dictionary
id2word: Dictionary = corpora.Dictionary(data_words)
# Create Corpus
texts = data_words
# Term Document Frequency
corpus= [id2word.doc2bow(text) for text in texts]
# View
print(corpus[:1][0][:30])
# print(corpus)
file1 = open(os.path.join(os.getcwd(), 'Corpus.txt'), "w",
             errors="replace")
file1.writelines(str(corpus))

# number of topics
num_topics = 10
# Build LDA model
lda_model = gensim.models.ldamodel.LdaModel(corpus=corpus,
                                       id2word=id2word,
                                       num_topics=num_topics)
# Print the Keyword in the 10 topics
pprint(lda_model.print_topics())
doc_lda = lda_model[corpus]
pprint(lda_model)


# Visualize the topics
# pyLDAvis.enable_notebook()
# LDAvis_data_filepath = os.path.join('./results/ldavis_prepared_'+str(num_topics))
# # # this is a bit time consuming - make the if statement True
# # # if you want to execute visualization prep yourself
# if 1 == 1:
#     LDAvis_prepared = pyLDAvis.gensim.prepare(lda_model, corpus, id2word)
#     with open(LDAvis_data_filepath, 'wb') as f:
#         pickle.dump(LDAvis_prepared, f)
# # load the pre-prepared pyLDAvis data from disk
# with open(LDAvis_data_filepath, 'rb') as f:
#     LDAvis_prepared = pickle.load(f)
# pyLDAvis.save_html(LDAvis_prepared, './results/ldavis_prepared_'+ str(num_topics) +'.html')
# LDAvis_prepared

visualisation = pyLDAvis.gensim_models.prepare(lda_model, corpus, id2word)
pyLDAvis.save_html(visualisation, os.path.join(os.getcwd(),('LDA_Visualization' + str(num_topics) + '.html')))

# # https://www.machinelearningplus.com/nlp/topic-modeling-gensim-python/
#
# # Compute Coherence Score
# coherence_model_lda = CoherenceModel(model=lda_model, texts=data_lemmatized, dictionary=id2word, coherence='c_v')
# coherence_lda = coherence_model_lda.get_coherence()
# print('\nCoherence Score: ', coherence_lda)
#
#
# mallet_path = 'path/to/mallet-2.0.8/bin/mallet' # update this path
# ldamallet = gensim.models.wrappers.LdaMallet(mallet_path, corpus=corpus, num_topics=20, id2word=id2word)
# # Show Topics
# pprint(ldamallet.show_topics(formatted=False))
#
# # Compute Coherence Score
# coherence_model_ldamallet = CoherenceModel(model=ldamallet, texts=data_lemmatized, dictionary=id2word, coherence='c_v')
# coherence_ldamallet = coherence_model_ldamallet.get_coherence()
# print('\nCoherence Score: ', coherence_ldamallet)
#
# def compute_coherence_values(dictionary, corpus, texts, limit, start=2, step=3):
#     """
#     Compute c_v coherence for various number of topics
#
#     Parameters:
#     ----------
#     dictionary : Gensim dictionary
#     corpus : Gensim corpus
#     texts : List of input texts
#     limit : Max num of topics
#
#     Returns:
#     -------
#     model_list : List of LDA topic models
#     coherence_values : Coherence values corresponding to the LDA model with respective number of topics
#     """
#     coherence_values = []
#     model_list = []
#     for num_topics in range(start, limit, step):
#         model = gensim.models.wrappers.LdaMallet(mallet_path, corpus=corpus, num_topics=num_topics, id2word=id2word)
#         model_list.append(model)
#         coherencemodel = CoherenceModel(model=model, texts=texts, dictionary=dictionary, coherence='c_v')
#         coherence_values.append(coherencemodel.get_coherence())
#
#     return model_list, coherence_values
#
#
# # Can take a long time to run.
# model_list, coherence_values = compute_coherence_values(dictionary=id2word, corpus=corpus, texts=data_lemmatized, start=2, limit=40, step=6)
#
# # Show graph
# limit=40; start=2; step=6;
# x = range(start, limit, step)
# plt.plot(x, coherence_values)
# plt.xlabel("Num Topics")
# plt.ylabel("Coherence score")
# plt.legend(("coherence_values"), loc='best')
# plt.show()
#
# # Print the coherence scores
# for m, cv in zip(x, coherence_values):
#     print("Num Topics =", m, " has Coherence Value of", round(cv, 4))
#
# # Select the model and print the topics
# optimal_model = model_list[3]
# model_topics = optimal_model.show_topics(formatted=False)
# pprint(optimal_model.print_topics(num_words=10))
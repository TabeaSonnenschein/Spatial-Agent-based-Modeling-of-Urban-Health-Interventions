# Importing modules
import pandas as pd
import os
# Load the regular expression library
import re
import numpy as np
import PIL

# Import the wordcloud library
from wordcloud import WordCloud

import gensim
from gensim.utils import simple_preprocess
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
import gensim.corpora as corpora
#
# from pprint import pprint

import pyLDAvis
#import pyLDAvis.gensim
import pickle


# os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Literature\WOS_ModalChoice_Ref\CrossrefResults")
os.chdir(r"C:\Dokumente\PhD EXPANSE\Literature\WOSref\CrossrefResults\txt")

listOfFiles = os.listdir(path='C:/Dokumente/PhD EXPANSE/Literature/WOSref/CrossrefResults/txt')
print(listOfFiles)

text_df = pd.DataFrame(columns= ["DOI", "text"])
text_df['DOI'] = listOfFiles
#text_df['DOI'] = text_df['DOI'].replace(".txt", "")
print(text_df)

for textdoc in listOfFiles:
    print(listOfFiles.index(textdoc))
    text_df.iloc[listOfFiles.index(textdoc), 0] = text_df.iloc[listOfFiles.index(textdoc), 0].replace(".txt", "")
    text_df.iloc[listOfFiles.index(textdoc), 1] = str(open(textdoc, 'r').read())

print(text_df.head())
#csv = os.path.join(os.getcwd(),"textcsv.csv")
csv = r"C:\Dokumente\PhD EXPANSE\Literature\WOSref\CrossrefResults\textcsv.csv"
pd.DataFrame(text_df).to_csv(csv)
#
# Remove punctuation
text_df['paper_text_processed'] = \
text_df['text'].map(lambda x: re.sub('[,\.!?]', '', x))
# Convert the titles to lowercase
text_df['paper_text_processed'] = \
text_df['paper_text_processed'].map(lambda x: x.lower())
# Print out the first rows of papers
text_df['paper_text_processed'].head()


 # Join the different processed titles together.
long_string = ','.join(list(text_df.iloc[0, 2]))
# Create a WordCloud object
wordcloud = WordCloud(background_color="white", max_words=5000, contour_width=3, contour_color='steelblue')
# Generate a word cloud
wordcloud.generate(long_string)
# Visualize the word cloud
wordcloud.to_image()
#
#
stop_words = stopwords.words('english')
stop_words.extend(['from', 'subject', 're', 'edu', 'use'])
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
print(data_words[:1][0][:30])


# Create Dictionary
id2word = corpora.Dictionary(data_words)
# Create Corpus
texts = data_words
# Term Document Frequency
corpus = [id2word.doc2bow(text) for text in texts]
# View
print(corpus[:1][0][:30])

#
# # number of topics
# num_topics = 10
# # Build LDA model
# lda_model = gensim.models.LdaMulticore(corpus=corpus,
#                                        id2word=id2word,
#                                        num_topics=num_topics)
# # Print the Keyword in the 10 topics
# pprint(lda_model.print_topics())
# doc_lda = lda_model[corpus]

#
#
# # Visualize the topics
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
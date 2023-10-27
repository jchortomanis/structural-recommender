# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


# -*- coding: utf-8 -*-

"""
Main script used for article recommendations at Geoengineer.org.

Returns a list of entity_ids to be recommended to the user.
"""

# Fundamental imports
import time
start_time = time.time()
import pandas as pd
from bs4 import BeautifulSoup   # for html parsing
import unicodedata              # for \xa0 symbol removal
import nltk
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re
from structural_recommendations.text_preprocessor.text_preprocessing import clean_text, tokenizer, token_reduction     # text cleaning and tokenization functions
from structural_recommendations.generate_recommendations.get_recommendations_word2vec import predict_w2v
import csv
from gensim.models.word2vec import Word2Vec



STOPWORDS = set(stopwords.words('english'))
MIN_WORDS = 4
MAX_WORDS = 200

# Must also remove "-", ",", "/", "\", ".", "!" (why are they not removed?)
PATTERN_S = re.compile("\'s")           # matches `'s` from text
#PATTERN_T = re.compile("\'t")           # matches `'t` from text
PATTERN_RN = re.compile("\\r\\n")       # matches `\r` and `\n`
PATTERN_PUNC = re.compile(r"[^\w\s]")   # matches all non 0-9 A-z whitespace

all_entities = pd.read_csv('../../data/all_entities.csv')

print('number of rows:', len(all_entities))
print(all_entities.head())

# Drop rows without content
nan_indices = all_entities[all_entities['content'].isnull()].index.tolist()               # at which indices they are
print('number of entries without content', all_entities['content'].isna().sum())
print('indices of entries without content:', nan_indices)
all_entities = all_entities.dropna(subset=['title','content']).reset_index(drop=True)     # remove them
print('number of entries with content:', len(all_entities))

# Content conversion from html to text for all entries
all_entities['content'] = [' '.join(BeautifulSoup(string, "lxml").stripped_strings) for string in all_entities['content']]    # removal of most html elements
all_entities['content'] = [unicodedata.normalize("NFKD", string) for string in all_entities['content']]       # remove /xa0 etc
print(all_entities.head())


all_entities['title_content'] = all_entities['title'] + ' ' + all_entities['content']
print(all_entities.head())

all_entities = all_entities[['global_id', 'entity_type', 'entity_type_id', 'title_content']]
print(all_entities.head())

# Text cleaning and conversion to lowercase
text_list = [clean_text(individual_text) for individual_text in all_entities['title_content']]
[print(text_list[x]) for x in range(10)]

# OPTIONAL I - If we want a list of tokens instead of text for each entry
text_list_tokens = [tokenizer(individual_cleaned_text, min_words=MIN_WORDS, max_words=MAX_WORDS, stopwords=STOPWORDS, lemmatize=True) for individual_cleaned_text in text_list]
[print(text_list_tokens[x]) for x in range(10)]
[print(len(text_list_tokens[x])) for x in range(10)]

# OPTIONAL II - Reduction of the number of tokens per entry
reduced_tokens = token_reduction(text_list_tokens)
[print(len(reduced_tokens[x])) for x in range(10)]

# Concatenation of the common words in a string and conversion to tokens
#' '.join(STOPWORDS)
token_stop = [w for w in word_tokenize(' '.join(STOPWORDS))]

# Word2Vec model creation
word2vec_model = Word2Vec(min_count=0, workers = 8, vector_size=300)    # vector_size instead of size for newer Word2Vec versions
# Prepare vocab
# Το word2vec_model.build_vocab() λαμβάνει σαν όρισμα μια λίστα που αποτελείται από λίστες με αφιλτράριστα tokens
word2vec_model.build_vocab(text_list_tokens)
# Train
word2vec_model.train(text_list_tokens, total_examples=word2vec_model.corpus_count, epochs=30)

# Πρόβλεψη χρησιμοποιώντας το πρώτο στοιχείο του test set
#word2vec_best_index_1 = predict_w2v(text_list[0], text_list_tokens, word2vec_model)
#print('word2vec_best_index_1:', word2vec_best_index_1)

ten_most_similar = []
#tfidf_best_index_1 = get_recommendations_tfidf(text_list[40], tfidf_mat, vectorizer)
#print('tfidf_best_index_1:', tfidf_best_index_1)

#start_time = time.time()
for x in range(len(text_list)):
    print("x = ", x)
    ten_most_similar.append(predict_w2v(text_list[x], text_list_tokens, word2vec_model))
    print("ten_most_similar[x] = ", ten_most_similar[x])
#print("--- %s seconds ---" % (time.time() - start_time))

#[ten_most_similar.append(predict_w2v(text_list[x], text_list_tokens, word2vec_model)) for x in range(2)]
#print('ten_most_similar:', ten_most_similar)

# Save the recommendations list as a csv file
with open("output/word2vec_recommendations_list.csv", "w") as f:
    write = csv.writer(f)
    write.writerows(ten_most_similar)

# Remove the first element from each list (because is the global id of the same article)
ten_most_similar = [ten_most_similar[x][1:] for x in range(len(ten_most_similar))]

# Selecting only the 'global_id' column of the dataframe for lighter computation
global_id = all_entities['global_id']

# Mapping of the recommended list indices with the global ids of the recommended elements
most_similar_global_ids = []
for i in range(len(ten_most_similar)):
    most_similar_global_ids.append([global_id[x] for x in ten_most_similar[i]])


# Add the list of recommendations to the dataframe
all_entities_sample = all_entities[:len(ten_most_similar)].copy()
all_entities_sample['recommendations'] = most_similar_global_ids
#all_entities['recommendations'] = most_similar_global_ids

# Creation of a dictionary of recommendations with
# key: the global id of the article
# value: the list of the recommended global ids for this article
recommendations_dictionary = dict(zip(all_entities_sample['global_id'], all_entities_sample['recommendations']))
#recommendations_dictionary = dict(zip(all_entities['global_id'], all_entities['recommendations']))

# Save the recommendations dictionary as a csv file
with open("output/word2vec_recommendations_dictionary.csv", "w") as f:
    for key in recommendations_dictionary.keys():
        f.write("%s,%s\n"%(key,recommendations_dictionary[key]))

print("--- %s seconds ---" % (time.time() - start_time))
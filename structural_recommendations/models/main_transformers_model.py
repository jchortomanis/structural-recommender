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
from sentence_transformers import SentenceTransformer, util
import torch
import csv


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

# We will use paraphrase-MiniLM-L6-v2 model that satisfies “a quick model with high quality”.
model = SentenceTransformer('sentence-transformers/paraphrase-MiniLM-L6-v2')
#model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
corpus_embeddings = model.encode(text_list, convert_to_tensor=True)     # somewhat time-consuming (~4 min)

most_similar_text_indices = []

for x in range(len(text_list)):
    print("x = ", x)
    query_embedding = model.encode(text_list[x], convert_to_tensor=True)
    cos_scores = util.pytorch_cos_sim(query_embedding, corpus_embeddings)[0]
    top_results = torch.topk(cos_scores, k=len(text_list))
    most_similar_text_indices.append(top_results.indices.tolist())
    print("type(ten_most_similar[{}]) = ".format(x), type(most_similar_text_indices[x]))
    print("ten_most_similar[{}] = ".format(x), most_similar_text_indices[x])


# Save the recommendations list as a csv file
with open("../../output/transformers_all_recommendations_list_3_6.csv", "w") as f:
    write = csv.writer(f)
    write.writerows(most_similar_text_indices)

# Remove the first element from each list (because is the global id of the same article)
most_similar_text_indices = [most_similar_text_indices[x][1:] for x in range(len(most_similar_text_indices))]

# Selecting only the 'global_id' column of the dataframe for lighter computation
global_id = all_entities['global_id']

print('len(most_similar_text_indices):', len(most_similar_text_indices))

# Mapping of the recommended list indices with the global ids of the recommended elements
most_similar_global_ids = []
for i in range(len(most_similar_text_indices)):
    #print('i:', i)
    #print('most_similar_text_indices{} = '.format(i), most_similar_text_indices[i])
    most_similar_global_ids.append([global_id[x] for x in most_similar_text_indices[i]])

# Add the list of recommendations to the dataframe
all_entities_sample = all_entities[:len(most_similar_text_indices)].copy()
all_entities_sample['recommendations'] = most_similar_global_ids

# Creation of a dictionary of recommendations with
# key: the global entity id of the article
# value: the list of the recommended global ids for this article
recommendations_dictionary = dict(zip(all_entities_sample['global_id'], all_entities_sample['recommendations']))

# Save the recommendations dictionary as a csv file
with open("../../output/transformers_all_recommendations_dictionary_3_6.csv", "w") as f:
    for key in recommendations_dictionary.keys():
        f.write("%s,%s\n"%(key,recommendations_dictionary[key]))

print("--- %s seconds ---" % (time.time() - start_time))
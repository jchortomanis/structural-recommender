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
import spacy
from structural_recommendations.generate_recommendations.get_recommendations_spacy import predict_spacy
# for non-ORM queries
from orator import DatabaseManager
from structural_recommendations.database import queries
import config
db = DatabaseManager(config.database)


STOPWORDS = set(stopwords.words('english'))
MIN_WORDS = 4
MAX_WORDS = 200

# Must also remove "-", ",", "/", "\", ".", "!" (why are they not removed?)
PATTERN_S = re.compile("\'s")           # matches `'s` from text
#PATTERN_T = re.compile("\'t")           # matches `'t` from text
PATTERN_RN = re.compile("\\r\\n")       # matches `\r` and `\n`
PATTERN_PUNC = re.compile(r"[^\w\s]")   # matches all non 0-9 A-z whitespace

# Read the data
all_entities = db.select(queries.retrieve_all_entities)
all_entities = pd.DataFrame(all_entities)           # conversion to dataframe
#all_entities = pd.read_csv('data/all_entities.csv')

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

#Load pre-trained spacy model
#spacy.cli.download("en_core_web_lg")
nlp = spacy.load("en_core_web_lg")

# Το spaCy λαμβάνει σαν είσοδο κείμενο όπως το tf-idf (και όχι tokens όπως το word2vec)
# Apply the model to the sentences
spacy_train_text = [nlp(x) for x in text_list]

#spacy_best_index_1 = predict_spacy(nlp, text_list[0], spacy_train_text)
#print('spacy_best_index_1:', spacy_best_index_1)

most_similar_items = []

# Populate the list with items ordered by descending similarity
for x in range(len(text_list)):
    print("x = ", x)
    most_similar_items.append(predict_spacy(nlp, text_list[x], spacy_train_text, 10))
    print("most_similar_items[{}] = ".format(x), most_similar_items[x])

#[ten_most_similar.append(get_recommendations_tfidf(text_list[x], tfidf_mat, vectorizer)) for x in range(len(text_list))]
#print('most_similar_items:', most_similar_items)

"""
# Freshness calculation
freshness = db.select(queries.freshness)
freshness = pd.DataFrame(freshness)
freshness.to_csv('output/freshness.csv')

# Popularity calculation I
popularity_by_last_30_days_views = db.select(queries.popularity_of_items_by_last_30_days_views)
popularity_by_last_30_days_views = pd.DataFrame(popularity_by_last_30_days_views)
popularity_by_last_30_days_views.to_csv('output/popularity_by_last_30_days_views.csv')

# Popularity calculation II
popularity_of_news_created_in_2022 = db.select(queries.popularity_of_news_created_in_2022)
popularity_of_news_created_in_2022 = pd.DataFrame(popularity_of_news_created_in_2022)
popularity_of_news_created_in_2022.to_csv('output/popularity_of_news_created_in_2022.csv')
"""

"""
# Save the similarity recommendations list as a csv file
with open("output/spacy_similarity_list_3_6.csv", "w", newline='') as f:
    write = csv.writer(f)
    write.writerows(most_similar_items)
"""


# Remove the first element from each list (because is the global id of the same article)
most_similar_items = [most_similar_items[x][1:] for x in range(len(most_similar_items))]

# Selecting only the 'global_id' column of the dataframe for lighter computation
global_id = all_entities['global_id']

# Mapping of the recommended list indices with the global ids of the recommended elements
most_similar_global_ids = []
for i in range(len(most_similar_items)):
    most_similar_global_ids.append([global_id[x] for x in most_similar_items[i]])

# Add the list of recommendations to the dataframe
all_entities_sample = all_entities[:len(most_similar_items)].copy()
all_entities_sample['recommendations'] = most_similar_global_ids

# Creation of a dictionary of recommendations with
# key: the global id of the article
# value: the list of the recommended global ids for this article
recommendations_dictionary = dict(zip(all_entities_sample['global_id'], all_entities_sample['recommendations']))

# Save the recommendations dictionary as a csv file
with open("../../output/spacy_similarity_dictionary_3_6.csv", "w") as f:
    for key in recommendations_dictionary.keys():
        f.write("%s,%s\n"%(key,recommendations_dictionary[key]))

print("--- %s seconds ---" % (time.time() - start_time))
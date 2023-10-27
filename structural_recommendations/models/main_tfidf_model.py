# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


# -*- coding: utf-8 -*-

"""
Main script used for article recommendations at Geoengineer.org.

Returns a list of entity_ids to be recommended to the user.
"""

# Necessary imports
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
from sklearn.feature_extraction.text import TfidfVectorizer
from structural_recommendations.generate_recommendations.get_recommendations_tfidf import get_recommendations_tfidf
# for non-ORM queries
from orator import DatabaseManager
from structural_recommendations.database import queries
import config
import pendulum


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

all_entities = all_entities[['global_id', 'entity_type', 'entity_type_id', 'title_content', 'published_at']]
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

# TF-IDF model creation
vectorizer = TfidfVectorizer(stop_words=token_stop, tokenizer=tokenizer)

# Train the model with the corpus of documents
tfidf_mat = vectorizer.fit_transform(text_list) # -> (num_sentences, num_vocabulary)
print('tfidf_mat:', tfidf_mat)

#ten_most_similar = []
#tfidf_best_index_1 = get_recommendations_tfidf(text_list[40], tfidf_mat, vectorizer)
#print('tfidf_best_index_1:', tfidf_best_index_1)
#[ten_most_similar.append(get_recommendations_tfidf(text_list[x], tfidf_mat, vectorizer)) for x in range(len(text_list))]
#print('ten_most_similar:', ten_most_similar)


most_similar_indices = []
most_similar_scores = []

for x in range(len(all_entities)):
    print("x = ", x)
    indices, scores = get_recommendations_tfidf(text_list[x], tfidf_mat, vectorizer)
    most_similar_indices.append(indices)
    most_similar_scores.append(scores)

# Create an empty dataframe to store the n most recommended items for each entity id
grouped_recommendations = pd.DataFrame()

all_entities_ids = all_entities[['global_id', 'entity_type', 'entity_type_id', 'published_at']].copy()

# Adding a new column for the global id of the landing ('parent') page
all_entities_ids.insert(loc=0, column = 'parent_id', value = '')

# Another column to hold the score
all_entities_ids.insert(loc=5, column = 'similarity_score', value = '')


for i in range(len(all_entities)):
    print("i:", i)
    indices_scores = pd.DataFrame({'indices': most_similar_indices[i], 'scores': most_similar_scores[i]}, columns=['indices', 'scores']).sort_values('indices', ignore_index=True)
    all_entities_ids['similarity_score'] = indices_scores.scores
    df_small_education = all_entities_ids.iloc[most_similar_indices[i][1:]][all_entities_ids['entity_type'] == 'education'].copy()  # Dataframe containing all the recommended items of type 'education' ordered by descending similarity
    df_small_event = all_entities_ids.iloc[most_similar_indices[i][1:]][all_entities_ids['entity_type'] == 'event'].copy()  # The same for 'event' etc
    df_small_news = all_entities_ids.iloc[most_similar_indices[i][1:]][all_entities_ids['entity_type'] == 'news'].copy()
    df_small_software = all_entities_ids.iloc[most_similar_indices[i][1:]][all_entities_ids['entity_type'] == 'software'].copy()
    df_small = pd.concat([df_small_education[:10], df_small_event[:10], df_small_news[:10], df_small_software[:10]])  # Dataframe containing the most recommended items grouped by entity type for 'i'th item
    df_small['parent_id'] = all_entities.iloc[i]['global_id']  # Insertion of the "landing page" global id
    grouped_recommendations = grouped_recommendations.append(df_small)  # Incorporation in the global recommendations dataframe

# Optional
grouped_recommendations[['parent_id', 'global_id', 'entity_type_id']] = grouped_recommendations[['parent_id', 'global_id', 'entity_type_id']].astype('Int64')

for i in range(len(grouped_recommendations)):
    print("n:", i)
    db.table('entity_recommendations').insert_get_id({
        'entity_from_id': grouped_recommendations.iloc[i]['parent_id'],
        'entity_to_type': grouped_recommendations.iloc[i]['entity_type'],
        'entity_to_id': grouped_recommendations.iloc[i]['global_id'],
        'nlp_model': 'tf-idf',
        'weight': 1,
        'entity_to_published_at': grouped_recommendations.iloc[i]['published_at'],
        'created_at': pendulum.now(),
        'updated_at': pendulum.now()
    })


# Save the recommendations list as a csv file
grouped_recommendations.to_csv('output/tfidf_grouped_recommendations_score_published_at.csv')





"""
# Save the recommendations list as a csv file
with open("output/tfidf_all_recommendations_list.csv", "w") as f:
    write = csv.writer(f)
    write.writerows(most_similar_indices)
"""

"""
# Remove the first element from each list (because is the global id of the same article)
#ten_most_similar = [most_similar_indices[x][1:] for x in range(len(most_similar_indices))]

# Selecting only the 'global_id' column of the dataframe for lighter computation
global_id = all_entities['global_id']

# Mapping of the recommended list indices with the global ids of the recommended elements
most_similar_global_ids = []
for i in range(len(ten_most_similar)):
    most_similar_global_ids.append([global_id[x] for x in ten_most_similar[i]])

# Add the list of recommendations to the dataframe
all_entities_sample = all_entities[:len(ten_most_similar)].copy()
all_entities_sample['recommendations'] = most_similar_global_ids

# Creation of a dictionary of recommendations with
# key: the global id of the article
# value: the list of the recommended global ids for this article
recommendations_dictionary = dict(zip(all_entities_sample['global_id'], all_entities_sample['recommendations']))

# Save the recommendations dictionary as a csv file
with open("output/tfidf_all_recommendations_dictionary.csv", "w") as f:
    for key in recommendations_dictionary.keys():
        f.write("%s,%s\n"%(key,recommendations_dictionary[key]))
"""



print("--- %s seconds ---" % (time.time() - start_time))
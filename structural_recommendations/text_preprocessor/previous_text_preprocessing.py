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


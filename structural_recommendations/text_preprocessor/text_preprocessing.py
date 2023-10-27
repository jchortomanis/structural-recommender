# -*- coding: utf-8 -*-
"""
Created on Thu Jul 14 17:36:53 2022

@author: GiannisChortomanis
"""

import nltk
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from bs4 import BeautifulSoup   # for html parsing
import unicodedata              # for \xa0 symbol removal
import re

STOPWORDS = set(stopwords.words('english'))
MIN_WORDS = 4
MAX_WORDS = 200

# Must also remove "-", ",", "/", "\", ".", "!" (why are they not removed?)
PATTERN_S = re.compile("\'s")           # matches `'s` from text
#PATTERN_T = re.compile("\'t")           # matches `'t` from text
PATTERN_RN = re.compile("\\r\\n")       # matches `\r` and `\n`
PATTERN_PUNC = re.compile(r"[^\w\s]")   # matches all non 0-9 A-z whitespace


def drop_nan_content(all_entities):
    nan_indices = all_entities[all_entities['content'].isnull()].index.tolist()  # at which indices they are    # informative
    #print('number of entries without content', all_entities['content'].isna().sum())
    #print('indices of entries without content:', nan_indices)
    all_entities = all_entities.dropna(subset=['title', 'content']).reset_index(drop=True)  # remove them
    return all_entities


def html_to_text(html_series):
    text = [' '.join(BeautifulSoup(string, "lxml").stripped_strings) for string in html_series]  # removal of most html elements
    text = [unicodedata.normalize("NFKD", string) for string in text]  # remove /xa0 symbols etc
    return text


def common_words(stop_words = STOPWORDS):
    token_stop = [w for w in word_tokenize(' '.join(stop_words))]
    return token_stop


def clean_text(text):
    """
    Series of cleaning. String to lower case, remove non words characters and numbers.
        text (str): input text
    return (str): modified initial text
    """
    text = text.lower()  # lowercase text
    text = re.sub(PATTERN_S, ' ', text)
    #text = re.sub(PATTERN_T, ' ', text)
    text = re.sub(PATTERN_RN, ' ', text)
    text = re.sub(PATTERN_PUNC, ' ', text)
    return text


def tokenizer(sentence, min_words=MIN_WORDS, max_words=MAX_WORDS, stopwords=STOPWORDS, lemmatize=True):
    """
    Lemmatize, tokenize, crop and remove stop words.
    """
    if lemmatize:
        stemmer = WordNetLemmatizer()
        tokens = [stemmer.lemmatize(w) for w in word_tokenize(sentence)]
    else:
        tokens = [w for w in word_tokenize(sentence)]
        
    filtered_tokens = [w for w in tokens if (len(w) > min_words and len(w) < max_words
                                                        and w not in stopwords)]
    
    return tokens    # Να επιστρέφει τα filtered_tokens ή τα tokens;


def clean_sentences(text_list, tokens = False):
    """
    Remove irrelavant characters (in new column clean_sentence).
    Lemmatize, tokenize words into list of words (in new column tok_lem_sentence).
    """
    #print('Cleaning sentences...')
    text_list = [clean_text(individual_text) for individual_text in text_list]
    #print('cleaned text content:', text_list[0])
    if tokens == True:
        text_list_tokens = [tokenizer(individual_cleaned_text, min_words=MIN_WORDS, max_words=MAX_WORDS, stopwords=STOPWORDS, lemmatize=True) for individual_cleaned_text in text_list]
        return text_list_tokens
    else:
        return text_list
    

# OPTIONAL: Αφαίρεση των κοινών λέξεων και περικοπή του κάθε κειμένου στις 200 λέξεις ή όσες θέλουμε (αν είναι μεγαλύτερο από αυτό)
def token_reduction(text_list):
    reduced_text_list = []
    i = 0
    for sentence in text_list:
        internal = []
        counter = 0
        for w in sentence:    
            if w not in STOPWORDS:
                #print("i=:", i)
                internal.append(w)
                counter += 1
            if counter >= 200:
                break
        reduced_text_list.append(internal)
        i += 1
    return reduced_text_list
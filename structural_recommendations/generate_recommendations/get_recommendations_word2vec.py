# -*- coding: utf-8 -*-
"""
Created on Thu Jul 14 18:27:19 2022

@author: GiannisChortomanis
"""

import numpy as np


# Επιστροφή των κειμένων της βάσης, ταξινομημένες σύμφωνα με την ομοιότητα που έχουν με το κείμενο για το οποίο θέλουμε να βρούμε συστάσεις
# Ορίσματα: το κείμενο για το οποίο θέλουμε να βρούμε προτάσεις και ο αραιός πίνακας tfidf_mat που προκύπτει από την vectorizer.fit_transform()
def is_word_in_model(word, model):
    """
    Check on individual words ``word`` that it exists in ``model``.
    """
    #is_in_vocab = word in model.key_to_index.keys()
    is_in_vocab = word in model.key_to_index.keys()        # Λόγω της έκδοσης 3.6.0 της gensim (παλαιά έκδοση), το key_to_index πρέπει να αντικατασταθεί με το vocab
    #print("is_in_vocab:", is_in_vocab)
    return is_in_vocab

def predict_w2v(query_sentence, dataset, model, topk=10):
    query_sentence = query_sentence.split()
    in_vocab_list, best_index = [], [0]*topk
    for w in query_sentence:
        # remove unseen words from query sentence
        if is_word_in_model(w, model.wv):
            in_vocab_list.append(w)
    # Retrieve the similarity between two words as a distance
    if len(in_vocab_list) > 0:
        sim_mat = np.zeros(len(dataset))  # TO DO
        for i, data_sentence in enumerate(dataset):
            if data_sentence:
                sim_sentence = model.wv.n_similarity(
                        in_vocab_list, data_sentence)
            else:
                sim_sentence = 0
            sim_mat[i] = np.array(sim_sentence)
        # Take the topk highest norm
        best_index = np.argsort(sim_mat)[::-1][:topk+1]
    return best_index
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 14 18:27:19 2022

@author: GiannisChortomanis
"""

import numpy as np
from best_indices import extract_best_indices


# Επιστροφή των κειμένων της βάσης, ταξινομημένες σύμφωνα με την ομοιότητα που έχουν με το κείμενο για το οποίο θέλουμε να βρούμε συστάσεις
# Ορίσματα: το κείμενο για το οποίο θέλουμε να βρούμε προτάσεις και ο αραιός πίνακας tfidf_mat που προκύπτει από την vectorizer.fit_transform()
def predict_spacy(model, query_sentence, embed_mat, topk=10):
    """
    Predict the topk sentences after applying spacy model.
    """
    query_embed = model(query_sentence)
    mat = np.array([query_embed.similarity(line) for line in embed_mat])
    # keep if vector has a norm
    mat_mask = np.array(
        [True if line.vector_norm else False for line in embed_mat])
    best_index = extract_best_indices(mat, topk=topk, mask=mat_mask)
    return best_index
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 14 18:18:10 2022

@author: GiannisChortomanis
"""

from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# General evaluation function
def extract_best_indices(m, topk, mask=None):
    """
    Use sum of the cosine distance over all tokens and return best matches.
    m (np.array): cos matrix of shape (nb_in_tokens, nb_dict_tokens)
    topk (int): number of indices to return (from highest to lowest in order)
    """
    # return the sum on all tokens of cosinus for each sentence
    if len(m.shape) > 1:
        cos_sim = np.mean(m, axis=0)
    else: 
        cos_sim = m
    sorted_scores = np.sort(cos_sim)[::-1]
    sorted_indices = np.argsort(cos_sim)[::-1] # indices sorted from highest to smallest score
    #print("Index:", index)
    if mask is not None:
        assert mask.shape == m.shape
        mask = mask[sorted_indices]
    else:
        mask = np.ones(len(cos_sim))
    mask = np.logical_or(cos_sim[sorted_indices] != 0, mask)     # eliminate 0 cosine distance
    best_indices = sorted_indices[mask][:topk+1]   # topk+1 and not topk to overcome the fact that we will delete the first element
    sorted_scores = sorted_scores[mask][:topk+1]
    return best_indices, sorted_scores
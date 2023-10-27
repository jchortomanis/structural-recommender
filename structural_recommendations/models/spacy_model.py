"""
Main script used for article recommendations at Geoengineer.org.

Returns a list of entity_ids to be recommended to the user.
"""
from structural_recommendations.generate_recommendations import best_indices
import spacy
import numpy as np


def spacy_training(text_list):
    #Load pre-trained spacy model
    #spacy.cli.download("en_core_web_lg")
    nlp = spacy.load("en_core_web_lg")    # Το spaCy λαμβάνει σαν είσοδο κείμενο όπως το tf-idf (και όχι tokens όπως το word2vec)
    # Apply the model to the sentences
    spacy_train_text = [nlp(x) for x in text_list]
    return spacy_train_text


def predict_spacy(model, query_sentence, embed_mat, topk=10):
    """
    Predict the topk sentences after applying spacy model.
    """
    query_embed = model(query_sentence)
    mat = np.array([query_embed.similarity(line) for line in embed_mat])
    # keep if vector has a norm
    mat_mask = np.array(
        [True if line.vector_norm else False for line in embed_mat])
    best_index, sorted_scores = best_indices.extract_best_indices(mat, topk=topk, mask=mat_mask)
    return best_index, sorted_scores


def get_recommendations_spacy(nlp, text_list, text_list_spacy, topk):
    most_similar_items = []
    most_similar_scores = []
    for x in range(len(text_list)):
        #print("x = ", x)
        indices, scores = predict_spacy(nlp, text_list[x], text_list_spacy, topk)
        most_similar_items.append(indices)
        most_similar_scores.append(scores)
        #print("most_similar_items[{}] = ".format(x), most_similar_items[x])
    print('len(most_similar_items):', len(most_similar_items))
    return most_similar_items, most_similar_scores

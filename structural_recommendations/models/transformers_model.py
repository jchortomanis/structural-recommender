"""

"""

from sentence_transformers import SentenceTransformer, util
import torch
import pickle

def transformers_training(text_list):
    model = SentenceTransformer('paraphrase-MiniLM-L6-v2')      # Model selection
    corpus_embeddings = model.encode(text_list, convert_to_tensor=True)
    return model, corpus_embeddings


def get_recommendations_transformers(text_list, model, corpus_embeddings):
    most_similar_indices = []
    most_similar_scores = []
    for x in range(len(text_list)):
        #print("x = ", x)
        query_embedding = model.encode(text_list[x], convert_to_tensor=True)
        cos_scores = util.pytorch_cos_sim(query_embedding, corpus_embeddings)[0]
        top_results = torch.topk(cos_scores, k = len(corpus_embeddings))
        top_indices_list = top_results.indices.tolist()
        top_scores_list = top_results.values.tolist()
        most_similar_indices.append(top_indices_list)
        most_similar_scores.append(top_scores_list)
    return most_similar_indices, most_similar_scores
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from structural_recommendations.text_preprocessor.text_preprocessing import tokenizer
from structural_recommendations.generate_recommendations.best_indices import extract_best_indices
import pickle


def tfidf_training(text_list, stop_words, tokenizer):
    # TF-IDF model creation
    vectorizer = TfidfVectorizer(stop_words = stop_words, tokenizer = tokenizer)
    # Train the model with the corpus of documents
    tfidf_mat = vectorizer.fit_transform(text_list) # -> (num_sentences, num_vocabulary)
    #print('tfidf_mat:', tfidf_mat)
    return vectorizer, tfidf_mat


# Επιστροφή των κειμένων της βάσης, ταξινομημένες σύμφωνα με την ομοιότητα που έχουν με το κείμενο για το οποίο θέλουμε να βρούμε συστάσεις
# Ορίσματα: το κείμενο για το οποίο θέλουμε να βρούμε προτάσεις και ο αραιός πίνακας tfidf_mat που προκύπτει από την vectorizer.fit_transform()
def get_recommendations_tfidf(sentence, tfidf_mat, vectorizer):
    """
    Return the database sentences in order of highest cosine similarity relatively to each
    token of the target sentence.
    Arguments: the text for which we want to find recommendations and the sparse tfidf matrix
    which is computed by vectorizer.fit_transform()
    :param sentence: string
    :param tfidf_mat:
        shape (n_samples, n_features) or (M, n_samples, n_features)
    :param vectorizer: the tf-idf vectorizer
    """
    # Embed the query sentence
    tokens_query = [str(tok) for tok in tokenizer(sentence)]
    embed_query = vectorizer.transform(tokens_query)
    # Create list with similarity between query and dataset
    mat = cosine_similarity(embed_query, tfidf_mat)
    # Best cosine distance for each token independently
    best_indices, sorted_scores = extract_best_indices(mat, topk=tfidf_mat.shape[0])
    return best_indices, sorted_scores


def get_all_recommendations_tfidf(text_list, tfidf_mat, vectorizer):
    most_similar_indices = []
    most_similar_scores = []
    for x in range(len(text_list)):
        #print("x = ", x)
        indices, scores = get_recommendations_tfidf(text_list[x], tfidf_mat, vectorizer)
        most_similar_indices.append(indices)
        most_similar_scores.append(scores)
    return most_similar_indices, most_similar_scores
import config
from orator import DatabaseManager
import pendulum
import time
import pandas as pd


def populate_table(grouped_recommendations, model):
    #database_table_filling_time = time.time()
    db = DatabaseManager(config.database)
    chunk_size = 10000
    grouped_recommendations = [grouped_recommendations[i:i + chunk_size] for i in range(0, grouped_recommendations.shape[0], chunk_size)]
    #print('grouped_recommendations:', grouped_recommendations)
    #print('len(grouped_recommendations):', len(grouped_recommendations))
    for i in range(len(grouped_recommendations)):
        #print("chunk:", i)
        array_dict = get_chunk_dict_array(grouped_recommendations[i], model)
        db.table('entity_recommendations').insert(array_dict)
    #print("--- database_table_filling_time: %s seconds for chunk size = %s ---" % (time.time() - database_table_filling_time, chunk_size))


def get_chunk_dict_array(chunk_items, model):
    array = []
    for i in range(len(chunk_items)):
        if model not in ['tfidf', 'spacy']:
            model = 'transformers'
        array.append({
            'entity_from_type': chunk_items.iloc[i]['entity_from_type'],
            'entity_from_id': chunk_items.iloc[i]['entity_from_id'],
            'entity_from_sponsored_company_id': chunk_items.iloc[i]['entity_from_sponsored_company_id'],
            'entity_from_published_at': chunk_items.iloc[i]['entity_from_published_at'],
            'entity_to_type': chunk_items.iloc[i]['entity_to_type'],
            'entity_to_id': chunk_items.iloc[i]['entity_to_id'],
            'entity_to_sponsored_company_id': chunk_items.iloc[i]['entity_to_sponsored_company_id'],
            'entity_to_published_at': chunk_items.iloc[i]['entity_to_published_at'],
            'nlp_model': model,
            'similarity_score': chunk_items.iloc[i]['similarity_score'],
            'total_score': chunk_items.iloc[i]['similarity_score'],
            'created_at': pendulum.now(),
            'updated_at': pendulum.now()
        })
    return array






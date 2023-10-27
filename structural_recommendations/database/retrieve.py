import pandas as pd
from orator import DatabaseManager
from structural_recommendations.database import queries
import config


def data_retrieval():
    db = DatabaseManager(config.database)
    print('config.database:', config.database)
    # Read the data
    all_entities = db.select(queries.retrieve_all_entities)
    #print(all_entities)
    all_entities = pd.DataFrame(all_entities)           # conversion to dataframe
    return all_entities


def intermediate_data_retrieval(entity_type, entity_type_id):
    db = DatabaseManager(config.database)
    # Read the data
    if entity_type == 'education':
        one_entity = queries.retrieve_one_education_entry
    elif entity_type == 'events':
        one_entity = queries.retrieve_one_event_entry
    elif entity_type == 'news':
        one_entity = queries.retrieve_one_news_entry
    one_entity = one_entity.replace('local_id', entity_type_id)
    one_entity = db.select(one_entity)
    one_entity = pd.DataFrame(one_entity)           # conversion to dataframe
    return one_entity


def previous_records_deletion(model):
    db = DatabaseManager(config.database)
    delete_query = queries.previous_entries_deletion
    delete_query = delete_query.replace('MODEL', model)
    db.select(delete_query)


def reset_table_ids():
    db = DatabaseManager(config.database)
    db.select(queries.reset_1_table_ids)
    db.select(queries.reset_2_table_ids)
    db.select(queries.reset_3_table_ids)
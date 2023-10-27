import pandas as pd
import numpy as np


def dataframe_creation(all_entities, most_similar_indices, most_similar_scores):
    # Create an empty dataframe to store the n most recommended items for each entity id
    grouped_recommendations = pd.DataFrame()

    all_entities_ids = all_entities[['entity_type', 'global_id', 'company_sponsor_id', 'published_at']].copy()

    # Adding a new column for the entity type of the landing ('entity_from_id') page
    all_entities_ids.insert(loc=0, column='entity_from_type', value='')
    #all_entities_ids['entity_from_type'] = all_entities_ids['entity_type']

    # Adding a new column
    all_entities_ids.insert(loc=2, column='entity_from_sponsored_company_id', value='')

    # Adding a new column
    all_entities_ids.insert(loc=3, column='entity_from_published_at', value='')

    # Another column to hold the score
    all_entities_ids.insert(loc=6, column='similarity_score', value='')

    for i in range(len(all_entities)):
        #print("i:", i)
        indices_scores = pd.DataFrame({'indices': most_similar_indices[i], 'scores': most_similar_scores[i]}, columns=['indices', 'scores']).sort_values('indices', ignore_index=True)
        all_entities_ids['similarity_score'] = indices_scores.scores
        df_small_initial = all_entities_ids.iloc[most_similar_indices[i][1:]].copy()
        df_small_education = df_small_initial[df_small_initial['entity_type'] == 'education']  # Dataframe containing all the recommended items of type 'education' ordered by descending similarity
        df_small_event = df_small_initial[df_small_initial['entity_type'] == 'event']
        df_small_news = df_small_initial[df_small_initial['entity_type'] == 'news']
        df_small_software = df_small_initial[df_small_initial['entity_type'] == 'software']
        df_small = pd.concat([df_small_education[:10], df_small_event[:10], df_small_news[:10], df_small_software[:10]])  # Dataframe containing the most recommended items grouped by entity type for 'i'th item
        df_small['entity_from_type'] = all_entities.iloc[i]['entity_type']  # Insertion of the "landing page" entity type
        df_small['entity_from_id'] = all_entities.iloc[i]['global_id']      # Insertion of the "landing page" global id
        df_small['entity_from_sponsored_company_id'] = all_entities.iloc[i]['company_sponsor_id']
        df_small['entity_from_published_at'] = all_entities.iloc[i]['published_at']   #
        df_small = df_small.replace({np.nan: None})
        grouped_recommendations = pd.concat([grouped_recommendations, df_small])  # Incorporation in the global recommendations dataframe

    # Optional
    grouped_recommendations[['entity_from_id', 'global_id']] = grouped_recommendations[
        ['entity_from_id', 'global_id']].astype('Int64')      # entity_type_id is the 'local' entity id

    #grouped_recommendations = grouped_recommendations.replace({np.nan: None})
    grouped_recommendations.columns = ['entity_from_type', 'entity_to_type', 'entity_from_sponsored_company_id', 'entity_from_published_at', 'entity_to_id', 'entity_to_sponsored_company_id', 'similarity_score', 'entity_to_published_at', 'entity_from_id']

    #print('len(all_entities_ids):', len(all_entities_ids), '\n', "all_entities_ids.head():", all_entities_ids.head())
    return grouped_recommendations, all_entities_ids


def single_entry_dataframe_creation(all_entities, most_similar_indices, most_similar_scores, all_entities_ids, one_entity):
    # Create an empty dataframe to store the n most recommended items for the last entity id
    indices_scores = pd.DataFrame({'indices': most_similar_indices[0], 'scores': most_similar_scores[0]}, columns=['indices', 'scores']).sort_values('indices', ignore_index=True)
    all_entities_ids['similarity_score'] = indices_scores.scores
    df_small_initial = all_entities_ids.iloc[most_similar_indices[0][:]].sort_values('similarity_score', ascending=False).copy()    # The additional item is not compared to itself
    df_small_education = df_small_initial[df_small_initial['entity_type'] == 'education']  # Dataframe containing all the recommended items of type 'education' ordered by descending similarity
    df_small_event = df_small_initial[df_small_initial['entity_type'] == 'event']
    df_small_news = df_small_initial[df_small_initial['entity_type'] == 'news']
    df_small_software = df_small_initial[df_small_initial['entity_type'] == 'software']
    df_small = pd.concat([df_small_education[:10], df_small_event[:10], df_small_news[:10], df_small_software[:10]])  # Dataframe containing the most recommended items grouped by entity type for 'i'th item
    df_small['entity_from_type'] = one_entity.iloc[0]['entity_type']  # Insertion of the "landing page" entity type
    df_small['entity_from_id'] = one_entity.iloc[0]['global_id']      # Insertion of the "landing page" global id
    df_small['entity_from_sponsored_company_id'] = one_entity.iloc[0]['company_sponsor_id']
    df_small['entity_from_published_at'] = one_entity.iloc[0]['published_at']   #
    df_small = df_small.replace({np.nan: None})
    grouped_recommendations = df_small.copy()  # Incorporation in the global recommendations dataframe

    # Optional
    grouped_recommendations[['entity_from_id', 'global_id']] = grouped_recommendations[
        ['entity_from_id', 'global_id']].astype('Int64')      # entity_type_id is the 'local' entity id

    #grouped_recommendations = grouped_recommendations.replace({np.nan: None})
    grouped_recommendations.columns = ['entity_from_type', 'entity_to_type', 'entity_from_sponsored_company_id', 'entity_from_published_at', 'entity_to_id', 'entity_to_sponsored_company_id', 'similarity_score', 'entity_to_published_at', 'entity_from_id']

    return grouped_recommendations


import sys
import time
import pickle
import pandas as pd
import os
start_time = time.time()


def main(model, full_execution, export, entity_type, entity_type_id):

    import_time = time.time()

    from datetime import datetime
    from structural_recommendations.database import retrieve, fill_tables
    from structural_recommendations.text_preprocessor import text_preprocessing
    from structural_recommendations.generate_recommendations import recommendations_dataframe
    base_path = os.path.dirname(os.path.realpath(__file__))
    print(base_path)
    print('type(entity_type_id):', type(entity_type_id))
    #entity_type_id = int(entity_type_id)
    # print('type(entity_type_id):', type(entity_type_id))

    if model == 'tfidf':
        #print('\ntfidf model is used\n')
        from structural_recommendations.models import tfidf_model
    elif model == 'transformers':
        #print('\ntransformers model is used\n')
        from structural_recommendations.models import transformers_model
    elif model == 'word2vec':
        #print('\nword2vec model is used\n')
        from structural_recommendations.models import word2vec_model
    else:
        #print('\nspacy model is used\n')
        from structural_recommendations.models import spacy_model
        import spacy
        nlp = spacy.load("en_core_web_lg")      # Load pre-trained model


# *** ----------------------- PROCEDURE FOR CREATING RECOMMENDATIONS FOR ALL ITEMS ------------------------------ ***

    if full_execution != 'False':

        print("--- imports_time: %s seconds ---" % (time.time() - import_time))

        print('full_execution == True')
        data_retrieval_time = time.time()
        # i) Data retrieval
        all_entities = retrieve.data_retrieval()
        #print('Number of entries:', len(all_entities))
        #print(all_entities[:5])
        print("--- data_retrieval_time: %s seconds ---" % (time.time() - data_retrieval_time))

        text_preprocessing_time = time.time()
        # ii) Drop entries without content
        all_entities = text_preprocessing.drop_nan_content(all_entities)
        #print(all_entities['content'][:5])

        # iii) Content conversion from html to text for all entries
        all_entities['content'] = text_preprocessing.html_to_text(all_entities['content'])
        #print(all_entities['content'][:5])

        # iv) Creation of a new column containing both the title and the content for each entry. Selection of the wanted features.
        all_entities['title_content'] = all_entities['title'] + ' ' + all_entities['content']
        all_entities = all_entities[['global_id', 'entity_type', 'entity_type_id', 'title_content', 'company_sponsor_id', 'published_at']]
        print(type(all_entities))

        # v) Text cleaning and conversion to lowercase
        if model in ('tfidf', 'spacy', 'transformers'):
            text_list = text_preprocessing.clean_sentences(all_entities['title_content'])
        else:
            text_list_tokens = text_preprocessing.clean_sentences(all_entities['title_content'], tokens = True)
            """
            if reduced == 'reduced':
                text_list_tokens = text_preprocessing.token_reduction(text_list_tokens)
            """
            #[print(text_list_tokens[x]) for x in range(10)]

        # vi) Concatenation of the common words in a string and conversion to tokens
        token_stop = text_preprocessing.common_words()
        #print(token_stop)
        print("--- text_preprocessing_time: %s seconds ---" % (time.time() - text_preprocessing_time))

        # vii) Model selection, training and recommendations list creation
        if model == 'tfidf':
            tfidf_model_training_time = time.time()
            vectorizer, tfidf_mat = tfidf_model.tfidf_training(text_list, token_stop, text_preprocessing.tokenizer)
            pickle.dump(vectorizer, open(base_path + "/model_weights/vectorizer.pickle", "wb"))
            pickle.dump(tfidf_mat, open(base_path + "/model_weights/tfidf_mat.pickle", "wb"))
            print("--- tfidf_model_training_time: %s seconds ---" % (time.time() - tfidf_model_training_time))
            #print('vectorizer:', vectorizer, 'tfidf_mat:', tfidf_mat)
            tfidf_get_recommendations_time = time.time()
            most_similar_indices, most_similar_scores = tfidf_model.get_all_recommendations_tfidf(text_list, tfidf_mat, vectorizer)
            print("--- tfidf_get_recommendations_time: %s seconds ---" % (time.time() - tfidf_get_recommendations_time))
            #print('most_similar_indices:', most_similar_indices[:10], 'most_similar_scores:', most_similar_scores[:10])
        elif model == 'spacy':
            spacy_model_training_time = time.time()
            text_list_spacy = spacy_model.spacy_training(text_list)     # returns text_list items as 'spacy.tokens.doc.Doc' type
            print("--- spacy_model_training_time: %s seconds ---" % (time.time() - spacy_model_training_time))
            spacy_get_recommendations_time = time.time()
            most_similar_indices, most_similar_scores = spacy_model.get_recommendations_spacy(nlp, text_list, text_list_spacy, len(text_list))
            print("--- spacy_get_recommendations_time: %s seconds ---" % (time.time() - spacy_get_recommendations_time))
            #print('most_similar_indices:', most_similar_indices[:10], 'most_similar_scores:', most_similar_scores[:10])
        elif model == 'transformers':
            transformers_model_training_time = time.time()
            model_transformers, corpus_embeddings = transformers_model.transformers_training(text_list)      # model train
            pickle.dump(model_transformers, open(base_path + "/model_weights/model_transformers.pickle", "wb"))
            pickle.dump(corpus_embeddings, open(base_path + "/model_weights/corpus_embeddings.pickle", "wb"))
            print("--- transformers_model_training_time: %s seconds ---" % (time.time() - transformers_model_training_time))
            transformers_get_recommendations_time = time.time()
            most_similar_indices, most_similar_scores = transformers_model.get_recommendations_transformers(text_list, model_transformers, corpus_embeddings)
            print("--- transformers_get_recommendations_time: %s seconds ---" % (time.time() - transformers_get_recommendations_time))

        # viii) Store the information regarding the n most recommended items for each entity id in a dataframe
        dataframe_creation_time = time.time()
        grouped_recommendations, all_entities_ids = recommendations_dataframe.dataframe_creation(all_entities, most_similar_indices, most_similar_scores)
        all_entities_ids.to_pickle(base_path + "/model_weights/all_entities_ids.pickle")
        all_entities.to_pickle(base_path + "/model_weights/all_entities.pickle")
        #print('dataframe_length:', len(grouped_recommendations))
        print("--- dataframe_creation_time: %s seconds ---" % (time.time() - dataframe_creation_time))
        #print('grouped_recommendations:', grouped_recommendations[:20])

        # ix) Populate the database table with data from previous dataframe
        database_table_filling_time = time.time()
        #for chunk_size in [50, 100, 200, 500, 750, 1000, 2000, 5000, 10000, 20000, 50000]:
        #    fill_tables.populate_table(grouped_recommendations, model, chunk_size)
        fill_tables.populate_table(grouped_recommendations, model)
        print("--- database_table_filling_time: %s seconds ---" % (time.time() - database_table_filling_time))

        # x) Deletion of the obsolete recommendations
        retrieve.previous_records_deletion(model)
        #retrieve.reset_table_ids()

        # xi) (Optional) Save the recommendations dataframe as a compressed (zip) csv file
        csv_export_time = time.time()
        if export == 'export':
            date_time = datetime.now().strftime('%Y_%m_%d')
            grouped_recommendations = grouped_recommendations[
                ['entity_from_type', 'entity_from_id', 'entity_from_sponsored_company_id', 'entity_from_published_at',
                 'entity_to_type', 'entity_to_id', 'entity_to_sponsored_company_id', 'entity_to_published_at',
                 'similarity_score']]       # rearranging the column order
            # Without compression
            #grouped_recommendations.to_csv(base_path + '/output/{}_recommendations_{}.csv'.format(model,date_time))    # Uncompressed output csv file
            # zip compression
            compression_opts = dict(method='zip', archive_name = '{}_recommendations_{}.csv'.format(model,date_time))
            grouped_recommendations.to_csv(base_path + '/output/{}_recommendations_{}.zip'.format(model,date_time), index=False, compression=compression_opts)



        print("--- csv_export_time: %s seconds ---" % (time.time() - csv_export_time))

        print("--- main_total_time: %s seconds ---" % (time.time() - start_time))


    # *** ----------------------- PROCEDURE FOR CREATING RECOMMENDATIONS FOR ONE JUST PUBLISHED ITEM ------------------------------ ***

    else:
        model_retrieval_time = time.time()
        if model == 'tfidf':
            vectorizer_2 = pickle.load(open(base_path + '/model_weights/vectorizer.pickle', 'rb'))
            tfidf_mat_2 = pickle.load(open(base_path + '/model_weights/tfidf_mat.pickle', 'rb'))
            #print(vectorizer_2, '\n', tfidf_mat_2)
        else:
            model_transformers = pickle.load(open(base_path + '/model_weights/model_transformers.pickle', 'rb'))
            corpus_embeddings = pickle.load(open(base_path + '/model_weights/corpus_embeddings.pickle', 'rb'))
        print("--- model_retrieval_time: %s seconds ---" % (time.time() - model_retrieval_time))

        intermediate_data_retrieval_time = time.time()
        # i) Data retrieval
        #print("Entity type:", entity_type)
        one_entity = retrieve.intermediate_data_retrieval(entity_type, entity_type_id)
        #print('Number of entries:', len(one_entity))
        #print(one_entity)
        print("--- intermediate_data_retrieval_time: %s seconds ---" % (time.time() - intermediate_data_retrieval_time))

        text_preprocessing_time = time.time()
        # ii) Drop entries without content
        one_entity = text_preprocessing.drop_nan_content(one_entity)
        # print(all_entities['content'][:5])

        # iii) Content conversion from html to text for the single entry
        one_entity['content'] = text_preprocessing.html_to_text(one_entity['content'])
        # print(all_entities['content'][:5])

        # iv) Creation of a new column containing both the title and the content for the entry. Selection of the wanted features.
        one_entity['title_content'] = one_entity['title'] + ' ' + one_entity['content']
        one_entity = one_entity[
            ['global_id', 'entity_type', 'entity_type_id', 'title_content', 'company_sponsor_id', 'published_at']]
        #print(one_entity.head())

        # v) Text cleaning and conversion to lowercase
        if model in ('tfidf', 'spacy', 'transformers'):
            text_list = text_preprocessing.clean_sentences(one_entity['title_content'])
        else:
            text_list_tokens = text_preprocessing.clean_sentences(one_entity['title_content'], tokens=True)
            """
            if reduced == 'reduced':
                text_list_tokens = text_preprocessing.token_reduction(text_list_tokens)
            """
            # [print(text_list_tokens[x]) for x in range(10)]

        # vi) Concatenation of the common words in a string and conversion to tokens
        token_stop = text_preprocessing.common_words()
        # print(token_stop)
        print("--- text_preprocessing_time: %s seconds ---" % (time.time() - text_preprocessing_time))

        # vii) Model selection, training and recommendations list creation
        if model == 'tfidf':
            tfidf_get_one_recommendation_time = time.time()
            most_similar_indices, most_similar_scores = tfidf_model.get_all_recommendations_tfidf(text_list, tfidf_mat_2,
                                                                                                  vectorizer_2)
            print('most_similar_indices:', most_similar_indices, '\n', 'most_similar_scores:', most_similar_scores)
            print("--- tfidf_get_recommendations_time: %s seconds ---" % (time.time() - tfidf_get_one_recommendation_time))
            # print('most_similar_indices:', most_similar_indices[:10], 'most_similar_scores:', most_similar_scores[:10])
        elif model == 'spacy':
            spacy_model_training_time = time.time()
            text_list_spacy = spacy_model.spacy_training(
                text_list)  # returns text_list items as 'spacy.tokens.doc.Doc' type
            print("--- spacy_model_training_time: %s seconds ---" % (time.time() - spacy_model_training_time))
            spacy_get_recommendations_time = time.time()
            most_similar_indices, most_similar_scores = spacy_model.get_recommendations_spacy(nlp, text_list,
                                                                                              text_list_spacy,
                                                                                              len(text_list))
            print("--- spacy_get_recommendations_time: %s seconds ---" % (time.time() - spacy_get_recommendations_time))
            #print('most_similar_indices:', most_similar_indices[:10], 'most_similar_scores:', most_similar_scores[:10])
        elif model == 'transformers':
            transformers_get_recommendations_time = time.time()
            #print('text_list:', text_list)
            #print('len(text_list):', len(text_list), 'len(corpus_embeddings):', len(corpus_embeddings))
            most_similar_indices, most_similar_scores = transformers_model.get_recommendations_transformers(text_list,
                                                                                                            model_transformers,
                                                                                                            corpus_embeddings)
            #print('most_similar_indices:', most_similar_indices, '\n', 'most_similar_scores:', most_similar_scores)
            print("--- transformers_get_recommendations_time: %s seconds ---" % (
                        time.time() - transformers_get_recommendations_time))

        # viii) Store the information regarding the n most recommended items for the latest entity id in a dataframe
        intermediate_dataframe_creation_time = time.time()
        all_entities_ids = pd.read_pickle(base_path + "/model_weights/all_entities_ids.pickle")
        all_entities = pd.read_pickle(base_path + "/model_weights/all_entities.pickle")
        #print('len(all_entities_ids):', len(all_entities_ids), '\n', "all_entities_ids.head():", all_entities_ids.head())
        grouped_recommendations = recommendations_dataframe.single_entry_dataframe_creation(all_entities, most_similar_indices,
                                                                               most_similar_scores, all_entities_ids, one_entity)
        # print('dataframe_length:', len(grouped_recommendations))
        print("--- dataframe_creation_time: %s seconds ---" % (time.time() - intermediate_dataframe_creation_time))
        # print('grouped_recommendations:', grouped_recommendations[:20])

        # ix) Populate the database table with data from previous dataframe
        intermediate_database_table_filling_time = time.time()
        # for chunk_size in [50, 100, 200, 500, 750, 1000, 2000, 5000, 10000, 20000, 50000]:
        #    fill_tables.populate_table(grouped_recommendations, model, chunk_size)
        fill_tables.populate_table(grouped_recommendations, model)
        print("--- database_table_filling_time: %s seconds ---" % (time.time() - intermediate_database_table_filling_time))

        print("--- main_total_time: %s seconds ---" % (time.time() - start_time))

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])







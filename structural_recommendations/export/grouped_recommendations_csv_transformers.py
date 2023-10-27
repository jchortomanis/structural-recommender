import time
import pandas as pd
import nltk
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')
start_time = time.time()

# Read the dataframe with all the
all_entities = pd.read_csv('../../data/all_entities.csv')

# Drop rows without content
nan_indices = all_entities[all_entities['content'].isnull()].index.tolist()               # at which indices they are
all_entities = all_entities.dropna(subset=['title','content']).reset_index(drop=True)     # remove them

# Read the recommendations list from the tfidf model
transformers_recommendations_list = pd.read_csv('../../output/transformers_all_recommendations_list.csv', header=None)       # the csv has been saved without headers

print('len(all_entities), len(transformers_recommendations_list):', len(all_entities), len(transformers_recommendations_list))

all_entities_ids = all_entities[['global_id', 'entity_type', 'entity_type_id']].copy()

# Adding a new column for the global id of the landing page
all_entities_ids.insert(loc=0, column = 'parent_id', value = '')

# Create an empty dataframe to store the 10 most recommended items for each entity id
grouped_recommendations = pd.DataFrame()

for i in range(len(all_entities)):
    print("i:", i)
    most_similar_text_indices = transformers_recommendations_list.iloc[i][1:]      # [1:] because we do not want the first recommendation (which we assume that is the landing page itself)
    df_small_education = all_entities_ids.iloc[most_similar_text_indices[1:]][all_entities_ids['entity_type'] == 'education'].copy()  # Dataframe containing all the recommended items of type 'education' ordered by descending similarity
    df_small_equipment = all_entities_ids.iloc[most_similar_text_indices[1:]][all_entities_ids['entity_type'] == 'equipment'].copy()  # The same for 'equipment' etc
    df_small_event = all_entities_ids.iloc[most_similar_text_indices[1:]][all_entities_ids['entity_type'] == 'event'].copy()
    df_small_news = all_entities_ids.iloc[most_similar_text_indices[1:]][all_entities_ids['entity_type'] == 'news'].copy()
    df_small_software = all_entities_ids.iloc[most_similar_text_indices[1:]][all_entities_ids['entity_type'] == 'software'].copy()
    df_small = pd.concat([df_small_education[:10], df_small_equipment, df_small_event[:10], df_small_news[:10], df_small_software[:10]])  # Dataframe containing the most recommended items grouped by entity type for 'i'th item
    df_small['parent_id'] = all_entities.iloc[i]['global_id']  # Insertion of the "landing page" global id
    grouped_recommendations = grouped_recommendations.append(df_small)  # Incorporation in the global recommendations dataframe


# Optional
grouped_recommendations[['parent_id', 'global_id', 'entity_type_id']] = grouped_recommendations[['parent_id', 'global_id', 'entity_type_id']].astype('Int64')

# Save the recommendations list as a csv file
grouped_recommendations.to_csv('output/transformers_grouped_recommendations.csv')

print("--- %s seconds ---" % (time.time() - start_time))


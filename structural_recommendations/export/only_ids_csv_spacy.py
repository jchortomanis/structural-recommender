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


all_entities = all_entities[['global_id', 'entity_type', 'entity_type_id']]

# Read the recommendations list from the tfidf model
spacy_recommendations_list = pd.read_csv('../../output/spacy_recommendations_list_n_3894.csv', header=None)       # the csv has been saved without headers

print('len(all_entities), len(spacy_recommendations_list):', len(all_entities), len(spacy_recommendations_list))

# Adding a new column for the global id of the landing page
all_entities.insert(loc=0, column = 'parent_id', value = '')

# Create an empty dataframe to store the 10 most recommended items for each entity id
all_recommendations = pd.DataFrame()

for i in range(len(all_entities)):
    most_similar_text_indices = spacy_recommendations_list.iloc[i][1:]                      # get the recommended sequence numbers for the 'i'th item of the list
    df_small = all_entities.iloc[most_similar_text_indices][['parent_id', 'global_id', 'entity_type', 'entity_type_id']].copy()     # Mini dataframe containing the most recommended items for 'i'th item
    df_small['parent_id'] = all_entities.iloc[i]['global_id']           # Insertion of the "landing page" global id
    all_recommendations = all_recommendations.append(df_small)          # Incorporation in the global recommendations dataframe

#print('all_recommendations:', all_recommendations.columns)

#print('all_recommendations:', all_recommendations)

# Optional
all_recommendations[['parent_id', 'global_id', 'entity_type_id']] = all_recommendations[['parent_id', 'global_id', 'entity_type_id']].astype('Int64')

# Save the recommendations list as a csv file
all_recommendations.to_csv('output/spacy_only_ids_recommendations.csv')

print("--- %s seconds ---" % (time.time() - start_time))


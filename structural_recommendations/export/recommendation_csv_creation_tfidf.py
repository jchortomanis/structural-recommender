import time
import pandas as pd
from bs4 import BeautifulSoup   # for html parsing
import unicodedata              # for \xa0 symbol removal
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

# Content conversion from html to text for all entries
all_entities['content'] = [' '.join(BeautifulSoup(string, "lxml").stripped_strings) for string in all_entities['content']]    # removal of most html elements
all_entities['content'] = [unicodedata.normalize("NFKD", string) for string in all_entities['content']]       # remove /xa0 etc

all_entities['title_content'] = all_entities['title'] + ' ' + all_entities['content']

all_entities = all_entities[['global_id', 'entity_type', 'entity_type_id', 'title', 'content', 'title_content']]

# Read the recommendations list from the tfidf model
tfidf_recommendations_list = pd.read_csv('../../output/tfidf_recommendations_list_n_3894.csv', header=None)       # the csv has been saved without headers

print('len(all_entities), len(tfidf_recommendations_list):', len(all_entities), len(tfidf_recommendations_list))


# Create an empty dataframe to store the 10 most recommended items for each entity id
all_recommendations = pd.DataFrame()

for i in range(len(all_entities)):
    most_similar_text_indices = tfidf_recommendations_list.iloc[i][1:]                      # get the recommended sequence numbers for the 'i'th item of the list
    #print('type(most_similar_text_indices):', type(most_similar_text_indices))
    #print('most_similar_text_indices:', most_similar_text_indices)
    print('i:', i)
    all_recommendations = all_recommendations.append(all_entities.iloc[i])                  # append the 'i'th item in the "recommendation" dataframe
    all_recommendations = all_recommendations.append(all_entities.iloc[most_similar_text_indices])      # append the ten most similar items for the the 'i'th item
    all_recommendations = all_recommendations.append(pd.Series(), ignore_index=True)        # insert two empty lines for readability
    all_recommendations = all_recommendations.append(pd.Series(), ignore_index=True)

#print('all_recommendations:', all_recommendations.columns)

#print('all_recommendations:', all_recommendations)

# Optional
all_recommendations[['global_id', 'entity_type_id']] = all_recommendations[['global_id', 'entity_type_id']].astype('Int64')

# Save the recommendations list as a csv file
all_recommendations.to_csv('output/tfidf_all_recommendations.csv')

print("--- %s seconds ---" % (time.time() - start_time))


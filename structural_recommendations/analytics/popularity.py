# Necessary imports
import time
start_time = time.time()
import pandas as pd
from orator import DatabaseManager
from structural_recommendations.database import queries
import config

db = DatabaseManager(config.database)

# Read the data
all_entities = db.select(queries.retrieve_all_entities)
all_entities = pd.DataFrame(all_entities)           # conversion to dataframe

print('number of rows:', len(all_entities))
print(all_entities.head())

# Drop rows without content
nan_indices = all_entities[all_entities['content'].isnull()].index.tolist()               # at which indices they are
print('number of entries without content', all_entities['content'].isna().sum())
print('indices of entries without content:', nan_indices)
all_entities = all_entities.dropna(subset=['title','content']).reset_index(drop=True)     # remove them
print('number of entries with content:', len(all_entities))

pageviews_during_2022 = f"""
SELECT *, COUNT(*) AS day_views, sum(value) AS total_views
FROM `stats`
WHERE `key` = 'pageviews' AND YEAR(date) >= 2022
GROUP BY entity_id
ORDER BY total_views DESC 
"""

# Popularity calculation I
popularity_views_during_2022 = db.select(pageviews_during_2022)
popularity_views_during_2022 = pd.DataFrame(popularity_views_during_2022)
popularity_views_during_2022.to_csv('output/popularity_by_last_30_days_views.csv')


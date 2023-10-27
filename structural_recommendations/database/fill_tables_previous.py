import config
from orator import DatabaseManager
import pendulum


def populate_table(grouped_recommendations, model):
    db = DatabaseManager(config.database)
    for i in range(len(grouped_recommendations)):
        print("n:", i)
        db.table('entity_recommendations').insert_get_id({
            'entity_from_id': grouped_recommendations.iloc[i]['parent_id'],
            'entity_to_type': grouped_recommendations.iloc[i]['entity_type'],
            'entity_to_id': grouped_recommendations.iloc[i]['global_id'],
            'nlp_model': model,
            'weight': 1,
            'entity_to_published_at': grouped_recommendations.iloc[i]['published_at'],
            'created_at': pendulum.now(),
            'updated_at': pendulum.now()
        })






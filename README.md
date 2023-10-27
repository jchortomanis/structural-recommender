

Before executing, make sure that you have installed the environment running 'setup.py'.

main() arguments: model, full_execution, export, entity_type, entity_type_id

Typical arguments for execution for all entries:

tfidf main export

Typical arguments for execution for one item:

tfidf intermediate export news 1096

_______________________________________________________________________________________________________________________________________________________________________


--- Basic flowchart of the regular execution (finding similar recommendations for a corpus of articles/documents) ---

1. At first, after some necessary imports, we check what model did the user gave as an argument.
The 'main' function has been called using two arguments:
'model': for NLP model selection (possible values: 'tfidf', 'spacy' and 'transformers')
'intermediate': anything but 'intermediate' as a value for this case
'export': if set to 'export', a csv file with the generated recommendations will be created.
'entity_type': inactive in this case (can take any value)

2. Secondly, the data are retrieved from the database.
A query selecting all the items that belong to the categories 'Education', 'Events', 'News' and 'Software' is executed.

3. The html content of the articles is processed in order to be converted to text.

4. For each item, its title is concatenated with the previously generated text content.
A process to remove common words (stopwords), to convert the text to lowercase and to tokenize the sentences is performed.

5. The appropriate Natural Language Processing model is created (or loaded) and then is trained with the corpus of articles (if it is untrained). 
The trained model then is saved as a .pickle file in order to be used, if needed, with the "intermediate" execution discussed below. 

6. The group of recommendations is generated. For every concatenated title/content text, a list of recommended items is produced, sorted by descending cosine similarity.

7. Using the previous recommendation lists, a dataframe is created which contains the recommendations with additional information needed.
The number of the most recommended items for each entity id is limited to n (eg, 10). 
The dataframes containing the information of the whole corpus of documents are saved as a pickle file, too.

8. The database table is populated with the entries from the dataframe, so the updated recommendations are now in the database.
The obsolete recommendations are then removed.

9. (Optional) The dataframe is exported and saved as a csv file.   


_______________________________________________________________________________________________________________________________________________________________________


--- Flowchart of the non-regular or "intermediate" execution (finding similar recommendations for one just published article) ---

1. At first, after some necessary imports, we check what model did the user gave as an argument.
The 'main' function has been called using four arguments:
'model': for NLP model selection (possible values: 'tfidf', 'spacy' and 'transformers'). A model which already exists as .pickle file must be selected
'intermediate': takes the value 'False' if we have a non-regular procedure of recommendations creation for one newly published page
'export': inactive in this case (can take any value)
'entity_type': the entity type of the last published page (possible values: 'education', 'events' and 'news')

2. Secondly, the data are retrieved from the database.
The latest published item, for which we want to find similar recommendations, is selected using an SQL query.

3. The html content of the article is processed in order to be converted to text.

4. Its title is concatenated with the previously generated text content.
A process to remove common words (stopwords), to convert the text to lowercase and to tokenize the sentences is performed.

5. The previously saved as .pickle file Natural Language Processing model is loaded from the disk. No need for training here, the model is already trained.

6. The recommendations for the fresh page are generated. A list of recommended items is produced, sorted by descending cosine similarity.

7. The saved dataframes containing the information of the whole corpus of documents are loaded from disk.
Using the previous recommendation list, a dataframe is created which contains the recommendations with additional information needed.

8. The database table is populated with the entries from the dataframe, so the additional recommendations are now in the database, 
along with the recommendations generated via the "regular" execution.


_________________________________________________________________________________________________________________________________________________________________________

--- Evaluation of the recommender system ---


Definitions:

i. True Positive (TP) - Item recommended and consumed by the user.
For each 'to_id', TP = number of times 'to_id' was selected by users while it was recommended.

ii. False Positive (FP) - Item was recommended but the user didn’t consume it.
FP = number of times 'to_id' was not selected by users while it was recommended.

iii. False Negative (FN) - The recommender didn’t include the item in a recommendation and the user consumed it.
For each 'to_id', FN = # times the 'to_id' was selected at a next session step without been recommended.

iv. True Negative (TN) - It wasn’t recommended and the user didn’t consume it. There is no need to count that.


Metrics:

1. (General) Hit Rate: (# recommendation selections) / (# pageviews of the education, events, news categories)

2. Precision - What fraction of the recommended items the users consumed.
Precision = True Positive / True Positive + False Positive.
Precision = (number of times selected) / (number of times recommended), for each 'from_id' --> 'to_id' tuple (and for each 'to_id' only, if we add the numbers up for this 'to_id').
So, we 'll need for each 'from_id' --> 'to_id' couple, daily count of # times 'to_id' was recommended and # of times 'to_id' was selected.

Daily generated table/csv should have the form:

| from_id | to_id | # times to_id was recommended | # times to_id was selected |
|   41367 | 11296 |                            23 |                          5 |
|   41367 | 39764 |                             0 |                          0 |
|   41367 |  9291 |                            38 |                          0 |
|   41367 | 22670 |                             0 |                          2 |    <-- selected 2 times without been recommended
|   41367 |     . |                             . |                          . |
|   41367 |     . |                             . |                          . |
|   41367 |     . |                             . |                          . |
|    8252 | 11296 |                            12 |                          1 |
|    8252 | 22670 |                             5 |                          1 |
|    8252 |     . |                             . |                          . |
|    8252 |     . |                             . |                          . |
|    8252 |     . |                             . |                          . |
|       . |     . |                             . |                          . |
|       . |     . |                             . |                          . |
|       . |     . |                             . |                          . |

Eg:
Precision(41367 --> 11296) = 5/23 = 0.22
Precision(11296) = (5 + 1) / (23 + 12) = 0.17           <-- Average Precision of an item

Mean Average Precision (MAP) over all recommendations = sum(# times to_id was selected) / sum(# times to_id was recommended and viewed) = sum(selections) / sum(recommendations).
MAP = (2 + 5 + 1 + 1) / (23 + 38 + 12 + 5) = 9/78 = 0.12

High precision score means that our recommendations are generally selected.

3. Recall - What, out of all the items that the users consumed, was recommended.
Recall = True Positive / True Positive + False Negative.
Recall = (number of times the item was selected from the recommendations) / (number of times was viewed in general (except as a landing page / from organic search etc)).

Eg:
Recall(22670) = (1) / (1 + 2) = 1/3 = 0.33

4. Daily count of sidebar selections (popular + fresh), daily count of taskbar selections (similar).
We can infer whether the users generally prefer the most popular, fresh or similar items.

________________________________________________________________________________________________________________________________________________________________________________

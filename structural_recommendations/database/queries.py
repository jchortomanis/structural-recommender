# /* ------------------------------------------------------------------------------ */

# /* FRESHNESS - Select the 20 most recent entities from each entity type (204 total, Query took 0.2891 seconds.) */

freshness = f"""
SELECT * 
FROM (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY entity_type ORDER BY created_at DESC) AS n 
    FROM entities
    WHERE `entities`.`entity_type` IN ('education', 'events', 'news', 'software')  
    ) AS x 
WHERE n <= 50
"""

# /* ------------------------------------------------------------------------------ */

# /* POPULARITY I - Select the most popular entities by current year's pageviews (4273 total, Query took 80.5155 seconds.) */

popularity_views_during_2022 = f"""
SELECT *, COUNT(*) AS day_views, sum(value) AS total_views
FROM `stats`
WHERE `key` = 'pageviews' AND YEAR(date) >= 2022
GROUP BY entity_id
ORDER BY total_views DESC
"""

# /* ------------------------------------------------------------------------------ */

# /* POPULARITY II - Select the most popular news viewed after June 2022, regardless of when they were created (2400 total, Query took 83.2185 seconds.) */

popularity_views_from_June_2022_onwards = f"""
SELECT `stats`.`entity_id`, `stats`.`key`, `entities`.`entity_type`, `entities`.`created_at`, `entities`.`updated_at`, COUNT(*) AS days_viewed, sum(value) AS total_pageviews
FROM `stats`
INNER JOIN `entities` ON `stats`.`entity_id` = `entities`.`id`
WHERE `stats`.`key` = 'pageviews' AND YEAR(`stats`.`date`) = 2022 AND MONTH(`stats`.`date`) >= 06 AND `entities`.`entity_type` = 'news'
GROUP BY entity_id
ORDER BY total_pageviews DESC
"""

# /* ------------------------------------------------------------------------------ */

# /* POPULARITY III - Select the most popular news created in 2022 (133 total, Query took 68.0236 seconds.) */

popularity_of_news_created_in_2022 = f"""
SELECT `stats`.`entity_id`, `stats`.`key`, `entities`.`entity_type`, `entities`.`created_at`, `entities`.`updated_at`, COUNT(*) AS days_viewed, sum(value) AS total_pageviews
FROM `stats`
INNER JOIN `entities` ON `stats`.`entity_id` = `entities`.`id`
WHERE `stats`.`key` = 'pageviews' AND YEAR(`entities`.`created_at`) = 2022 AND `entities`.`entity_type` = 'news'
GROUP BY entity_id
ORDER BY total_pageviews DESC
"""

# /* ------------------------------------------------------------------------------ */

# /* POPULARITY IV - Select the most popular news created in 2022 by July 2022 pageviews (131 total, Query took 72.4081 seconds.) */

popularity_of_news_created_during_2022_and_viewed_in_July_2022 = f"""
SELECT `stats`.`entity_id`, `stats`.`key`, `entities`.`entity_type`, `entities`.`created_at`, `entities`.`updated_at`, COUNT(*) AS days_viewed, sum(value) AS total_pageviews
FROM `stats`
INNER JOIN `entities` ON `stats`.`entity_id` = `entities`.`id`
WHERE `stats`.`key` = 'pageviews'  AND YEAR(`entities`.`created_at`) = 2022 AND YEAR(`stats`.`date`) = 2022 AND MONTH(`stats`.`date`) = 07 AND `entities`.`entity_type` = 'news'
GROUP BY entity_id
ORDER BY total_pageviews DESC
"""

# /* ------------------------------------------------------------------------------ */

# /* POPULARITY V - Select the most popular items viewed during the last 30 days, regardless of when they were created (4136 total, Query took 0.7198 seconds.) */

popularity_of_items_by_last_30_days_views = f"""
SELECT `stats`.`entity_id`, `stats`.`key`, `entities`.`entity_type`, `entities`.`created_at`, `entities`.`updated_at`, COUNT(*) AS days_viewed, sum(value) AS total_pageviews
FROM `stats`
INNER JOIN `entities` ON `stats`.`entity_id` = `entities`.`id`
WHERE `stats`.`key` = 'pageviews' AND `stats`.`date` BETWEEN CURDATE() - INTERVAL 30 DAY AND CURDATE()
GROUP BY entity_id
ORDER BY total_pageviews DESC
"""

# /* ------------------------------------------------------------------------------ */

# /* POPULARITY VI (TRENDING) - Select the most popular items viewed during the last 30 days, and were also created in the last 30 days (39 total, Query took 0.7319 seconds.) */

popularity_of_items_created_in_the_previous_30_days = f"""
SELECT `stats`.`entity_id`, `stats`.`key`, `entities`.`entity_type`, `entities`.`created_at`, `entities`.`updated_at`, COUNT(*) AS days_viewed, sum(value) AS total_pageviews
FROM `stats`
INNER JOIN `entities` ON `stats`.`entity_id` = `entities`.`id`
WHERE `stats`.`key` = 'pageviews' AND `stats`.`date` BETWEEN CURDATE() - INTERVAL 30 DAY AND CURDATE() AND `entities`.`created_at` BETWEEN CURDATE() - INTERVAL 30 DAY AND CURDATE()
GROUP BY entity_id
ORDER BY total_pageviews DESC
"""

# /* ------------------------------------------------------------------------------ */

# /* POPULARITY VII (TRENDING I) - Select the most popular news items viewed during the last 30 days, and were also created in the last 30 days, including item titles */

popularity_of_news_created_in_the_previous_30_days_with_title = f"""
SELECT `trending`.`entity_id`, `trending`.`entity_type_id`, `trending`.`key`, `trending`.`entity_type`, `news`.`title`, `trending`.`created_at`, `trending`.`updated_at`, `trending`.`days_viewed`, `trending`.`total_pageviews`
FROM
(SELECT `stats`.`entity_id`, `entities`.`entity_type_id`, `stats`.`key`, `entities`.`entity_type`, `entities`.`created_at`, `entities`.`updated_at`, COUNT(*) AS days_viewed, sum(value) AS total_pageviews
FROM `stats`
JOIN `entities` ON `stats`.`entity_id` = `entities`.`id`
WHERE `stats`.`key` = 'pageviews' AND `stats`.`date` BETWEEN CURDATE() - INTERVAL 30 DAY AND CURDATE() AND `entities`.`created_at` BETWEEN CURDATE() - INTERVAL 30 DAY AND CURDATE()
GROUP BY entity_id) AS `trending`
JOIN `news` ON `trending`.`entity_type_id` = `news`.`id`
WHERE `trending`.`entity_type` = 'news'
ORDER BY total_pageviews DESC
"""

# /* ------------------------------------------------------------------------------ */

# /* NEWS TRENDS - Select the most popular news items viewed during the last 30 days, and were also created in the last 30 days (39 total, Query took 0.7319 seconds.) */

trend_of_news_created_in_the_previous_30_days = f"""
SELECT `stats`.`entity_id`, `stats`.`key`, `entities`.`entity_type`, `entities`.`created_at`, `entities`.`updated_at`, COUNT(*) AS days_viewed, sum(value) AS total_pageviews
FROM `stats`
INNER JOIN `entities` ON `stats`.`entity_id` = `entities`.`id`
WHERE `stats`.`key` = 'pageviews' AND `entities`.`entity_type` = 'news' AND `stats`.`date` BETWEEN CURDATE() - INTERVAL 30 DAY AND CURDATE() AND `entities`.`created_at` BETWEEN CURDATE() - INTERVAL 30 DAY AND CURDATE()
GROUP BY entity_id
ORDER BY total_pageviews DESC
"""

# /* ------------------------------------------------------------------------------ */

# /* NEWS POPULARITY - Select the most popular news items viewed during the last 60 days, regardless of when they were created */

popularity_of_news_viewed_in_the_previous_60_days = f"""
SELECT `stats`.`entity_id`, `stats`.`key`, `entities`.`entity_type`, `entities`.`created_at`, `entities`.`updated_at`, COUNT(*) AS days_viewed, sum(value) AS total_pageviews
FROM `stats`
INNER JOIN `entities` ON `stats`.`entity_id` = `entities`.`id`
WHERE `stats`.`key` = 'pageviews' AND `entities`.`entity_type` = 'news' AND `stats`.`date` BETWEEN CURDATE() - INTERVAL 60 DAY AND CURDATE()
GROUP BY entity_id
ORDER BY total_pageviews DESC
"""

# /* ------------------------------------------------------------------------------ */

# /* EVENTS TRENDS - Select the most popular event items viewed during the last 30 days, and were also created in the last 30 days (39 total, Query took 0.7319 seconds.) */

trend_of_events_created_in_the_previous_30_days = f"""
SELECT `trending`.`entity_id`, `trending`.`entity_type_id`, `trending`.`key`, `trending`.`entity_type`, `trending`.`created_at`, `trending`.`updated_at`, `trending`.`days_viewed`, `trending`.`total_pageviews`
FROM
(SELECT `stats`.`entity_id`, `entities`.`entity_type_id`, `stats`.`key`, `entities`.`entity_type`, `entities`.`created_at`, `entities`.`updated_at`, COUNT(*) AS days_viewed, sum(value) AS total_pageviews
FROM `stats`
JOIN `entities` ON `stats`.`entity_id` = `entities`.`id`
WHERE `stats`.`key` = 'pageviews' AND `stats`.`date` BETWEEN CURDATE() - INTERVAL 30 DAY AND CURDATE() AND `entities`.`created_at` BETWEEN CURDATE() - INTERVAL 30 DAY AND CURDATE()
GROUP BY entity_id) AS `trending`
JOIN `events` ON `trending`.`entity_type_id` = `events`.`id`
WHERE `trending`.`entity_type` = 'event' AND (`events`.`type` = 'webinar' OR `events`.`start_datetime` >= CURDATE())
ORDER BY total_pageviews DESC
"""

# /* ------------------------------------------------------------------------------ */

# /* EVENTS POPULARITY - Select the most popular event items viewed during the last 60 days, regardless of when they were created */

popularity_of_events_viewed_in_the_previous_60_days = f"""
SELECT `trending`.`entity_id`, `trending`.`entity_type_id`, `trending`.`key`, `trending`.`entity_type`, `events`.`type`, `trending`.`created_at`, `trending`.`updated_at`, `trending`.`days_viewed`, `trending`.`total_pageviews`
FROM
(SELECT `stats`.`entity_id`, `entities`.`entity_type_id`, `stats`.`key`, `entities`.`entity_type`, `entities`.`created_at`, `entities`.`updated_at`, COUNT(*) AS days_viewed, sum(value) AS total_pageviews
FROM `stats`
JOIN `entities` ON `stats`.`entity_id` = `entities`.`id`
WHERE `stats`.`key` = 'pageviews' AND `stats`.`date` BETWEEN CURDATE() - INTERVAL 60 DAY AND CURDATE()
GROUP BY entity_id) AS `trending`
JOIN `events` ON `trending`.`entity_type_id` = `events`.`id`
WHERE `trending`.`entity_type` = 'event' AND (`events`.`type` = 'webinar' OR `events`.`start_datetime` >= CURDATE())
ORDER BY total_pageviews DESC
"""

# /* ------------------------------------------------------------------------------ */

# /* EDUCATION POPULARITY - Select the most popular education items viewed during the last 60 days, regardless of when they were created */

popularity_of_education_viewed_in_the_previous_60_days = f"""
SELECT `stats`.`entity_id`, `stats`.`key`, `entities`.`entity_type`, `entities`.`created_at`, `entities`.`updated_at`, COUNT(*) AS days_viewed, sum(value) AS total_pageviews
FROM `stats`
INNER JOIN `entities` ON `stats`.`entity_id` = `entities`.`id`
WHERE `stats`.`key` = 'pageviews' AND `entities`.`entity_type` = 'education' AND `stats`.`date` BETWEEN CURDATE() - INTERVAL 60 DAY AND CURDATE()
GROUP BY entity_id
ORDER BY total_pageviews DESC
"""

# /* ------------------------------------------------------------------------------ */

# /* WEBINAR POPULARITY - Select the most popular webinar items viewed during the last 60 days, regardless of when they were created */
popularity_of_webinars_viewed_in_the_previous_60_days = f"""
SELECT `trending`.`entity_id`, `trending`.`entity_type_id`, `trending`.`key`, `trending`.`entity_type`, `events`.`type`, `trending`.`created_at`, `trending`.`updated_at`, `trending`.`days_viewed`, `trending`.`total_pageviews`
FROM
(SELECT `stats`.`entity_id`, `entities`.`entity_type_id`, `stats`.`key`, `entities`.`entity_type`, `entities`.`created_at`, `entities`.`updated_at`, COUNT(*) AS days_viewed, sum(value) AS total_pageviews
FROM `stats`
JOIN `entities` ON `stats`.`entity_id` = `entities`.`id`
WHERE `stats`.`key` = 'pageviews' AND `stats`.`date` BETWEEN CURDATE() - INTERVAL 60 DAY AND CURDATE()
GROUP BY entity_id) AS `trending`
JOIN `events` ON `trending`.`entity_type_id` = `events`.`id`
WHERE `trending`.`entity_type` = 'event' AND `events`.`type` = 'webinar'
ORDER BY total_pageviews DESC
"""

# /* ------------------------------------------------------------------------------ */

# /* SOFTWARE POPULARITY - Select the most popular news items viewed during the last 60 days, regardless of when they were created */

popularity_of_software_viewed_in_the_previous_60_days = f"""
SELECT `stats`.`entity_id`, `stats`.`key`, `entities`.`entity_type`, `entities`.`created_at`, `entities`.`updated_at`, COUNT(*) AS days_viewed, sum(value) AS total_pageviews
FROM `stats`
INNER JOIN `entities` ON `stats`.`entity_id` = `entities`.`id`
WHERE `stats`.`key` = 'pageviews' AND `entities`.`entity_type` = 'software' AND `stats`.`date` BETWEEN CURDATE() - INTERVAL 60 DAY AND CURDATE()
GROUP BY entity_id
ORDER BY total_pageviews DESC
"""

# /* ------------------------------------------------------------------------------ */

# /* DATA RETRIEVAL - Select all the published education, events, news and software entries with their local and global entity ids (3922 total, Query took 0.2530 seconds.) */

retrieve_all_entities = f"""
(
SELECT `entities`.`id` AS global_id, `entities`.`entity_type`, `entities`.`entity_type_id`, `education`.`title`, `education`.`content`, `education`.`company_sponsor_id`, `education`.`published_at`
FROM `education`
INNER JOIN `entities` ON `education`.`id` = `entities`.`entity_type_id`
WHERE `entities`.`entity_type` = 'education' AND `education`.`published_at` IS NOT NULL
ORDER BY `entities`.`id`
)
UNION
(
SELECT `entities`.`id` AS global_id, `entities`.`entity_type`, `entities`.`entity_type_id`, `events`.`title`, `events`.`description` AS content, `events`.`company_sponsor_id`, `events`.`published_at`
FROM `events`
INNER JOIN `entities` ON `events`.`id` = `entities`.`entity_type_id`
WHERE `entities`.`entity_type` = 'event' AND `events`.`published_at` IS NOT NULL AND (`events`.`type` = 'webinar' OR `events`.`start_datetime` >= CURDATE())
ORDER BY `events`.`start_datetime`
)
UNION
(
SELECT `entities`.`id` AS global_id, `entities`.`entity_type`, `entities`.`entity_type_id`, `news`.`title`, `news`.`content`, `news`.`company_sponsor_id`, `news`.`published_at`
FROM `news`
INNER JOIN `entities` ON `news`.`id` = `entities`.`entity_type_id`
WHERE `entities`.`entity_type` = 'news' AND `news`.`published_at` IS NOT NULL
ORDER BY `entities`.`id`
)
UNION
(
SELECT `entities`.`id` AS global_id, `entities`.`entity_type`, `entities`.`entity_type_id`, `software`.`title`, `software`.`full_description` AS content, `software`.`company_id` AS company_sponsor_id, `software`.`published_at`
FROM `software`
INNER JOIN `entities` ON `software`.`id` = `entities`.`entity_type_id`
WHERE `entities`.`entity_type` = 'software' AND `software`.`published_at` IS NOT NULL
ORDER BY `entities`.`id`
)
"""

# /* ------------------------------------------------------------------------------ */

# /* SINGLE DATA RETRIEVAL - Select the last published education, events or news entry with its local and global entity id */

retrieve_one_education_entry = f"""
SELECT `entities`.`id` AS global_id, `entities`.`entity_type`, `entities`.`entity_type_id`, `education`.`title`, `education`.`content`, `education`.`company_sponsor_id`, `education`.`published_at`
FROM `education`
INNER JOIN `entities` ON `education`.`id` = `entities`.`entity_type_id`
WHERE `entities`.`entity_type` = 'education' AND `entities`.`entity_type_id` = 'local_id'
"""

retrieve_one_event_entry = f"""
SELECT `entities`.`id` AS global_id, `entities`.`entity_type`, `entities`.`entity_type_id`, `events`.`title`, `events`.`description` AS content, `events`.`company_sponsor_id`, `events`.`published_at`
FROM `events`
INNER JOIN `entities` ON `events`.`id` = `entities`.`entity_type_id`
WHERE `entities`.`entity_type` = 'event' AND `entities`.`entity_type_id` = 'local_id'
"""

retrieve_one_news_entry = f"""
SELECT `entities`.`id` AS global_id, `entities`.`entity_type`, `entities`.`entity_type_id`, `news`.`title`, `news`.`content`, `news`.`company_sponsor_id`, `news`.`published_at`
FROM `news`
INNER JOIN `entities` ON `news`.`id` = `entities`.`entity_type_id`
WHERE `entities`.`entity_type` = 'news' AND `entities`.`entity_type_id` = 'local_id'
"""

# /* ------------------------------------------------------------------------------ */

# /* DATA DELETION - Delete all entries older than today */

previous_entries_deletion = f"""
DELETE FROM `entity_recommendations` where `nlp_model` = 'MODEL' and DATE(`created_at`) <= CURDATE() - INTERVAL 1 DAY
"""

reset_1_table_ids = f"""
ALTER TABLE `entity_recommendations` DROP `id`;
"""

reset_2_table_ids = f"""
ALTER TABLE `entity_recommendations` AUTO_INCREMENT = 1;
"""

reset_3_table_ids = f"""
ALTER TABLE `entity_recommendations` ADD `id` int UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY FIRST;
"""

# /* ------------------------------------------------------------------------------ */

# /* POPULARITY INCLUDING TITLES - Select the most popular items viewed during the last 30 days, including item titles */

popularity_of_items_created_in_the_previous_30_days_with_title = f"""
(
SELECT `trending`.`entity_id`, `trending`.`entity_type_id`, `trending`.`key`, `trending`.`entity_type`, `news`.`title`, `trending`.`created_at`, `trending`.`updated_at`, `trending`.`days_viewed`, `trending`.`total_pageviews`
FROM
(SELECT `stats`.`entity_id`, `entities`.`entity_type_id`, `stats`.`key`, `entities`.`entity_type`, `entities`.`created_at`, `entities`.`updated_at`, COUNT(*) AS days_viewed, sum(value) AS total_pageviews
FROM `stats`
JOIN `entities` ON `stats`.`entity_id` = `entities`.`id`
WHERE `stats`.`key` = 'pageviews' AND `stats`.`date` BETWEEN CURDATE() - INTERVAL 30 DAY AND CURDATE()
GROUP BY entity_id) AS `trending`
JOIN `news` ON `trending`.`entity_type_id` = `news`.`id`
WHERE `trending`.`entity_type` = 'news'
)
UNION
(
SELECT `trending`.`entity_id`, `trending`.`entity_type_id`, `trending`.`key`, `trending`.`entity_type`, `education`.`title`, `trending`.`created_at`, `trending`.`updated_at`, `trending`.`days_viewed`, `trending`.`total_pageviews`
FROM
(SELECT `stats`.`entity_id`, `entities`.`entity_type_id`, `stats`.`key`, `entities`.`entity_type`, `entities`.`created_at`, `entities`.`updated_at`, COUNT(*) AS days_viewed, sum(value) AS total_pageviews
FROM `stats`
JOIN `entities` ON `stats`.`entity_id` = `entities`.`id`
WHERE `stats`.`key` = 'pageviews' AND `stats`.`date` BETWEEN CURDATE() - INTERVAL 30 DAY AND CURDATE()
GROUP BY entity_id) AS `trending`
JOIN `education` ON `trending`.`entity_type_id` = `education`.`id`
WHERE `trending`.`entity_type` = 'education'
)
UNION
(
SELECT `trending`.`entity_id`, `trending`.`entity_type_id`, `trending`.`key`, `trending`.`entity_type`, `events`.`title`, `trending`.`created_at`, `trending`.`updated_at`, `trending`.`days_viewed`, `trending`.`total_pageviews`
FROM
(SELECT `stats`.`entity_id`, `entities`.`entity_type_id`, `stats`.`key`, `entities`.`entity_type`, `entities`.`created_at`, `entities`.`updated_at`, COUNT(*) AS days_viewed, sum(value) AS total_pageviews
FROM `stats`
JOIN `entities` ON `stats`.`entity_id` = `entities`.`id`
WHERE `stats`.`key` = 'pageviews' AND `stats`.`date` BETWEEN CURDATE() - INTERVAL 30 DAY AND CURDATE()
GROUP BY entity_id) AS `trending`
JOIN `events` ON `trending`.`entity_type_id` = `events`.`id`
WHERE `trending`.`entity_type` = 'event'
)
UNION
(
SELECT `trending`.`entity_id`, `trending`.`entity_type_id`, `trending`.`key`, `trending`.`entity_type`, `software`.`title`, `trending`.`created_at`, `trending`.`updated_at`, `trending`.`days_viewed`, `trending`.`total_pageviews`
FROM
(SELECT `stats`.`entity_id`, `entities`.`entity_type_id`, `stats`.`key`, `entities`.`entity_type`, `entities`.`created_at`, `entities`.`updated_at`, COUNT(*) AS days_viewed, sum(value) AS total_pageviews
FROM `stats`
JOIN `entities` ON `stats`.`entity_id` = `entities`.`id`
WHERE `stats`.`key` = 'pageviews' AND `stats`.`date` BETWEEN CURDATE() - INTERVAL 30 DAY AND CURDATE()
GROUP BY entity_id) AS `trending`
JOIN `software` ON `trending`.`entity_type_id` = `software`.`id`
WHERE `trending`.`entity_type` = 'software'
)
ORDER BY total_pageviews DESC
"""

# /* ------------------------------------------------------------------------------ */

# /* ITEMS WITHOUT IMAGES - Select news items that do not contain images */

news_items_without_images = f"""
SELECT *
FROM `news`
WHERE `news`.`id` NOT IN (SELECT `media`.`model_id`
FROM `media` 
JOIN `news` ON `media`.`model_id` = `news`.`id`
WHERE `media`.`model_type` LIKE '%news%' AND `media`.`collection_name` = 'featured_image' AND `news`.`published_at` IS NOT NULL) AND `news`.`published_at` IS NOT NULL
ORDER BY `news`.`id` DESC
"""

event_items_without_images = f"""
SELECT *
FROM `events`
WHERE `events`.`id` NOT IN (SELECT `media`.`model_id`
FROM `media` 
JOIN `events` ON `media`.`model_id` = `events`.`id`
WHERE `media`.`model_type` LIKE '%event%' AND `media`.`collection_name` = 'featured_image' AND `events`.`published_at` IS NOT NULL) AND `events`.`published_at` IS NOT NULL
ORDER BY `events`.`id` DESC
"""

education_items_without_images = f"""
SELECT *
FROM `education`
WHERE `education`.`id` NOT IN (SELECT `media`.`model_id`
FROM `media` 
JOIN `education` ON `media`.`model_id` = `education`.`id`
WHERE `media`.`model_type` LIKE '%education%' AND `media`.`collection_name` = 'featured_image' AND `education`.`published_at` IS NOT NULL) AND `education`.`published_at` IS NOT NULL
ORDER BY `education`.`id` DESC
"""

# /* ------------------------------------------------------------------------------ */








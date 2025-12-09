-- Clean up duplicate topics
USE social_engineering_db;

-- First, let's see what we have
SELECT topic_id, topic_number, topic_name, icon FROM topics ORDER BY topic_number, topic_id;

-- Delete duplicates, keeping only the first occurrence of each topic_number
DELETE t1 FROM topics t1
INNER JOIN topics t2 
WHERE t1.topic_number = t2.topic_number 
AND t1.topic_id > t2.topic_id;

-- Verify we have exactly 5 topics
SELECT topic_id, topic_number, topic_name, icon FROM topics ORDER BY topic_number;
SELECT COUNT(*) as topic_count FROM topics;

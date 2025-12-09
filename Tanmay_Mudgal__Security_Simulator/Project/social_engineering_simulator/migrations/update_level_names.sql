-- Migration to update level names to topic names
-- This updates the path_levels table to use specific security topics instead of generic level names

USE social_engineering_db;

-- Update level names to topics
UPDATE path_levels 
SET level_name = 'Phishing & Variations',
    description = 'Learn about phishing attacks, email scams, and social manipulation techniques.'
WHERE level_number = 1;

UPDATE path_levels 
SET level_name = 'Passwords',
    description = 'Password security, authentication best practices, and credential management.'
WHERE level_number = 2;

UPDATE path_levels 
SET level_name = 'Cloud Security',
    description = 'Securing cloud services, data protection, and cloud-based threats.'
WHERE level_number = 3;

UPDATE path_levels 
SET level_name = 'Ransomware',
    description = 'Understanding ransomware attacks, prevention, and response strategies.'
WHERE level_number = 4;

-- If there's a level 5 (though schema only shows 4), update it too
UPDATE path_levels 
SET level_name = 'Deepfakes',
    description = 'AI-generated deepfakes, manipulation detection, and digital forensics.'
WHERE level_number = 5;

SELECT 'Level names updated successfully!' as status;

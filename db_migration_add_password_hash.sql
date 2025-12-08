/* =========================================================
   CRITICAL DATABASE MIGRATION
   Add password_hash column to Users table
   =========================================================
   
   This migration adds the password_hash column that is required
   for secure user authentication with bcrypt password hashing.
   
   Run this AFTER importing DBMS_PROJECT.sql if the password_hash
   column doesn't exist in the Users table.
*/

USE FlightBookingDB;

-- Check if column already exists before adding
SET @col_exists = (SELECT COUNT(*) 
                   FROM INFORMATION_SCHEMA.COLUMNS 
                   WHERE TABLE_SCHEMA = 'FlightBookingDB' 
                   AND TABLE_NAME = 'Users' 
                   AND COLUMN_NAME = 'password_hash');

-- Add password_hash column if it doesn't exist
SET @sql_add_column = IF(@col_exists = 0,
    'ALTER TABLE Users ADD COLUMN password_hash VARCHAR(255) NOT NULL AFTER phone',
    'SELECT "Column password_hash already exists" AS status');

PREPARE stmt FROM @sql_add_column;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Add index on email for faster login queries
CREATE INDEX IF NOT EXISTS idx_users_email ON Users(email);

-- Add index on Flights for search performance
CREATE INDEX IF NOT EXISTS idx_flights_search ON Flights(source, destination, journey_date);

-- Add index on Bookings for user bookings query
CREATE INDEX IF NOT EXISTS idx_bookings_user ON Bookings(user_id);

-- Verify the changes
DESCRIBE Users;

SELECT 'Migration completed successfully!' AS status;

/* =========================================================
   USAGE INSTRUCTIONS
   =========================================================
   
   1. First, import the main schema:
      mysql -u root -p < DBMS_PROJECT.sql
   
   2. Then run this migration:
      mysql -u root -p < db_migration_add_password_hash.sql
   
   3. Verify:
      mysql -u root -p
      USE FlightBookingDB;
      DESCRIBE Users;
      
      You should see:
      - password_hash VARCHAR(255) NOT NULL
   =========================================================
*/

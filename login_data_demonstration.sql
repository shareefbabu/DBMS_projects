-- ==================================================================================
-- LOGIN DATA STORAGE DEMONSTRATION
-- ==================================================================================
-- This file demonstrates where and how login data is stored in the database
-- ==================================================================================

USE FlightBookingDB;

-- ==================================================================================
-- 1. USERS TABLE STRUCTURE
-- ==================================================================================
-- This shows the schema of the Users table where all login data is stored

DESCRIBE Users;

/*
Expected Output:
+---------------+--------------+------+-----+---------+----------------+
| Field         | Type         | Null | Key | Default | Extra          |
+---------------+--------------+------+-----+---------+----------------+
| user_id       | int          | NO   | PRI | NULL    | auto_increment |
| name          | varchar(100) | YES  |     | NULL    |                |
| email         | varchar(100) | YES  | UNI | NULL    |                |
| phone         | varchar(15)  | YES  |     | NULL    |                |
| password_hash | varchar(255) | YES  |     | (hash)  |                |
+---------------+--------------+------+-----+---------+----------------+

KEY POINTS:
- user_id: Primary Key, Auto-incremented unique identifier
- email: UNIQUE constraint ensures no duplicate registrations
- password_hash: Stores SHA-256 encrypted password (NOT plain text)
*/

-- ==================================================================================
-- 2. VIEW ALL REGISTERED USERS
-- ==================================================================================
-- This query shows all users currently registered in the system

SELECT 
    user_id,
    name,
    email,
    phone,
    LEFT(password_hash, 20) AS password_preview,
    CHAR_LENGTH(password_hash) AS hash_length
FROM Users;

/*
This displays:
- All user information
- First 20 characters of password hash (for security demonstration)
- Length of the hash (SHA-256 produces 64 character hex string)
*/

-- ==================================================================================
-- 3. COUNT TOTAL REGISTERED USERS
-- ==================================================================================

SELECT COUNT(*) AS total_registered_users FROM Users;

-- ==================================================================================
-- 4. FIND A SPECIFIC USER BY EMAIL
-- ==================================================================================
-- This is similar to what happens during login

SELECT 
    user_id,
    name,
    email,
    phone
FROM Users 
WHERE email = 'test@example.com';

-- ==================================================================================
-- 5. CHECK IF EMAIL EXISTS (Registration Validation)
-- ==================================================================================

SELECT 
    CASE 
        WHEN COUNT(*) > 0 THEN 'Email already registered'
        ELSE 'Email available'
    END AS registration_status
FROM Users 
WHERE email = 'test@example.com';

-- ==================================================================================
-- 6. VIEW USERS WITH THEIR BOOKING COUNT
-- ==================================================================================
-- Shows login data connected to booking activity

SELECT 
    u.user_id,
    u.name,
    u.email,
    u.phone,
    COUNT(b.booking_id) AS total_bookings
FROM Users u
LEFT JOIN Bookings b ON u.user_id = b.user_id
GROUP BY u.user_id, u.name, u.email, u.phone
ORDER BY total_bookings DESC;

-- ==================================================================================
-- 7. RECENT REGISTRATIONS
-- ==================================================================================
-- Shows the most recently registered users (based on user_id)

SELECT 
    user_id,
    name,
    email,
    phone,
    'Registered' AS status
FROM Users
ORDER BY user_id DESC
LIMIT 5;

-- ==================================================================================
-- 8. PASSWORD HASH VERIFICATION EXAMPLE
-- ==================================================================================
-- This demonstrates how login verification works
-- Note: In production, password hashing is done by Python backend

-- Example: Check if a specific email and password hash combination exists
SELECT 
    user_id,
    name,
    email,
    'Login Successful' AS status
FROM Users 
WHERE email = 'test@example.com' 
  AND password_hash = '8776f108e247ab1e2b323042c049c266407c81fbad41bde1e8dfc1bb66fd267e'
LIMIT 1;

-- If no rows returned, login fails

-- ==================================================================================
-- 9. SECURITY FEATURES DEMONSTRATION
-- ==================================================================================

-- Check for duplicate emails (should return 0 due to UNIQUE constraint)
SELECT email, COUNT(*) as duplicate_count
FROM Users
GROUP BY email
HAVING COUNT(*) > 1;

-- Verify all passwords are hashed (length should be 64 for SHA-256)
SELECT 
    user_id,
    name,
    email,
    CHAR_LENGTH(password_hash) AS hash_length,
    CASE 
        WHEN CHAR_LENGTH(password_hash) = 64 THEN 'Properly Hashed'
        ELSE 'WARNING: Weak Hash'
    END AS security_status
FROM Users;

-- ==================================================================================
-- 10. COMPLETE USER PROFILE WITH BOOKINGS
-- ==================================================================================
-- Shows how login data connects to the entire system

SELECT 
    u.user_id,
    u.name,
    u.email,
    u.phone,
    b.pnr,
    b.booking_date,
    b.status AS booking_status,
    f.flight_number,
    a.airline_name
FROM Users u
LEFT JOIN Bookings b ON u.user_id = b.user_id
LEFT JOIN Flights f ON b.flight_id = f.flight_id
LEFT JOIN Airlines a ON f.airline_id = a.airline_id
ORDER BY u.user_id, b.booking_date DESC;

-- ==================================================================================
-- 11. STORED PROCEDURE: RegisterUser (How registration works)
-- ==================================================================================
-- This is called by the Python backend during registration

DELIMITER //
-- Note: This procedure already exists in your database
-- Showing it here for educational purposes
/*
CREATE PROCEDURE RegisterUser(
    IN p_name VARCHAR(100),
    IN p_email VARCHAR(100),
    IN p_phone VARCHAR(15),
    IN p_password_hash VARCHAR(255)
)
BEGIN
    INSERT INTO Users (name, email, phone, password_hash)
    VALUES (p_name, p_email, p_phone, p_password_hash);
END //
*/
DELIMITER ;

-- Usage example (this is what Python backend calls):
-- CALL RegisterUser('John Doe', 'john@example.com', '9876543210', 'hashed_password_here');

-- ==================================================================================
-- 12. DATA FLOW SUMMARY
-- ==================================================================================

/*
REGISTRATION FLOW:
1. User enters: Name, Email, Phone, Password (in website/CLI)
2. Python backend (flight_booking_system.py):
   - Validates email format
   - Validates phone number
   - Hashes password using SHA-256
3. Backend calls: RegisterUser stored procedure
4. Data stored in Users table with hashed password
5. Success message returned to user

LOGIN FLOW:
1. User enters: Email, Password (in website/CLI)
2. Python backend:
   - Hashes entered password using SHA-256
   - Queries Users table: WHERE email = ? AND password_hash = ?
3. If match found:
   - User authenticated
   - user_id stored in session
   - User can now book flights
4. If no match:
   - Login fails
   - Error message shown

DATA STORAGE LOCATION:
- Database: FlightBookingDB
- Table: Users
- Columns: user_id, name, email, phone, password_hash
- Security: Passwords stored as SHA-256 hash (64 characters)
- Constraint: Email must be unique (prevents duplicate accounts)
*/

-- ==================================================================================
-- END OF DEMONSTRATION
-- ==================================================================================

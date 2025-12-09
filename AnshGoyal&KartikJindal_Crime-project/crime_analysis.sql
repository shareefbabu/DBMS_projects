DROP DATABASE IF EXISTS crime_analysis;
CREATE DATABASE crime_analysis;
USE crime_analysis;

CREATE TABLE Crime_Type (
    type_id INT AUTO_INCREMENT PRIMARY KEY,
    type_name VARCHAR(80) NOT NULL UNIQUE
);

CREATE TABLE Location (
    location_id INT AUTO_INCREMENT PRIMARY KEY,
    area VARCHAR(120) NOT NULL,
    city VARCHAR(80) NOT NULL,
    state VARCHAR(80) NOT NULL
);

CREATE TABLE Officer (
    officer_id INT AUTO_INCREMENT PRIMARY KEY,
    officer_name VARCHAR(120) NOT NULL,
    rank_name VARCHAR(60),
    phone VARCHAR(20) UNIQUE
);

CREATE TABLE Criminal (
    criminal_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    age INT,
    gender ENUM('Male','Female','Other'),
    address VARCHAR(255),
    crime_history TEXT
);

CREATE TABLE Victim (
    victim_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    age INT,
    gender ENUM('Male','Female','Other'),
    contact VARCHAR(20)
);

CREATE TABLE Crime_Case (
    case_id INT AUTO_INCREMENT PRIMARY KEY,
    case_code VARCHAR(30),
    case_date DATE NOT NULL,
    type_id INT,
    location_id INT,
    officer_id INT,
    description TEXT,
    status ENUM('Open','Investigating','Closed') DEFAULT 'Open',
    FOREIGN KEY (type_id) REFERENCES Crime_Type(type_id),
    FOREIGN KEY (location_id) REFERENCES Location(location_id),
    FOREIGN KEY (officer_id) REFERENCES Officer(officer_id)
);

CREATE TABLE Evidence (
    evidence_id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT,
    evidence_type VARCHAR(80),
    evidence_details VARCHAR(255),
    collected_on DATE,
    FOREIGN KEY (case_id) REFERENCES Crime_Case(case_id)
);
-- sample data
INSERT INTO Crime_Type(type_name) VALUES
('Theft'),('Robbery'),('Murder'),('Fraud');

INSERT INTO Location(area, city, state) VALUES
('Andheri','Mumbai','Maharashtra'),
('Noida','Delhi','Delhi');

INSERT INTO Officer(officer_name,rank_name,phone) VALUES
('Raj Kumar','Inspector','9876543210'),
('Anita Singh','SI','9876501234');

INSERT INTO Criminal(name,age,gender,address,crime_history) VALUES
('Vijay',32,'Male','Delhi','Theft Case'),
('Raman',40,'Male','Mumbai','Robbery Case');

INSERT INTO Victim(name,age,gender,contact) VALUES
('Amit',35,'Male','9090909090'),
('Sita',28,'Female','8080808080');

INSERT INTO Crime_Case(case_code,case_date,type_id,location_id,officer_id,description,status) VALUES
('CASE-001','2024-02-01',1,1,1,'Mobile theft','Open'),
('CASE-002','2024-03-10',2,2,2,'Shop robbery','Closed');

/* -------------------------------------------------------
   1) JOIN QUERY 
   ------------------------------------------------------- */
SELECT 
    c.case_code, 
    c.case_date, 
    t.type_name,
    o.officer_name,
    CONCAT(l.area, ', ', l.city) AS location
FROM crime_case c
INNER JOIN crime_type t ON c.type_id = t.type_id
LEFT JOIN officer o ON c.officer_id = o.officer_id
LEFT JOIN location l ON c.location_id = l.location_id;

/* -------------------------------------------------------
   2) VIEW CREATION 
   ------------------------------------------------------- */
CREATE OR REPLACE VIEW case_overview AS
SELECT 
    c.case_id,
    c.case_code,
    c.case_date,
    t.type_name,
    o.officer_name,
    c.status
FROM crime_case c
JOIN crime_type t ON c.type_id = t.type_id
JOIN officer o ON c.officer_id = o.officer_id;



/* -------------------------------------------------------
   3) NESTED QUERY 
   ------------------------------------------------------- */
SELECT case_code, case_date
FROM crime_case
WHERE officer_id = (
    SELECT officer_id 
    FROM officer 
    WHERE officer_name = 'Rahul Sharma'
);



/* -------------------------------------------------------
   4) AGGREGATION + GROUP BY + HAVING 
   ------------------------------------------------------- */
SELECT type_id, COUNT(*) AS total_cases
FROM crime_case
GROUP BY type_id
HAVING COUNT(*) > 2;



/* -------------------------------------------------------
   5) UNION QUERY 
   ------------------------------------------------------- */
SELECT name FROM criminal
UNION
SELECT name FROM victim;



/* -------------------------------------------------------
   6) TRIGGER (AFTER UPDATE)
   ------------------------------------------------------- */
DELIMITER $$

CREATE TRIGGER update_closed_cases
AFTER UPDATE ON crime_case
FOR EACH ROW
BEGIN
    IF NEW.status = 'Closed' AND OLD.status <> 'Closed' THEN
        UPDATE officer 
        SET case_closed = case_closed + 1
        WHERE officer_id = NEW.officer_id;
    END IF;
END $$

DELIMITER ;

/* ============================================================
   RESET DATABASE
   ============================================================ */
DROP DATABASE IF EXISTS hostel_mess;
CREATE DATABASE hostel_mess;
USE hostel_mess;

/* ============================================================
   TABLES
   ============================================================ */

CREATE TABLE admin (
  admin_id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE rooms (
  room_no INT PRIMARY KEY,
  capacity INT NOT NULL,
  occupied INT NOT NULL DEFAULT 0,
  CHECK (capacity >= 0),
  CHECK (occupied >= 0 AND occupied <= capacity)
) ENGINE=InnoDB;

CREATE TABLE students (
  student_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  roll_no VARCHAR(20) NOT NULL UNIQUE,
  room_no INT NULL,
  contact VARCHAR(15),
  email VARCHAR(100),
  FOREIGN KEY (room_no) REFERENCES rooms(room_no)
      ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE mess_menu (
  menu_id INT AUTO_INCREMENT PRIMARY KEY,
  menu_date DATE NOT NULL,
  breakfast VARCHAR(200),
  lunch VARCHAR(200),
  dinner VARCHAR(200),
  UNIQUE KEY uq_menu_date (menu_date)
) ENGINE=InnoDB;

CREATE TABLE mess_attendance (
  attendance_id INT AUTO_INCREMENT PRIMARY KEY,
  student_id INT NOT NULL,
  attendance_date DATE NOT NULL,
  status ENUM('Present','Absent') NOT NULL,
  FOREIGN KEY (student_id) REFERENCES students(student_id)
      ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE fee (
  fee_id INT AUTO_INCREMENT PRIMARY KEY,
  student_id INT NOT NULL,
  hostel_fee INT NOT NULL DEFAULT 0,
  mess_fee INT NOT NULL DEFAULT 0,
  total_fee INT NOT NULL DEFAULT 0,
  paid_fee INT NOT NULL DEFAULT 0,
  pending_fee INT NOT NULL DEFAULT 0,
  last_payment_date DATE NULL,
  FOREIGN KEY (student_id) REFERENCES students(student_id)
      ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE complaints (
  complaint_id INT AUTO_INCREMENT PRIMARY KEY,
  student_id INT NOT NULL,
  complaint_text TEXT NOT NULL,
  status ENUM('Pending','In Progress','Resolved') NOT NULL DEFAULT 'Pending',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP 
      ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (student_id) REFERENCES students(student_id)
      ON DELETE CASCADE
) ENGINE=InnoDB;

/* ============================================================
   INSERT ROOMS (100 ROOMS)
   ============================================================ */
INSERT INTO rooms (room_no, capacity, occupied) VALUES
(101,2,0),(102,2,0),(103,2,0),(104,2,0),(105,2,0),
(106,2,0),(107,2,0),(108,2,0),(109,2,0),(110,2,0),

(201,2,0),(202,2,0),(203,2,0),(204,2,0),(205,2,0),
(206,2,0),(207,2,0),(208,2,0),(209,2,0),(210,2,0),

(301,2,0),(302,2,0),(303,2,0),(304,2,0),(305,2,0),
(306,2,0),(307,2,0),(308,2,0),(309,2,0),(310,2,0),

(401,2,0),(402,2,0),(403,2,0),(404,2,0),(405,2,0),
(406,2,0),(407,2,0),(408,2,0),(409,2,0),(410,2,0),

(501,2,0),(502,2,0),(503,2,0),(504,2,0),(505,2,0),
(506,2,0),(507,2,0),(508,2,0),(509,2,0),(510,2,0);

/* ============================================================
   ADMIN
   ============================================================ */
INSERT INTO admin (username, password) 
VALUES ('warden','wardenpass');

/* ============================================================
   INDEXES
   ============================================================ */
CREATE INDEX idx_students_roll ON students(roll_no);
CREATE INDEX idx_students_room ON students(room_no);
CREATE INDEX idx_attendance_date ON mess_attendance(attendance_date);
CREATE INDEX idx_fee_student ON fee(student_id);

/* ============================================================
   TRIGGERS
   ============================================================ */
DELIMITER $$

CREATE TRIGGER trg_fee_before_insert
BEFORE INSERT ON fee
FOR EACH ROW
BEGIN
    SET NEW.pending_fee = NEW.total_fee - NEW.paid_fee;
END$$

CREATE TRIGGER trg_fee_before_update
BEFORE UPDATE ON fee
FOR EACH ROW
BEGIN
    SET NEW.pending_fee = NEW.total_fee - NEW.paid_fee;
END$$

CREATE TRIGGER trg_students_after_insert
AFTER INSERT ON students
FOR EACH ROW
BEGIN
  IF NEW.room_no IS NOT NULL THEN
    UPDATE rooms SET occupied = occupied + 1 WHERE room_no = NEW.room_no;
  END IF;
END$$

CREATE TRIGGER trg_students_before_update
BEFORE UPDATE ON students
FOR EACH ROW
BEGIN
  IF OLD.room_no IS NOT NULL AND NEW.room_no IS NULL THEN
    UPDATE rooms SET occupied = occupied - 1 WHERE room_no = OLD.room_no;

  ELSEIF OLD.room_no IS NULL AND NEW.room_no IS NOT NULL THEN
    UPDATE rooms SET occupied = occupied + 1 WHERE room_no = NEW.room_no;

  ELSEIF OLD.room_no <> NEW.room_no THEN
    UPDATE rooms SET occupied = occupied - 1 WHERE room_no = OLD.room_no;
    UPDATE rooms SET occupied = occupied + 1 WHERE room_no = NEW.room_no;
  END IF;
END$$

CREATE TRIGGER trg_students_after_delete
AFTER DELETE ON students
FOR EACH ROW
BEGIN
  IF OLD.room_no IS NOT NULL THEN
    UPDATE rooms SET occupied = occupied - 1 WHERE room_no = OLD.room_no;
  END IF;
END$$

DELIMITER ;

/* ============================================================
   STORED PROCEDURES
   ============================================================ */
DELIMITER $$

CREATE PROCEDURE allocate_room(IN p_roll VARCHAR(20), IN p_room INT)
BEGIN
  DECLARE v_student INT;
  DECLARE v_vac INT;

  SELECT student_id INTO v_student FROM students WHERE roll_no = p_roll;
  IF v_student IS NULL THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Student not found'; END IF;

  SELECT (capacity - occupied) INTO v_vac FROM rooms WHERE room_no = p_room;
  IF v_vac IS NULL THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Room not found'; END IF;

  IF v_vac <= 0 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='No vacancy in room'; END IF;

  UPDATE students SET room_no = p_room WHERE student_id = v_student;
END$$

CREATE PROCEDURE free_room(IN p_roll VARCHAR(20))
BEGIN
  DECLARE v_student INT;
  SELECT student_id INTO v_student FROM students WHERE roll_no = p_roll;
  IF v_student IS NULL THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Student not found'; END IF;

  UPDATE students SET room_no = NULL WHERE student_id = v_student;
END$$

DELIMITER ;

/* ============================================================
   50 STUDENTS
   ============================================================ */
INSERT INTO students (name, roll_no, contact, email, room_no) VALUES
('Aarav Sharma', 'BT23CSE001', '9876543210', 'aarav.sharma@upes.ac.in', 101),
('Priya Singh', 'BT23CSE002', '9898989898', 'priya.singh@upes.ac.in', 102),
('Rohan Verma', 'BT23CSE003', '9123456780', 'rohan.verma@upes.ac.in', 103),
('Ananya Mehta', 'BT23CSE004', '9988776655', 'ananya.mehta@upes.ac.in', 104),
('Kunal Mishra', 'BT23CSE005', '9900112233', 'kunal.mishra@upes.ac.in', 105),
('Simran Kaur', 'BT23CSE006', '9812345678', 'simran.kaur@upes.ac.in', 106),
('Aditya Raj', 'BT23CSE007', '9001234567', 'aditya.raj@upes.ac.in', 107),
('Neha Gupta', 'BT23CSE008', '9876501234', 'neha.gupta@upes.ac.in', 108),
('Yash Dubey', 'BT23CSE009', '9123987654', 'yash.dubey@upes.ac.in', 109),
('Sanya Kapoor', 'BT23CSE010', '9876123450', 'sanya.kapoor@upes.ac.in', 110),

('Ritesh Malhotra','BT23CSE011','9812234510','ritesh.malhotra@upes.ac.in',201),
('Tanya Bansal','BT23CSE012','9023456712','tanya.bansal@upes.ac.in',202),
('Arjun Nair','BT23CSE013','9005678923','arjun.nair@upes.ac.in',203),
('Mehak Arora','BT23CSE014','7788996655','mehak.arora@upes.ac.in',204),
('Shivam Yadav','BT23CSE015','9785612340','shivam.yadav@upes.ac.in',205),
('Isha Malviya','BT23CSE016','9877001122','isha.malviya@upes.ac.in',206),
('Krishna Chauhan','BT23CSE017','9786543211','krishna.chauhan@upes.ac.in',207),
('Aditi Kulkarni','BT23CSE018','8899776611','aditi.kulkarni@upes.ac.in',208),
('Harsh Sharma','BT23CSE019','9123098765','harsh.sharma@upes.ac.in',209),
('Diya Narang','BT23CSE020','9786509876','diya.narang@upes.ac.in',210),

('Manav Sethi', 'BT23CSE021', '9812345098', 'manav.sethi@upes.ac.in', 301),
('Kiara Arora', 'BT23CSE022', '9023145678', 'kiara.arora@upes.ac.in', 302),
('Akash Thapa', 'BT23CSE023', '9887654321', 'akash.thapa@upes.ac.in', 303),
('Suhana Jain', 'BT23CSE024', '9988774400', 'suhana.jain@upes.ac.in', 304),
('Vikram Jha', 'BT23CSE025', '9090904545', 'vikram.jha@upes.ac.in', 305),
('Pooja Rana', 'BT23CSE026', '9815671234', 'pooja.rana@upes.ac.in', 306),
('Naveen Kumar', 'BT23CSE027', '9877891234', 'naveen.kumar@upes.ac.in', 307),
('Sakshi Patel', 'BT23CSE028', '9123678901', 'sakshi.patel@upes.ac.in', 308),
('Varun Singh', 'BT23CSE029', '8700123456', 'varun.singh@upes.ac.in', 309),
('Meera Joshi', 'BT23CSE030', '9898123456', 'meera.joshi@upes.ac.in', 310),

('Ayaan Khan', 'BT23CSE031', '7788123456', 'ayaan.khan@upes.ac.in', 401),
('Ritika Taneja', 'BT23CSE032', '9988123499', 'ritika.taneja@upes.ac.in', 402),
('Sanskar Malhotra', 'BT23CSE033', '9800112233', 'sanskar.malhotra@upes.ac.in', 403),
('Shreya Chopra', 'BT23CSE034', '9877005566', 'shreya.chopra@upes.ac.in', 404),
('Devansh Goel', 'BT23CSE035', '9090901234', 'devansh.goel@upes.ac.in', 405),
('Nisha Tiwari', 'BT23CSE036', '9812234567', 'nisha.tiwari@upes.ac.in', 406),
('Yuvraj Singh', 'BT23CSE037', '9001239876', 'yuvraj.singh@upes.ac.in', 407),
('Lavanya Bhatia', 'BT23CSE038', '9876612345', 'lavanya.bhatia@upes.ac.in', 408),
('Hemant Rawat', 'BT23CSE039', '9123123498', 'hemant.rawat@upes.ac.in', 409),
('Ira Kapoor', 'BT23CSE040', '9988775511', 'ira.kapoor@upes.ac.in', 410),

('Zara Sheikh', 'BT23CSE041', '9800786543', 'zara.sheikh@upes.ac.in', 501),
('Rudra Tomar', 'BT23CSE042', '9123459087', 'rudra.tomar@upes.ac.in', 502),
('Anvi Goyal', 'BT23CSE043', '9988012345', 'anvi.goyal@upes.ac.in', 503),
('Kartik Bhandari', 'BT23CSE044', '9812456789', 'kartik.bhandari@upes.ac.in', 504),
('Tara Desai', 'BT23CSE045', '9090876543', 'tara.desai@upes.ac.in', 505),
('Raghav Puri', 'BT23CSE046', '9812346700', 'raghav.puri@upes.ac.in', 506),
('Mahima Yadav', 'BT23CSE047', '8899001122', 'mahima.yadav@upes.ac.in', 507),
('Keshav Dixit', 'BT23CSE048', '9123009988', 'keshav.dixit@upes.ac.in', 508),
('Shruti Sethi', 'BT23CSE049', '9877009988', 'shruti.sethi@upes.ac.in', 509),
('Om Prakash', 'BT23CSE050', '9001198765', 'om.prakash@upes.ac.in', 510);

/* ============================================================
   RANDOM FEE DATA (50)
   ============================================================ */
INSERT INTO fee (student_id, hostel_fee, mess_fee, total_fee, paid_fee, last_payment_date)
SELECT 
    student_id,
    50000,
    12000,
    62000,
    FLOOR(RAND()*62000),
    CURDATE() - INTERVAL FLOOR(RAND()*200) DAY
FROM students;

/* ============================================================
   RANDOM MESS ATTENDANCE (15 DAYS x 50 students)
   ============================================================ */
INSERT INTO mess_attendance (student_id, attendance_date, status)
SELECT 
    student_id,
    CURDATE() - INTERVAL (n1.num) DAY,
    IF(RAND() > 0.2, 'Present','Absent')
FROM students,
(
  SELECT 0 AS num UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION 
  SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9 UNION 
  SELECT 10 UNION SELECT 11 UNION SELECT 12 UNION SELECT 13 UNION SELECT 14
) AS n1;

/* ============================================================
   RANDOM 25 COMPLAINTS
   ============================================================ */
INSERT INTO complaints (student_id, complaint_text, status)
SELECT 
  student_id,
  CONCAT('Complaint about: ', 
         ELT(FLOOR(RAND()*6)+1,
             'Water issue','Mess food','Electricity','Cleanliness',
             'WiFi not working','Fan not working')),
  ELT(FLOOR(RAND()*3)+1,'Pending','In Progress','Resolved')
FROM students
ORDER BY RAND()
LIMIT 25;

/* ============================================================
   MESS MENU - 30 DAYS
   ============================================================ */
INSERT INTO mess_menu (menu_date, breakfast, lunch, dinner)
SELECT 
  CURDATE() + INTERVAL n DAY,
  'Poha / Paratha',
  'Dal, Sabzi, Rice',
  'Roti, Paneer / Chicken'
FROM (
  SELECT 0 n UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION
  SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9 UNION
  SELECT 10 UNION SELECT 11 UNION SELECT 12 UNION SELECT 13 UNION SELECT 14 UNION
  SELECT 15 UNION SELECT 16 UNION SELECT 17 UNION SELECT 18 UNION SELECT 19 UNION
  SELECT 20 UNION SELECT 21 UNION SELECT 22 UNION SELECT 23 UNION SELECT 24 UNION
  SELECT 25 UNION SELECT 26 UNION SELECT 27 UNION SELECT 28 UNION SELECT 29
) AS days;

/* ============================================================
   VIEWS
   ============================================================ */

CREATE VIEW vw_pending_fees AS
SELECT s.student_id, s.name, s.roll_no, f.total_fee, f.paid_fee, f.pending_fee
FROM students s
JOIN fee f ON s.student_id = f.student_id
WHERE f.pending_fee > 0;

CREATE VIEW vw_room_summary AS
SELECT room_no, capacity, occupied, (capacity - occupied) AS vacancy
FROM rooms;

CREATE VIEW vw_mess_attendance_summary AS
SELECT a.attendance_date, s.roll_no, s.name, a.status
FROM mess_attendance a
JOIN students s ON a.student_id = s.student_id;

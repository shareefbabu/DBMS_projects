CREATE DATABASE waste_sorter_db;
USE waste_sorter_db;
CREATE TABLE SORTING_LOGS (
    log_id INT PRIMARY KEY AUTO_INCREMENT,
    file_name VARCHAR(255) NOT NULL,
    ai_prediction VARCHAR(50) NOT NULL,
    prediction_score DECIMAL(5, 4),
    time_stamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
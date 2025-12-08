CREATE DATABASE IF NOT EXISTS pet_adoption CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE pet_adoption;

CREATE TABLE IF NOT EXISTS pets (
    pet_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    species VARCHAR(50) NOT NULL,
    breed VARCHAR(100),
    age INT,
    gender VARCHAR(10),
    status VARCHAR(20) DEFAULT 'Available',
    arrival_date DATE,
    description TEXT,
);

CREATE INDEX idx_pets_species ON pets(species);
CREATE INDEX idx_pets_arrival ON pets(arrival_date);

CREATE TABLE IF NOT EXISTS adopters (
    adopter_id INT PRIMARY KEY AUTO_INCREMENT,
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    date_registered DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS adoption_applications (
    application_id INT PRIMARY KEY AUTO_INCREMENT,
    pet_id INT NOT NULL,
    adopter_id INT NOT NULL,
    application_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'Pending',
    notes TEXT,
    FOREIGN KEY (pet_id) REFERENCES pets(pet_id) ON DELETE CASCADE,
    FOREIGN KEY (adopter_id) REFERENCES adopters(adopter_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS medical_records (
    record_id INT PRIMARY KEY AUTO_INCREMENT,
    pet_id INT NOT NULL,
    checkup_date DATE,
    vaccination VARCHAR(150),
    health_condition TEXT,
    treatment TEXT,
    next_due DATE,
    FOREIGN KEY (pet_id) REFERENCES pets(pet_id) ON DELETE CASCADE
);

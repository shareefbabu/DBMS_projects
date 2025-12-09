♻️ AI-Powered Waste Sorting System (Hybrid ML/DBMS)

This project implements a complete, end-to-end data pipeline for autonomous waste classification, integrating a Convolutional Neural Network (CNN) for classification with a MySQL database for auditable logging and performance analysis.

The system proves that a Relational Database Management System (DBMS) is essential for operational intelligence in Machine Learning (ML) deployment.

🌟 Project Highlights

Core Technology: TensorFlow/Keras (CNN) + MySQL (DBMS) + Python (Flask/Subprocess).

Dataset: Trained on 5,927 images across 10 categories (Plastic, Metal, Glass, etc.).

Key Feature: Implements a Live Log Streaming Bridge to securely execute local Python scripts from a web browser and display real-time terminal output.

DBMS Focus: The SORTING_LOGS table captures prediction scores, enabling complex analytical SQL queries for quality control and operational monitoring.

🛠️ System Architecture

The project runs on a three-tier model, controlled by Python scripts:

Component

Role in Project

Technology

DBMS (The Accountant)

Central Audit Log and Analytical Engine. Stores every AI decision permanently.

MySQL 8.0

AI/ML (The Brain)

Core Classification Logic. Generates category and confidence score.

TensorFlow / Keras CNN

Integration Layer (The Manager)

Connects the web interface to the local ML script and database.

Python (Flask, Subprocess)

File System

Physical input queue (UNSORTED_INPUT) and final output sorting.

shutil, os

📦 Local Setup and Installation

Follow these steps to set up the environment and execute the project locally.

1. Prerequisites

You must have the following software installed:

Python 3.8+ (Anaconda environment recommended)

MySQL Server 8.0+ (With root credentials established)

2. Install Python Dependencies

Navigate to the CODE/ directory and install the required libraries:

pip install tensorflow keras pandas scikit-learn numpy Pillow mysql-connector-python
pip install Flask flask-cors  # For the server bridge


3. Prepare the Database (DBMS Setup)

Run the SQL script to create the database and the required log table.

Log into your MySQL Command Line Client:

mysql -u root -p


Execute the setup file (adjust the path if necessary, using forward slashes /):

SOURCE C:/path/to/WasteSorter_ML/CODE/setup.sql;


This creates the waste_sorter_db and the necessary SORTING_LOGS table.

🧠 Training and Model Preparation

Note: Ensure your labeled images are organized into sub-folders within the DATASET/ directory (e.g., DATASET/Plastic/, DATASET/Metal/).

Run Training: Execute the training script to generate the model file.

cd CODE/
python train_model.py


This generates waste_sorter_model.h5 and class_labels.txt in the MODEL/ folder.

🚀 Execution and Demonstration

This project requires two processes running simultaneously for the web interface to trigger the sorting.

Step 1: Start the Server Bridge (Terminal 1)

This server listens for the command from the browser.

Open a dedicated terminal and navigate to CODE/.

Run the Flask server:

python server_bridge.py


The terminal must show: * Running on http://127.0.0.1:5000

Step 2: Prepare Input Images

Place your test images (e.g., 120 mixed files) into the UNSORTED_INPUT/ folder.

Step 3: Trigger Classification (Web Browser)

Open the Dashboard: Double-click the saved index.html file in your browser.

Execute: Navigate to the "Interactive Sorter Input" section, select the files, and click "Start Classification Run."

Verification: Live Logs and Database Proof

Live Logs: The Browser's Live Operations Monitor will start streaming the output from the Python script, showing the prediction score and low-confidence warnings in real-time.

Physical Sort: The images will be moved from UNSORTED_INPUT/ to OUTPUT_FOLDERS/.

DBMS Proof: Open a third terminal, log into MySQL, and confirm the logs were inserted:

SELECT COUNT(*) FROM waste_sorter_db.SORTING_LOGS; 
-- Expected result: The total count of images classified.


📈 Key Analytical Queries (DBMS Value)

These queries demonstrate the core functionality required for a strong DBMS project:

Analysis Goal

SQL Query Structure

DBMS Feature

Waste Volume

SELECT ai_prediction, COUNT(*) FROM SORTING_LOGS GROUP BY ai_prediction;

Aggregation, Grouping

Quality Control (Audit)

SELECT file_name, prediction_score FROM SORTING_LOGS WHERE prediction_score < 0.80;

Filtering (WHERE), Performance Indexing
import tensorflow as tf
import numpy as np
import os, shutil, csv, mysql.connector
from PIL import Image
from datetime import datetime

# --- CONFIGURATION ---
MODEL_PATH = '../MODEL/waste_sorter_model.h5'
LABELS_PATH = '../MODEL/class_labels.txt'
INPUT_DIR = '../UNSORTED_INPUT'
OUTPUT_ROOT = '../OUTPUT_FOLDERS'
LOG_CSV_FOLDER = '../CSV_LOGS'
IMG_SIZE = 128
DB_CONFIG = {
    'user': 'root', 'password': 'letitbeX',  # <<< VERIFY PASSWORD!
    'host': '127.0.0.1', 'database': 'waste_sorter_db'
    }

# --- 1. Model & Label Loading (Runs once at start) ---
model = tf.keras.models.load_model(MODEL_PATH)
with open(LABELS_PATH, 'r') as f:
    CLASS_LABELS = [line.strip() for line in f]

# --- 2. CORE CLASSIFICATION FUNCTION (Must be defined here) ---
def classify_and_process(file_path, filename):
    
    # 2a. IMAGE PROCESSING
    try:
        img = Image.open(file_path).convert('RGB')
    except Exception as e:
        print(f"ERROR: Could not open image {filename}: {e}")
        return

    img = img.resize((IMG_SIZE, IMG_SIZE))
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    # 2b. MAKE PREDICTION
    predictions = model.predict(img_array, verbose=0)[0]
    predicted_index = np.argmax(predictions)
    predicted_category = CLASS_LABELS[predicted_index]
    confidence_score = predictions[predicted_index]

    # 2c. LOGGING AND MOVING
    target_folder = os.path.join(OUTPUT_ROOT, predicted_category)
    os.makedirs(target_folder, exist_ok=True)
    
    # Use try-except for robust file moving
    try:
        shutil.move(file_path, os.path.join(target_folder, filename))
    except Exception as e:
        print(f"FATAL ERROR: Could not move file {filename}. Check permissions. Error: {e}")
        return

    # 2d. DATABASE LOG
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        sql = "INSERT INTO SORTING_LOGS (file_name, ai_prediction, prediction_score) VALUES (%s, %s, %s)"
        cursor.execute(sql, (filename, predicted_category, float(confidence_score)))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"DATABASE ERROR: Failed to log {filename}. Check MySQL status/credentials. Error: {e}")
        return

    # 2e. CSV LOG
    csv_path = os.path.join(LOG_CSV_FOLDER, f'{predicted_category}.csv')
    os.makedirs(LOG_CSV_FOLDER, exist_ok=True)
    with open(csv_path, 'a', newline='') as f:
        writer = csv.writer(f)
        if os.path.getsize(csv_path) == 0:
            writer.writerow(['File Name', 'Category', 'Confidence Score', 'Timestamp'])
        # NOTE: Fixed CSV writing to only write one row per call
        writer.writerow([filename, predicted_category, f'{confidence_score:.4f}', datetime.now().strftime("%Y-%m-%d %H:%M:%S")]) 

    print(f"[{datetime.now().strftime('%H:%M:%S')}] {filename} -> {predicted_category} ({confidence_score:.2f})")

# --- 3. MAIN LOOP FUNCTION (Must be defined here) ---
def run_deployment():
    files_to_process = [f for f in os.listdir(INPUT_DIR) if os.path.isfile(os.path.join(INPUT_DIR, f))]
    if not files_to_process:
        print(f"ERROR: {INPUT_DIR} is empty. Place images there to start.")
        return
    
    print(f"--- Starting Classification of {len(files_to_process)} Images ---")
    
    for filename in files_to_process:
        file_path = os.path.join(INPUT_DIR, filename)
        classify_and_process(file_path, filename)

# --- 4. EXECUTION START (Must be at the far left) ---
if __name__ == "__main__":
    run_deployment()
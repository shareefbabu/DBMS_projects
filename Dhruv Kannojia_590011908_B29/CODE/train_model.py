import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.model_selection import train_test_split

# --- Configuration ---
DATA_DIR = '../DATASET'
MODEL_PATH = '../MODEL/waste_sorter_model.h5'
IMG_SIZE = 128
BATCH_SIZE = 32
EPOCHS = 10

# --- 1. Data Preparation and Splitting ---
datagen = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.3
    )
train_generator = datagen.flow_from_directory(
    DATA_DIR, target_size=(IMG_SIZE, IMG_SIZE), batch_size=BATCH_SIZE,
    class_mode='categorical', subset='training'
    )
test_generator = datagen.flow_from_directory(
    DATA_DIR, target_size=(IMG_SIZE, IMG_SIZE), batch_size=BATCH_SIZE,
    class_mode='categorical', subset='validation'
    )
num_classes = train_generator.num_classes

# --- 2. Model Architecture (Simple CNN) ---
model = Sequential([
    Conv2D(32, (3, 3), activation='relu', input_shape=(IMG_SIZE, IMG_SIZE, 3)),
    MaxPooling2D((2, 2)),
    Conv2D(64, (3, 3), activation='relu'),
    MaxPooling2D((2, 2)),
    Flatten(),
    Dense(128, activation='relu'),
    Dense(num_classes, activation='softmax')
    ])

# --- 3. Compile and Train ---
model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
    )
model.summary()
history = model.fit(
    train_generator, epochs=EPOCHS, validation_data=test_generator
    )

# --- 4. Save Model ---
model.save(MODEL_PATH)
print(f"\nModel saved successfully to {MODEL_PATH}")
class_labels = list(train_generator.class_indices.keys())
with open('../MODEL/class_labels.txt', 'w') as f:
    f.write('\n'.join(class_labels))
    print("Class labels saved.")
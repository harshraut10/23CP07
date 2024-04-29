import lcddriver
import numpy as np
import cv2
import os
import json
import random
from datetime import datetime
from tensorflow.keras.models import load_model
import shutil
import time

# Define the classes
binary_classes = ['cataract', 'normal']
ternary_classes = ['cortical', 'MC', 'PSC']

# Initialize LCD display
display = lcddriver.lcd()

# Function to extract features from an image
def extract_features(image_path):
    image = cv2.imread(image_path)
    image = cv2.resize(image, (224, 224))
    image = image / 255.0  # Normalize pixel values
    return np.expand_dims(image, axis=0)  # Add batch dimension

# Function to move images and JSON file to predictions folder
def move_files_to_predictions_folder(img_paths, folder_id, predictions):
    # Create folder for predictions
    predictions_folder = os.path.join(os.path.dirname(__file__), 'predictions', f'{folder_id:04d}')
    os.makedirs(predictions_folder, exist_ok=True)

    # Move images to predictions folder and update data JSON
    data = {
        'pid': folder_id,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'age': "",
        'image_urls': "",
        'name': "",
        'phone_number': "",
        'sex': "",
        'Grade_R': predictions['Grade_R'],
        'Grade_L': predictions['Grade_L']
    }
    json_file_path = os.path.join(predictions_folder, 'data.json')

    for img_path in img_paths:
        image_name = os.path.basename(img_path)
        new_img_path = os.path.join(predictions_folder, image_name)
        shutil.move(img_path, new_img_path)

    # Write data to JSON file
    with open(json_file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)

    print(f'Data saved to JSON file: {json_file_path}')

# Scan directory for images and predict their classes
def predict_and_move_images(directory):
    images = []
    for filename in os.listdir(directory):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            images.append(os.path.join(directory, filename))

    if not images:
        print("No images found in the directory. Exiting...")
        return

    predictions = {'Grade_R': 'Normal', 'Grade_L': 'Normal'}  # Initialize predictions

    for img_path in images:
        # Predict binary class and save prediction
        binary_prediction = (binary_model.predict(extract_features(img_path)) > 0.5).astype("int32")
        binary_predicted_class = "normal" if binary_prediction == 1 else "cataract"

        if binary_predicted_class == 'cataract':
            ternary_prediction = ternary_model.predict(extract_features(img_path))
            ternary_predicted_class = ternary_classes[np.argmax(ternary_prediction)]
            print(f"Binary Prediction: {binary_predicted_class}, Ternary Prediction: {ternary_predicted_class}")
            if img_path.lower().endswith('_r.jpg') or img_path.lower().endswith('_r.png'):
                predictions['Grade_R'] = ternary_predicted_class
            elif img_path.lower().endswith('_l.jpg') or img_path.lower().endswith('_l.png'):
                predictions['Grade_L'] = ternary_predicted_class
        else:
            print(f"Binary Prediction: {binary_predicted_class}")

        # Save binary predicted class
        if img_path.lower().endswith('_r.jpg') or img_path.lower().endswith('_r.png'):
            predictions['Grade_R'] = binary_predicted_class
        elif img_path.lower().endswith('_l.jpg') or img_path.lower().endswith('_l.png'):
            predictions['Grade_L'] = binary_predicted_class

    # Move images and create predictions folder
    folder_id = random.randint(0, 9999)
    move_files_to_predictions_folder(images, folder_id, predictions)
    print(f'Images and JSON moved to predictions folder with ID: {folder_id}')

    # Display results on LCD screen for 20 seconds
    start_time = time.time()
    while time.time() - start_time < 20:
        display.lcd_clear()
        display.lcd_display_string(f"Folder ID: {folder_id}", 1)
        display.lcd_display_string(f"Grade_R: {predictions['Grade_R']}", 2)
        time.sleep(3)
        display.lcd_display_string(f"Grade_L: {predictions['Grade_L']}", 2)
        time.sleep(3)

# Path to the directory containing images
# Get the current directory
image_directory  = os.path.dirname(os.path.abspath(__file__))

# Load the binary model
current_dir = os.path.dirname(os.path.abspath(__file__))
models_dir = os.path.join(current_dir, '..', 'binary')
binary_model_path = os.path.join(models_dir, 'cnn_model_binary.h5')
binary_model = load_model(binary_model_path)

# Load the ternary model
ternary_model_path = os.path.join(models_dir, 'ternary.h5')
ternary_model = load_model(ternary_model_path)

# Perform predictions and move images to predictions folder
predict_and_move_images(image_directory)

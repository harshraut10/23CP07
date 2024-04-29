import os
import json
import cloudinary.uploader
import firebase_admin
from firebase_admin import credentials, db
import lcddriver
import shutil

# Initialize Firebase Admin SDK with service account credentials
cred = credentials.Certificate("cataract-a5e99-firebase-adminsdk-ar8g9-a54d96e265.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://cataract-a5e99-default-rtdb.firebaseio.com/'
})

# Initialize Cloudinary
cloudinary.config(
    cloud_name="dn38byosw",
    api_key="891473364547868",
    api_secret="kTjKYCynZk-zd-FISGD76OXvjIY"
)

# Initialize LCD display
display = lcddriver.lcd()

# Function to upload images to Cloudinary
def upload_images(image_paths, folder_name):
    image_urls = []
    for image_path in image_paths:
        # Check if the file is an image (jpg, jpeg, png)
        if image_path.lower().endswith(('.jpg', '.jpeg', '.png')):
            # Extract the file name without extension
            file_name = os.path.splitext(os.path.basename(image_path))[0]
            # Upload the image with the original file name
            upload_result = cloudinary.uploader.upload(image_path, folder=folder_name, public_id=file_name)
            image_urls.append(upload_result["secure_url"])
        else:
            print(f"Ignoring non-image file: {image_path}")
    return image_urls

# Function to update Firebase with image URLs and JSON data
def update_firebase(image_urls, json_data, folder_id):
    ref = firebase_admin.db.reference('/')
    try:
        # Add the folder ID as the key for Firebase entry
        ref.child(folder_id).set({**json_data, "image_urls": image_urls})
        print("Data inserted into Firebase Realtime Database.")
        display.lcd_display_string("Data Uploaded", 2)
    except Exception as e:
        print("Error:", e)
        display.lcd_display_string("Error: Firebase", 2)

# Function to move folders to the "uploaded" folder
def move_folders_to_uploaded(predictions_folder):
    uploaded_folder = os.path.join(os.path.dirname(predictions_folder), 'uploaded')
    os.makedirs(uploaded_folder, exist_ok=True)
    for root, dirs, files in os.walk(predictions_folder):
        for folder in dirs:
            src = os.path.join(root, folder)
            dst = os.path.join(uploaded_folder, folder)
            shutil.move(src, dst)

# Path to the Predictions folder
predictions_folder = "predictions"

# Iterate through subfolders in Predictions folder
for subdir, dirs, files in os.walk(predictions_folder):
    for folder in dirs:
        folder_path = os.path.join(predictions_folder, folder)
        json_file = os.path.join(folder_path, "data.json")
        image_paths = [
            os.path.join(folder_path, file)
            for file in os.listdir(folder_path)
            if file.lower().endswith(('.jpg', '.jpeg', '.png'))
        ]

        # Check if JSON file exists
        if os.path.exists(json_file):
            # Load JSON data
            with open(json_file, 'r') as f:
                json_data = json.load(f)

            # Get the folder ID (name of the subfolder)
            folder_id = folder

            # Upload images to Cloudinary in the "cataract" folder
            image_urls = upload_images(image_paths, f"cataract/{folder_id}")

            # Update Firebase with image URLs and JSON data, using folder ID as key
            update_firebase(image_urls, json_data, folder_id)

# Move folders to the "uploaded" folder
move_folders_to_uploaded(predictions_folder)

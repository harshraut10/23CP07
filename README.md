#button.py
used to capture the image when the button is clicked

#prediction.py
does predictions on the captured images and moves them to the predictions folder with respective id inorder to upload it to the database

#upload.py
uploads the folders that contains images and fetches info from the json file and builds form data which contains prediction details

#lcddriver
used to drive the lcd display and is used to print messages in the above codes

#i2c_lib.py
used to find the lcd screen

#cataract-a5e99-firebase-adminsdk-ar8g9-a54d96e265.json
Authentication details of firebase used in upload.py

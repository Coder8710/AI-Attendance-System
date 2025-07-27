Face Recognition Attendance System using ArcFace & Firebase
This project is a real-time face recognition-based attendance system. It includes two main functionalities:

User Registration: Register users by capturing multiple facial expressions.

Attendance Detection: Recognize users in real-time using webcam and mark attendance with a click.

It uses InsightFace's ArcFace model for highly accurate facial recognition and Firebase Realtime Database for storing user data and attendance history.

💡 Features
Real-time face detection and recognition using webcam

Robust registration process with multiple facial angles

Clean GUI using Tkinter

Attendance marking with timestamp

Firebase integration for cloud-based storage

🛠️ Requirements
Install the following packages using pip:

bash
Copy
Edit
pip install opencv-python pillow numpy firebase-admin insightface
⚠️ You also need:

A working webcam

A Firebase Realtime Database setup with service account credentials (JSON file)

🏗️ Project Structure
bash
Copy
Edit
├── arcface_register.py     # GUI for new user registration
├── arcface_detect.py       # GUI for real-time attendance detection
├── YOUR_SERVICE_ACCOUNT_KEY.json  # Firebase service account key (not provided)
├── YOUR_COLLEGE_LOGO.jpg   # Optional: Logo image to display in UI
🔧 Firebase Setup
Create a Firebase project at console.firebase.google.com

Add a Realtime Database and set read/write rules appropriately

Generate a service account key (.json) and download it

Place it in your project folder and replace this line in both Python files:

python
Copy
Edit
cred = credentials.Certificate("YOUR_SERVICE_ACCOUNT_KEY.json")
Replace the database URL:

python
Copy
Edit
"databaseURL": "https://YOUR-PROJECT-ID-default-rtdb.firebaseio.com/"
🚀 How to Use
1. Register New User
Run:

bash
Copy
Edit
python arcface_register.py
Enter Full Name, Roll Number, and Year

Follow guided steps like looking in different directions and smiling

Click "Capture Face" at each step

After all steps, the user is saved to Firebase

2. Mark Attendance
Run:

bash
Copy
Edit
python arcface_detect.py
The webcam opens

If a face matches a registered user, their details will appear

Click "Mark Attendance" to log the time and date

📦 Future Improvements
Admin login dashboard for viewing attendance logs

Email/SMS alerts

Mobile version using Flutter/Kivy
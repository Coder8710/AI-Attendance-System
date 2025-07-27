
# 📸 Face Recognition Attendance System using ArcFace & Firebase

A **real-time face recognition-based attendance system** using [InsightFace](https://github.com/deepinsight/insightface)'s ArcFace model and Firebase Realtime Database.

---

## 🚀 Features

✅ Real-time face detection and recognition using webcam  
✅ Multi-angle user registration with 6 facial expressions  
✅ Tkinter-based interactive GUI  
✅ Attendance marking with live timestamp  
✅ Firebase Realtime Database integration for cloud storage

---

## 🧰 Requirements

Install Python libraries:

```bash
pip install opencv-python pillow numpy firebase-admin insightface
```

Additional:
- A working webcam
- Firebase project & service account JSON

---

## 📂 Project Structure

```
├── arcface_register.py         # GUI to register new users
├── arcface_detect.py           # GUI to detect and mark attendance
├── YOUR_SERVICE_ACCOUNT_KEY.json  # Firebase credentials (add your file)
├── YOUR_COLLEGE_LOGO.jpg       # Optional: GUI branding image
```

---

## 🔧 Firebase Setup

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project
3. Add **Realtime Database** and click **Start in test mode**
4. Go to **Project Settings > Service Accounts > Generate new private key** → download JSON
5. Place the JSON file in your project directory and replace this line in both `.py` files:

```python
cred = credentials.Certificate("YOUR_SERVICE_ACCOUNT_KEY.json")
```

Also replace the database URL:
```python
"databaseURL": "https://YOUR-PROJECT-ID-default-rtdb.firebaseio.com/"
```

---

## 📝 How to Use

### 👤 1. Register a New User

Run:

```bash
python arcface_register.py
```

Steps:
- Fill in **Name**, **Roll Number**, and **Year**
- Follow instructions: Look straight, left, right, up, down, smile
- Each pose captures 3 images for better accuracy
- Registration is saved to Firebase

---

### 🧑‍💻 2. Detect & Mark Attendance

Run:

```bash
python arcface_detect.py
```

Steps:
- The webcam opens automatically
- If a face is recognized, user details appear
- Click “**Mark Attendance**” to save the timestamp

---

## 📌 Notes

- Make sure Firebase credentials and database URL are correctly set
- You can add a custom college logo (`YOUR_COLLEGE_LOGO.jpg`) for better branding
- To handle multiple users, register each one individually

---

## 🌱 Future Enhancements

- Web-based dashboard to view attendance logs  
- Export to Excel/CSV  
- OTP/email verification  
- Mobile app using Flutter/Kivy

---

## 📜 License

This project is open-source and free for educational or personal use.

---

import cv2
import numpy as np
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import firebase_admin
from firebase_admin import credentials, db
from insightface.app import FaceAnalysis

# Initialize InsightFace
face_analyzer = FaceAnalysis(name="buffalo_l",
                             providers=['CUDAExecutionProvider','CPUExecutionProvider'])
face_analyzer.prepare(ctx_id=0, det_size=(640,640))

# Firebase setup - Replace with your own credentials
cred = credentials.Certificate("YOUR_SERVICE_ACCOUNT_KEY.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://YOUR-PROJECT-ID-default-rtdb.firebaseio.com/"
})

instructions = [
    "Look straight", "Turn slightly left", "Turn slightly right",
    "Look slightly up", "Look slightly down", "Smile"
]
IMGS_PER_ANGLE = 3

class RegistrationApp:
    def __init__(self):
        self.reset_state()
        
        # Camera setup
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Camera Error", "Cannot access camera")
            exit()
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        # GUI setup
        self.window = tk.Tk()
        self.window.title("Face Registration")
        self.window.geometry("1000x600")
        
        # Left frame - Camera
        left_frame = tk.Frame(self.window, bg="black")
        left_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Camera title
        tk.Label(left_frame, text="Camera View", 
                font=("Helvetica", 14, "bold"), bg="black", fg="white").pack(pady=5)
        
        # Video label
        self.video_label = tk.Label(left_frame, bg="gray")
        self.video_label.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        # Status label
        self.status_var = tk.StringVar(value="Fill details to enable Capture")
        status_label = tk.Label(left_frame, textvariable=self.status_var, 
                               font=("Helvetica", 12, "bold"), bg="black", fg="yellow")
        status_label.pack(pady=5)
        
        # Right frame - Form and logo
        right_frame = tk.Frame(self.window, width=300)
        right_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.Y)
        right_frame.pack_propagate(False)
        
        # College logo - Replace with your college logo
        try:
            logo = Image.open("YOUR_COLLEGE_LOGO.jpg").resize((180, 180))
            self.logo_tk = ImageTk.PhotoImage(logo)
            tk.Label(right_frame, image=self.logo_tk).pack(pady=5)
        except:
            tk.Label(right_frame, text="College Logo\n(File not found)", bg="lightgray", 
                    width=20, height=8).pack(pady=5)

        tk.Label(right_frame, text="Register New User", 
                font=("Helvetica", 16, "bold")).pack(pady=5)
        
        # Form frame
        form_frame = tk.Frame(right_frame, bd=2, relief=tk.GROOVE, bg="#f0f8ff")
        form_frame.pack(pady=5, fill=tk.X)
        
        # Name field
        tk.Label(form_frame, text="Full Name:", bg="#f0f8ff", 
                font=("Arial", 11, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.name_var = tk.StringVar()
        self.name_entry = tk.Entry(form_frame, textvariable=self.name_var, 
                                  font=("Arial", 11), width=18)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Roll field
        tk.Label(form_frame, text="Roll No:", bg="#f0f8ff", 
                font=("Arial", 11, "bold")).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.roll_var = tk.StringVar()
        self.roll_entry = tk.Entry(form_frame, textvariable=self.roll_var, 
                                  font=("Arial", 11), width=18)
        self.roll_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Year field
        tk.Label(form_frame, text="Year:", bg="#f0f8ff", 
                font=("Arial", 11, "bold")).grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.year_var = tk.StringVar()
        self.year_entry = tk.Entry(form_frame, textvariable=self.year_var, 
                                  font=("Arial", 11), width=18)
        self.year_entry.grid(row=2, column=1, padx=5, pady=5)

        # Buttons
        btn_frame = tk.Frame(right_frame)
        btn_frame.pack(pady=15)
        
        self.reg_btn = tk.Button(btn_frame, text="Start Registration", 
                                font=("Helvetica", 11, "bold"),
                                bg="#4CAF50", fg="white", padx=8, pady=4,
                                command=self.start_registration)
        self.reg_btn.pack(pady=3, fill=tk.X)
        
        self.capture_btn = tk.Button(btn_frame, text="Capture Face", 
                                    font=("Helvetica", 11, "bold"),
                                    bg="#FF9800", fg="white", padx=8, pady=4,
                                    state="disabled", command=self.capture_face)
        self.capture_btn.pack(pady=3, fill=tk.X)
        
        self.next_btn = tk.Button(btn_frame, text="Next/Exit", 
                                 font=("Helvetica", 11, "bold"),
                                 bg="#2196F3", fg="white", padx=8, pady=4,
                                 state="disabled", command=self.finish_user)
        self.next_btn.pack(pady=3, fill=tk.X)

        # Simplified instructions
        instructions_text = """📷 Instructions:
• Your full face should be visible
• Sit at proper distance from camera
• Ensure good lighting"""
        
        tk.Label(right_frame, text=instructions_text, font=("Arial", 10), 
                justify=tk.LEFT, bg="#e8f5e8", relief=tk.RIDGE, 
                padx=8, pady=6).pack(pady=8, fill=tk.X)
        
        # Trace entries to enable capture button
        for var in (self.name_var, self.roll_var, self.year_var):
            var.trace_add("write", self.update_capture_state)
        
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        self.update_frame()
        self.window.mainloop()

    def reset_state(self):
        self.registering = False
        self.step = 0
        self.count = 0
        self.embs = []

    def update_capture_state(self, *_):
        """Enable capture button only when all details are filled"""
        if (self.name_var.get().strip() and 
            self.roll_var.get().strip() and 
            self.year_var.get().strip()):
            if not self.registering:
                self.capture_btn.config(state="normal")
                self.status_var.set("Ready to capture - Full face should be visible")
        else:
            self.capture_btn.config(state="disabled")
            self.status_var.set("Fill all details to enable Capture")

    def update_frame(self):
        """Update camera frame with proper bounds checking"""
        ret, frame = self.cap.read()
        if ret:
            original_height, original_width = frame.shape[:2]
            
            # Add bounds checking for self.step
            if self.registering and self.step < len(instructions):
                cv2.putText(frame, f"Step: {instructions[self.step]} ({self.count}/{IMGS_PER_ANGLE})", 
                           (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                
                faces = face_analyzer.get(frame)
                if faces:
                    for face in faces:
                        bbox = face.bbox.astype(int)
                        cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2)
                    cv2.putText(frame, "Face Detected", (20, 70), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                else:
                    cv2.putText(frame, "No face detected", (20, 70), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            elif self.registering and self.step >= len(instructions):
                # Registration completed, show completion message
                cv2.putText(frame, "Registration Complete!", (20, 40), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            
            # Scale to fit label
            self.window.update_idletasks()
            label_width = self.video_label.winfo_width()
            label_height = self.video_label.winfo_height()
            
            if label_width > 1 and label_height > 1:
                scale_w = label_width / original_width
                scale_h = label_height / original_height
                scale = min(scale_w, scale_h)
                
                new_width = int(original_width * scale)
                new_height = int(original_height * scale)
                
                display_frame = cv2.resize(frame, (new_width, new_height))
            else:
                display_frame = cv2.resize(frame, (640, 480))
            
            rgb = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
            imgtk = ImageTk.PhotoImage(Image.fromarray(rgb))
            self.video_label.imgtk = imgtk
            self.video_label.config(image=imgtk)
        
        self.window.after(30, self.update_frame)

    def start_registration(self):
        """Validate inputs and start registration process"""
        name = self.name_var.get().strip()
        roll = self.roll_var.get().strip()
        year = self.year_var.get().strip()
        
        if not (name and roll and year):
            messagebox.showwarning("Missing Data", "Please fill all fields")
            return
        if not roll.isdigit():
            messagebox.showwarning("Invalid", "Roll must be numeric")
            return
            
        try:
            if db.reference(f'users/{roll}').get():
                messagebox.showerror("Exists", "Roll already registered")
                return
        except Exception as e:
            print(f"Firebase error: {e}")
        
        self.registering = True
        self.status_var.set("Registration started - Click Capture when ready")
        self.reg_btn.config(state="disabled")
        self.capture_btn.config(state="normal")
        self.next_btn.config(state="disabled")
        
        self.name_entry.config(state="disabled")
        self.roll_entry.config(state="disabled")
        self.year_entry.config(state="disabled")

    def capture_face(self):
        """Capture face for current step with proper bounds checking"""
        if not self.registering:
            messagebox.showinfo("Info", "Click Start Registration first")
            return
            
        # Add bounds checking before accessing instructions
        if self.step >= len(instructions):
            messagebox.showinfo("Complete", "All steps completed!")
            return
            
        ret, frame = self.cap.read()
        if not ret:
            self.status_var.set("Camera error")
            return
            
        faces = face_analyzer.get(frame)
        if not faces:
            self.status_var.set("No face detected - adjust position")
            return
        
        self.embs.append(faces[0].embedding)
        self.count += 1
        self.status_var.set(f"Captured {self.count}/{IMGS_PER_ANGLE} for: {instructions[self.step]}")
        
        if self.count >= IMGS_PER_ANGLE:
            self.step += 1
            self.count = 0
            
            if self.step >= len(instructions):
                # All steps completed
                self.save_registration()
            else:
                self.status_var.set(f"Next step: {instructions[self.step]}")

    def save_registration(self):
        """Save registration data to Firebase"""
        try:
            emb_mean = np.mean(np.array(self.embs), axis=0).tolist()
            data = {
                "name": self.name_var.get().strip(),
                "roll": self.roll_var.get().strip(),
                "year": self.year_var.get().strip(),
                "embedding": emb_mean,
                "total_attendance": 0,
                "attendance_history": []
            }
            db.reference(f'users/{data["roll"]}').set(data)
            self.status_var.set("Registration completed successfully!")
            self.capture_btn.config(state="disabled")
            self.next_btn.config(state="normal")
        except Exception as e:
            messagebox.showerror("Error", f"Registration failed: {str(e)}")
            self.status_var.set("Registration failed")

    def finish_user(self):
        """Handle completion of user registration"""
        if messagebox.askyesno("Continue", "Register another user?"):
            self.name_var.set("")
            self.roll_var.set("")
            self.year_var.set("")
            self.reset_state()
            
            self.name_entry.config(state="normal")
            self.roll_entry.config(state="normal")
            self.year_entry.config(state="normal")
            self.reg_btn.config(state="normal")
            self.next_btn.config(state="disabled")
            self.status_var.set("Fill all details to enable Capture")
        else:
            self.on_close()

    def on_close(self):
        """Clean up and close"""
        if self.cap.isOpened():
            self.cap.release()
        self.window.destroy()

if __name__ == "__main__":
    RegistrationApp()

import cv2
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, db
from insightface.app import FaceAnalysis

# Initialize InsightFace with GPU preference (falls back to CPU automatically)
face_analyser = FaceAnalysis(
    name="buffalo_l",
    providers=['CUDAExecutionProvider', 'CPUExecutionProvider']
)
face_analyser.prepare(ctx_id=0, det_size=(640, 640))

# Firebase setup - Replace with your own credentials
cred = credentials.Certificate("YOUR_SERVICE_ACCOUNT_KEY.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://YOUR-PROJECT-ID-default-rtdb.firebaseio.com/"
})

def load_users():
    raw = db.reference("users").get() or {}
    users = {}
    # Robustly parse both dict and list outputs
    if isinstance(raw, dict):
        iterable = raw.items()
    elif isinstance(raw, list):
        # list may contain None if there are firebase "gaps"
        iterable = ((str(u.get('roll')) if u else '', u) for u in raw if isinstance(u, dict))
    else:
        iterable = []
    for roll, data in iterable:
        if not isinstance(data, dict): continue
        emb = np.asarray(data.get("embedding", []), dtype=np.float32)
        emb_norm = emb / np.linalg.norm(emb) if np.linalg.norm(emb) > 0 else emb
        users[str(roll)] = {
            "name": data.get("name", ""),
            "roll": str(data.get("roll", roll)),
            "year": data.get("year", ""),
            "emb_norm": emb_norm,
            "hist": data.get("attendance_history", [])
        }
    return users

def write_attendance(roll):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ref = db.reference(f"users/{roll}/attendance_history")
    hist = ref.get() or []
    hist.append(ts)
    ref.set(hist)
    return ts

class App:
    def __init__(self):
        self.users = load_users()
        self.current_roll = None  # Currently recognized user's roll

        # ---- GUI ----
        self.root = tk.Tk()
        self.root.title("Face-Recognition Attendance")
        self.root.geometry("950x540")

        lf = tk.Frame(self.root, bg="black")
        lf.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8, pady=8)
        tk.Label(lf, text="Camera", bg="black", fg="white", font=("Helvetica", 14, "bold")).pack()
        self.video_lbl = tk.Label(lf, bg="gray")
        self.video_lbl.pack(fill=tk.BOTH, expand=True)

        rf = tk.Frame(self.root, width=280, bg="#F5F5F5")
        rf.pack(side=tk.RIGHT, fill=tk.Y, padx=8, pady=8)
        rf.pack_propagate(False)

        # logo - Replace with your college logo
        try:
            logo = Image.open("YOUR_COLLEGE_LOGO.jpg").resize((180, 180))
            self.logo_img = ImageTk.PhotoImage(logo)
            tk.Label(rf, image=self.logo_img, bg="#F5F5F5").pack(pady=5)
        except:
            tk.Label(rf, text="College Logo\n(File not found)", bg="#ccc", width=20, height=8).pack(pady=5)

        # details
        tk.Label(rf, text="Student Details", bg="#F5F5F5",
                 font=("Helvetica", 14, "bold")).pack(pady=4)

        self.nameVar = tk.StringVar(value="—")
        self.rollVar = tk.StringVar(value="—")
        self.yearVar = tk.StringVar(value="—")
        self.lastVar = tk.StringVar(value="—")
        
        for lbl, var in (("Name:", self.nameVar), ("Roll:", self.rollVar),
                         ("Year:", self.yearVar), ("Last:", self.lastVar)):
            fr = tk.Frame(rf, bg="#F5F5F5")
            fr.pack(fill=tk.X, padx=8)
            tk.Label(fr, text=lbl, width=7, anchor="w", bg="#F5F5F5",
                     font=("Arial", 11, "bold")).pack(side=tk.LEFT)
            tk.Label(fr, textvariable=var, anchor="w", bg="#F5F5F5",
                     font=("Arial", 11)).pack(side=tk.LEFT, fill=tk.X)

        self.mark_btn = tk.Button(rf, text="Mark Attendance", bg="#4CAF50",
                                  fg="white", font=("Helvetica", 12, "bold"),
                                  state="disabled", command=self.do_mark)
        self.mark_btn.pack(pady=12, fill=tk.X, padx=25)

        self.statusVar = tk.StringVar(value="Waiting for face…")
        tk.Label(rf, textvariable=self.statusVar, bg="#F5F5F5",
                 fg="red", font=("Arial", 11, "bold")).pack(pady=4)

        self.cam = cv2.VideoCapture(0)
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.update()
        self.root.mainloop()

    def update(self):
        ok, frame = self.cam.read()
        if ok:
            self.recognize(frame.copy())
            self.show(frame)
        self.root.after(30, self.update)

    def recognize(self, frame):
        faces = face_analyser.get(frame)
        best_roll, best_sim = None, 0.45

        for f in faces:
            emb = f.embedding.astype(np.float32)
            nrm = np.linalg.norm(emb)
            if nrm == 0: continue
            emb /= nrm
            for roll, data in self.users.items():
                sim = np.dot(emb, data["emb_norm"]) if len(emb) == len(data["emb_norm"]) else 0
                if sim > best_sim:
                    best_sim, best_roll = sim, roll
            x1, y1, x2, y2 = f.bbox.astype(int)
            clr = (0, 255, 0) if best_roll else (0, 0, 255)
            # Only show name, not confidence
            cv2.rectangle(frame, (x1, y1), (x2, y2), clr, 2)
            cv2.putText(frame, f"{self.users[best_roll]['name']}" if best_roll else "Unknown",
                        (x1, y1 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, clr, 2)

        if best_roll:
            usr = self.users[best_roll]
            self.nameVar.set(usr["name"])
            self.rollVar.set(usr["roll"])
            self.yearVar.set(usr["year"])
            last = usr["hist"][-1] if usr["hist"] else "—"
            self.lastVar.set(last)
            self.current_roll = best_roll
            self.mark_btn.config(state="normal")
            self.statusVar.set("Recognized • click button to mark")
        else:
            self.clear_details()

    def clear_details(self):
        self.current_roll = None
        self.mark_btn.config(state="disabled")
        for var in (self.nameVar, self.rollVar, self.yearVar):
            var.set("—")
        self.lastVar.set("—")
        self.statusVar.set("Waiting for face…")

    def do_mark(self):
        if self.current_roll:
            ts = write_attendance(self.current_roll)
            self.users[self.current_roll]["hist"].append(ts)
            self.lastVar.set(ts)
            self.statusVar.set("Attendance recorded ✔")
            self.mark_btn.config(state="disabled")

    def show(self, frame):
        h, w = frame.shape[:2]
        self.root.update_idletasks()
        label_w, label_h = self.video_lbl.winfo_width(), self.video_lbl.winfo_height()
        if label_w > 1 and label_h > 1:
            scale = min(label_w / w, label_h / h)
            new_w, new_h = max(1, int(w * scale)), max(1, int(h * scale))
            frame = cv2.resize(frame, (new_w, new_h))
        else:
            frame = cv2.resize(frame, (640, 480))
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        imgtk = ImageTk.PhotoImage(Image.fromarray(rgb))
        self.video_lbl.imgtk = imgtk
        self.video_lbl.configure(image=imgtk)

    def close(self):
        if self.cam.isOpened():
            self.cam.release()
        self.root.destroy()

if __name__ == "__main__":
    App()

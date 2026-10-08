import cv2
import mediapipe as mp
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from datetime import datetime
import threading
import time
import math
from PIL import Image, ImageTk

class ExerciseCounter:
    def __init__(self):
        # MediaPipe setup
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Exercise state variables
        self.exercise_type = "Push-Up"
        self.counter = 0
        self.stage = "UP"  # UP, DOWN, COUNTED
        self.is_running = False
        self.start_time = None
        self.session_data = []
        
        # Camera setup
        self.cap = None
        self.current_frame = None
        
        # GUI setup
        self.setup_gui()
        
    def setup_gui(self):
        """Setup the main GUI interface"""
        self.root = tk.Tk()
        self.root.title("Exercise Repetition Counter")
        self.root.geometry("1000x700")
        self.root.configure(bg='#2c3e50')
        
        # Main frame
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel for camera feed
        left_panel = tk.Frame(main_frame, bg='#34495e', relief=tk.RAISED, bd=2)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Camera label
        self.camera_label = tk.Label(left_panel, bg='#34495e', text="Camera Feed")
        self.camera_label.pack(pady=10)
        
        # Right panel for controls and stats
        right_panel = tk.Frame(main_frame, bg='#34495e', relief=tk.RAISED, bd=2, width=300)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        right_panel.pack_propagate(False)
        
        # Title
        title_label = tk.Label(right_panel, text="Exercise Counter", 
                              font=('Arial', 16, 'bold'), fg='white', bg='#34495e')
        title_label.pack(pady=10)
        
        # Exercise selection
        exercise_frame = tk.Frame(right_panel, bg='#34495e')
        exercise_frame.pack(pady=10, padx=20, fill=tk.X)
        
        tk.Label(exercise_frame, text="Exercise Type:", 
                font=('Arial', 10), fg='white', bg='#34495e').pack(anchor=tk.W)
        
        self.exercise_var = tk.StringVar(value="Push-Up")
        exercise_combo = ttk.Combobox(exercise_frame, textvariable=self.exercise_var,
                                     values=["Push-Up", "Squat"], state="readonly")
        exercise_combo.pack(fill=tk.X, pady=5)
        exercise_combo.bind('<<ComboboxSelected>>', self.on_exercise_change)
        
        # Counter display
        counter_frame = tk.Frame(right_panel, bg='#2c3e50', relief=tk.RAISED, bd=2)
        counter_frame.pack(pady=20, padx=20, fill=tk.X)
        
        tk.Label(counter_frame, text="Repetitions", 
                font=('Arial', 12), fg='white', bg='#2c3e50').pack(pady=5)
        
        self.counter_label = tk.Label(counter_frame, text="0", 
                                     font=('Arial', 36, 'bold'), fg='#e74c3c', bg='#2c3e50')
        self.counter_label.pack(pady=10)
        
        # Status indicator
        self.status_label = tk.Label(counter_frame, text="READY", 
                                    font=('Arial', 14, 'bold'), fg='#f39c12', bg='#2c3e50')
        self.status_label.pack(pady=5)
        
        # Control buttons
        button_frame = tk.Frame(right_panel, bg='#34495e')
        button_frame.pack(pady=20, padx=20, fill=tk.X)
        
        self.start_button = tk.Button(button_frame, text="Start", 
                                     font=('Arial', 12, 'bold'), bg='#27ae60', fg='white',
                                     command=self.start_exercise, relief=tk.FLAT, pady=10)
        self.start_button.pack(fill=tk.X, pady=5)
        
        self.stop_button = tk.Button(button_frame, text="Stop", 
                                    font=('Arial', 12, 'bold'), bg='#e74c3c', fg='white',
                                    command=self.stop_exercise, relief=tk.FLAT, pady=10)
        self.stop_button.pack(fill=tk.X, pady=5)
        
        self.reset_button = tk.Button(button_frame, text="Reset", 
                                     font=('Arial', 12, 'bold'), bg='#f39c12', fg='white',
                                     command=self.reset_counter, relief=tk.FLAT, pady=10)
        self.reset_button.pack(fill=tk.X, pady=5)
        
        # Statistics panel
        stats_frame = tk.LabelFrame(right_panel, text="Session Statistics", 
                                   font=('Arial', 10, 'bold'), fg='white', bg='#34495e')
        stats_frame.pack(pady=20, padx=20, fill=tk.X)
        
        self.duration_label = tk.Label(stats_frame, text="Duration: 00:00", 
                                      font=('Arial', 10), fg='white', bg='#34495e')
        self.duration_label.pack(anchor=tk.W, pady=2)
        
        self.start_time_label = tk.Label(stats_frame, text="Start Time: --", 
                                        font=('Arial', 10), fg='white', bg='#34495e')
        self.start_time_label.pack(anchor=tk.W, pady=2)
        
        # Export button
        export_button = tk.Button(right_panel, text="Export Data", 
                                 font=('Arial', 10), bg='#3498db', fg='white',
                                 command=self.export_data, relief=tk.FLAT, pady=5)
        export_button.pack(pady=10, padx=20, fill=tk.X)
        
    def calculate_angle(self, a, b, c):
        """Calculate angle between three points"""
        a = np.array(a)  # First point
        b = np.array(b)  # Mid point
        c = np.array(c)  # End point
        
        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        
        if angle > 180.0:
            angle = 360 - angle
            
        return angle
    
    def detect_push_up(self, landmarks):
        """Detect push-up movement based on elbow angle"""
        try:
            # Get coordinates
            shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                       landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            elbow = [landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                    landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
            wrist = [landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                    landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].y]
            
            # Calculate angle
            angle = self.calculate_angle(shoulder, elbow, wrist)
            
            # State machine logic
            if angle > 160 and self.stage == "DOWN":
                self.stage = "UP"
                self.counter += 1
                self.update_counter_display()
            elif angle < 90 and self.stage == "UP":
                self.stage = "DOWN"
                
            return angle
            
        except Exception as e:
            return None
    
    def detect_squat(self, landmarks):
        """Detect squat movement based on knee angle"""
        try:
            # Get coordinates
            hip = [landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x,
                  landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y]
            knee = [landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                   landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].y]
            ankle = [landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                    landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
            
            # Calculate angle
            angle = self.calculate_angle(hip, knee, ankle)
            
            # State machine logic
            if angle > 170 and self.stage == "DOWN":
                self.stage = "UP"
                self.counter += 1
                self.update_counter_display()
            elif angle < 100 and self.stage == "UP":
                self.stage = "DOWN"
                
            return angle
            
        except Exception as e:
            return None
    
    def update_counter_display(self):
        """Update the counter display in GUI"""
        self.counter_label.config(text=str(self.counter))
        
        # Update status color
        if self.stage == "UP":
            self.status_label.config(text="UP", fg='#27ae60')
        elif self.stage == "DOWN":
            self.status_label.config(text="DOWN", fg='#e74c3c')
        else:
            self.status_label.config(text="READY", fg='#f39c12')
    
    def update_duration(self):
        """Update session duration display"""
        if self.start_time and self.is_running:
            duration = time.time() - self.start_time
            minutes = int(duration // 60)
            seconds = int(duration % 60)
            self.duration_label.config(text=f"Duration: {minutes:02d}:{seconds:02d}")
            
        if self.is_running:
            self.root.after(1000, self.update_duration)
    
    def process_frame(self):
        """Process camera frame for pose detection"""
        if not self.is_running or self.cap is None:
            return
            
        ret, frame = self.cap.read()
        if not ret:
            return
            
        # Flip frame horizontally for mirror effect
        frame = cv2.flip(frame, 1)
        
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process pose detection
        results = self.pose.process(rgb_frame)
        
        # Draw landmarks
        if results.pose_landmarks:
            self.mp_drawing.draw_landmarks(
                frame, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
            
            # Detect exercise based on type
            angle = None
            if self.exercise_type == "Push-Up":
                angle = self.detect_push_up(results.pose_landmarks.landmark)
            elif self.exercise_type == "Squat":
                angle = self.detect_squat(results.pose_landmarks.landmark)
            
            # Display angle on frame
            if angle is not None:
                cv2.putText(frame, f'Angle: {int(angle)}', 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Display counter and stage on frame
        cv2.putText(frame, f'Reps: {self.counter}', 
                   (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f'Stage: {self.stage}', 
                   (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        cv2.putText(frame, f'Exercise: {self.exercise_type}', 
                   (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
        
        # Convert frame to PhotoImage for Tkinter
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_pil = Image.fromarray(frame_rgb)
        frame_pil = frame_pil.resize((640, 480), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(frame_pil)
        
        # Update camera label
        self.camera_label.config(image=photo)
        self.camera_label.image = photo
        
        # Schedule next frame processing
        if self.is_running:
            self.root.after(10, self.process_frame)
    
    def start_exercise(self):
        """Start exercise session"""
        try:
            if self.cap is None:
                self.cap = cv2.VideoCapture(0)
                
            if not self.cap.isOpened():
                messagebox.showerror("Error", "Cannot access camera!")
                return
                
            self.is_running = True
            self.start_time = time.time()
            self.start_time_label.config(text=f"Start Time: {datetime.now().strftime('%H:%M:%S')}")
            
            # Start frame processing and duration update
            self.process_frame()
            self.update_duration()
            
            # Update button states
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start camera: {str(e)}")
    
    def stop_exercise(self):
        """Stop exercise session"""
        self.is_running = False
        
        # Save session data
        if self.start_time:
            duration = time.time() - self.start_time
            session_record = {
                'date_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'exercise_type': self.exercise_type,
                'repetitions': self.counter,
                'duration_seconds': round(duration, 2),
                'duration_formatted': f"{int(duration//60):02d}:{int(duration%60):02d}"
            }
            self.session_data.append(session_record)
        
        # Update button states
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
        # Release camera
        if self.cap:
            self.cap.release()
            self.cap = None
    
    def reset_counter(self):
        """Reset counter and stage"""
        self.counter = 0
        self.stage = "UP"
        self.update_counter_display()
        self.duration_label.config(text="Duration: 00:00")
        self.start_time_label.config(text="Start Time: --")
        self.start_time = None
    
    def on_exercise_change(self, event):
        """Handle exercise type change"""
        self.exercise_type = self.exercise_var.get()
        self.reset_counter()
    
    def export_data(self):
        """Export session data to CSV"""
        if not self.session_data:
            messagebox.showwarning("Warning", "No session data to export!")
            return
            
        try:
            df = pd.DataFrame(self.session_data)
            filename = f"exercise_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(filename, index=False)
            messagebox.showinfo("Success", f"Data exported to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export data: {str(e)}")
    
    def on_closing(self):
        """Handle window closing"""
        if self.is_running:
            self.stop_exercise()
        if self.cap:
            self.cap.release()
        self.root.destroy()
    
    def run(self):
        """Run the application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

if __name__ == "__main__":
    app = ExerciseCounter()
    app.run()
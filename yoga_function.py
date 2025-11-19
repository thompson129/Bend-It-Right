import cv2
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import tkinter as tk
import time

def upload_video_yoga(self, canvas):
    # Upload a video and display it on the canvas
    video_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.avi *.mov")])
    if video_path:
        messagebox.showinfo("Video Upload", "Video uploaded successfully!")
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            messagebox.showerror("Error", "Could not open video file.")
            return

        self.update_frame_yoga(canvas)  # Start updating frames on the canvas

        
def start_detection_yoga(self, canvas):
    # Open the live camera feed
    self.cap = cv2.VideoCapture(1)  # Open the default camera
    if not self.cap.isOpened():
        messagebox.showerror("Error", "Could not open video device.")
        return

    self.update_frame_yoga(canvas)  # Start updating frames on the canvas

def update_frame_yoga(self, canvas):
    if self.cap is not None:
        ret, frame = self.cap.read()
        if ret:
            

            # Process pose detection
            annotated_frame = self.process_pose_detection(frame, canvas)               

            # Update GUI with processed frame
            img = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)))
            if canvas.winfo_exists():
                canvas.create_image(0, 0, anchor=tk.NW, image=img)
                canvas.image = img  # To prevent garbage collection

            # Schedule next frame update, adjust delay to 33 ms (about 30 FPS)
            self.root.after(33, lambda: self.update_frame_yoga(canvas))
        else:
            # Release the capture if no frame is retrieved
            self.cap.release()

def stop_detection_yoga(self, canvas=None):
        # Stop the frame update thread
        if hasattr(self, 'stop_event'):
            self.stop_event.set()
            self.thread.join()
            
        # Release the video capture if it's opened
        if self.cap and self.cap.isOpened():
            self.cap.release()
            self.cap = None    
            
        # Display the default image on the canvas
        if canvas:
            canvas.create_image(0, 0, anchor=tk.NW, image=self.default_image)
            canvas.image = self.default_image

def process_pose_detection(self, frame, canvas):
    # Resize frame for pose detection
    pose_frame = cv2.resize(frame, (650, 430))  # Adjust the size for the model
    results = self.model(pose_frame)
    detected_poses = []  # List to store actual detected poses

    for result in results:
        # Check if keypoints exist and if boxes contain detected classes
        if result.keypoints is not None and result.boxes is not None and len(result.boxes.cls) > 0:
            for i, keypoints in enumerate(result.keypoints):
                if i < len(result.boxes.cls):  # Check if index is within bounds
                    class_id = int(result.boxes.cls[i])  # Get class ID (integer) for the detected pose
                    if class_id in self.class_labels:  # Check confidence level
                        pose_name = self.class_labels[class_id]  # Map class ID to pose name
                        detected_poses.append(pose_name)  # Store the detected pose
                        
                        confidence = result.boxes.conf[i]
                        if(confidence > 0.8):
                            self.start_pose_timer(pose_name)  # Start the timer for the detected pose

            # **Draw bounding box but no lines**:
            # Get the coordinates for the bounding box
            for box in result.boxes.xyxy:
                x1, y1, x2, y2 = map(int, box)  # Convert to integer coordinates
                # Draw bounding box around the detected pose
                cv2.rectangle(pose_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Green box with thickness 2
                
                # Display confidence score (optional)
                confidence = result.boxes.conf[0]  # Confidence score of the detected pose
                label = f"{self.class_labels[class_id]}: {confidence:.2f}"
                cv2.putText(pose_frame, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    # Stop timers for poses that are no longer detected
    for pose_name in self.pose_durations:
        if pose_name not in detected_poses:
            self.stop_pose_timer(pose_name)

    # **No need to convert to RGB now; we use BGR directly**
    annotated_frame = pose_frame  # No need for color conversion now, keep it in BGR

    # Convert the frame to PIL Image for Tkinter canvas
    annotated_frame_rgb = Image.fromarray(annotated_frame)  # Use BGR directly
    return annotated_frame_rgb

def start_pose_timer(self, pose_name):
    """Start or resume the timer for the detected pose."""
    # If this is the first time the pose is detected, initialize the start time
    if pose_name not in self.pose_start_time:
        self.pose_start_time[pose_name] = time.time()

    # Calculate the elapsed time since the pose was first detected or resumed
    elapsed_time = time.time() - self.pose_start_time[pose_name] + self.pose_durations[pose_name]
    minutes = int(elapsed_time // 60)
    seconds = elapsed_time % 60

    # Update the GUI for this specific pose's timer
    self.update_timer_in_gui(pose_name, f"{minutes:.0f}:{seconds:.2f}")

def stop_pose_timer(self, pose_name):
    """Stop the timer for a pose when it's no longer detected."""
    if pose_name in self.pose_start_time:
        # Calculate the elapsed time and store it
        elapsed_time = time.time() - self.pose_start_time[pose_name]
        self.pose_durations[pose_name] += elapsed_time
        # Remove the start time since the pose is no longer detected
        del self.pose_start_time[pose_name]

def update_timer_in_gui(self, pose_name, time_str):
    """Update the timer label for the detected pose only."""
    if pose_name in self.pose_labels:  # Ensure the detected pose is linked to a label
        label = self.pose_labels[pose_name]  # Get the specific label for the detected pose
        label.config(text=time_str)  # Update only the label for the detected pose

def reset_count_yoga(self):
    """Reset the frame count, pose durations, and timers in the GUI."""
    # Reset the frame count and pose durations
    self.frame_count = 0
    self.pose_durations = {pose: 0 for pose in self.class_labels.values()}  # Reset all durations to 0
    self.pose_start_time = {}  # Clear all start times

    #manually reset the timers in the GUI
    for pose_name in self.pose_labels:
        self.update_timer_in_gui(pose_name, "00:00:00")

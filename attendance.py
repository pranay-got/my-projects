# Attendance_Voice_Only.py
import cv2
from pyzbar import pyzbar
import pandas as pd
from datetime import datetime
import os
from voice_assistant import speak, listen

# --- Files ---
attendance_file = "Attendance.csv"
subject_name = "Database Management System"
columns = ["Subject", "Name", "Student_ID", "Time"]

# Load or create attendance CSV
if os.path.exists(attendance_file):
    attendance = pd.read_csv(attendance_file)
else:
    attendance = pd.DataFrame(columns=columns)
    attendance.to_csv(attendance_file, index=False)

# --- Functions ---
def mark_attendance():
    global attendance
    cap = cv2.VideoCapture(0)
    speak("Camera started. Scanning for QR codes. Press 'q' to quit.")
    print("📷 Scanning for QR Codes... Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.putText(frame, f"Subject: {subject_name}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        decoded_objects = pyzbar.decode(frame)
        for obj in decoded_objects:
            data = obj.data.decode("utf-8")
            if "," in data:
                student_id, name = data.split(",", 1)
                x, y, w, h = obj.rect
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
                cv2.putText(frame, f"{name} ({student_id})", (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

                # Mark attendance if not already present
                if not ((attendance["Student_ID"] == student_id) & (attendance["Name"] == name)).any():
                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    new_row = pd.DataFrame([[subject_name, name, student_id, now]], columns=columns)
                    attendance = pd.concat([attendance, new_row], ignore_index=True)
                    attendance.to_csv(attendance_file, index=False)
                    print(f"✅ Attendance marked for {name} ({student_id}) at {now}")
                    speak(f"Attendance marked for {name}")
            else:
                print(f"⚠️ Ignored invalid QR code: {data}")

        cv2.imshow("QR Attendance System", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    speak("Attendance session ended. Data saved.")

# --- Main Voice-Control Loop ---
speak("Hi Pranay! I am ready. Say 'start camera' or 'exit'.")

while True:
    command = listen()

    if "start camera" in command:
        mark_attendance()

    elif "exit" in command:
        speak("Exiting the system. Goodbye!")
        break

    elif command == "none":
        continue

    else:
        speak("Command not recognized. Please try again.")

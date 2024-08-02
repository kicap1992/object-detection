import torch
import cv2
import pandas as pd
import os
import string
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import tkinter as tk
from threading import Thread

# Load YOLOv5 model from GitHub
model = torch.hub.load('ultralytics/yolov5', 'yolov5n')

# Initialize webcam capture
cap = cv2.VideoCapture(0)  # Use 0 for default webcam, or specify a different index if needed

# Global variable for summary text
summary_text = ''

# Function to play sound or text-to-speech
def play_sound_or_tts(word, text_dir='suaraku', speed=1):
    filename = os.path.join(text_dir, f"{word}.wav")
    print(filename)

    if os.path.exists(filename):
        sound = AudioSegment.from_file(filename)
        sound = sound.speedup(playback_speed=speed)
        return sound
    else:
        tts = gTTS(word)
        tts.save('temp.mp3')
        sound = AudioSegment.from_file('temp.mp3')
        sound = sound.speedup(playback_speed=speed)
        os.remove('temp.mp3')
        return sound

def play_full_text(text, text_dir='suaraku', speed=1.0):
    translator = str.maketrans('', '', string.punctuation)
    words = text.translate(translator).split()
    
    combined_sound = AudioSegment.silent(duration=0)
    
    for word in words:
        print(word)
        sound = play_sound_or_tts(word, text_dir, speed)
        combined_sound += sound
    
    play(combined_sound)

def on_button_press():
    global summary_text
    play_button.config(text="Loading...")
    play_thread = Thread(target=play_audio_and_update_button)
    play_thread.start()

def play_audio_and_update_button():
    global summary_text
    play_full_text(summary_text, 'suaraku', 1.1)
    play_button.config(text="Play Summary")

def process_frame():
    global summary_text
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        return

    result = model(frame)
    data_frame = result.pandas().xyxy[0]

    # Filter detections with confidence above 70%
    data_frame = data_frame[data_frame['confidence'] > 0.4]

    label_counts = data_frame['name'].value_counts()
    indexes = data_frame.index
    for index in indexes:
        x1 = int(data_frame['xmin'][index])
        y1 = int(data_frame['ymin'][index])
        x2 = int(data_frame['xmax'][index])
        y2 = int(data_frame['ymax'][index])
        label = data_frame['name'][index]
        conf = data_frame['confidence'][index]
        text = label + ' ' + str(conf.round(decimals=2))
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 0), 2)
        cv2.putText(frame, text, (x1, y1-5), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 0), 2)

    if label_counts.empty:
        summary_text = 'No objects detected.'
    else:
        summary_text = 'There are: '
        for label, count in label_counts.items():
            summary_text += f'{count} {label}, '
        summary_text = summary_text[:-2]  # Remove the last comma and space
        summary_text += ' detected.'

    cv2.putText(frame, summary_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
    cv2.imshow('Webcam Feed', frame)
    cv2.waitKey(1)
    root.after(10, process_frame)

# GUI setup
root = tk.Tk()
root.title("Object Detection with Sound Playback")

play_button = tk.Button(root, text="Play Summary", command=on_button_press)
play_button.pack()

# Start the webcam processing
root.after(10, process_frame)

root.mainloop()

cap.release()
cv2.destroyAllWindows()

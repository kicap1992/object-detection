import os
from gtts import gTTS
import pygame
from pydub import AudioSegment
from pydub.playback import play

def play_sound_or_tts(filename, text):
    # Check if the sound file exists
    if os.path.exists(filename):
        # Play the sound file using pygame
        pygame.mixer.init()
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():  # Wait for the sound to finish playing
            continue
    else:
        # Convert text to speech using gTTS
        tts = gTTS(text)
        tts.save('temp.mp3')  # Save the generated speech to a temporary file
        
        # Load the temporary file into an AudioSegment
        sound = AudioSegment.from_file('temp.mp3')
        
        # Play the sound using pydub
        play(sound)
        
        # Remove the temporary file after playing
        os.remove('temp.mp3')

# Example usage
play_sound_or_tts('dog.wav', 'dog')

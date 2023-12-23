import pygame.mixer
import numpy as np

# Initialize the mixer
pygame.mixer.init()

# Load the sound
standstill_sound = pygame.mixer.Sound('sounds/standstill_sound.wav')
direction_change_sound = pygame.mixer.Sound('sounds/direction_change_sound.wav')

def detect_movement_unit_end(landmarks, threshold=0.01):
    # Initialize previous frame and direction
    prev_frame = None
    direction = None

    for i, frame in enumerate(landmarks):
        # Convert frame to numpy array of coordinates
        frame = np.array([[landmark.x, landmark.y, landmark.z] for landmark in frame])
                          
        if prev_frame is not None:
            # Calculate difference between frames
            diff = frame - prev_frame

           # Check if landmarks are at a standstill
            if np.all(np.abs(diff) < threshold):
                standstill_sound.play()

            # Check if direction of movement has changed
            if direction is not None and np.any(np.sign(diff) != np.sign(direction)):
                direction_change_sound.play()

            # Update direction
            direction = diff

        # Update previous frame
        prev_frame = frame
import pygame.mixer
import numpy as np
import mediapipe as mp
from mediapipe.python.solutions import pose as mp_pose

# Initialize the mixer
pygame.mixer.init()

# Load the sound
standstill_sound = pygame.mixer.Sound('sounds/standstill_sound.wav')
direction_change_sound = pygame.mixer.Sound('sounds/direction_change_sound.wav')

def calculate_angle(a, b, c):
    # Calculate the vectors from point B to point A and point B to point C
    ba = a - b
    bc = c - b

    # Calculate the cosine of the angle between these vectors
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))

    # Convert this to an angle in degrees
    angle = np.arccos(cosine_angle)

    return np.degrees(angle)

def detect_movement_unit_end(landmarks, threshold=0.01):
    # Initialize previous frame and direction
    prev_angles = None
    direction = None

    for i, frame in enumerate(landmarks):
        # Convert frame to numpy array of coordinates
        frame = np.array([[landmark.x, landmark.y, landmark.z] for landmark in frame])

        angles = np.array([
              calculate_angle(frame[mp_pose.PoseLandmark.LEFT_SHOULDER.value], 
              frame[mp_pose.PoseLandmark.LEFT_ELBOW.value],
                frame[mp_pose.PoseLandmark.LEFT_WRIST.value]
                ), # Left Elbow
              calculate_angle(frame[mp_pose.PoseLandmark.RIGHT_SHOULDER.value],
                frame[mp_pose.PoseLandmark.RIGHT_ELBOW.value],
                frame[mp_pose.PoseLandmark.RIGHT_WRIST.value]
                ), # Right Elbow
              calculate_angle(frame[mp_pose.PoseLandmark.LEFT_HIP.value],
                frame[mp_pose.PoseLandmark.LEFT_KNEE.value],
                frame[mp_pose.PoseLandmark.LEFT_ANKLE.value]
                ), # Left knee
              calculate_angle(frame[mp_pose.PoseLandmark.RIGHT_HIP.value],
                frame[mp_pose.PoseLandmark.RIGHT_KNEE.value],
                frame[mp_pose.PoseLandmark.RIGHT_ANKLE.value]
                ), # Right knee
              calculate_angle(frame[mp_pose.PoseLandmark.RIGHT_SHOULDER.value],
                frame[mp_pose.PoseLandmark.LEFT_SHOULDER.value],
                frame[mp_pose.PoseLandmark.LEFT_ELBOW.value]
                ), # Left shoulder
              calculate_angle(frame[mp_pose.PoseLandmark.LEFT_SHOULDER.value],
                frame[mp_pose.PoseLandmark.RIGHT_SHOULDER.value],
                frame[mp_pose.PoseLandmark.LEFT_ELBOW.value]
                ), # Right shoulder
              calculate_angle(frame[mp_pose.PoseLandmark.RIGHT_HIP.value],
                frame[mp_pose.PoseLandmark.LEFT_HIP.value],
                frame[mp_pose.PoseLandmark.LEFT_KNEE.value]
                ), # Left hip
              calculate_angle(frame[mp_pose.PoseLandmark.LEFT_HIP.value],
                frame[mp_pose.PoseLandmark.RIGHT_HIP.value],
                frame[mp_pose.PoseLandmark.RIGHT_KNEE.value]
                ), # Right hipd
              ])

        print(angles)

        if prev_angles is not None:
            # Calculate difference between frames
            diff = angles - prev_angles

            # Check if landmarks are at a standstill
            if np.all(np.abs(diff) < threshold):
                standstill_sound.play()
                print('Standstill detected')

            # Check if direction of movement has changed
            if direction is not None and np.any(np.sign(diff) != np.sign(direction)):
                direction_change_sound.play()
                print('Direction change detected')

            # Update direction
            direction = diff

        # Update previous frame
        prev_angles = angles
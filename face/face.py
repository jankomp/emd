import cv2
import mediapipe as mp

class FacialRecognition:
    def __init__(self):
        # Initialize MediaPipe FaceMesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh()

        # Initialize MediaPipe drawing utility
        self.mp_drawing = mp.solutions.drawing_utils

        self.face_landmarks = None

    def draw_face_landmarks(self, frame):
        # Convert the BGR image to RGB
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the image to detect faces and facial landmarks
        results = self.face_mesh.process(rgb_image)

        # Draw the facial landmarks on the frame
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                self.mp_drawing.draw_landmarks(frame, face_landmarks, self.mp_face_mesh.FACE_CONNECTIONS)

        return frame
    
    def estimate_happiness(self, face_landmarks):
        # Get the landmarks for the corners of the mouth
        mouth_corner_left = face_landmarks.landmark[self.mp_face_mesh.FACEMESH_CONTOURS['mouthCornerLeft']]
        mouth_corner_right = face_landmarks.landmark[self.mp_face_mesh.FACEMESH_CONTOURS['mouthCornerRight']]

        # Calculate the distance between the corners of the mouth
        mouth_width = ((mouth_corner_right.x - mouth_corner_left.x) ** 2 + (mouth_corner_right.y - mouth_corner_left.y) ** 2) ** 0.5

        # Get the landmarks for the upper and lower lips
        upper_lip = face_landmarks.landmark[self.mp_face_mesh.FACEMESH_CONTOURS['upperLip']]
        lower_lip = face_landmarks.landmark[self.mp_face_mesh.FACEMESH_CONTOURS['lowerLip']]

        # Calculate the distance between the upper and lower lips
        mouth_height = ((upper_lip.x - lower_lip.x) ** 2 + (upper_lip.y - lower_lip.y) ** 2) ** 0.5

        # The "happiness score" is the ratio of the mouth's width to its height
        happiness_score = mouth_width / mouth_height

        return happiness_score
import cv2
import mediapipe as mp
import numpy as np

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
                self.mp_drawing.draw_landmarks(
                    image=frame, 
                    landmark_list=face_landmarks, 
                    connections=self.mp_face_mesh.FACEMESH_CONTOURS,
                    landmark_drawing_spec=self.mp_drawing.DrawingSpec(color=(80,110,10), thickness=1, circle_radius=1),
                    connection_drawing_spec=self.mp_drawing.DrawingSpec(color=(80,256,121), thickness=1, circle_radius=1)
                )
                self.face_landmarks = face_landmarks

        return frame
    
    def draw_face_landmarks_indices(self, frame):
        # Convert the BGR image to RGB
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the image to detect faces and facial landmarks
        results = self.face_mesh.process(rgb_image)

        # Draw the facial landmarks on the frame
        if results.multi_face_landmarks:
            # Create a blank black frame
            blank_frame = np.zeros_like(frame)

            for face_landmarks in results.multi_face_landmarks:
                # Define the list of special indices
                special_indices = [61, 291, 78, 95, 93, 234, 33, 263, 454, 323]

                # First draw the regular indices
                for i, landmark in enumerate(face_landmarks.landmark):
                    if i not in special_indices:
                        # Convert the landmark point
                        landmark_point = [int(landmark.x * frame.shape[1]), int(landmark.y * frame.shape[0])]

                        # Draw the landmark on the blank frame
                        cv2.circle(blank_frame, tuple(landmark_point), 1, (0, 255, 0), -1)

                        # Write the index of the landmark next to the point on the blank frame
                        cv2.putText(blank_frame, str(i), tuple(landmark_point), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)

                # Then draw the special indices
                for i in special_indices:
                    landmark = face_landmarks.landmark[i]
                    # Convert the landmark point
                    landmark_point = [int(landmark.x * frame.shape[1]), int(landmark.y * frame.shape[0])]

                    # Draw the landmark on the blank frame
                    cv2.circle(blank_frame, tuple(landmark_point), 1, (0, 0, 255), -1)

                    # Write the index of the landmark next to the point on the blank frame
                    cv2.putText(blank_frame, str(i), tuple(landmark_point), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 2)

                self.face_landmarks = face_landmarks

            # Return the blank frame with the landmarks drawn on it
            return blank_frame
    
    def estimate_happiness(self):
        if self.face_landmarks is None:
            return 0.75

        # Get the landmarks for the corners of the mouth (AU12 ~ lip corner puller)
        mouth_corner_left = self.face_landmarks.landmark[61]
        mouth_corner_right = self.face_landmarks.landmark[291]

        # Calculate the distance between the corners of the mouth
        mouth_width = ((mouth_corner_right.x - mouth_corner_left.x) ** 2 + (mouth_corner_right.y - mouth_corner_left.y) ** 2) ** 0.5

        # Get the landmarks for the upper and lower lips (AU25 ~ lips part)
        upper_lip = self.face_landmarks.landmark[78]
        lower_lip = self.face_landmarks.landmark[95]

        # Calculate the distance between the upper and lower lips
        mouth_height = ((upper_lip.x - lower_lip.x) ** 2 + (upper_lip.y - lower_lip.y) ** 2) ** 0.5

        # Get the landmarks for the right cheeks (AU6 ~ cheek raiser)
        right_cheek_low = self.face_landmarks.landmark[93]
        right_cheek_high = self.face_landmarks.landmark[234]

        # Get the landmarks for the left cheeks (AU6 ~ cheek raiser)
        left_cheek_low = self.face_landmarks.landmark[454]
        left_cheek_high = self.face_landmarks.landmark[323]

        # Calculate the distance between the cheek points
        cheek_distance = (((right_cheek_high.x - right_cheek_low.x) ** 2 + (right_cheek_high.y - right_cheek_low.y) ** 2) ** 0.5 + ((left_cheek_high.x - left_cheek_low.x) ** 2 + (left_cheek_high.y - left_cheek_low.y) ** 2) ** 0.5) / 2

        # Get the landmarks for the eyes
        eye_left = self.face_landmarks.landmark[33]
        eye_right = self.face_landmarks.landmark[263]

        # Calculate the interocular distance
        interocular_distance = ((eye_right.x - eye_left.x) ** 2 + (eye_right.y - eye_left.y) ** 2) ** 0.5

        # The "happiness score" is a combination of the normalized mouth's width, its height, and the cheek distance
        happiness_score = (mouth_width + mouth_height + cheek_distance) / interocular_distance

        return happiness_score

#MESH_ANNOTATIONS: {[key: string]: number[]} = {
#  silhouette: [
#    10,  338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288,
#    397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136,
#    172, 58,  132, 93,  234, 127, 162, 21,  54,  103, 67,  109
#  ],
#
#  lipsUpperOuter: [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291],
#  lipsLowerOuter: [146, 91, 181, 84, 17, 314, 405, 321, 375, 291],
#  lipsUpperInner: [78, 191, 80, 81, 82, 13, 312, 311, 310, 415, 308],
#  lipsLowerInner: [78, 95, 88, 178, 87, 14, 317, 402, 318, 324, 308],
#
#  rightEyeUpper0: [246, 161, 160, 159, 158, 157, 173],
#  rightEyeLower0: [33, 7, 163, 144, 145, 153, 154, 155, 133],
#  rightEyeUpper1: [247, 30, 29, 27, 28, 56, 190],
#  rightEyeLower1: [130, 25, 110, 24, 23, 22, 26, 112, 243],
#  rightEyeUpper2: [113, 225, 224, 223, 222, 221, 189],
#  rightEyeLower2: [226, 31, 228, 229, 230, 231, 232, 233, 244],
#  rightEyeLower3: [143, 111, 117, 118, 119, 120, 121, 128, 245],
#
#  rightEyebrowUpper: [156, 70, 63, 105, 66, 107, 55, 193],
#  rightEyebrowLower: [35, 124, 46, 53, 52, 65],
#
#  rightEyeIris: [473, 474, 475, 476, 477],
#
#  leftEyeUpper0: [466, 388, 387, 386, 385, 384, 398],
#  leftEyeLower0: [263, 249, 390, 373, 374, 380, 381, 382, 362],
#  leftEyeUpper1: [467, 260, 259, 257, 258, 286, 414],
#  leftEyeLower1: [359, 255, 339, 254, 253, 252, 256, 341, 463],
#  leftEyeUpper2: [342, 445, 444, 443, 442, 441, 413],
#  leftEyeLower2: [446, 261, 448, 449, 450, 451, 452, 453, 464],
#  leftEyeLower3: [372, 340, 346, 347, 348, 349, 350, 357, 465],
#
#  leftEyebrowUpper: [383, 300, 293, 334, 296, 336, 285, 417],
#  leftEyebrowLower: [265, 353, 276, 283, 282, 295],
#
#  leftEyeIris: [468, 469, 470, 471, 472],
#
#  midwayBetweenEyes: [168],
#
#  noseTip: [1],
#  noseBottom: [2],
#  noseRightCorner: [98],
#  noseLeftCorner: [327],
#
#  rightCheek: [205],
#  leftCheek: [425]
#};
def main():
    # Open the webcam
    cap = cv2.VideoCapture(0)

    # Create an instance of the FacialRecognition class
    facial_recognition = FacialRecognition()

    # Capture a single frame from the webcam
    ret, frame = cap.read()

    # Draw the facial landmarks on the frame
    frame = facial_recognition.draw_face_landmarks_indices(frame)

    # save frame to file with opencv
    cv2.imwrite('docs/face_landmark_indices.jpg', frame)

    # Display the image
    cv2.imshow('Image', frame)

    # Wait for a key press and then close the image window
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Release the webcam
    cap.release()

if __name__ == "__main__":
    main()
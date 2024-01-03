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
                self.mp_drawing.draw_landmarks(
                    image=frame, 
                    landmark_list=face_landmarks, 
                    connections=self.mp_face_mesh.FACEMESH_CONTOURS,
                    landmark_drawing_spec=self.mp_drawing.DrawingSpec(color=(80,110,10), thickness=1, circle_radius=1),
                    connection_drawing_spec=self.mp_drawing.DrawingSpec(color=(80,256,121), thickness=1, circle_radius=1)
                )
                self.face_landmarks = face_landmarks

        return frame
    
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

        # Get the landmarks for the cheeks (AU6 ~ cheek raiser)
        cheek_left = self.face_landmarks.landmark[93]
        cheek_right = self.face_landmarks.landmark[234]

        # Calculate the distance between the cheeks
        cheek_distance = ((cheek_right.x - cheek_left.x) ** 2 + (cheek_right.y - cheek_left.y) ** 2) ** 0.5

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
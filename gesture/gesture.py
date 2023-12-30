import mediapipe as mp
from mediapipe.framework.formats import landmark_pb2
import csv
import numpy as np

class GestureRecognition:
    def __init__(self, csv_filename):
        # initialize mediapipe
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose()
        self.mp_drawing = mp.solutions.drawing_utils
        # open csv files
        self.file = open(csv_filename, 'w', newline='')
        self.writer = csv.writer(self.file)
        # write header row
        self.landmark_names = [f'landmark_{i}_{k}' for i in range(33) for k in ['x', 'y', 'z', 'visibility']]
        self.writer.writerow(self.landmark_names)
        # variables
        self.landmark_list = None
        self.adjusted_pose_connections = None

    def exclude_landmarks_and_connections(self, result):
        # Exclude landmarks 0 to 10 and the respective connections
        filtered_landmarks = [result.pose_landmarks.landmark[i] for i in range(11, 33)]
        filtered_pose_connections = [connection for connection in self.mp_pose.POSE_CONNECTIONS
                                     if connection[0] not in range(1, 11) and connection[1] not in range(1, 11)]
        # Adjust the indices of the connections to account for the removed landmarks
        adjusted_pose_connections = [(connection[0] - 11, connection[1] - 11) for connection in filtered_pose_connections]

        # Create a new NormalizedLandmarkList and populate it with the filtered landmarks
        landmark_list = landmark_pb2.NormalizedLandmarkList()
        for landmark in filtered_landmarks:
            landmark_list.landmark.add().CopyFrom(landmark)

        return landmark_list, adjusted_pose_connections

    def get_landmarks(self, rgb_image):
        # Get the landmarks from the frame
        results = self.pose.process(rgb_image)
        if results.pose_landmarks:
            self.landmark_list, self.adjusted_pose_connections = self.exclude_landmarks_and_connections(results)

    def draw_landmarks(self, rgb_image, frame):
        self.get_landmarks(rgb_image)

        # Draw the landmarks with the adjusted connections
        self.mp_drawing.draw_landmarks(frame, self.landmark_list, self.adjusted_pose_connections)

        return frame

    def center_and_scale(self, landmarks):
        # Filter out landmarks 1 to 10
        landmarks = [landmark for i, landmark in enumerate(landmarks) if i == 0 or i >= 11]
        
        # Calculate the average position
        avg_x = sum(landmark.x for landmark in landmarks) / len(landmarks)
        avg_y = sum(landmark.y for landmark in landmarks) / len(landmarks)
        avg_z = sum(landmark.z for landmark in landmarks) / len(landmarks)

        # Calculate the standard deviation
        std_dev = np.std([(landmark.x, landmark.y, landmark.z) for landmark in landmarks])

        # Subtract the average position from each landmark and divide by the standard deviation
        scaled_landmarks = []
        for landmark in landmarks:
            scaled_landmark = type(landmark)()  # Create a new instance of the same class
            scaled_landmark.x = (landmark.x - avg_x) / std_dev
            scaled_landmark.y = (landmark.y - avg_y) / std_dev
            scaled_landmark.z = (landmark.z - avg_z) / std_dev
            scaled_landmark.visibility = landmark.visibility  # Keep the same visibility
            scaled_landmarks.append(scaled_landmark)

        return scaled_landmarks, avg_x, avg_y, avg_z, std_dev
    
    def dance(self):
        # Save the landmarks to the CSV
        scaled_landmarks, _, _, _, _ = self.center_and_scale(self.landmark_list.landmark)                 
        landmark_row = [[landmark.x, landmark.y, landmark.z, landmark.visibility] for landmark in scaled_landmarks]
        landmark_row = [item for sublist in landmark_row for item in sublist]
        self.writer.writerow(landmark_row)

        return scaled_landmarks

    def copy(self, counter):
        # also saved the copied landmarks to a csv file
        scaled_landmarks = self.dance()
        # Return the difference between the saved landmarks and the current ones
        # Initialize saved_pose
        saved_pose = None
        with open('dance/dance_landmarks.csv', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for i, row in enumerate(reader):
                if i == counter:
                    saved_pose = row
                    break
        
        squared_diff = 0
        # calculate the squared difference between the current pose and the saved pose                        
        # Check if saved_pose is not None before calculating the squared difference
        if saved_pose is not None:
            for i, landmark in enumerate(scaled_landmarks):
                squared_diff += (landmark.x - float(saved_pose[i*4]))**2 + (landmark.y - float(saved_pose[i*4+1]))**2 + (landmark.z - float(saved_pose[i*4+2]))**2

        return squared_diff
    
    def cleanup(self):    
        # Close the CSV file
        self.file.close()
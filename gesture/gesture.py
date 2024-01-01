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
        self.raw_landmark_list = None
        self.current_landmarks = None
        self.adjusted_pose_connections = None
        self.last_three_poses = []
        self.main_poses = []

    def listToNormailizedLandmarkList(self, landmarks):
        # Create a new NormalizedLandmarkList and populate it with the filtered landmarks
        landmark_list = landmark_pb2.NormalizedLandmarkList()
        for landmark in landmarks:
            landmark_list.landmark.add().CopyFrom(landmark)
        return landmark_list

    def exclude_landmarks_and_connections(self, result):
        # Exclude landmarks 0 to 10 and the respective connections
        filtered_landmarks = [result.pose_landmarks.landmark[i] for i in range(11, 33)]
        filtered_pose_connections = [connection for connection in self.mp_pose.POSE_CONNECTIONS
                                     if connection[0] not in range(1, 11) and connection[1] not in range(1, 11)]
        # Adjust the indices of the connections to account for the removed landmarks
        adjusted_pose_connections = [(connection[0] - 11, connection[1] - 11) for connection in filtered_pose_connections]

        # Create a new NormalizedLandmarkList and populate it with the filtered landmarks
        landmark_list = self.listToNormailizedLandmarkList(filtered_landmarks)

        return landmark_list, adjusted_pose_connections

    def get_landmarks(self, rgb_image):
        # Get the landmarks from the frame
        results = self.pose.process(rgb_image)
        if results.pose_landmarks:
            self.raw_landmark_list, self.adjusted_pose_connections = self.exclude_landmarks_and_connections(results)
            self.current_landmarks, _, _, _, _ = self.center_and_scale(self.raw_landmark_list.landmark)
        # Update the last three poses
            self.last_three_poses.append(self.current_landmarks.landmark)
            if len(self.last_three_poses) > 5:
                self.last_three_poses.pop(0)

    def save_interesting_landmarks(self):
        # Update the last three poses
        self.main_poses.append(self.current_landmarks.landmark)

    def draw_landmarks(self, rgb_image, frame):
        self.get_landmarks(rgb_image)

        # Draw the landmarks with the adjusted connections
        self.mp_drawing.draw_landmarks(frame, self.raw_landmark_list, self.adjusted_pose_connections)

        return frame

    def center_and_scale(self, landmarks):        
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
        
        scaled_landmarks = self.listToNormailizedLandmarkList(scaled_landmarks)

        return scaled_landmarks, avg_x, avg_y, avg_z, std_dev
    
    def dance(self):
        # Save the landmarks to the CSV               
        landmark_row = [[landmark.x, landmark.y, landmark.z, landmark.visibility] for landmark in self.current_landmarks.landmark]
        landmark_row = [item for sublist in landmark_row for item in sublist]
        self.writer.writerow(landmark_row)

    def copy(self, counter):
        # Return the difference between the saved landmarks and the current ones
        # Initialize saved_pose
        saved_pose = None
        with open('dance/dance_landmarks.csv', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for i, row in enumerate(reader):
                if i == counter:
                    saved_pose = row
                    break
        
        squared_diff = self.compare(self.current_landmarks.landmark, saved_pose)

        return squared_diff        
    
    def compare(self, landmarks_1, landmarks_2):
        squared_diff = 0.0
        # calculate the squared difference between the current pose and the saved pose                        
        # Check if saved_pose is not None before calculating the squared difference
        if landmarks_1 is  None or landmarks_2 is None:
            return 10.0
            
        n = len(landmarks_2) // 4
        for i, landmark in enumerate(landmarks_1):
                if i >= n:
                    break
                squared_diff += (landmark.x - float(landmarks_2[i*4]))**2 + (landmark.y - float(landmarks_2[i*4+1]))**2 + (landmark.z - float(landmarks_2[i*4+2]))**2

        return squared_diff

    def dynamicTimeWarping(self, fromRow, toRow):
        # Read the saved landmarks from the CSV file
        saved_landmarks = []
        with open('dance/dance_landmarks.csv', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for i, row in enumerate(reader):
                if fromRow <= i <= toRow:
                    saved_landmarks.append(row)

        # Initialize the DTW matrix with infinity
        dtw_matrix = [[float('inf')] * (len(saved_landmarks) + 1) for _ in range(len(self.last_three_poses) + 1)]

        # Set the first cell to 0
        dtw_matrix[0][0] = 0

        # Calculate the DTW matrix
        for i in range(1, len(self.last_three_poses) + 1):
            for j in range(1, len(saved_landmarks) + 1):
                cost = self.compare(self.last_three_poses[i-1], saved_landmarks[j-1])
                dtw_matrix[i][j] = cost + min(dtw_matrix[i-1][j], dtw_matrix[i][j-1], dtw_matrix[i-1][j-1])

        # The last cell in the DTW matrix is the total cost of aligning the sequences
        return dtw_matrix[-1][-1]
    
    def find_most_similar_pose_in_current_dance(self, threshold):
        # Initialize the minimum squared difference and the index of the most similar pose
        min_squared_diff = float('inf')
        most_similar_pose_index = -1

        # initialize this_dance as a copy of last_three_poses with index % 5 == 0 and omit the last pose
        if self.main_poses == []:
            return None
        
        other_poses = self.main_poses[:-1]

        # Iterate over the saved landmarks
        for i, other_pose in enumerate(other_poses):
            other_pose = self.landmarks_to_list(other_pose)
            # Calculate the squared difference between the current pose and the saved landmark
            squared_diff = self.compare(self.current_landmarks.landmark, other_pose)
            print(f'move {i+1} squared diff: {squared_diff}')
            # If the squared difference is smaller than the current minimum, update the minimum and the index
            if squared_diff < min_squared_diff:
                min_squared_diff = squared_diff
                most_similar_pose_index = i

        # If the minimum squared difference is smaller than the threshold, return the index of the most similar pose
        if min_squared_diff < threshold:
            return most_similar_pose_index

        # If no pose is similar enough to the current pose, return None
        return None
    
    def landmarks_to_list(self, landmarks):
        return [coord for landmark in landmarks for coord in (landmark.x, landmark.y, landmark.z, landmark.visibility)]
    
    def cleanup(self):    
        # Close the CSV file
        self.file.close()
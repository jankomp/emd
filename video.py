import cv2
import mediapipe as mp
from mediapipe.framework.formats import landmark_pb2
import time
import csv
import numpy as np
import ctypes
import pygame.mixer

# Global variable to control the video loop
video_running = True
window_name = 'Little Dance Copiers'

def exclude_landmarks_and_connections(result, mp_pose):
        # Exclude landmarks 0 to 10 and the respective connections
        filtered_landmarks = [result.pose_landmarks.landmark[i] for i in range(11, 33)]
        # Create a new NormalizedLandmarkList and populate it with the filtered landmarks
        landmark_list = landmark_pb2.NormalizedLandmarkList()
        for landmark in filtered_landmarks:
            landmark_list.landmark.add().CopyFrom(landmark)

        # Filter out connections that involve landmarks 1 to 10
        filtered_pose_connections = [connection for connection in mp_pose.POSE_CONNECTIONS
                                    if connection[0] not in range(1, 11) and connection[1] not in range(1, 11)]
        # Adjust the indices of the connections to account for the removed landmarks
        adjusted_pose_connections = [(connection[0] - 11, connection[1] - 11) for connection in filtered_pose_connections]

        return landmark_list, adjusted_pose_connections

def center_and_scale(landmarks):
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

def resize_window(window_name, cap):    # Get the size of the screen
    user32 = ctypes.windll.user32
    screen_width, screen_height = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    #multiply screen width and height by 0.8 to get 80% of the screen size but cast to int
    screen_width, screen_height = int(screen_width * 0.9), int(screen_height * 0.9)
    # Get the aspect ratio of the video
    ret, frame = cap.read()
    if ret:
        video_height, video_width = frame.shape[:2]
        aspect_ratio = video_width / video_height

    # Calculate the new width to maintain the aspect ratio
    new_width = int(screen_height * aspect_ratio)

    # Create a window
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    # Resize the window
    cv2.resizeWindow(window_name, new_width, screen_height)



def draw_border(frame, color=(0, 255, 0), border_size=10):
    # Draw a colored border around the edges of the video
    frame[:border_size, :] = color
    frame[-border_size:, :] = color
    frame[:, :border_size] = color
    frame[:, -border_size:] = color

def run(mode, moves=5, bpm=60):
    global video_running
    video_running = True
    # Create a VideoCapture object
    cap = cv2.VideoCapture(0)

    # Initialize MediaPipe Pose
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose()

    # Initialize drawing utility
    mp_drawing = mp.solutions.drawing_utils

    # Check if camera opened successfully
    if not cap.isOpened(): 
        print("Unable to read camera feed")

    #resize the window
    resize_window(window_name, cap)

    # Initialize the mixer
    pygame.mixer.init()
    error_sound = pygame.mixer.Sound('sounds/error.wav')
    correct_sound = pygame.mixer.Sound('sounds/correct.wav')
    countdown_sound = pygame.mixer.Sound('sounds/countdown.wav')

    # Initialize the counter
    counter = -4
    start_time = time.time()

    # Define the codec and create a VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # or use 'XVID'
    out = cv2.VideoWriter(f'dance/{mode}_output.mp4', fourcc, 20.0, (640, 480))

    # Open the CSV file for writing
    file = open(f'dance/{mode}_landmarks.csv', 'w', newline='')
    writer = csv.writer(file)
    
    # Write the header row
    landmark_names = [f'landmark_{i}_{k}' for i in range(33) for k in ['x', 'y', 'z', 'visibility']]
    writer.writerow(landmark_names)

    
    ret, frame = cap.read()
    screenshots = []
    screenshot_height = frame.shape[0] // moves
    screenshot_width = frame.shape[1] // moves

    border_color = (0, 255, 0)

    delta_move = 60.0 / bpm
    
    while video_running:
        # Capture frame-by-frame
        ret, frame = cap.read()

        if ret:
            # Convert the BGR image to RGB
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Process the image and draw poses on it
            result = pose.process(rgb_image)
        if result.pose_landmarks:
            # Exclude landmarks 0 to 10 and the respective connections
            landmark_list, adjusted_pose_connections = exclude_landmarks_and_connections(result, mp_pose)
            # Draw the landmarks with the adjusted connections
            mp_drawing.draw_landmarks(frame, landmark_list, adjusted_pose_connections)

            # Update the counter every second
            if time.time() - start_time >= delta_move:
                counter += 1
                start_time = time.time()


                if counter <= 0:
                    countdown_sound.play()
                    draw_border(frame, (255, 0, 0), 10)

                if counter > 0 and counter <= moves and result.pose_landmarks:
                    screenshot = frame.copy()
                    screenshots.append(screenshot)
                    if mode == "dance":
                        #write landmark x, y, z, visibility of all 33 landmarks to csv
                        landmarks = [result.pose_landmarks.landmark[i] for i in range(33)]   
                        scaled_landmarks, _, _, _, _ = center_and_scale(landmarks)                 
                        landmark_row = [[landmark.x, landmark.y, landmark.z, landmark.visibility] for landmark in scaled_landmarks]
                        landmark_row = [item for sublist in landmark_row for item in sublist]
                        writer.writerow(landmark_row)

                        correct_sound.play()
                    elif mode == "copy":
                        #compare the current pose to the saved pose on row counter - 1
                        # Initialize saved_pose
                        saved_pose = None
                        landmarks = [result.pose_landmarks.landmark[i] for i in range(33)]
                        scaled_landmarks, _, _, _, _ = center_and_scale(landmarks)
                        with open('dance/dance_landmarks.csv', newline='') as csvfile:
                            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
                            for i, row in enumerate(reader):
                                if i == counter:
                                    saved_pose = row
                                    break

                        # calculate the squared difference between the current pose and the saved pose                        
                        # Check if saved_pose is not None before calculating the squared difference
                        if saved_pose is not None:
                            squared_diff = 0
                            for i, landmark in enumerate(scaled_landmarks):
                                squared_diff += (landmark.x - float(saved_pose[i*4]))**2 + (landmark.y - float(saved_pose[i*4+1]))**2 + (landmark.z - float(saved_pose[i*4+2]))**2
                            print(f"squared difference of row {counter}: {squared_diff}")
                            # if the squared difference is greater than 0.5, draw a red border and play alow sound
                            if squared_diff > 5:
                                border_color = (0, 0, 255)
                                error_sound.play()
                            else:
                                border_color = (0, 255, 0)
                                correct_sound.play()

            if counter < moves:
                # Draw the counter in the bottom right corner
                text = str(counter) if counter >= 1 else "GO" if counter == 0 else str(-counter)
                (text_width, text_height), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 2, 2)
                text_x = frame.shape[1] - text_width // 2 - 50
                text_y = frame.shape[0] - 10
                cv2.putText(frame, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 2.5, (255, 255, 255), 2)

            if counter > moves:
                video_running = False
            elif counter > 0 and time.time() - start_time <= 0.05:
                draw_border(frame, border_color, 10)

            # Create a larger frame to display the video and screenshots
            large_frame = np.zeros((frame.shape[0] + screenshot_height, frame.shape[1], 3), dtype=np.uint8)
            large_frame[:frame.shape[0], :] = frame

            # Place the screenshots below the video
            for i, screenshot in enumerate(screenshots):
                start_x = i * screenshot_width
                end_x = start_x + screenshot_width
                large_frame[frame.shape[0]:, start_x:end_x] = cv2.resize(screenshot, (screenshot_width, screenshot_height))

            # Write the frame into the file 'output.mp4'
            out.write(frame)
            # Display the resulting frame
            cv2.imshow(window_name, large_frame)

            # Break the loop on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                video_running = False
        else:
            break
    
    # Close the CSV file
    file.close()

    # When everything done, release the video capture and video write objects
    cap.release()
    out.release()
    cv2.destroyWindow(window_name)

def stop():
    global video_running
    video_running = False

if __name__ == "__main__":
    #run("dance")
    run("copy")
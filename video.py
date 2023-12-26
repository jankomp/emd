import cv2
import mediapipe as mp
import time
import csv

# Global variable to control the video loop
video_running = True
window_name = 'Little Dance Copiers'

def run(mode):
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

    # Initialize the counter
    counter = -3
    start_time = time.time()

    # Open the CSV file for writing
    file = open('dance/landmarks.csv', 'w', newline='')
    writer = csv.writer(file)
    
    # Write the header row
    landmark_names = [f'landmark_{i}_{k}' for i in range(33) for k in ['x', 'y', 'z', 'visibility']]
    writer.writerow(landmark_names)

    while video_running:
        # Capture frame-by-frame
        ret, frame = cap.read()

        if ret:
            # Convert the BGR image to RGB
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Process the image and draw poses on it
            result = pose.process(rgb_image)
            if result.pose_landmarks:
                mp_drawing.draw_landmarks(frame, result.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            # Update the counter every second
            if time.time() - start_time >= 1:
                counter += 1
                start_time = time.time()
                if counter > 5:
                    video_running = False

                if counter == -1:
                    #save idle pose
                    idle_pose = [result.pose_landmarks.landmark[i] for i in range(33)]

                if counter > 0 & counter <= 5:
                    if mode == "dance":
                        #write landmark x, y, z, visibility of all 33 landmarks to csv
                        landmarks = [result.pose_landmarks.landmark[i] for i in range(33)]                    
                        landmark_row = [[landmark.x - idle_pose[i].x, landmark.y - idle_pose[i].y, landmark.z - idle_pose[i].z, landmark.visibility] for i, landmark in enumerate(landmarks)]
                        landmark_row = [item for sublist in landmark_row for item in sublist]
                        writer.writerow(landmark_row)
                    elif mode == "copy":
                        #compare the current pose to the saved pose on row counter - 1
                        landmarks = [result.pose_landmarks.landmark[i] for i in range(33)]
                        with open('dance/landmarks.csv', newline='') as csvfile:
                            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
                            for i, row in enumerate(reader):
                                if i == counter - 1:
                                    saved_pose = row
                                    break
                        #calculate the squared difference between the current pose and the saved pose
                        squared_diff = 0
                        for i, landmark in enumerate(landmarks):
                            squared_diff += (landmark.x - float(saved_pose[i*4]))**2 + (landmark.y - float(saved_pose[i*4+1]))**2 + (landmark.z - float(saved_pose[i*4+2]))**2

            # Draw the counter in the bottom right corner
            text = str(counter) if counter >= 1 else "GO" if counter == 0 else str(-counter)
            (text_width, text_height), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 2, 2)
            text_x = frame.shape[1] - text_width // 2 - 50
            text_y = frame.shape[0] - 10
            cv2.putText(frame, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2)

            # Display the resulting frame
            cv2.imshow(window_name, frame)

            # Break the loop on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                video_running = False
        else:
            break
    
    # Close the CSV file
    file.close()

    # When everything done, release the video capture and video write objects
    cap.release()

    # Closes all the frames
    cv2.destroyWindow(window_name)

def stop():
    global video_running
    video_running = False
import cv2
import time
import numpy as np
import ctypes
import pygame.mixer
from gesture.gesture import GestureRecognition
from face.face import FacialRecognition
import matplotlib.pyplot as plt
from music import Music


# Global variable to control the video loop
video_running = True
window_name = 'Little Dance Copiers'

def score(dtw_score, squared_diff_score, happiness_score):
    dtw_score = (50 - dtw_score) * 10
    print(f'dtw score: {dtw_score}')
    dtw_score = dtw_score if dtw_score > 0 else 0
    squared_diff_score = (20 - squared_diff_score) * 100
    print(f'squared diff score: {squared_diff_score}')
    squared_diff_score = squared_diff_score if squared_diff_score > 0 else 0
    happiness_score = happiness_score * 100
    print(f'happiness score: {happiness_score}')

    return int(dtw_score + squared_diff_score + happiness_score)

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

def run(mode, moves=5, bpm=60, happy_face=False):
    global video_running
    video_running = True
    # Create a VideoCapture object
    cap = cv2.VideoCapture(0)

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

    music = Music()
    if mode == "dance":
        music.generate_starting_note()

    # Initialize the counter
    counter = -4
    pose_counter = counter * 5
    start_time = time.time()
    frame_time = start_time
    current_score_time = start_time
    total_score = 0

    # Define the codec and create a VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # or use 'XVID'
    #get current date and time
    video_datetime = str(time.time())
    out = cv2.VideoWriter(f'dance/{video_datetime}_{mode}_output.mp4', fourcc, 20.0, (640, 480))
    
    ret, frame = cap.read()
    screenshots = []
    screenshot_height = frame.shape[0] // moves
    screenshot_width = frame.shape[1] // moves

    border_color = (0, 255, 0)

    delta_move = 60.0 / bpm

    gr = GestureRecognition(csv_filename=f'dance/{mode}_landmarks.csv')
    fr = FacialRecognition()

    all_happiness = []
    all_sq_diff = []
    all_dtw = []
    
    while video_running:
        # Capture frame-by-frame
        ret, frame = cap.read()

        if ret:
            # Convert the BGR image to RGB
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # draw the landmarks
            frame = gr.draw_landmarks(rgb_image, frame)

            # draw the face landmarks
            if happy_face:
                frame = fr.draw_face_landmarks(frame)

            # Update the counter every second
            if time.time() - start_time >= delta_move / 5.0:
                pose_counter += 1
                start_time = time.time()

                # Save pose every time pose_counter increments
                if pose_counter > 0:
                    gr.dance()

                # if it's not a 3rd iterarion we are done, otherwise we increment counter
                if pose_counter % 5 == 0:
                    counter += 1
                    frame_time = time.time()
                    current_score_time = time.time()
                
                    if counter <= 0:
                        countdown_sound.play()
                        border_color = (255, 0, 0)

                    if counter > 0 and counter <= moves:
                        screenshot = frame.copy()
                        screenshots.append(screenshot)
                        gr.save_interesting_landmarks()
                        if mode == "dance":
                            border_color = (0, 255, 0)
                            if counter > 1:
                                similar_move = gr.find_most_similar_pose_in_current_dance(threshold=3)
                                music.generate_next_note(similar_move)

                            music.play_melody_at_index(counter - 1)
                        elif mode == "copy":
                            #compare the current pose to the saved pose on row counter
                            squared_diff = gr.copy(pose_counter)
                            
                            # if the squared difference is greater than 3, draw a red border and play a low sound
                            if squared_diff > 3:
                                border_color = (0, 0, 255)
                                error_sound.play()
                            else:
                                border_color = (0, 255, 0)
                                music.play_melody_at_index(counter - 1)
                    
                            # score happiness of face
                            happiness_score = 0.75
                            if happy_face:
                                happiness_score = fr.estimate_happiness()

                            # Call dynamicTimeWarping with poseCounter - 4 and poseCounter and a set of the last five poses
                            # divide the result by squared difference to ignore the scale of the difference
                            sd = squared_diff if squared_diff > 1 else 1
                            dtw_score = gr.dynamicTimeWarping(pose_counter - 4, pose_counter) / sd

                            # Append the scores to the lists
                            if happy_face:
                                all_happiness.append(happiness_score)
                            all_sq_diff.append(squared_diff)
                            all_dtw.append(dtw_score)

                            # Calculate the score
                            current_score = score(dtw_score, squared_diff, happiness_score)
                            total_score += current_score

            if mode == "copy" and counter > 0 and counter <= moves:
                if time.time() - current_score_time <= delta_move / 2:
                    # Display total score in blue
                    cv2.putText(frame, f'Score: {total_score - current_score}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3, cv2.LINE_AA)
                    (text_width, text_height), _ = cv2.getTextSize(f'Score: {total_score - current_score}', cv2.FONT_HERSHEY_SIMPLEX, 1, 3)
                    # Display current score in orange for a fraction of a second
                    cv2.putText(frame, f' + {current_score}', (10 + text_width, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 3, cv2.LINE_AA)
                else:
                    # Display total score in blue
                    cv2.putText(frame, f'Score: {total_score}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3, cv2.LINE_AA)

            if counter < moves:
                # Draw the counter in the bottom right corner
                text = str(counter) if counter >= 1 else "GO" if counter == 0 else str(-counter)
                (text_width, text_height), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 2, 2)
                text_x = frame.shape[1] - text_width // 2 - 50
                text_y = frame.shape[0] - 10
                cv2.putText(frame, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 2.5, (255, 255, 255), 2)

            if counter > moves:
                video_running = False
            elif time.time() - frame_time <= 0.05:
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

    # When everything done, release the video capture and video write objects
    cap.release()
    out.release()
    cv2.destroyWindow(window_name)
    gr.cleanup()
   
    # display a plot of the three scores
    if mode == "copy":
        fig, axs = plt.subplots(3, 1, figsize=(10, 15))
        axs[0].bar(range(len(all_sq_diff)), all_sq_diff, label="Squared Difference")
        axs[0].legend()
        axs[1].bar(range(len(all_dtw)), all_dtw, label="Dynamic Time Warping")
        axs[1].legend()
        if happy_face:
            axs[2].bar(range(len(all_happiness)), all_happiness, label="Happiness")
            axs[2].legend()
        plt.savefig(f'dance/{video_datetime}_{mode}_scores.png')

def stop():
    global video_running
    video_running = False

if __name__ == "__main__":
    #run("dance", 5, 60, True)
    run("copy", 5, 60, True)
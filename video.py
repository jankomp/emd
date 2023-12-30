import cv2
import time
import numpy as np
import ctypes
import pygame.mixer
from gesture.gesture import GestureRecognition
from face.face import FacialRecognition


# Global variable to control the video loop
video_running = True
window_name = 'Little Dance Copiers'

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

    # Initialize the counter
    counter = -4
    start_time = time.time()

    # Define the codec and create a VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # or use 'XVID'
    out = cv2.VideoWriter(f'dance/{mode}_output.mp4', fourcc, 20.0, (640, 480))
    
    ret, frame = cap.read()
    screenshots = []
    screenshot_height = frame.shape[0] // moves
    screenshot_width = frame.shape[1] // moves

    border_color = (0, 255, 0)

    delta_move = 60.0 / bpm

    gr = GestureRecognition(csv_filename=f'dance/{mode}_landmarks.csv')
    fr = FacialRecognition()
    
    while video_running:
        # Capture frame-by-frame
        ret, frame = cap.read()

        if ret:
            # Convert the BGR image to RGB
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # draw the landmarks
            frame = gr.draw_landmarks(rgb_image, frame)

            # draw the face landmarks
            frame = fr.draw_face_landmarks(frame)

            # Update the counter every second
            if time.time() - start_time >= delta_move:
                counter += 1
                start_time = time.time()


                if counter <= 0:
                    countdown_sound.play()
                    draw_border(frame, (255, 0, 0), 10)

                if counter > 0 and counter <= moves:
                    screenshot = frame.copy()
                    screenshots.append(screenshot)
                    if mode == "dance":
                        gr.dance()

                        correct_sound.play()
                    elif mode == "copy":
                        #compare the current pose to the saved pose on row counter
                        squared_diff = gr.copy(counter)
                        
                        # if the squared difference is greater than 0.5, draw a red border and play alow sound
                        if squared_diff > 5:
                            border_color = (0, 0, 255)
                            error_sound.play()
                        else:
                            border_color = (0, 255, 0)
                            correct_sound.play()
                
                if happy_face:
                    # score happiness of face
                    happiness_score = fr.estimate_happiness()
                    print(f"happiness score: {happiness_score}")

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

    # When everything done, release the video capture and video write objects
    cap.release()
    out.release()
    cv2.destroyWindow(window_name)
    gr.cleanup()

def stop():
    global video_running
    video_running = False

if __name__ == "__main__":
    #run("dance")
    run("copy", 5, 60, True)
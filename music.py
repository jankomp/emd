import csv
import random
import pygame

class Music:
    def __init__(self):
        self.notes = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
        self.note_sounds = {note: pygame.mixer.Sound(f"sounds/notes/{note}.wav") for note in self.notes}
        
        # Initialize the melody from the CSV file
        with open('dance/melody.csv', 'r') as f:
            reader = csv.reader(f)
            self.melody = next(reader)

    def generate(self, length):
        melody = [random.choice(self.notes) for _ in range(length)]
        
        # Save the melody to the CSV file
        with open('dance/melody.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(melody)
        
        self.melody = melody
    
    def play_melody_at_index(self, index):
        pygame.mixer.Sound.play(self.note_sounds[self.melody[index]])

    def play_melody(self):
        for note in self.melody:
            pygame.mixer.Sound.play(self.note_sounds[note])
            pygame.time.wait(500)  # Wait for 500 milliseconds

if __name__ == "__main__":
    pygame.mixer.init()
    music = Music()
    melody = music.generate(5)
    music.play_melody_at_index(3)
    pygame.mixer.quit()
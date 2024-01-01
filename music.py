import csv
import random
import pygame

class Music:
    def __init__(self):
        self.notes = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
        self.note_sounds = {note: pygame.mixer.Sound(f"sounds/notes/{note}.wav") for note in self.notes}
        self.melody = None

        # Initialize the melody from the CSV file
        with open('dance/melody.csv', 'r') as f:
            reader = csv.reader(f)
            self.melody = next(reader)

    def generate_starting_note(self):
        self.melody.clear()
        self.melody.append(random.choice(self.notes))
        
        # Save the melody to the CSV file
        self.write_melody()

    def generate_next_note(self, similar_note=None):
        if similar_note is None:
            # pop the last note in melody from the notes
            other_notes = self.notes.copy()
            other_notes.remove(self.melody[-1])
            # Choose a random note (except the previous note)
            next_note = random.choice(other_notes)
        else:
            next_note = random.choice(self.melody[similar_note])

        self.melody.append(next_note)

        # Save the melody to the CSV file
        self.write_melody()
    
    def write_melody(self):
        with open('dance/melody.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(self.melody)

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
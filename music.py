import random
import pygame

class Music:
    def __init__(self):
        self.notes = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
        self.note_sounds = {note: pygame.mixer.Sound(f"sounds/notes/{note}.wav") for note in self.notes}

    def generate(self, length):
        melody = [random.choice(self.notes) for _ in range(length)]
        return melody
    
    def play_melody_at_note(self, note):
        pygame.mixer.Sound.play(self.note_sounds[note])

    def play_melody(self, melody):
        for note in melody:
            pygame.mixer.Sound.play(self.note_sounds[note])
            pygame.time.wait(500)  # Wait for 500 milliseconds

if __name__ == "__main__":
    pygame.mixer.init()
    music = Music()
    melody = music.generate(5)
    music.play_melody(melody)
    pygame.mixer.quit()
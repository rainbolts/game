import pygame


class AudioSystem:
    def __init__(self):
        self.playing = False

    def play(self):
        if not self.playing:
            pygame.mixer.music.load('audio/Whispers of the Deep (edited).mp3')
            pygame.mixer.music.set_volume(0.05)
            pygame.mixer.music.play(-1)
            self.playing = True

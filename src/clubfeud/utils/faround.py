import sys
import pygame
import time

__author__ = 'boaz'





def main():
    freq = 44100     # audio CD quality
    bitsize = -16    # unsigned 16 bit
    channels = 2     # 1 is mono, 2 is stereo
    buffer = 2048    # number of samples (experiment to get right sound)
    pygame.mixer.init(freq, bitsize, channels, buffer)
    c = pygame.mixer.Channel(1)
    c.queue(pygame.mixer.Sound(sys.argv[1]))
    for f in sys.argv[2:]:
        c.queue(pygame.mixer.Sound(f))
        while not c.get_queue():
            time.sleep(1);


    while c.get_busy():
        time.sleep(1);







if __name__ == "__main__":
    main()
  
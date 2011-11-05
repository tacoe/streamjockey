from Queue import Queue
import logging
import sys
import threading
import pygame
import time

__author__ = 'boaz'


class QueuedWavePlayer(object):

    def __init__(self):
        self.queue = Queue();
        freq = 44100     # audio CD quality
        bitsize = -16    # unsigned 16 bit
        channels = 2     # 1 is mono, 2 is stereo
        buffer = 2048    # number of samples (experiment to get right sound)
        pygame.mixer.init(freq, bitsize, channels, buffer)
        self.channel = pygame.mixer.Channel(1)

        self.logger = logging.getLogger("qplayer")

        t=threading.Thread(target=self.playing_target);
        t.daemon = True;
        t.start()


    def playing_target(self):

        while True:
            file_to_play=self.queue.get()
            self.logger.info("Queuing %s in channel",file_to_play)
            self.channel.queue(pygame.mixer.Sound(file_to_play))
            self.queue.task_done()
            while self.channel.get_queue():
                time.sleep(1);


    def queue_for_playing(self,file_to_play):
        self.queue.put(file_to_play)



def main():
    logger= logging.getLogger()
    logger.setLevel(logging.DEBUG)
    ch= logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("%(asctime)s | %(process)d|%(thread)d | %(name)s | %(levelname)s | %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)


    qwp=QueuedWavePlayer()

    for f in sys.argv[1:]:
        qwp.queue_for_playing(f)
        logger.info("Main loop: queued %s",f)
        time.sleep(1)



    qwp.queue.join()


if __name__ == "__main__":
    main()
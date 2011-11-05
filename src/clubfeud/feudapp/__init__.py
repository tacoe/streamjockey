import functools
import logging
import threading

from . import models
import os
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import signals
import traceback
import sys
from clubfeud.utils import spotysuck, mixer


class QueueListener(object):
    """
       base class of queue listener
    """
    def __init__(self,name):
        self.lock = threading.RLock()
        self.dj_busy= dict() # a diction saying if a dj already sucks
        self.logger = logging.getLogger("name")
        self.queue_changed_condition = threading.Condition(self.lock) # this is some reason to see if you spotysuck something

        queue_changed_thread = threading.Thread(target=self.queue_changed_target)
        queue_changed_thread.daemon=True
        queue_changed_thread.start()

    def queue_changed_target(self):
        with self.lock:
             while True:
                try:

                    for queued_track_working_unit in self.get_queued_trackes_to_be_processed():
                        self.process_queued(queued_track_working_unit)

                    self.queue_changed_condition.wait()

                except Exception as e:
                    self.logger.exception(e)


    def process_queued(self,queued_track_working_unit):
        raise NotImplementedError("process_queued")

    def notify_track_queue_change(self):
        with self.lock:
            self.queue_changed_condition.notify()



class Sucker(QueueListener):


    def get_queued_trackes_to_be_processed(self):
        with self.lock:
            for dj in models.DJ_DICT.keys():
                if not self.dj_busy.get(dj):
                    # yay!
                    queued_track = models.QueuedTrack.objects.filter(dj=dj,state='requested')[0:1]
                    if queued_track:
                        yield (dj,queued_track[0])



    def _mark_dj_as_busy(self,dj):
        self.logger.debug("Sucker: Setting Dj %s to busy",dj)
        with self.lock:
            self.dj_busy[dj]=True


    def _mark_dj_as_free(self,dj):
        self.logger.debug("Sucker: Dj %s has nothing to do",dj)
        with self.lock:
            self.dj_busy[dj]=False


    def process_queued(self,queued_track_working_unit):
        (dj,queued_track) = queued_track_working_unit

        def background():
            try:
                track = queued_track.track
                if not os.path.exists(track.get_mp3_file_name()):
                    self.logger.info("sucking %s",track.spotifyid)
                    self._mark_dj_as_busy(dj)
                    spotysuck.suckit(dj,models.get_dj_password(dj),track.spotifyid,track.get_mp3_file_name())
                else:
                    self.logger.info("skipping %s as it is already in cache",track.spotifyid)

                queued_track.state="fetched"
                queued_track.save() # triggers a track change notification

            except Exception as e:
                self.logger.exception("background spotisuck thread had an error: %s",e)
                queued_track.state="error"
                queued_track.save() # triggers a track change notification


            self._mark_dj_as_free(dj) ## what ever happens dj is free now




        t = threading.Thread(target=background)
        t.daemon=True
        t.start()


class Mixer(QueueListener):


    def get_queued_trackes_to_be_processed(self):
        with self.lock:
            for queued_track in models.QueuedTrack.objects.filter(state='fetched'):
                following_track = models.QueuedTrack.objects.filter(state='fetched',position=queued_track.position+1)
                self.logger.debug("Found %s following tracks",following_track)
                if following_track:
                    yield (queued_track,following_track[0])


    def process_queued(self,queued_track_working_unit):
        (queued_track,following_track) = queued_track_working_unit

        def background():
            try:

                ta = queued_track.track.get_mp3_file_name()
                tb=following_track.track.get_mp3_file_name()
                self.logger.info("Mixing %s and %s. GO TACO!",ta,tb)
                m=mixer.mix(ta,tb,0)

                wav = os.path.join(settings.TRACK_PLAYER_DIR,"playlist.%s.mp3",queued_track.position)
                self.logger.info("Saving the mix of %s and %s to %s",ta,tb,queued_track.position)
                mixer.save_mixing_result(m,wav)

                queued_track.state="mixed"
                queued_track.save() # triggers a track change notification

            except Exception as e:
                self.logger.exception("background spotisuck thread had an error: %s",e)
                queued_track.state="error"
                queued_track.save() # triggers a track change notification






        t = threading.Thread(target=background)
        t.daemon=True
        t.start()


GLOBAL_SUCKER=Sucker("sucker")
GLOBAL_MIXER=Mixer("mixer")

def queued_post_save(sender, instance, signal, *args, **kwargs):
   # Creates user profile
    GLOBAL_SUCKER.notify_track_queue_change()
    GLOBAL_MIXER.notify_track_queue_change()

signals.post_save.connect(queued_post_save, sender=models.QueuedTrack)



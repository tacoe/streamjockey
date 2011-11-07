import re
from django.conf import settings
from django.db import models


# Create your models here.
import os


# TODO: Modeliz this
DJ_DICT = dict(bleskes="streamjockey",tacoe="streamjockey")

def verify_known_dj(dj):
    return dj in DJ_DICT

def add_dj(dj,password):
    DJ_DICT[dj]=password

def get_dj_password(dj):
    return DJ_DICT[dj]


class Track(models.Model):
    spotifyid = models.CharField(max_length=200,db_index=True,unique=True)

    title = models.CharField(max_length=256)
    artist = models.CharField(max_length=256)
    cover_url = models.CharField(max_length=1024)


    @staticmethod
    def get_track_cache_dir():
        return settings.TRACK_CACHE_DIR

    def get_mp3_file_name(self):
        """ returns a full path to the track's mp3 file
        """
        return os.path.join(Track.get_track_cache_dir(),self.spotifyid[len("spotify:track:"):] + ".mp3")




class QueuedTrack(models.Model):

    STATE_CHOICES = (
        ('requested'),
        ('fetched'),
        ('mixed'),
        ('playing'),
        ('done'),
        ('error'),
      )


    position = models.IntegerField() # tbd what it should be.
    track = models.ForeignKey(Track)
    dj = models.CharField(max_length=100) # username spotify
    state = models.CharField(choices=zip(STATE_CHOICES,STATE_CHOICES),max_length=20)


    def get_wav_file_name(self):
        """ returns a full path to the track's wave file
        """
        return os.path.join(settings.TRACK_PLAYER_DIR,"playlist.%s.wav" % (self.position,))

    class Meta:
        ordering = ['position']




# Create your views here.
from . import models
import logging
from django.db.models.aggregates import Max
from django.http import HttpResponse
from django.shortcuts import get_object_or_404


def enqueue(request,dj,spotifyid):
    track = get_object_or_404(models.Track,spotifyid=spotifyid)
    queued_track = models.QueuedTrack()
    queued_track.track=track
    if not (models.verify_known_dj(dj)):
        raise Exception("Dj %s not found" % (dj,))
    queued_track.dj=dj
    queued_track.state="requested"

    # TODO: atomize
    pos= models.QueuedTrack.objects.aggregate(position=Max('position'))['position'] or 0
    queued_track.position=pos+1
    queued_track.save()

    return HttpResponse("{ success : true }")






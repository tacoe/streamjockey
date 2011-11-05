# MIXER.PY
# mixes track runs for ClubFeud
# takes mp3s and produces one mix run
# heavily borrows from Echonest Remix sample code (echonest rules!)

import spotimeta
import urllib
import simplejson
import numpy 
from pyechonest import song
from pprint import pprint
from echonest.action import render, Crossfade, Playback, Crossmatch, Fadein, Fadeout, humanize_time
from echonest.audio import LocalAudioFile
from copy import deepcopy

metacache = {}
metadata = spotimeta.Metadata(cache=metacache)

CROSSFADETIME = 15.0 # crossfade time
PLAYTIME = 10.0 # play time (TODO ability to set to -1 for full tracks)
FADE_IN = 0

FUSION_INTERVAL = .06   # this is what we use in the analyzer
AVG_PEAK_OFFSET = 0.025 # Estimated time between onset and peak of segment.
X_FADE = 3 #

SHORTENTRACKS = 64 # in beats


def main():
	m = mix("mp3/output1.mp3", "mp3/coldenergy.mp3", 0)
	print " * rendering"
	render(m, 'outA.mp3')

	m = mix("mp3/coldenergy.mp3", "mp3/1998.mp3", 967)
	print " * rendering"
	render(m, 'outB.mp3')

	m = mix("mp3/1998.mp3", "mp3/milano.mp3", 575)
	print " * rendering"
	render(m, 'outC.mp3')

def mix(fnA, fnB, offset = 0):
	print "------------------------- mixing tracks -------------------------"
	# get mp3 from spotisuck
	print " * loading and analyzing track A"
	trackA = LocalAudioFile(fnA)
	print " * loading and analyzing track B"
	trackB = LocalAudioFile(fnB)

	tracks = [trackA, trackB]
	print " * resampling tracks"
	for track in tracks:
		track.resampled = resample_features(track)
		track.resampled['matrix'] = timbre_whiten(track.resampled['matrix'])

	# refactor this bit and specificy fill in matrix bars
	tAs = trackA.analysis.beats[0].start
	tAe = trackA.analysis.beats[len(trackA.analysis.beats)-1-SHORTENTRACKS-offset].start - CROSSFADETIME
	afill = tAe - tAs
	print "TO PLAY: from %5.2fs to %5.2fs over %5.2fs" % (tAs, tAe, afill)
	print "A offset: %f" % tAs
	print "A xfade start: %f" % tAe

	markers = getattr(trackA.analysis, trackA.resampled['rate'])
	print "A index: %f" % markers[track.resampled['index']].start
	print "A cursor: %f" % markers[track.resampled['cursor']].start

	start = initialize(trackA, afill, CROSSFADETIME)
	mid = make_transition(trackA, trackB, 0, CROSSFADETIME)
	return start + mid

def timbre_whiten(mat):
	if rows(mat) < 2: return mat
	m = numpy.zeros((rows(mat), 12), dtype=numpy.float32)
	m[:,0] = mat[:,0] - numpy.mean(mat[:,0],0)
	m[:,0] = m[:,0] / numpy.std(m[:,0],0)
	m[:,1:] = mat[:,1:] - numpy.mean(mat[:,1:].flatten(),0)
	m[:,1:] = m[:,1:] / numpy.std(m[:,1:].flatten(),0) # use this!
	return m

# find initial cursor position
def initialize(track, inter, transition):
	mat = track.resampled['matrix']
	markers = getattr(track.analysis, track.resampled['rate'])

	try:
		# compute duration of matrix
		mat_dur = markers[track.resampled['index'] + rows(mat)].start - markers[track.resampled['index']].start
		start = (mat_dur - inter - transition - FADE_IN) / 2
		dur = start + FADE_IN + inter
		print "start %5.2f plus inter %5.2f becomes duration %5.2f" % (start, inter, dur)
		# move cursor to transition marker
		duration, track.resampled['cursor'] = move_cursor(track, dur, 0)
		# work backwards to find the exact locations of initial fade in and playback sections
		fi = Fadein(track, markers[track.resampled['index'] + track.resampled['cursor']].start - inter - FADE_IN, FADE_IN)
		pb = Playback(track, markers[track.resampled['index'] + track.resampled['cursor']].start - inter, inter)
		print "Playback starts at %5.2f and lasts %5.2f" % (markers[track.resampled['index'] + track.resampled['cursor']].start - inter, inter)
	except:
		track.resampled['cursor'] = FADE_IN + inter
		fi = Fadein(track, 0, FADE_IN)
		pb = Playback(track, FADE_IN, inter)

	return [fi, pb]

def initializewithstartindex(track, startindex, transition):
	mat = track.resampled['matrix']
	markers = getattr(track.analysis, track.resampled['rate'])

	try:
		# compute duration of matrix
		mat_dur = markers[track.resampled['index'] + rows(mat)].start - markers[track.resampled['index']].start
		inter = mat_dur - transition
		start = markers[startindex].start
		dur = start + inter
		# move cursor to transition marker
		duration, track.resampled['cursor'] = move_cursor(track, dur, 0)
		# work backwards to find the exact locations of initial fade in and playback sections
		fi = Fadein(track, markers[track.resampled['index'] + track.resampled['cursor']].start - inter, 0)
		pb = Playback(track, markers[track.resampled['index'] + track.resampled['cursor']].start - inter, inter)
		#track.resampled['index'] = startindex
	except:
		raise
		print "initialize excepted"
		track.resampled['cursor'] = FADE_IN + inter
		fi = Fadein(track, 0, FADE_IN)
		pb = Playback(track, FADE_IN, inter)

#TODO mix on BARS not BEATS
def resample_features(data):
	feature='timbre'
	rate='beats' 
 
	ret = {'rate': rate, 'index': 0, 'cursor': 0, 'matrix': numpy.zeros((1, 12), dtype=numpy.float32)}
	segments, ind = get_central(data.analysis, 'segments')
	markers, ret['index'] = get_central(data.analysis, rate)
	# right now, markers has all beats -- segments has all tantums (sixteenths)

	if len(segments) < 2 or len(markers) < 2:
		return ret
		
	# Find the optimal attack offset
	meanOffset = get_mean_offset(segments, markers)
	tmp_markers = deepcopy(markers)

	# Apply the offset
	for m in tmp_markers:
		m.start -= meanOffset
		if m.start < 0: m.start = 0
	
	# Allocate output matrix, give it alias mat for convenience.
	# the output matrix is #beats by 12. 
	mat = ret['matrix'] = numpy.zeros((len(tmp_markers)-1, 12), dtype=numpy.float32)
	
	# Find the index of the segment that corresponds to the first marker
	f = lambda x: tmp_markers[0].start < x.start + x.duration
	index = (i for i,x in enumerate(segments) if f(x)).next()
	
	# Do the resampling
	try:
		for (i, m) in enumerate(tmp_markers):
			while segments[index].start + segments[index].duration < m.start + m.duration:
				dur = segments[index].duration
				if segments[index].start < m.start:
					dur -= m.start - segments[index].start
				
				C = min(dur / m.duration, 1)
				
				mat[i, 0:12] += C * numpy.array(getattr(segments[index], feature))
				index += 1
				
			C = min( (m.duration + m.start - segments[index].start) / m.duration, 1)
			mat[i, 0:12] += C * numpy.array(getattr(segments[index], feature))
	except IndexError, e:
		pass # avoid breaking with index > len(segments)
		
	return ret


#TODO ?
MIN_SEARCH = 4

def make_transition(track1, track2, inter = 10, transition = 10):

	markers1 = getattr(track1.analysis, track1.resampled['rate'])
	markers2 = getattr(track2.analysis, track2.resampled['rate'])

	if len(markers1) < MIN_SEARCH or len(markers2) < MIN_SEARCH:
		return make_crossfade(track1, track2, inter)
	
	mat1 = get_mat_out(track1, transition)
	mat2 = get_mat_in(track2, transition, inter)

	try:
		loc, n, rate1, rate2 = align(track1, track2, mat1, mat2)
	except:
		raise
		print "aligning excepted"
		return make_crossfade(track1, track2, inter)
		
	print "rates: %5.3f %5.3f" % (rate1, rate2)
	print "loc n: %5.3f %5.3f" % (loc, n)

	xm = make_crossmatch(track1, track2, rate1, rate2, loc, n)

	# loc and n are both in terms of potentially upsampled data. 
	# Divide by rate here to get end_crossmatch in terms of the original data.
	end_crossmatch = (loc + n) / rate2
	
	if markers2[-1].start < markers2[end_crossmatch].start + inter + transition:
		inter = max(markers2[-1].start - transition, 0)
		
	# move_cursor sets the cursor properly for subsequent operations, and gives us duration.
	dur, track2.resampled['cursor'] = move_cursor(track2, inter, end_crossmatch)
	print "track 2 cursor at %f" % track2.resampled['cursor']
	print "TODO make sure we skip this on the next run on song A"

	pb = Playback(track2, sum(xm.l2[-1]), dur)
	
	return [xm, pb]

def make_crossmatch(track1, track2, rate1, rate2, loc2, rows):
	markers1 = upsample_list(getattr(track1.analysis, track1.resampled['rate']), rate1)
	markers2 = upsample_list(getattr(track2.analysis, track2.resampled['rate']), rate2)
	
	def to_tuples(l, i, n):
		return [(t.start, t.duration) for t in l[i : i + n]]
	
	start1 = rate1 * (track1.resampled['index'] + track1.resampled['cursor'])
	start2 = loc2 + rate2 * track2.resampled['index'] # loc2 has already been multiplied by rate2

	return Crossmatch((track1, track2), (to_tuples(markers1, start1, rows), to_tuples(markers2, start2, rows)))
	
def upsample_list(l, rate=2):
	""" Upsample lists by a factor of 2."""
	if rate != 2: return l[:]
	# Assume we're an AudioQuantumList.
	def split(x):
		a = deepcopy(x)
		a.duration = x.duration / 2
		b = deepcopy(a)
		b.start = x.start + a.duration
		return a, b
	
	return flatten(map(split, l))

def get_central(analysis, member='segments'):
	""" Returns a tuple: 
		1) copy of the members (e.g. segments) between end_of_fade_in and start_of_fade_out.
		2) the index of the first retained member.
	"""
	def central(s):
		return analysis.end_of_fade_in <= s.start and (s.start + s.duration) < analysis.start_of_fade_out
	
	members = getattr(analysis, member) # this is nicer than data.__dict__[member]
	ret = filter(central, members[:]) 
	index = members.index(ret[0]) if ret else 0
	
	return ret, index

def get_mean_offset(segments, markers):
	if segments == markers:
		return 0
	
	index = 0
	offsets = []
	try:
		for marker in markers:
			while segments[index].start < marker.start + FUSION_INTERVAL:
				offset = abs(marker.start - segments[index].start)
				if offset < FUSION_INTERVAL:
					offsets.append(offset)
				index += 1
	except IndexError, e:
		pass
	
	return numpy.average(offsets) if offsets else AVG_PEAK_OFFSET

# vind matrix voor volgende transitie
def get_mat_out(track, transition):
	cursor = track.resampled['cursor']
	mat = track.resampled['matrix']
	# update cursor location to after the transition
	duration, cursor = move_cursor(track, transition, cursor)
	# output matrix with a proper number of rows, from beginning of transition
	return mat[track.resampled['cursor']:cursor,:]

def average_duration(l):
	return sum([i.duration for i in l]) / float(len(l))

def upsample_matrix(m):
	""" Upsample matrices by a factor of 2."""
	r, c = m.shape
	out = np.zeros((2*r, c), dtype=np.float32)
	for i in xrange(r):
		out[i*2  , :] = m[i, :]
		out[i*2+1, :] = m[i, :]
	return out

# Constrained search between a settled section and a new section.
# Outputs location in mat2 and the number of rows used in the transition.
def align(track1, track2, mat1, mat2):
	# Get the average marker duration.
	marker1 = average_duration(getattr(track1.analysis, track1.resampled['rate'])[track1.resampled['index']:track1.resampled['index']+rows(mat1)])
	marker2 = average_duration(getattr(track2.analysis, track2.resampled['rate'])[track2.resampled['index']:track2.resampled['index']+rows(mat2)])

	def get_adjustment(tr1, tr2):
		"""Update tatum rate if necessary"""
		dist = numpy.log2(tr1 / tr2)
		if  dist < -0.5: return (1, 2)
		elif dist > 0.5: return (2, 1)
		else:            return (1, 1)
	
	rate1, rate2 = get_adjustment(marker1, marker2)
	if rate1 == 2: mat1 = upsample_matrix(mat1)
	if rate2 == 2: mat2 = upsample_matrix(mat2)
	
	# Update sizes.
	rows2 = rows(mat2)
	rows1 = min( rows(mat1), max(rows2 - MIN_SEARCH, 2)) # at least the best of MIN_SEARCH choices
	
	# Search for minimum.
	def dist(i):
		return evaluate_distance(mat1[0:rows1,:], mat2[i:i+rows1,:])
	
	min_loc = min(xrange(rows2 - rows1), key=dist)
	min_val = dist(min_loc)
	
	# Let's make sure track2 ends its transition on a regular tatum.
	if rate2 == 2 and (min_loc + rows1) & 1: 
		rows1 -= 1

	return min_loc, rows1, rate1, rate2
	
# vind matrix voor volgende alignment
# DEZE moet aangepast nog
def get_mat_in(track, transition, inter):
	# search from the start
	cursor = 0
	track.resampled['cursor'] = cursor
	mat = track.resampled['matrix']
	
	# compute search zone by anticipating what's playing after the transition
	marker_end = getattr(track.analysis, track.resampled['rate'])[track.resampled['index'] + rows(mat)].start
	marker_start = getattr(track.analysis, track.resampled['rate'])[track.resampled['index']].start
	search_dur = (marker_end - marker_start) - inter - 2 * transition
	
	if search_dur < 0: 
		return mat[:2,:]
	
	# find what the location is in rows
	duration, cursor = move_cursor(track, search_dur, cursor)
	
	return mat[:cursor,:]

def move_cursor(track, duration, cursor, buf=2):
	dur = 0
	while dur < duration and cursor < rows(track.resampled['matrix']) - buf:
		markers = getattr(track.analysis, track.resampled['rate'])    
		dur += markers[track.resampled['index'] + cursor].duration
		cursor += 1
	return dur, cursor

def make_crossfade(track1, track2, inter):
	markers1 = getattr(track1.analysis, track1.resampled['rate'])    
	start1 = markers1[track1.resampled['index'] + track1.resampled['cursor']].start

	start2 = max((track2.analysis.duration - (inter + 2 * X_FADE)) / 2, 0)
	markers2 = getattr(track2.analysis, track2.resampled['rate'])
	
	duration, track2.resampled['cursor'] = move_cursor(track2, start2+X_FADE+inter, 0)
	dur = markers2[track2.resampled['index'] + track2.resampled['cursor']].start - X_FADE - start2

	xf = Crossfade((track1, track2), (start1, start2), X_FADE)
	pb = Playback(track2, start2 + X_FADE, dur)

	return [xf, pb]


# some utils
def rows(m):
	return m.shape[0]

def flatten(l):
	return [item for pair in l for item in pair]

def evaluate_distance(mat1, mat2):
	return numpy.linalg.norm(mat1.flatten() - mat2.flatten())

if __name__ == "__main__":
	main()

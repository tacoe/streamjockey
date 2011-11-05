import spotimeta
import urllib
import simplejson
from pyechonest import song
from pprint import pprint

metacache = {}
metadata = spotimeta.Metadata(cache=metacache)

class track(object):
	pass

searches = ["juslo fly away original mix", "estroe late night thinking winter depression remix",
			"Luomo the present lover", "Junior Boys Hazel Ewan Pearson House Remix", 
			"don't see the point alex smoke", "fatand50 Estroe phat remix rocco caine"]
tracks = []

print "------------------------- analyzing tracks -------------------------"
for ts in searches:
	t = track()
	t.search = ts
	sp = spotimeta.search_track(ts)
	t.s_artist = sp["result"][0]["artist"]["name"]
	t.s_name   = sp["result"][0]["name"]
	t.s_length = sp["result"][0]["length"]
	t.s_href   = sp["result"][0]["href"]

	#pprint(sp)

	print "Spotify top hit: %s -- %s (%5.2fs) : href %s" % (t.s_artist, t.s_name, t.s_length, t.s_href)
	#echonestresult = song.search(artist=s_artist, title=s_name, buckets=['id:7digital', 'tracks'], limit=True)
	echonestresult = song.search(artist=t.s_artist, title=t.s_name, buckets=['audio_summary'])
	ares = echonestresult[0]
	asum = ares.audio_summary
	print "                 %s -- %s (%5.2fs) @ %3.3f bpm / %d %% energy " % (ares.artist_name, ares.title, asum["duration"], asum["tempo"], asum["energy"] * 100)
	t.tempo = asum["tempo"]
	t.length = asum["duration"]

	t.e_length = asum["duration"]
	tempomatch = t.e_length/t.s_length

	if tempomatch<1.02 and tempomatch>0.98:
		print "  - Lengths match"
	else:
		print "!!! Warning - lengths don't match; expect bad beat matching results"

	analysisurl = asum["analysis_url"]
	analysis = simplejson.load(urllib.urlopen(analysisurl))

	bars = analysis["bars"]
	print "  - has %d bars, first starting at %5.2fs (confidence %d %%)" % (len(bars), bars[0]["start"], bars[0]["confidence"] * 100)
	beats = analysis["beats"]
	print "  - has %d beats, first starting at %5.2fs (confidence %d %%)" % (len(beats), beats[0]["start"], beats[0]["confidence"] * 100)

	t.bars = bars # save bars for later use
	t.goodbar = None
	for threshold in [85.0, 75.0, 50.0, 25.0]:
		for bar in bars:
			if bar["confidence"] > (threshold/100):
				print "  - %d%%+ confidence level found at %5.2fs (%d %%)" % (threshold, bar["start"], bar["confidence"] * 100)
				t.goodbar = bar
				break
	print "\n"
	t.index = len(tracks)
	tracks.append(t)

print "------------------------- constructing mix -------------------------"
prevt = None
xfl = 30.0

# runway is the amount of time left after the crossfade has completed
# !!! crossfade-start needs to snap to a beat in B !!!
for t in tracks:
	if prevt:
		print "MIX # %d" % (t.index)
		print "Joining A [%s] to B [%s]" % (t.s_name, prevt.s_name)
		print "Offset-A        = %05.2f seconds" % prevt.goodbar["start"]
		print "Bridge          = %05.3f bpm to %5.3f bpm" % (t.tempo, prevt.tempo)
		print "B tempo factor  = %05.4fx A tempo" % (t.tempo / prevt.tempo)
		print "Crossfade-len   = %05.2f seconds" % xfl

		# calc match point == crossfade-start-point
		# it's the length minus the crossfade, and the first bar *before* that	
		crossfadestart = prevt.s_length - xfl
		for bar in reversed(prevt.bars):
			if(float(bar["start"]) < crossfadestart):
				crossfadestartcorr = float(bar["start"])
				break;

		print "Crossfade-start = %05.2f seconds (counting from A start; uncorrected is %5.2f)" % (crossfadestartcorr, crossfadestart)
		print "Offset-B        = %05.2f seconds" % float(t.goodbar["start"])
		print "Runway          = %05.2f seconds" % (float(t.s_length) - xfl - float(t.goodbar["start"]))
		print "\n"
	prevt = t

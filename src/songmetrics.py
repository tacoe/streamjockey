import spotimeta
from pyechonest import song
from pprint import pprint

def main():
    metacache = {}
    metadata = spotimeta.Metadata(cache=metacache)
    tracksearches = ["juslo fly away original mix", "estroe late night thinking winter depression remix"]
    for ts in tracksearches:
        sp = spotimeta.search_track(ts)
        s_artist = spotifyresult["result"][0]["artist"]["name"]
        s_name = spotifyresult["result"][0]["name"]
        s_length = spotifyresult["result"][0]["length"]
    print "SPOTIFY CHOICE: %s -- %s (%5.2fs)" % (s_artist, s_name, s_length)
    #echonestresult = song.search(artist=s_artist, title=s_name, buckets=['id:7digital', 'tracks'], limit=True)
    echonestresult = song.search(artist=s_artist, title=s_name, buckets=['audio_summary'])
    ares = echonestresult[0]
    asum = ares.audio_summary
    print "ECHONEST MATCH: %s -- %s (%5.2fs) @ %3.3f bpm / %d %% energy " % (
    ares.artist_name, ares.title, asum["duration"], asum["tempo"], asum["energy"] * 100)
    e_length = asum["duration"]
    tempomatch = e_length / s_length
    if tempomatch < 1.02 and tempomatch > 0.98:
        print ">>> Lengths match - continuing"
    else:
        print "!!! Length match fail: BOO HOO"
    aurl = asum["analysis_url"]

if __name__ == '__main__':
    main()

# NEXT: 
# two tracks
# speed factor
# get analysis
# offset timings

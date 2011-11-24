import flask
import shark
import thread
import time
import collections
import urllib
import urllib2
import mpd
import os

import config

app = flask.Flask(__name__)
app.debug = True
download_queue_lock = thread.allocate_lock()
download_queue = collections.deque()
download_status = "Nothing to see here, move along."
song_cache = {}

s = None

m = mpd.MPDClient()
m.connect("localhost", 6600)

@app.route("/")
def root():
    data = "Song queue status: %s <br /><br />" % download_status
    data += "Song download queue:<br /><br />"
    for song in download_queue:
        data += "(%s) %s - %s<br />" % ("DL" if not song[1] else "DL&Q", song[0].name, song[0].artist)
    
    data += '<br />Song search: <form action="/search" type="GET"><input name="song" /><input type="submit"></form>'
    return data

@app.route("/search")
def search():
    song = flask.request.args.get("song")
    songs = s.search_songs(song)
    for song in songs:
        song_cache[song.song_id] = song
    return 'dl - download; dl&q - download and queue to MPD<br /><br />' + '<br />'.join(['<a href="/dl/%s">dl</a> | <a href="/dlq/%s">dl&q</a> %s - %s (%s)' % (song.song_id, song.song_id, song.artist, song.name, song.album) for song in songs])

@app.route("/dl/<int:song_id>")
def dl(song_id):
    song = song_cache[song_id]
    data = song.get_download_data()
    download_queue.append((song, False))
    return 'downloading... <a href="/">go to queue</a> <br /><br />(%s; %s)' % data

@app.route("/dlq/<int:song_id>")
def dlq(song_id):
    song = song_cache[song_id]
    data = song.get_download_data()
    download_queue.append((song, True))
    return 'downloading... <a href="/">go to queue</a> <br /><br />(%s; %s)' % data

def worker():
    print "[i] starting worker..."
    while 1:
        with download_queue_lock:
            if len(download_queue) > 0:
                d = download_queue.popleft()
                song = d[0]
                should_queue = d[1]
                dl_data = song.get_download_data()
                
                global download_status
                
                r = urllib2.Request(dl_data[0], dl_data[1])
                h = urllib2.urlopen(r)
                headers = h.info()

                f = open("%s/%s/%s - %s.mp3" % (config.MPD_DIR, config.DL_DIR, song.artist, song.name), "wb")
                size = int(headers["Content-Length"])

                print "[i] File size: %i kb" % (size / 1024)
                done = 0
                while 1:
                    download_status = "Downloading %s - %s.mp3...% 4i/% 4ikb (% 3i%%) " % (song.artist, song.name, done/1024, size/1024, done * 100.0/size)
                    
                    block = h.read(8096)
                    if block == "":
                        break
                    f.write(block)
                    done += 8096
                os.chmod("%s/%s/%s - %s.mp3" % (config.MPD_DIR, config.DL_DIR, song.artist, song.name), 0777)
                if should_queue:
                    download_status = "Queued %s - %s.mp3 to MPD..." % (song.artist, song.name)
                    try:
                        m.update("%s/%s - %s.mp3" % (config.DL_DIR, song.artist, song.name))
                        time.sleep(10)
	                m.add("%s/%s - %s.mp3" % (config.DL_DIR, song.artist, song.name))
                    except Exception as e:
                        time.sleep(10)
                        m.add("%s/%s - %s.mp3" % (config.DL_DIR, song.artist, song.name))
                        print "COULD NOT QUEUE '%s/%s - %s.mp3': %s" % (config.DL_DIR, song.artist, song.name, e)
                    m.play()
                else:
                    download_status = "Done downloading."
        time.sleep(2)

if __name__ == "__main__":
    global s
    s = shark.GroovesharkClient()
    s.connect()
    thread.start_new_thread(worker, ())
    app.run(host="0.0.0.0")

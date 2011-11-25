#!/usr/bin/env python2

# This file is part of pythonshark.
#
# pythonshark is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pythonshark is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pythonshark.  If not, see <http://www.gnu.org/licenses/>.

import urllib
import urllib2
import cookielib
import os
import random
import time
import json
import hashlib
import uuid
import gzip
import io
import sys

import config


class GroovesharkProtocolException(Exception):
    def __init__(self, error):
        self.error = error

    def __str__(self):
        return self.error

class GroovesharkSong(object):
    def __init__(self, client, data):
        self.client = client
        self.song_id = data["SongID"]
        self.artist = data["ArtistName"]
        self.name = data["SongName"]
        self.album = data["AlbumName"]
        self.score = data["Score"]

    def __str__(self):
        return "%s - %s" % (self.artist, self.name)

    def get_download_data(self):
        return self.client.get_song_download_data(self.song_id)

class GroovesharkClient(object):
    def __init__(self):
        self.cookie_jar = cookielib.LWPCookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie_jar))
        urllib2.install_opener(opener)

        self.uuid = UUID = str(uuid.uuid4()).upper()
        self.session_id = None
        self.token = None

    def pillow_talk(self, url, data=None, additional_headers=None):
        """
        Make Grooveshark servers feel warm and fuzzy inside.
        """
        if not additional_headers:
            additional_headers = {}
        r = urllib2.Request(url, data, dict(config.HEADERS.items() + additional_headers.items()))
        response = urllib2.urlopen(r)
        return response.read()

    def menstruate(self, _time=200, delta=50):
        """
        Wait some time to simulate real browser delay,
        """
        t = random.randint(_time - delta, _time + delta)
        time.sleep(t * 0.001)

    def connect(self):
        """
        Connect to the main grooveshrk web app server, and get a PHP session ID.
        """
        self.session_id = None
        self.pillow_talk("http://grooveshark.com")
        for cookie in self.cookie_jar:
            if cookie.name == "PHPSESSID":
                self.session_id = cookie.value

        if not self.session_id :
            raise GroovesharkProtocolException("Could not get session id.")

    def do_json_request(self, method, data, referer=config.REFERER):
        """
        Execute an RPC JSON request to /more.php.
        """
        d = self.pillow_talk(config.JSONURL % method, json.dumps(data), {"Referer": referer, "Origin": config.ORIGIN, "content-type": "application/json"})
        g = gzip.GzipFile(fileobj=io.BytesIO(d), mode="rb")
        du = g.read()
        return json.loads(du)


    @property
    def secretkey(self):
        """
        Apparently Grooveshark's idea of 'secret' is an MD5 hash of the PHP session ID...
        I have no idea why you would want to hash it, as if anyone actaully does intercept traffic, the PHP session ID is stored in cleartext in a cookie. Whatever.
        """
        if not self.session_id:
            raise GroovesharkProtocolException("No session ID - did you connect?")

        return hashlib.md5(self.session_id).hexdigest()

    def get_hashtoken(self, method, alternative=None):
        """
        Do Grooveshark's weird token encryption thing.
        """
        if not self.token:
            self.get_communication_token()
            if not self.token:
                raise GroovesharkProtocolException("Could not retrieve communication token.")
        if alternative == None:
            if method in config.TOKEN_ALTERNATIVE:
                alternative = True
            else:
                alternative = False

        salt = ''.join(["%02x" % random.randint(0, 255) for _ in range(3)])
        password = config.PASSWORD1 if alternative == False else config.PASSWORD0
        return salt + hashlib.sha1("%s:%s:%s:%s" % (method, self.token, password, salt)).hexdigest()

    def get_header(self, client="htmlshark"):
        """
        Generate a JSON request header.
        """

        if not self.session_id:
            raise GroovesharkProtocolException("No session ID - did you connect?")

        return {
            "country": config.COUNTRY_DATA,
            "clientRevision": config.CLIENT_REVISION,
            "client": client,
            "session": self.session_id,
            "uuid": self.uuid,
            "privacy": 0
        }

    def get_communication_token(self):
        """
        Get the token required for communication.
        """
        data = {
            "method": "getCommunicationToken",
            "parameters": {
                "secretKey": self.secretkey
            },
            "header": self.get_header(),
        }
        d = self.do_json_request("getCommunicationToken", data)
        self.token = d["result"]

    def run_method(self, method, parameters, client="htmlshark", fail_on_token=False):
        """
        Run an API method.
        """
        data = {
            "method": method,
            "parameters": parameters,
            "header": dict(self.get_header(client).items() + {"token": self.get_hashtoken(method)}.items())
        }
        d = self.do_json_request(method, data)
        if "fault" in d:
            fault = d["fault"]["message"]
            if fault == "invalid token":
                if fail_on_token:
                    raise Exception("Could not get communication token!")
                print "[i] Communication token expired, sleeping."
                self.get_communication_token()
                return self.run_method(self, method, parameters, client, True)
            else:
                raise Exception("Could not parse fault! %s" % str(fault))
        try:
            return d["result"]
        except:
            raise Exception("Error while parsing return from JSON: %s" % str(d))

    def search_songs(self, query):
        songs_raw = self.run_method("getResultsFromSearch", {
            "query": query,
            "type": "Songs",
            "guts": 0,
            "ppOverride" : ""
        })["result"]

        songs = []
        for song_raw in songs_raw:
            song = GroovesharkSong(self, song_raw)
            songs.append(song)
        return songs

    def get_song_download_data(self, song_id):
        song_source = self.run_method("getStreamKeysFromSongIDs", {
            "country": self.get_header()["country"],
            "prefetch": False,
            "mobile": False,
            "songIDs": [song_id, ],
        }, client="jsqueue")

        host = song_source[str(song_id)]["ip"]
        key = song_source[str(song_id)]["streamKey"]

        return ("http://%s/stream.php" % host, "streamKey=%s" % key)

if __name__ == "__main__":
    c = GroovesharkClient()
    c.connect()
    songs = c.search_songs("catgroove")
    for song in songs:
        print song.name, song.artist, song.album, song.score

    print songs[0].get_download_data()

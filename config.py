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

MPD_DIR = "/home/q3k/gsmusic"
DL_DIR = "Grooveshark Music"

USERAGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/15.0.874.106 Safari/535.2"
HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.3",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Accept-Language": "en-US,en;q=0.8",
    "Connection": "keep-alive",
    "Host": "grooveshark.com",
    "User-Agent": USERAGENT,
}

# These change from time to time...
PASSWORD0 = "imOnAHorse"
PASSWORD1 = "theTicketsAreNowDiamonds"

# No idea what this is.
COUNTRY_DATA = {
    "IPR": "10632",
    "CC3": "35184372088832",
    "CC2": "0",
    "CC1": "0",
    "ID": "174",
    "CC4": "0"
}

CLIENT_REVISION = "20110906"

REFERER = "https://grooveshark.com/JSQueue.swf?20111111.113"
ORIGIN = "https://grooveshark.com"

JSONURL = "https://grooveshark.com/more.php?%s"

TOKEN_ALTERNATIVE = [
    "getQueueSongListFromSongIDs",
    "getResultsFromSearch",
]

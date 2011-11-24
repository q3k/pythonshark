MPD_DIR = "/nas/Music"
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

REFERER = "http://grooveshark.com/JSQueue.swf?20111111.113"
ORIGIN = "http://grooveshark.com"

JSONURL = "http://grooveshark.com/more.php?%s"

TOKEN_ALTERNATIVE = [
    "getQueueSongListFromSongIDs",
    "getResultsFromSearch",
]

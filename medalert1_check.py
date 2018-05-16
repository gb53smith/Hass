'''
Checks that medalert1 Home Assistant is running.
'''
from urllib.request import urlopen
from urllib.error import URLError
try:
    HTML = urlopen("https://medalert1.duckdns.org:8123")
    if "Home Assistant" in str(HTML.read()):
        print("Up")
    else:
        print("Down")
except URLError:
    print("FIX")

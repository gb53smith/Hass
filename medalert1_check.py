'''
Checks that medalert1 Home Assistant is running.
Tolerant to 1 error in 3 tries.
'''
from urllib.request import urlopen
from urllib.error import URLError
count = 0
try:
    HTML = urlopen("https://medalert1.duckdns.org:8123")
    if "Home Assistant" in str(HTML.read()):
        count += 1
except URLError:
    pass
try:
    HTML = urlopen("https://medalert1.duckdns.org:8123")
    if "Home Assistant" in str(HTML.read()):
        count += 1
except URLError:
    pass
try:
    HTML = urlopen("https://medalert1.duckdns.org:8123")
    if "Home Assistant" in str(HTML.read()):
        count += 1
except URLError:
    pass
if count >= 2 :
    print("Up" + str(count))
else:
    print("FIX")
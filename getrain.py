#!/usr/bin/python3.4

import urllib.request
import urllib.parse 
import re 
import xml.etree.ElementTree as ET 
from urllib import request 

#Now I can make the API call.  
id_request = urllib.request.urlopen('http://dd.weatheroffice.ec.gc.ca/citypage_weather/xml/BC/s0000141_e.xml')

#Let's now read this baby in XML format!
id_pubmed = id_request.read()
root = ET.fromstring(id_pubmed)

# Find the data I want
#elements are numbered with integers.  Uncomment to see order of elements
#for child in root:
	#print(child.tag,child.attrib)
#This is yesterday's rainfall in mm.
print(root[8][2].text)



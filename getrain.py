'''
Reads weather report from gc.ca website in xml format.  Extracts
and returns yesterday's rainfall.
'''
import xml.etree.ElementTree as ET
from urllib import request

# Now I can make the API call.
id_request = request.urlopen\
    ('http://dd.weatheroffice.ec.gc.ca/citypage_weather/xml/BC/s0000141_e.xml')

#Let's now read this baby in XML format!
id_pubmed = id_request.read()
root = ET.fromstring(id_pubmed)

# Find the data I want
# elements are numbered with integers.  Uncomment to see order of elements
# i = 0
# for child in root:
    # print(i,child.tag,child.attrib)
    # i += 1
    
#This is yesterday's rainfall in mm.
rain = root[8][2].text
# Report 0.0 if no data found
if rain == None:
    print('0.0')
else:
    # Report 0.1 mm if trace is reported
    if rain[0].isdigit():
        print(rain)
    else:
        print('0.1')


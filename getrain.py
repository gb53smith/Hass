'''
Reads weather report from weather.gc.ca website in html format.  
Extracts and returns yesterday's rainfall.
It relies on a particular HTML format so it can break.
'''
import re
from urllib import request

# Now I can make the API call.
id_request = request.urlopen\
    ('https://weather.gc.ca/city/pages/bc-74_metric_e.html')

html_data = id_request.read().decode('utf-8')  # Need to convert bytes to string

# Data is spread over three lines so \n is required.
m = re.search("(Total Precipitation.*\n.*\n.*millimetres)", html_data)

if m:
    splitdata = m.group(1).split('">')
    rain = splitdata[1].split('<')[0].strip()
    # Report 0.1 mm if trace is reported
    if rain[0].isdigit():
        print(rain)
    else:
        print('0.1')
else:
    print('0.0')

#!/usr/bin/python3.4

import urllib.request
import json
owm_url = "http://api.openweathermap.org/data/2.5/weather?id=5911606&appid=6ba0b719372607e5a99106e08e877a80"

response = urllib.request.urlopen(owm_url)
content = response.read()
json_data = json.loads(content.decode("utf8"))

json_dt = json_data['dt'] #Unix time
json_temp = json_data['main']['temp']
if '"rain"' in json_data:
	json_rain = json_data['rain']['3h']
	print(json_dt,json_temp,json_rain)
else:
	print(json_dt,json_temp,0)
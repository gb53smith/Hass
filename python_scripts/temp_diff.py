
'''
Replaced by platform: filter
Date:  April 16, 2020

Versions used: HA108.0, HassOS and Raspberry PI 3 B

Description:
This Python Script to accumulates sensor.temp_dff every 5 minutes and 
calculates its average over one hour.

Uses:
sensor.temp_diff - inside - outside temperature difference, measured every 5 minutes.
input_number.temp_diff_accum  - accumulation of 12 sensor.temp_diff ie over one hour.
input_number.hour_diff - records average of hourly accumulation.

Instructions:
1. Python Script setup
   1.1 Create /config/python_scripts directory and copy this file to it.
   1.2 Add this line to configuration.yaml
       python_script:       
 
2. Add these input_number entities to configuration.yaml

  temp_diff_accum:
    min: 0
    max: 1000
    step: 0.1
    
  hour_diff:
    min: -20
    max: 100
    step: 0.1
    mode: box

  daily_temp_diff:
    min: -20
    max: 100
    step: 0.1
    mode: box  

        
3.  Add this automation to automations.yaml
    * items are your choosing but must match your sensor/input_number names above

  - alias: Hourly Temperature Difference
    initial_state: True
    trigger:
      - platform: time_pattern
        minutes: '/5'      
    action:
      service: python_script.temp_diff
      data:
        temp_diff: temp_diff*
        temp_diff_accum: temp_diff_accum*
        hour_diff: hour_diff*

4. Use the history_graph lovelace card to display the result.
   

'''
#logger.warning("Got to temp_diff")
#Get data parameters from service call

data_temp_diff = data.get('temp_diff', '0')
data_temp_diff_accum = data.get('temp_diff_accum', '0')
data_hour_diff = data.get('hour_diff', '0')

if data_temp_diff != '0':
	sensor_temp_diff = "sensor." + data_temp_diff
else:
	logger.error("Energy script missing temp_diff data.")
       
if data_temp_diff_accum != '0':
	input_number_temp_diff_accum = "input_number." + data_temp_diff_accum
else:
	logger.error("Energy script missing temp_diff_accum data.")

if data_hour_diff != '0':
	input_number_hour_diff = "input_number." + data_hour_diff
else:
	logger.error("Energy script missing hour_diff data.")
    
time = datetime.datetime.now()
time_sec = time.second
time_min = time.minute
timestamp = time.timestamp()

# Get power unit and use to set the units for the other sensors used.
temp_attr = hass.states.get(sensor_temp_diff).attributes
temp_unit = temp_attr['unit_of_measurement']
temp_diff = float(hass.states.get(sensor_temp_diff).state)
temp_diff_accum = float(hass.states.get(input_number_temp_diff_accum).state)

# Needed here for debug
average = 0

#Transfer average difference calculation to input_number_hour_diff
#Clear temp_diff accumulation at start of interval.

if time_sec == 0 and time_min == 0:
    temp_diff_accum = temp_diff_accum + temp_diff
    average = round((temp_diff_accum / 12), 1)
    hass.states.set(input_number_hour_diff, average, {"unit_of_measurement": temp_unit}) 
    hass.states.set(input_number_temp_diff_accum, 0, {"unit_of_measurement": temp_unit})
    temp_diff_accum = 0
else:
    temp_diff_accum = round(temp_diff_accum + temp_diff, 1)
    hass.states.set(input_number_temp_diff_accum, temp_diff_accum, {"unit_of_measurement": temp_unit}) 


#logger.warning("time_min = {} time_sec = {} temp_diff = {} temp_diff_accum = {} average = {}".format(time_min, time_sec,temp_diff,temp_diff_accum,average))


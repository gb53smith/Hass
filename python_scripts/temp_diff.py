
'''
Date:  Feb. 12, 2019

Versions used: HA87.0, HassOS and Raspberry PI 3 B

Description:
This Python Script to accumulates sensor.temp_dff every 5 minutes and 
calculates its average over one hour.

Uses:
sensor.temp_diff
sensor.temp_diff_accum
sensor.hour_diff

Instructions:
1. Python Script setup
   1.1 Create /config/python_scripts directory and copy this file to it.
   1.2 Add this line to configuration.yaml
       python_scripts:
       
2. Add these sensors to sensors.yaml

  - platform: template
    sensors:
      temp_diff_accum:
        value_template: '0'

  - platform: template
    sensors:
      hour_diff_accum:
        value_template: '0'

        
3.  Add this automation to automations.yaml
    * items are your choosing but must match your sensor names above
    sensor.power_test is the input power sensor in this example

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

5. Use the Statistics Sensor to average hourly temperature difference over longer periods.  (Not tried yet)    

'''
#logger.warning("Got to to temp_diff")
#Get data parameters from service call

data_temp_diff = data.get('temp_diff', '0')
data_temp_diff_accum = data.get('temp_diff_accum', '0')
data_hour_diff = data.get('hour_diff', '0')

if data_temp_diff != '0':
	sensor_temp_diff = "sensor." + data_temp_diff
else:
	logger.error("Energy script missing temp_diff data.")
       
if data_temp_diff_accum != '0':
	sensor_temp_diff_accum = "sensor." + data_temp_diff_accum
else:
	logger.error("Energy script missing temp_diff_accum data.")

if data_hour_diff != '0':
	sensor_hour_diff = "sensor." + data_hour_diff
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
temp_diff_accum = float(hass.states.get(sensor_temp_diff_accum).state)

# logger.warning("temp_diff = {}".format(temp_diff))
# logger.warning("temp_diff_accum = {}".format(temp_diff_accum))
# logger.warning("time_min = {}".format(time_min))
# logger.warning("time_sec = {}".format(time_sec))

#Transfer average difference calculation to sensor_hour_diff
#Clear temp_diff accumulation at start of interval.

if time_sec == 0 and time_min == 0:
    temp_diff_accum = temp_diff_accum + temp_diff
    average = round((temp_diff_accum / 12), 1)
    hass.states.set(sensor_hour_diff, average, {"unit_of_measurement": temp_unit}) 
    hass.states.set(sensor_temp_diff_accum, 0, {"unit_of_measurement": temp_unit})
else:
    temp_diff_accum = temp_diff_accum + temp_diff
    hass.states.set(sensor_temp_diff_accum, temp_diff_accum, {"unit_of_measurement": temp_unit}) 




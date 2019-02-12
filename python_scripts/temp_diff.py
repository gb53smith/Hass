
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

#Get data paramters from service call

temp_diff = data.get('temp_diff', '0')
temp_diff_accum = data.get('temp_diff_accum', '0')
hour_diff = data.get('hour_diff', '0')

if temp_diff != '0':
	sensor_temp_diff = "sensor." + temp_diff
else:
	logger.error("Energy script missing temp_diff data.")
       
if temp_diff_accum != '0':
	sensor_temp_diff_accum = "sensor." + temp_diff_accum
else:
	logger.error("Energy script missing temp_diff_accum data.")

if hour_diff != '0':
	sensor_hour_diff = "sensor." + hour_diff
else:
	logger.error("Energy script missing hour_diff data.")
    
time = datetime.datetime.now()
time_sec = time.second
time_min = time.minute
timestamp = time.timestamp()

# Get power unit and use to set the units for the other sensors used.
temp_attr = hass.states.get(sensor_temp_diff).attributes
temp_unit = temp_attr['unit_of_measurement']
    
temp_diff_accum = float(hass.states.get(sensor_temp_diff_accum).state)

# #Clear energy accumulation at start of interval.
# #Transfer sum of energy from previous period to the hourly log
# if time_sec == 0 and time_min == 0:
    # #logger.warning("Start of Window")
    # last_power_state = hass.states.get(sensor_last_power)
    # last_power = float(last_power_state.state)
    # ##logger.warning("Last Power = {}".format(last_power))
    # last_power_change = last_power_state.last_changed.timestamp()
    # delta_time = timestamp - last_power_change
    # ##logger.warning("Time since last power change = {}".format(delta_time))    
    # #Add remnant from last window
    # if last_power > 0:
        # remnant = last_power * delta_time / WINDOW_SIZE
        # energy_accum = energy_accum + remnant
    # #refresh last_power to change the timestamp to beginning of window period
    # hass.states.set(sensor_last_power, (last_power + 0.1), {"unit_of_measurement": power_unit})
    # hass.states.set(sensor_last_power, last_power, {"unit_of_measurement": power_unit})
    # hass.states.set(sensor_hourly_energy, energy_accum, {"unit_of_measurement": power_unit})        
    # hass.states.set(sensor_energy_accum, 0, {"unit_of_measurement": power_unit})
    
    # #logger.warning("Last Window energy_accum = {}".format(energy_accum))    
# else:
    # #logger.warning("Within Window")
    # #Need to get last_power_state since it is reset at start of window
    # last_power_state = hass.states.get(sensor_last_power)
    # last_power = float(last_power_state.state)
    # ##logger.warning("Last Power = {}".format(last_power))
    # last_power_change = last_power_state.last_changed.timestamp()
    
    # power_state = hass.states.get(sensor_power)
    # power = float(power_state.state)

    # ##logger.warning("Power Test = {}".format(power))
    # power_change = power_state.last_changed.timestamp()
    # ##logger.warning("power_change = {}".format(power_change))

    # delta_time = power_change - last_power_change
    # #logger.warning("delta_time = {}".format(delta_time))

    # #Convert to energy per hour
    # delta_energy = delta_time * last_power / WINDOW_SIZE

    # ##logger.warning("energy_accum = {}".format(energy_accum))
    # #logger.warning("delta_energy = {}".format(delta_energy))
    # energy_accum = energy_accum + delta_energy
    # hass.states.set(sensor_energy_accum, energy_accum, {"unit_of_measurement": energy_unit})
    # #logger.warning("energy_accum next = {}".format(energy_accum))

    # hass.states.set(sensor_last_power, power, {"unit_of_measurement": power_unit})



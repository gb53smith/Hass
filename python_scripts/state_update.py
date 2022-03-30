
'''
Date:  Feb. 24, 2019

Versions used: HA88.1, HassOS and Raspberry PI 3 B

Description:
This Python Script updates a sensor state to new timestamp

Instructions:
1. Python Script setup
   1.1 Create /config/python_scripts directory and copy this file to it.
   1.2 Add this line to configuration.yaml
       python_script:
        
2.  Add this automation to automations.yaml
    * items are your choosing but must match your sensor names above
    sensor.power_test is the input power sensor in this example

  - alias: force power change
    initial_state: true
    trigger:
      platform: time_pattern
      minutes: 59
      seconds: 59
    action:
      service: python_script.state_update
      data: 
        sensor: power_test 

'''

sensor = data.get('sensor', '0')

if sensor != '0':
    sensor_power = "sensor." + sensor
    power_state = hass.states.get(sensor_power)
    power = float(power_state.state)
    if power > 0:
        power_attr = hass.states.get(sensor_power).attributes
        hass.states.set(sensor_power, (power + 0.1), power_attr)
        hass.states.set(sensor_power, power, power_attr)   
else:
	logger.error("Energy script missing sensor data.")



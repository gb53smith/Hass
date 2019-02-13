
'''
Date:  Feb. 13, 2019

Versions used: HA87.0, HassOS and Raspberry PI 3 B

Description:
This Python Script converts histograph type power to energy accumulation over one hour
It needs four sensors to be passed as data values:  power, last_power, energy_accum and hourly_energy

Instructions:
1. Python Script setup
   1.1 Create /config/python_scripts directory and copy this file to it.
   1.2 Add this line to configuration.yaml
       python_scripts:
       
2. Add these sensors to sensors.yaml

# Units derived from the input power sensor
  - platform: template
    sensors:
      last_power:
        value_template: '0'
        
  - platform: template
    sensors:
      energy_accum:
        value_template: '0'

  - platform: template
    sensors:
      hourly_energy:
        value_template: ''
        
3.  Add this automation to automations.yaml
    * items are your choosing but must match your sensor names above
    sensor.power_test is the input power sensor in this example

  - alias: Hourly Energy
    initial_state: True
    trigger:
      - platform: state
        entity_id: sensor.power_test*
      - platform: time_pattern
        hours: '/1'      
    action:
      service: python_script.energy
      data:
        power: power_test*
        last_power: last_power*
        energy_accum: energy_accum*
        hourly_energy: hourly_energy*

4. Use the history_graph lovelace card to display the result.

5. Use the Statistics Sensor to average hourly energy over longer periods.  (Not tried yet)    

'''

#logger.warning("Got to energy")
WINDOW_SIZE = 60*60

power = data.get('power', '0')
last_power = data.get('last_power', '0')
energy_accum = data.get('energy_accum', '0')
hourly_energy = data.get('hourly_energy', '0')

if power != '0':
	sensor_power = "sensor." + power
else:
	logger.error("Energy script missing power data.")
    
if last_power != '0':
	sensor_last_power = "sensor." + last_power
else:
	logger.error("Energy script missing last_power data.")
    
if energy_accum != '0':
	sensor_energy_accum = "sensor." + energy_accum
else:
	logger.error("Energy script missing energy_accum data.")

if hourly_energy != '0':
	sensor_hourly_energy = "sensor." + hourly_energy
else:
	logger.error("Energy script missing hourly_energy data.")
    
time = datetime.datetime.now()
time_sec = time.second
time_min = time.minute
timestamp = time.timestamp()

# Get power unit and use to set the units for the other sensors used.
power_attr = hass.states.get(sensor_power).attributes
power_unit = power_attr['unit_of_measurement']
energy_unit = power_unit + 'h'
    
energy_accum_state = hass.states.get(sensor_energy_accum)
energy_accum = float(energy_accum_state.state)

#Clear energy accumulation at start of interval.
#Transfer sum of energy from previous period to the hourly log
if time_sec == 0 and time_min == 0:
    #logger.warning("Start of Window")
    last_power_state = hass.states.get(sensor_last_power)
    last_power = float(last_power_state.state)
    ##logger.warning("Last Power = {}".format(last_power))
    last_power_change = last_power_state.last_changed.timestamp()
    delta_time = timestamp - last_power_change
    ##logger.warning("Time since last power change = {}".format(delta_time))    
    #Add remnant from last window
    if last_power > 0:
        remnant = last_power * delta_time / WINDOW_SIZE
        energy_accum = energy_accum + remnant
    #refresh last_power to change the timestamp to beginning of window period
    hass.states.set(sensor_last_power, (last_power + 0.1), {"unit_of_measurement": power_unit})
    hass.states.set(sensor_last_power, last_power, {"unit_of_measurement": power_unit})
    hass.states.set(sensor_hourly_energy, round(energy_accum, 2), {"unit_of_measurement": energy_unit})        
    hass.states.set(sensor_energy_accum, 0, {"unit_of_measurement": energy_unit})
    
    #logger.warning("Last Window energy_accum = {}".format(energy_accum))    
else:
    #logger.warning("Within Window")
    #Need to get last_power_state since it is reset at start of window
    last_power_state = hass.states.get(sensor_last_power)
    last_power = float(last_power_state.state)
    ##logger.warning("Last Power = {}".format(last_power))
    last_power_change = last_power_state.last_changed.timestamp()
    
    power_state = hass.states.get(sensor_power)
    power = float(power_state.state)

    ##logger.warning("Power Test = {}".format(power))
    power_change = power_state.last_changed.timestamp()
    ##logger.warning("power_change = {}".format(power_change))

    delta_time = power_change - last_power_change
    #logger.warning("delta_time = {}".format(delta_time))

    #Convert to energy per hour
    delta_energy = delta_time * last_power / WINDOW_SIZE

    ##logger.warning("energy_accum = {}".format(energy_accum))
    #logger.warning("delta_energy = {}".format(delta_energy))
    energy_accum = energy_accum + delta_energy
    hass.states.set(sensor_energy_accum, energy_accum, {"unit_of_measurement": energy_unit})
    #logger.warning("energy_accum next = {}".format(energy_accum))

    hass.states.set(sensor_last_power, power, {"unit_of_measurement": power_unit})



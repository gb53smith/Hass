
'''
Date:  April 16, 2020

Versions used: HA108.0, HassOS and Raspberry PI 3 B

Description:
This Python Script converts histograph type power to energy accumulation over one hour
It needs three input_number entities to be passed as data values:  power, last_power and hourly_energy
input_number.energy_accum is used to accumulate the energy calculation over an hoour period.
input_number entities restore the last known value on HA restart.  Sensors do not restore.

Instructions:
1. Python Script setup
   1.1 Create /config/python_scripts directory and copy this file to it.
   1.2 Add this line to configuration.yaml
       python_scripts:    
        
2.  Add these input_number entity to configuration.yaml
    input_number used because their values are restored after HA restarts.
    
    furnace_power:
      name: Furnace Power
      min: 0
      max: 50
      step: 0.1
      unit_of_measurement: 'kW'
    
    last_power:
      min: 0
      max: 100
      step: 0.1
      mode: box
      
    energy_accum:
      min: 0
      max: 1000
      step: 0.1 
      
    hourly_energy:
      min: 0
      max: 100
      step: 0.1
      mode: box 
        
3.  Add this automation to automations.yaml
    * items are your choosing but must match your sensor names above
    input_number.furnace_power is the input power sensor in this example

  - alias: Hourly Energy
    initial_state: True
    trigger:
      - platform: state
        entity_id: input_number.furnace_power*
      - platform: time_pattern
        hours: '/1'      
    action:
      service: python_script.energy
      data:
        power: furnace_power*
        last_power: last_power*
        energy_accum: energy_accum*
        hourly_energy: hourly_energy*

4. Use the history_graph lovelace card to display the result.

5. Use the Statistics Sensor to average hourly energy over longer periods.  (Not tried yet)

6. Save database size by not recording the last power and energy accumulator values.  
   Only the last value needed by the algorithm to calculate the hourly energy.
   The last value of all sensors is recorded in the database.  

'''

#logger.warning("Got to energy")
WINDOW_SIZE = 60*60

power = data.get('power', '0')
last_power = data.get('last_power', '0')
energy_accum = data.get('energy_accum', '0')
hourly_energy = data.get('hourly_energy', '0')

if power != '0':
	input_number_power = "input_number." + power
else:
	logger.error("Energy script missing power data.")
    
if last_power != '0':
	input_number_last_power = "input_number." + last_power
else:
	logger.error("Energy script missing last_power data.")
    
if energy_accum != '0':
	input_number_energy_acum = "input_number." + energy_accum
else:
	logger.error("Energy script missing energy_accum data.")

if hourly_energy != '0':
	input_number_hourly_energy = "input_number." + hourly_energy
else:
	logger.error("Energy script missing hourly_energy data.")
    
time = datetime.datetime.now()
time_sec = time.second
time_min = time.minute
timestamp = time.timestamp()

# Get power unit and use to set the units for the other sensors used.
power_attr = hass.states.get(input_number_power).attributes
power_unit = power_attr['unit_of_measurement']
energy_unit = power_unit + 'h'
    
energy_accum_state = hass.states.get(input_number_energy_acum)
energy_accum = float(energy_accum_state.state)

#Clear energy accumulation at start of interval.
#Transfer sum of energy from previous period to the hourly log
if time_sec == 0 and time_min == 0:
    #logger.warning("Start of Window")
    last_power_state = hass.states.get(input_number_last_power)
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
        hass.states.set(input_number_last_power, (last_power + 0.1), {"unit_of_measurement": power_unit})
        hass.states.set(input_number_last_power, last_power, {"unit_of_measurement": power_unit})
    #Update hourly energy
    hass.states.set(input_number_hourly_energy, round(energy_accum, 1), {"unit_of_measurement": energy_unit})        
    # Clear energy accumulation for the start of the next window
    hass.states.set(input_number_energy_acum, 0, {"unit_of_measurement": energy_unit})
    #logger.warning("Last Window energy_accum = {}".format(energy_accum))    
else:
    #logger.warning("Within Window")
    power_state = hass.states.get(input_number_power)
    power = float(power_state.state)
 
    #Need to get last_power_state since it is reset at start of window
    last_power_state = hass.states.get(input_number_last_power)
    last_power = float(last_power_state.state)
    #No new energy if last power was zero.
    if last_power > 0:
        ##logger.warning("Last Power = {}".format(last_power))
        last_power_change = last_power_state.last_changed.timestamp()

        ##logger.warning("Power Test = {}".format(power))
        power_change = power_state.last_changed.timestamp()
        ##logger.warning("power_change = {}".format(power_change))

        delta_time = power_change - last_power_change
        #logger.warning("delta_time = {}".format(delta_time))

        #Convert to energy per hour
        delta_energy = delta_time * last_power / WINDOW_SIZE

        ##logger.warning("energy_accum = {}".format(energy_accum))
        #logger.warning("delta_energy = {}".format(delta_energy))
        energy_accum = round(energy_accum + delta_energy,1)
        hass.states.set(input_number_energy_acum, energy_accum, {"unit_of_measurement": energy_unit})
        #logger.warning("energy_accum next = {}".format(energy_accum))
    
    #Update last_power with new power
    hass.states.set(input_number_last_power, power, {"unit_of_measurement": power_unit})



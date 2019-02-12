# Python Script to Convert histograph type power to energy over one hour
# Needs four sensors to be passed as data values:  power, last_power, energy_accum and hourly_energy

#logger.warning("Got to GBS energy")
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
    #refresh last_power to change the timestamp, last_power never exceeds 1000
    hass.states.set(sensor_last_power, 1000, {"unit_of_measurement": "kW"})
    hass.states.set(sensor_last_power, last_power, {"unit_of_measurement": "kW"})
    hass.states.set(sensor_hourly_energy, energy_accum, {"unit_of_measurement": "kW"})        
    hass.states.set(sensor_energy_accum, 0, {"unit_of_measurement": "kW"})
    
    #logger.warning("Last Window energy_accum = {}".format(energy_accum))    
else:
    #logger.warning("Within Window")
    #Need to get last_power_state since it is reset at start of window
    last_power_state = hass.states.get(sensor_last_power)
    last_power = float(last_power_state.state)
    ##logger.warning("Last Power = {}".format(last_power))
    last_power_change = last_power_state.last_changed.timestamp()
    
    power_test_state = hass.states.get(sensor_power)
    power = float(power_test_state.state)
    ##logger.warning("Power Test = {}".format(power))
    power_change = power_test_state.last_changed.timestamp()
    ##logger.warning("power_change = {}".format(power_change))

    delta_time = power_change - last_power_change
    #logger.warning("delta_time = {}".format(delta_time))

    #Convert to kWm
    delta_energy = delta_time * last_power / WINDOW_SIZE

    ##logger.warning("energy_accum = {}".format(energy_accum))
    #logger.warning("delta_energy = {}".format(delta_energy))
    energy_accum = energy_accum + delta_energy
    hass.states.set(sensor_energy_accum, energy_accum, {"unit_of_measurement": "kWm"})
    #logger.warning("energy_accum next = {}".format(energy_accum))

    hass.states.set(sensor_last_power, power, {"unit_of_measurement": "kW"})



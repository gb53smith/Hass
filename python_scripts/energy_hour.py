
'''
Date:  April 12, 2023

Versions used: HA2023.4.1

Description:
This Python Script calculates the energy used from the last power change to the hour boundary
time, adds the energy accumulation over the last hour.  The hourly energy is recorded in 
"hourly_energy" and the energy accumulation is reset for the next hour window.
This script waits for the energy script calculation to finish in the case where there is
a power level change at the hour window boundary.
It needs three input_number entities to be passed as data values:  power, last_power and hourly_energy
input_number.energy_accum is used to accumulate the energy calculation over an hour period.
input_number entities restore the last known value on HA restart.  Sensors do not restore.

Instructions:
1. Python Script setup
   1.1 Create /config/python_scripts directory and copy this file to it.
   1.2 Add this line to configuration.yaml
       python_script:    
        
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
    

- alias: Hourly Energy
  initial_state: True
  trigger:
    - platform: time_pattern
      hours: "/1"
  action:
    service: script.turn_on
    entity_id: script.energy_hour
    
4. Add this script to scripts.yaml
* items are your choosing but must match your sensor names above
    input_number.furnace_power is the input power sensor in this example

energy_hour:
  alias: Hourly Energy
  sequence:
  #delay start if furnace power is changing of hour boundary.
    - wait_template: "{{ is_state('script.energy', 'off') }}"
    - service: python_script.energy_hour
      data:
        power: furnace_power*
        last_power: last_power
        energy_accum: energy_accum
        hourly_energy: hourly_energy

5. Use the history_graph lovelace card to display the result.

6. Save database size by not recording the last power and energy accumulator values.  
   Only the last value needed by the algorithm to calculate the hourly energy.
   The last value of all sensors is recorded in the database.

7. A separate automation "Daily Energy Total" and Python Script, "hour2day.py" is used 
   to accumulate hourly energy values on the half hour and then to transfer the daily
   accumulation to "input_number.daily_energy" at Midnight.
   There should be a correlation between the daily average temperature difference
   and the daily average energy consumption.

'''

#logger.warning("Got to energy_hour")
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
    

# timestamp is required to calculate energy from last power to the end of the window
time = datetime.datetime.now()
timestamp = time.timestamp()

# Get power unit and use to set the units for the other sensors used.
power_attr = hass.states.get(input_number_power).attributes
power_unit = power_attr['unit_of_measurement']
energy_unit = power_unit + 'h'
    
energy_accum_state = hass.states.get(input_number_energy_acum)
energy_accum = float(energy_accum_state.state)

#Clear energy accumulation at start of interval.
#Transfer sum of energy from previous period to the hourly log

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



'''
Date:  April 16, 2020

Versions used: HA10.3., HassOS and Raspberry PI 3 B

Description:
This Python Script sums 24 hourly energy accumulations to a daily energy use value at midnight.
It needs four input_numbers to be passed as data values:  hour_energy, hourly_energy_accum and daily_energy
The mode option when specified is used the average the values.
mode: average #Divides sum by 24 for the average hourly value
Replaced sensors with input_number since input_number is restored on HA restart.  Accumulation
and plot waveforms are not then disturbed.

Instructions:
1. Python Script setup
   1.1 Create /config/python_scripts directory and copy this file to it.
   1.2 Add this line to configuration.yaml
       python_scripts:
        
2. Add these input_number entities to configuration.yaml

  hourly_energy_accum:
    min: 0
    max: 1000
    step: 0.1
    
  daily_energy:
    min: 0
    max: 100
    step: 0.1
    mode: box
      
3.  Add this automation to automations.yaml
    * items are your choosing but must match your sensor names above

  - alias: Daily Energy
    initial_state: True
    trigger:
      - platform: time_pattern
        minutes: '/30'      
    action:
      service: python_script.hour2day
      data:
        hourly: hourly_energy
        hourly_accum: hourly_energy_accum
        daily: daily_energy
        mode: total
        
  - alias: Daily Temp Diff Average
    initial_state: True
    trigger:
      - platform: time_pattern
        minutes: '/30'      
    action:
      service: python_script.hour2day
      data:
        hourly: hour_diff
        hourly_accum: hourly_temp_diff_accum
        daily: daily_temp_diff
        mode: average

4. Use the history_graph lovelace card to display the result.

5. Save database size by not recording the hour_accum values.  
   Only the last value needed by the algorithm to calculate the daily energy.
   The last value of all sensors is recorded in the database.  

'''

#logger.warning("Got to hour2day")

hourly = data.get('hourly', '0')
hourly_accum = data.get('hourly_accum', '0')
daily = data.get('daily', '0')
mode = data.get('mode', '0')

if hourly != '0':
	input_number_hourly = "input_number." + hourly
else:
	logger.error("Hour2day script missing hourly data.")
    
if hourly_accum != '0':
	input_number_hourly_accum = "input_number." + hourly_accum
else:
	logger.error("Hour2day script missing hourly_accum data.")

if daily != '0':
	input_number_daily = "input_number." + daily
else:
	logger.error("Hour2day script missing daily data.")

if mode == 'average':
    samples = 24
else:
    samples = 1
    
time = datetime.datetime.now()
time_min = time.minute
time_hour = time.hour

#logger.warning("time_min = {} ".format(time_min))

# Get hourly unit and use to set the units for the other sensors used.
hourly_attr = hass.states.get(input_number_hourly).attributes
hourly_attr_unit = hourly_attr['unit_of_measurement']
#logger.warning("hourly_attr_unit = {} ".format(hourly_attr_unit))
hourly_accum_state = hass.states.get(input_number_hourly_accum)
hourly_accum = float(hourly_accum_state.state)
#logger.warning("hourly_accum = {} ".format(hourly_accum))
#Clear energy accumulation at start of interval.
#Transfer sum of energy from previous period to the hourly log
if time_hour == 0 and time_min == 0:  #At midnight
    if time.weekday() == 0 and time.month == 3 and time.day > 8 and time.day < 16:
        samples = 23 # Switch to DST occured on previous day
    if time.weekday() == 0 and time.month == 11 and time.day < 9:
        samples = 25 # Switch to PST occured on previous day
    average = hourly_accum / samples
    hass.states.set(input_number_daily, round(average, 1), {"unit_of_measurement": hourly_attr_unit})
    hass.states.set(input_number_hourly_accum, 0, {"unit_of_measurement": hourly_attr_unit}) 
elif time_min == 30:
    hourly_state = hass.states.get(input_number_hourly)
    try: #input_number_hourly may be unknown at startup
        hourly = float(hourly_state.state)
    except ValueError:
        hourly = 0.0
    hourly_accum = round(hourly_accum + hourly,1)
    hass.states.set(input_number_hourly_accum, hourly_accum, {"unit_of_measurement": hourly_attr_unit}) 





'''
Date:  May 31, 2021

Versions used: HA2021.4.3, HassOS and Raspberry PI 3 B

Description:

Instructions:
1. Python Script setup
   1.1 Create /config/python_scripts directory and copy this file to it.
   1.2 Add this line to configuration.yaml
       python_scripts:
        
2.  Add this automation to automations.yaml
  - alias: HVAC
    initial_state: True
    trigger:
      - platform: time_pattern
        minutes: '/5'      
    action:
      service: python_script.heatpump
      
Design heat and cool the house using the Mitsubishi heatpump

MQTT Topics
heatpump/status  (Updated every minute)
    "roomTemperature": <degrees C>
    "operating": <true or false>
heatpump
    "power": <ON or OFF>
    "mode":  <OFF, HEAT, DRY, COOL, FAN_ONLY, AUTO>
    "temperature": <degrees C>
    "fan": <AUTO, QUIET, 1, 2, 3, 4>
    "vane": <AUTO, 1, 2, 3, 4, 5, SWING>
    "wideVane": "<<"  Other codes?

Goals
1. Use the furnace only to bring up the room temperature to the target temperature 
and if outside temperature is below the heat pump's lower effective limit (1 degrees C)
2. Use the heat pump to maintain the house temperature.
3. Use the heat pump to cool house when hot
4. Heat pump should be off when the furnace is operating or house is 1 degree below cooling set point.
    
Every 5 minutes (determined by the HVAC automation trigger) a transition to
another state is determined based on the current room temperature

A little too complicated for a yaml automation so done using Python.

Testing with home_temperature = 21.0, ac_home = 24.0
Furnace heat from  -n to 19.5
Heat pump heat from 20.0 to 21.5, Furnace is OFF (Furnace is ON for all other temperature ranges.)
Heat pump OFF from 22.0 to 23.0
Heat pump cool starts at 25.5 and is turned off at 23.0

Furnace set point is not affected.

'''

#logger.warning("Got to heatpump")

hvac = hass.states.get('climate.mitsubishi_heatpump')
#hvac_state = hvac.state
hvac_attr = hvac.attributes

furnace = hass.states.get('climate.house')
#furnace_state = furnace.state
furnace_attr = furnace.attributes
#logger.warning("hvac_state = {}".format(hvac_state))

current_temperature = hvac_attr['current_temperature']
# Using max_tmp for testing only
#current_temperature = hass.states.get('input_number.max_temp').state
#heatpump_setpoint = hvac_attr['temperature']
operation_mode = hvac_attr['hvac_action']
furnace_setpoint = furnace_attr['temperature']
#furnace_mode = furnace_attr['hvac_action']
#logger.warning("operation_mode = {}".format(operation_mode))
#logger.warning("hvac_attr ct = {}".format(current_temperature))
#logger.warning("hvac_attr t = {}".format(temperature))

away = hass.states.get('binary_sensor.away').state
#logger.warning("away = {}".format(away))

# Heating temperature set points
#away_temperature = hass.states.get('input_number.slider_away').state
home_temperature = hass.states.get('input_number.slider_home').state
# Cooling Temperature set points
ac_away = hass.states.get('input_number.slider_ac_away').state
ac_home = hass.states.get('input_number.slider_ac_home').state
# Outside temperature
outside_temperature = hass.states.get('input_number.temperature').state

#logger.warning("heatpumpx current_temperature = {}".format(current_temperature))
#logger.warning("heatpumpx ac_home = {}".format(ac_home))
#logger.warning("heatpumpx home_temperature = {}".format(home_temperature))
#logger.warning("ac home = {}".format(ac_home))

if away == 'off':
    #logger.warning("Got to heatpumpxhome")
    # Start cooling if 2 degrees above set point
    if float(current_temperature) >= float(ac_home) + 1.5:
        #logger.warning("Got to heatpumpxcool1")
        if operation_mode != 'cooling': # Prevent repeat if already cooling
            #logger.warning("Got to heatpumpxcool2")
            #Update temperature set point to match ac_home slider value before cooling is started
            service_data = {'entity_id': 'climate.mitsubishi_heatpump', 'temperature': ac_home}
            hass.services.call('climate', 'set_temperature', service_data, False)
            # Wait 2 seconds to prevent MQTT message clash
            # Using queued mode in automation to prevent clash
            #time.sleep(2)
            # Set cooling
            service_data = {'entity_id': 'climate.mitsubishi_heatpump', 'hvac_mode': 'cool'}
            hass.services.call('climate', 'set_hvac_mode', service_data, False)
    # Turn off heat pump in zone between heating and cooling
    # OK to turn furnace back ON 
    elif float(current_temperature) <= float(ac_home) - 1.0 and \
        float(current_temperature) > float(home_temperature) + 0.5:
        #logger.warning("Got to heatpumpxoff1")
        if operation_mode != 'off': # Prevent repeat if already cooling
            #logger.warning("Got to heatpumpxoff2")
            service_data = {'entity_id': 'climate.mitsubishi_heatpump', 'hvac_mode': 'off'}
            hass.services.call('climate', 'set_hvac_mode', service_data, False)
        service_data = {'entity_id': 'climate.house', 'hvac_mode': 'heat'}
        hass.services.call('climate', 'set_hvac_mode', service_data, False)
    # Start heating +/- 1.0 around home set point.  Turn furnace heating off to prevent conflict
    # Don't allow heat pump heating when too cold outside for efficiency reasons
    # Don't allow heating when furnace set point is at the away temperature overnight
    elif float(current_temperature) <= float(home_temperature) + 0.5 and \
        float(current_temperature) >= float(home_temperature) - 1.0 and float(outside_temperature) >= 1.0 \
        and float(furnace_setpoint) == float(home_temperature) :
        #logger.warning("Got to heatpumpxheat1")
        if operation_mode != 'heating': # Prevent repeat if already heating.  Set mode and temperature in one MQTT json message.
            #logger.warning("Got to heatpumpxheat2")
            #Update temperature set point to match home slider value before heating is started
            service_data = {'entity_id': 'climate.mitsubishi_heatpump', 'temperature': home_temperature}
            hass.services.call('climate', 'set_temperature', service_data, False)
            # Wait 2 seconds to prevent MQTT message clash
            #time.sleep(2)
            service_data = {'entity_id': 'climate.mitsubishi_heatpump', 'hvac_mode': 'heat'}
            hass.services.call('climate', 'set_hvac_mode', service_data, False)
            # Disable furnace heating
            service_data = {'entity_id': 'climate.house', 'hvac_mode': 'off'}
            hass.services.call('climate', 'set_hvac_mode', service_data, False)
    # Enable furnace heating
    else :
        #logger.warning("Got to heatpumpxfurnace1")
        if operation_mode == 'heating':
            #logger.warning("Got to heatpumpxfurnace1")
            service_data = {'entity_id': 'climate.mitsubishi_heatpump', 'hvac_mode': 'off'}
            hass.services.call('climate', 'set_hvac_mode', service_data, False)
        service_data = {'entity_id': 'climate.house', 'hvac_mode': 'heat'}
        hass.services.call('climate', 'set_hvac_mode', service_data, False)

# When away use only the furnace to maintain the low away temperature.
# Use the heat pump to cool only if the higher ac away set point is exceeded.
# Prevent cooking the house plants when away in the summer time.
if away == 'on':
    #logger.warning("Got to heatpumpxaway")
    if float(current_temperature) >= float(ac_away) + 2.0 and operation_mode != 'cooling':
        # Update temperature set point to match ac_home slider value when cooling is started
        service_data = {'entity_id': 'climate.mitsubishi_heatpump', 'temperature': ac_away}
        hass.services.call('climate', 'set_temperature', service_data, False)
        #time.sleep(2)
        service_data = {'entity_id': 'climate.mitsubishi_heatpump', 'hvac_mode': 'cool'}
        hass.services.call('climate', 'set_hvac_mode', service_data, False)
    if float(current_temperature) <= float(ac_away) - 1.0 and operation_mode != 'off':
        service_data = {'entity_id': 'climate.mitsubishi_heatpump', 'hvac_mode': 'off'}
        hass.services.call('climate', 'set_hvac_mode', service_data, False)
        # Use furnace only to heat while away
        service_data = {'entity_id': 'climate.house', 'hvac_mode': 'heat'}
        hass.services.call('climate', 'set_hvac_mode', service_data, False) 



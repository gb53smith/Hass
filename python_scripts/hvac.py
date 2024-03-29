
'''
Date:  March 24, 2023

Versions used: HA2023.3.6

Description:

Instructions:
1. Python Script setup
   1.1 Create /config/python_scripts directory and copy this file to it.
   1.2 Add this line to configuration.yaml
       python_script:
        
2.  Add this automation to automations.yaml
  - alias: HVAC
    initial_state: True
    trigger:
      - platform: time_pattern
        minutes: '/1'      
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
    
Every minute (determined by the HVAC automation trigger) a transition to
another state is determined based on the current room temperature

A little too complicated for a yaml automation so done using Python.

Testing with home_temperature = 21.0, ac_home = 24.0

Evaluate temperature range from high to low temperture while home (not away)
Execute the first match and skip the rest.

- Start cooling
    house temperature >= ac_home + 1.5
- Stop cooling  
    house temperature <= ac_home - 1.0 
- Stop heating with heat pump    
    house temperature > home + 0.3  
- Start heating with heat pump and stop heating with furnace    
    house temperature <= home - 0.5 and house temperature <= home - 1.0   
- Start heating with furnace and stop heating with heat pump
    house temperature < home - 1.0       


To give the HVAC MQTT interface time to react only one publish to climate.mitsubishi_heatpump
is permitted each time this script is called.  The temperature set point does not change very 
often so the occasional additional delay is not an issue.

'''

#logger.warning("Got to heatpump")

hvac = hass.states.get('climate.mitsubishi_heatpump')
hvac_attr = hvac.attributes

furnace = hass.states.get('climate.house')
furnace_state = furnace.state
furnace_attr = furnace.attributes

#house_temperature switches to hvac_attr['current_temperature'] if the WiFi connection
#to multisensor2 fails
current_temperature = float(hass.states.get('sensor.house_temperature').state)
operation_mode = hvac_attr['hvac_action']
heatpump_setpoint = hvac_attr['temperature']
furnace_setpoint = furnace_attr['temperature']
#logger.warning("furnace_setpoint = {}".format(furnace_setpoint))
#logger.warning("operation_mode = {}".format(operation_mode))
#logger.warning("current_temperature = {}".format(current_temperature))
#logger.warning("Furnace State = {}".format(furnace_state))

### Debug service call with blocking option true to prevent warnings like this:
#2023-03-24 08:16:42.030 WARNING (MainThread) [homeassistant.components.websocket_api.http.connection]
#[140616493978560] Disconnected: Did not receive auth message within 10 seconds_api.http.connection]
# increased time limit from 10 to 30 seconds for good measure
# service_data = {'entity_id': 'climate.mitsubishi_heatpump', 'hvac_mode': 'heat'}
# hass.services.call('climate', 'set_hvac_mode', service_data, blocking=True, limit=30)
# service_data = {'entity_id': 'climate.house', 'hvac_mode': 'off'}
# hass.services.call('climate', 'set_hvac_mode', service_data, blocking=True, limit=30)
# home_temperature = float(hass.states.get('input_number.slider_home').state)
# service_data = {'entity_id': 'climate.mitsubishi_heatpump', 'temperature': home_temperature}
# hass.services.call('climate', 'set_temperature', service_data, blocking=True, limit=30)

away = hass.states.get('binary_sensor.away').state
#logger.warning("away = {}".format(away))

# Heating temperature set points
home_temperature = float(hass.states.get('input_number.slider_home').state)
away_temperature = float(hass.states.get('input_number.slider_away').state)
#logger.warning("home_temperature = {}".format(home_temperature))
# Cooling Temperature set points
ac_away = float(hass.states.get('input_number.slider_ac_away').state)
ac_home = float(hass.states.get('input_number.slider_ac_home').state)

            
# Outside temperature
if (hass.states.get('sensor.mysensors_bme280_2_2').state == "unavailable"):
    #Force heatpump to run when outside temperature sensor fails
    outside_temperature = 99.0 
else:
    #Use outside temperature to decide to enable the heatpump.
    outside_temperature = float(hass.states.get('sensor.mysensors_bme280_2_2').state)

if away == 'off':
    #logger.warning("Got to heatpumpxhome")
    ### Start cooling if 1.5 degrees above set point
    if current_temperature >= ac_home + 1.5:
        #logger.warning("Turning AC heatpump ON with current_temperature = {}".format(current_temperature))
        #logger.warning("Got to heatpumpxcool1")
        if operation_mode != 'cooling': # Prevent repeat if already cooling
            # Set cooling
            service_data = {'entity_id': 'climate.mitsubishi_heatpump', 'hvac_mode': 'cool'}
            hass.services.call('climate', 'set_hvac_mode', service_data, blocking=True, limit=30)
        elif heatpump_setpoint != ac_home:
            #logger.warning("Got to heatpumpxcool2")
            #Update temperature set point to match ac_home slider value.  After cooling has started.
            service_data = {'entity_id': 'climate.mitsubishi_heatpump', 'temperature': ac_home}
            hass.services.call('climate', 'set_temperature', service_data, blocking=True, limit=30)
    ### Turn off heat pump and furnance in zone between heating and cooling
    elif current_temperature <= ac_home - 1.0 and \
        current_temperature > home_temperature + 0.3:
        #logger.warning("Got to heatpumpxoff1")
        #logger.warning("Turning heatpump OFF, furnace OFF with current_temperature = {}".format(current_temperature))
        if operation_mode != 'off': # Prevent repeat if already cooling
            #logger.warning("Got to heatpumpxoff2")
            service_data = {'entity_id': 'climate.mitsubishi_heatpump', 'hvac_mode': 'off'}
            hass.services.call('climate', 'set_hvac_mode', service_data, blocking=True, limit=30)
        #elif heatpump_setpoint != home_temperature:
            #Update temperature set point to match home slider value.  If heating is already OFF.
            #service_data = {'entity_id': 'climate.mitsubishi_heatpump', 'temperature': home_temperature}
            #hass.services.call('climate', 'set_temperature', service_data, blocking=True, limit=30)
        #Turn off Furnace
        if furnace_state != 'off':
            #logger.warning("Got to heatpumpxoff3")
            service_data = {'entity_id': 'climate.house', 'hvac_mode': 'off'}
            hass.services.call('climate', 'set_hvac_mode', service_data, blocking=True, limit=30)
    # Don't allow heat pump heating when too cold outside for efficiency reasons
    # Don't allow heating when furnace set point is at the away temperature overnight
    ### HVAC Heating temperature range
    elif current_temperature <= home_temperature - 0.5 and \
        current_temperature >= home_temperature - 1.0 and outside_temperature >= 1.0 \
        and furnace_setpoint == home_temperature :
        #logger.warning("Got to heatpumpxheat1")
        #logger.warning("Turning heatpump ON, furnance OFF with current_temperature = {}".format(current_temperature))
        if operation_mode != 'heating': # Prevent repeat if already heating.  Set mode and temperature in one MQTT json message.
            #logger.warning("Got to heatpumpxheat2")
            service_data = {'entity_id': 'climate.mitsubishi_heatpump', 'hvac_mode': 'heat'}
            hass.services.call('climate', 'set_hvac_mode', service_data, blocking=True, limit=30)
            # Disable furnace heating
            #service_data = {'entity_id': 'climate.house', 'hvac_mode': 'off'}
            #hass.services.call('climate', 'set_hvac_mode', service_data, blocking=True, limit=30)
        elif heatpump_setpoint != home_temperature:
            #Update temperature set point to match home slider value.  After heating has started.
            service_data = {'entity_id': 'climate.mitsubishi_heatpump', 'temperature': home_temperature}
            hass.services.call('climate', 'set_temperature', service_data, blocking=True, limit=30)
        #Turn off Furnace
        if furnace_state != 'off':
            #logger.warning("Got to heatpumpxheat3")
            service_data = {'entity_id': 'climate.house', 'hvac_mode': 'off'}
            hass.services.call('climate', 'set_hvac_mode', service_data, blocking=True, limit=30)
    ### Enable furnace heating below range of heatpump
    elif current_temperature < home_temperature - 1.0 and \
        furnace_setpoint == home_temperature :
        #logger.warning("Got to heatpumpxfurnace1")
        #logger.warning("Turning heatpump OFF, furnace ON with current_temperature = {}".format(current_temperature))
        if operation_mode == 'heating':
            #logger.warning("Got to heatpumpxfurnace2")
            service_data = {'entity_id': 'climate.mitsubishi_heatpump', 'hvac_mode': 'off'}
            hass.services.call('climate', 'set_hvac_mode', service_data, blocking=True, limit=30)
        elif heatpump_setpoint != home_temperature:
            #Update temperature set point to match home slider value.  If heating is already OFF.
            service_data = {'entity_id': 'climate.mitsubishi_heatpump', 'temperature': home_temperature}
            hass.services.call('climate', 'set_temperature', service_data, blocking=True, limit=30)
        #Turn on Furnace
        if furnace_state != 'heat':
            #logger.warning("Got to heatpumpxfurnace3")
            service_data = {'entity_id': 'climate.house', 'hvac_mode': 'heat'}
            hass.services.call('climate', 'set_hvac_mode', service_data, blocking=True, limit=30)
    #else:
        #logger.warning("No operation with current_temperature = {}".format(current_temperature))
# When away use only the furnace to maintain the low away temperature.
# Use the heat pump to cool only if the higher ac away set point is exceeded.
# Prevent cooking the house plants when away in the summer time.
else: #away == 'on'
    #logger.warning("Got to heatpumpxaway")
    if current_temperature >= ac_away + 1.5:
        if operation_mode != 'cooling': # Prevent repeat if already cooling
            service_data = {'entity_id': 'climate.mitsubishi_heatpump', 'hvac_mode': 'cool'}
            hass.services.call('climate', 'set_hvac_mode', service_data, blocking=True, limit=30)
        elif heatpump_setpoint != ac_away:
            #Update temperature set point to match ac_away slider value.  After cooling has started.
            service_data = {'entity_id': 'climate.mitsubishi_heatpump', 'temperature': ac_away}
            hass.services.call('climate', 'set_temperature', service_data, blocking=True, limit=30)
    if current_temperature <= ac_away - 1.0 and operation_mode != 'off':
        service_data = {'entity_id': 'climate.mitsubishi_heatpump', 'hvac_mode': 'off'}
        hass.services.call('climate', 'set_hvac_mode', service_data, blocking=True, limit=30)
    # Use furnace only to heat while away
    if furnace_state != 'heat':
        service_data = {'entity_id': 'climate.house', 'hvac_mode': 'heat'}
        hass.services.call('climate', 'set_hvac_mode', service_data, blocking=True, limit=30) 

#Enable furnance heating while away or sleeping at night.  Turn off heatpump
if furnace_setpoint == away_temperature and furnace_state != 'heat':
    service_data = {'entity_id': 'climate.house', 'hvac_mode': 'heat'}
    hass.services.call('climate', 'set_hvac_mode', service_data, blocking=True, limit=30)
    if operation_mode != 'off': # Prevent repeat if already off
        service_data = {'entity_id': 'climate.mitsubishi_heatpump', 'hvac_mode': 'off'}
        hass.services.call('climate', 'set_hvac_mode', service_data, blocking=True, limit=30) 
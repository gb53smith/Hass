
'''
Date:  May 29, 2019

Versions used: HA89.1, HassOS and Raspberry PI 3 B

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
      service: python_script.hvac

'''

#logger.warning("Go to hvac")

hvac = hass.states.get('climate.mitsubishi_heatpump')
hvac_state = hvac.state
hvac_attr = hvac.attributes
#logger.warning("hvac_state = {}".format(hvac_state))

current_temperature = hvac_attr['current_temperature']
temperature = hvac_attr['temperature']
operation_mode = hvac_attr['operation_mode']

#logger.warning("hvac_attr ct = {}".format(current_temperature))
#logger.warning("hvac_attr t = {}".format(temperature))

away = hass.states.get('switch.away').state
#logger.warning("away = {}".format(away))

ac_away = hass.states.get('input_number.slider_ac_away').state
ac_home = hass.states.get('input_number.slider_ac_home').state

#logger.warning("ac away = {}".format(ac_away))

#logger.warning("ac home = {}".format(ac_home))

if away == 'off':
    #Update temperature set point to match ac_home slider value
    if float(temperature) != float(ac_home):
        service_data = {'entity_id': 'climate.mitsubishi_heatpump', 'temperature': ac_home}
        hass.services.call('climate', 'set_temperature', service_data, False)
    # Start cooling if 2 degress above set point
    if float(current_temperature) >= float(ac_home) + 1.5 and operation_mode != 'cool':
        service_data = {'entity_id': 'climate.mitsubishi_heatpump', 'operation_mode': 'cool'}
        hass.services.call('climate', 'set_operation_mode', service_data, False)
    # Stop cooling if 1 degress below set point
    if float(current_temperature) <= float(ac_home) - 1.0 and operation_mode != 'off':
        service_data = {'entity_id': 'climate.mitsubishi_heatpump', 'operation_mode': 'off'}
        hass.services.call('climate', 'set_operation_mode', service_data, False)
        
if away == 'on':
    if float(temperature) != float(ac_away):
        service_data = {'entity_id': 'climate.mitsubishi_heatpump', 'temperature': ac_away}
        hass.services.call('climate', 'set_temperature', service_data, False)
    if float(current_temperature) >= float(ac_away) + 2.0 and operation_mode != 'cool':
        service_data = {'entity_id': 'climate.mitsubishi_heatpump', 'operation_mode': 'cool'}
        hass.services.call('climate', 'set_operation_mode', service_data, False)
    if float(current_temperature) <= float(ac_away) - 1.0 and operation_mode != 'off':
        service_data = {'entity_id': 'climate.mitsubishi_heatpump', 'operation_mode': 'off'}
        hass.services.call('climate', 'set_operation_mode', service_data, False)




# Python Script to Randomize Light turn ON and OFF times
# to confuse burglars

#logger.info("Got to GBS random_lights")

def minutes2time(minutes):
    '''
    Converts a integer input into a hh:mm format string
    Allowing for over and underflow.
    '''
    #Convert negative time into previous day
    if minutes < 0:
        minutes + minutes + 1440
        
    #Convert back to hours and minutes
    new_hour, new_minute = divmod(minutes, 60)

    #Correct overflow into the next day
    new_hour = new_hour % 24

    #Format with leading zeros
    return "{:02}".format(new_hour) + ':' + "{:02}".format(new_minute) + ':00'

# Get time the living room light turns off when home
lr_off_time = hass.states.get('input_datetime.lr_off_time').state

#logger.info("lr_off_time = {}".format(lr_off_time))

# Add a random +/- 15 minutes to lr_off_time

# Set the living room random time off to be used when away
hour, minute, sec =  lr_off_time.split(':')

# Calculate number of minutes to enable math on time
minutes = int(hour) * 60 + int(minute)


# Get random offsets from random sensors
lr_random = int(hass.states.get('sensor.lr_random').state)
br_random = int(hass.states.get('sensor.br_random').state)

# Center Living Room Random OFF time around fixed at home time +/- 15 minutes
lr_off_time = minutes - 15 + lr_random
lr_off_time_random = minutes2time(lr_off_time)

# Turn ON bedroom light one minute before living room light goes OFF
br_on_time = lr_off_time - 1
br_on_time_random = minutes2time(br_on_time)

# Turn OFF bedroom light 5 to 15 minutes after turning ON
br_off_time = br_on_time + 5 + br_random
br_off_time_random = minutes2time(br_off_time)

#logger.info("br_random = {}".format(br_random))

# Set next random time values.  
# Note: Call this script when living room light is turned ON to schedule its OFF Time
# and bedroom light ON / OFF sequence

service_data = {'entity_id': 'input_datetime.lr_off_time_random', 'time': lr_off_time_random}
hass.services.call('input_datetime', 'set_datetime', service_data, False)

service_data = {'entity_id': 'input_datetime.br_on_time_random', 'time': br_on_time_random}
hass.services.call('input_datetime', 'set_datetime', service_data, False)

service_data = {'entity_id': 'input_datetime.br_off_time_random', 'time': br_off_time_random}
hass.services.call('input_datetime', 'set_datetime', service_data, False)

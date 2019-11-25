# volume_fade.py

step_size = int(data.get('step_size'))
end_volume = int(data.get('end_volume'))

# These values must be passed in
if (step_size is not None) and (end_volume is not None):
	current_volume = int(hass.states.get('sensor.chromecast_volume').state)
	entity_id = hass.states.get('sensor.media_output').state

	if (current_volume > end_volume):
		if (step_size > 0):
			step_size = step_size * -1
	else:
		if (step_size < 0):
			logger.warning('Passing a negative value when end_volume is greater than current_volume')
			step_size = step_size * -1

	while (current_volume is not end_volume):
		current_volume = current_volume + step_size
		if (step_size > 0):
			# We are increasing the volume, make sure we don't overshoot.
			if (current_volume >= end_volume):
				current_volume = end_volume
		elif (step_size < 0):
			# We are decreasing the volume, make sure we don't overshoot.
			if (current_volume <= end_volume):
				current_volume = end_volume
		service_data = {'entity_id': entity_id, 'volume_level': (float(current_volume) / 100)}
		hass.services.call('media_player', 'volume_set', service_data, False)
		
		time.sleep(1)
else:
	logger.error('Invalid parameter value.')
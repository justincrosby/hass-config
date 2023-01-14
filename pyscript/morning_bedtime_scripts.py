@service
def shutdown():
    """yaml
name: Shutdown
description: Turn everything off
"""
    if(state.get("light.bedroom_lights") == "on"):
        light.turn_on(entity_id="light.bedroom_lights", brightness=0, transition=15)
    light.turn_off(entity_id="light.all_lights")
    homeassistant.turn_off(entity_id="group.media_players")
    if(state.get("sensor.media_player_status") == "on"):
        media_player.stop(entity_id=state.get("sensor.media_player_output"))

@service
def morning():
    """yaml
name: Morning
description: Gradually wake up in the morning :)
"""
    if(state.get("binary_sensor.justin_presence") == "on"):
        script.turn_on(entity_id="script.phone_morning")
    input_boolean.turn_off(entity_id="input_boolean.bedtime")
    input_boolean.turn_on(entity_id="input_boolean.enable_presence_automations")
    # Only execute the full alarm routine if requested
    if(state.get("binary_sensor.alarm_full") == "on"):
        pyscript.morning_music()
        # Wait for 5 minutes while the chill playlist plays
        task.sleep(5*60)
        # Okay, now it's wake up time, start the lights red and transition
        light.turn_on(entity_id="light.bedroom_lights", rgb_color=[255, 0, 0], brightness_pct=1)
        task.sleep(1)
        light.turn_on(entity_id="light.bedroom_lights", rgb_color=[255, 255, 0], brightness_pct=80, transition=300)
        task.sleep(25*60)
        light.turn_on(entity_id="light.bedroom_lights", rgb_color=[255, 255, 255], brightness_pct=100, transition=100)

@service
def bedtime():
    """yaml
name: Bedtime
description: Good night :)
"""
    shutdown()
    input_boolean.turn_on(entity_id="input_boolean.bedtime")
    input_boolean.turn_off(entity_id="input_boolean.enable_presence_automations")
    script.turn_on(entity_id="script.phone_bedtime")
    script.turn_on(entity_id="script.forgot_to_feed_fish")
    input_boolean.turn_off(entity_id="input_boolean.fish_fed_tracker")
    script.turn_on(entity_id="script.forgot_to_water_the_plants")
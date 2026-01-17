@service
def set_default_audio_levels():
    """yaml
name: Set Default Audio Levels
description: Sets all audio devices to an optimal volume
"""
    # Defaults here
    receiver_vol = 0.48
    living_room_vol = 0.8
    master_bed_vol = 0.8
    bathroom_vol = 0.5
    # Try to set the volume 10 times and if we fail exit
    max_retries = 10
    if state.get("media_player.home_audio") == "playing":
        retry_count = 0
        while round(state.getattr("media_player.denon_avr_x1300w")["volume_level"], 2) != receiver_vol:
            media_player.volume_set(entity_id="media_player.denon_avr_x1300w", volume_level=receiver_vol)
            task.sleep(0.5)
            if retry_count > max_retries:
                log.warning("Failed to set volume for receiver")
                return
        vol = round(state.getattr("media_player.denon_avr_x1300w")["volume_level"], 2)
        log.info(f"Set receiver volume to {vol}")
    if state.get("media_player.living_room_audio") == "playing":
        retry_count = 0
        while round(state.getattr("media_player.living_room_audio")["volume_level"], 2) != living_room_vol:
            media_player.volume_set(entity_id="media_player.living_room_audio", volume_level=living_room_vol)
            task.sleep(0.5)
            if retry_count > max_retries:
                log.warning("Failed to set volume for living room audio")
                return
        vol = round(state.getattr("media_player.living_room_audio")["volume_level"], 2)
        log.info(f"Set living room volume to {vol}")
    if state.get("media_player.master_bedroom_audio") == "playing":
        retry_count = 0
        while round(state.getattr("media_player.master_bedroom_audio")["volume_level"], 2) != master_bed_vol:
            media_player.volume_set(entity_id="media_player.master_bedroom_audio", volume_level=master_bed_vol)
            task.sleep(0.5)
            if retry_count > max_retries:
                log.warning("Failed to set volume for master bedroom audio")
                return
        vol = round(state.getattr("media_player.master_bedroom_audio")["volume_level"], 2)
        log.info(f"Set master bedroom volume to {vol}")
    if state.get("media_player.master_bathroom_speaker") == "playing":
        retry_count = 0
        while round(state.getattr("media_player.master_bathroom_speaker")["volume_level"], 2) != bathroom_vol:
            media_player.volume_set(entity_id="media_player.master_bathroom_speaker", volume_level=bathroom_vol)
            task.sleep(0.5)
            if retry_count > max_retries:
                log.warning("Failed to set volume for master bathroom speaker")
                return
        vol = round(state.getattr("media_player.master_bathroom_speaker")["volume_level"], 2)
        log.info(f"Set master bathroom volume to {vol}")
    if state.get("media_player.bathroom_speaker") == "playing":
        retry_count = 0
        while round(state.getattr("media_player.bathroom_speaker")["volume_level"], 2) != bathroom_vol:
            media_player.volume_set(entity_id="media_player.bathroom_speaker", volume_level=bathroom_vol)
            task.sleep(0.5)
            if retry_count > max_retries:
                log.warning("Failed to set volume for bathroom speaker")
                return
        vol = round(state.getattr("media_player.bathroom_speaker")["volume_level"], 2)
        log.info(f"Set bathroom volume to {vol}")

@service
def volume_fade(step_size=0, start_vol=0, end_vol=0):
    """yaml
name: Volume Fade
description: Slowly fades the volume of the chosen output device from start volume to end volume
fields:
  step_size:
    description: the volume step size in percentage
    example: 1
    required: true
  start_vol:
    description: the starting volume in percentage
    example: 0
    required: true
  end_vol:
    description: the ending volume in percentage
    example: 50
    required: true
"""
    log.info(f"volume fade: step size={step_size}, start volume={start_vol}, end volume={end_vol}")
    entity_id = state.get("sensor.media_player_selected_output")

    if start_vol == end_vol:
        if start_vol == end_vol:
            log.warning("Passing an end_vol value equal to the start_vol")
            return

    if start_vol > end_vol:
        if step_size > 0:
            step_size = step_size * -1
    else:
        if step_size < 0:
            loh.warning("Passing a negative value when end_vol is greater than start_vol")
            return

    while start_vol != end_vol:
        start_vol = start_vol + step_size
        if step_size > 0:
            # We are increasing the volume, make sure we don't overshoot.
            if start_vol >= end_vol:
                start_vol = end_vol
        elif step_size < 0:
            # We are decreasing the volume, make sure we don't overshoot.
            if start_vol <= end_vol:
                start_vol = end_vol
        media_player.volume_set(entity_id=entity_id, volume_level=(float(start_vol) / 100))
        task.sleep(0.5)

@service
def morning_music():
    """yaml
name: Morning Music
description: Starts the music quietly in the morning
"""
    # Start music with bedroom audio
    input_select.select_option(entity_id="input_select.media_output_select", option="Master Bedroom Audio")
    # Start up playlist
    playing = False
    curr_time = 0
    retries = 2
    while not playing:
        script.turn_on(entity_id="script.play_chill_music_var", variables={"volume_level":"0"})
        # Timeout after 10s
        while curr_time < 10:
            task.sleep(1)
            if state.get("sensor.media_player_status") == "playing":
                playing = True
                break
            curr_time += 1
        curr_time = 0
        retries += 1
        if retries > 2:
            break
    # Start music at 0 volume and slowly fade in
    pyscript.volume_fade(step_size=1, start_vol=0, end_vol=35)
    # Let the music play for 15 mins
    task.sleep(60*15)
    # Fade back down to 0
    pyscript.volume_fade(step_size=5, start_vol=35, end_vol=0)
    media_player.media_stop(entity_id="media_player.master_bedroom_audio")
    # Switch to whole suite
    input_select.select_option(entity_id="input_select.media_output_select", option="Master Suite Audio")
    # Start up playlist
    playing = False
    curr_time = 0
    while not playing:
        script.turn_on(entity_id="script.play_all_music_var", variables={"volume_level":"0"})
        # Timeout after 10s
        while curr_time < 10:
            task.sleep(1)
            if state.get("sensor.media_player_status") == "playing":
                playing = True
                break
            curr_time += 1
        curr_time = 0
        retries += 1
        if retries > 2:
            break
    # Start music at 0 volume and slowly fade in
    pyscript.volume_fade(step_size=5, start_vol=0, end_vol=45)

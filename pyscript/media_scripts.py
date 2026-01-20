# List of all google cast media players
MEDIA_PLAYERS = {
    "media_player.backyard_speaker",
    "media_player.denon_avr_x1300w",
    "media_player.kitchen_speaker",
    "media_player.living_room_audio",
    "media_player.master_bathroom_speaker",
    "media_player.master_bedroom_audio"
}

# Convert from music assistant media player to google cast media player
MEDIA_PLAYER_MASS_TRANSLATION = {
    "media_player.mass_home": "media_player.home_audio",
    "media_player.mass_fake_home": "media_player.fake_home_audio",
    "media_player.mass_master_suite": "media_player.master_suite_audio",
    "media_player.mass_backyard": "media_player.backyard_speaker",
    "media_player.denon_avr_x1300w": "media_player.denon_avr_x1300w",
    "media_player.mass_kitchen": "media_player.kitchen_speaker",
    "media_player.mass_living_room": "media_player.living_room_audio",
    "media_player.mass_master_bathroom": "media_player.master_bathroom_speaker",
    "media_player.mass_master_bedroom": "media_player.master_bedroom_audio"
}

# Default volume levels for media players
MEDIA_PLAYER_DEFAULT_VOLUME = {
    "media_player.backyard_speaker": 0.8,
    "media_player.denon_avr_x1300w": 0.48,
    "media_player.kitchen_speaker": 0.8,
    "media_player.living_room_audio": 0.8,
    "media_player.master_bathroom_speaker": 0.5,
    "media_player.master_bedroom_audio": 0.8
}

# Define speaker groups
MASTER_SUITE_SPEAKERS = [
    "media_player.master_bathroom_speaker",
    "media_player.master_bedroom_audio"
]

HOME_SPEAKERS = [
    "media_player.backyard_speaker",
    "media_player.denon_avr_x1300w",
    "media_player.kitchen_speaker",
    "media_player.living_room_audio",
    "media_player.master_bathroom_speaker",
    "media_player.master_bedroom_audio"
]

FAKE_HOME_SPEAKERS = [
    "media_player.backyard_speaker",
    "media_player.kitchen_speaker",
    "media_player.living_room_audio",
    "media_player.master_bathroom_speaker",
    "media_player.master_bedroom_audio"
]

# Media player groups definition
MEDIA_PLAYER_GROUPS = {
    "media_player.mass_home": HOME_SPEAKERS,
    "media_player.home_audio": HOME_SPEAKERS,
    "media_player.mass_fake_home": FAKE_HOME_SPEAKERS,
    "media_player.fake_home_audio": FAKE_HOME_SPEAKERS,
    "media_player.mass_master_suite": MASTER_SUITE_SPEAKERS,
    "media_player.master_suite_audio": MASTER_SUITE_SPEAKERS
}

@service
def set_default_audio_levels(group_name=""):
    """
    Set all media players in the specified group to their default volume levels.
    
    Args:
        group_name: The name of the group (key in MEDIA_PLAYER_DEFAULT_VOLUME)
    """
    if group_name in MEDIA_PLAYER_GROUPS:
        entities = MEDIA_PLAYER_GROUPS[group_name]
    elif group_name in MEDIA_PLAYER_MASS_TRANSLATION:
        entities = [MEDIA_PLAYER_MASS_TRANSLATION[group_name]]
    elif group_name in MEDIA_PLAYERS:
        entities = [MEDIA_PLAYERS[group_name]]
    else:
        log.error(f"Group '{group_name}' not found.")
        return
    
    for entity_id in entities:
        default_volume = MEDIA_PLAYER_DEFAULT_VOLUME.get(entity_id)
        if entity_id == "media_player.denon_avr_x1300w":
            media_player.select_source(entity_id=entity_id, source="CastAudio")
            expected_state = "on"
        else:
            expected_state = "playing"
        task.wait_until(state_trigger="{entity_id} == '{expected_state}'".format(entity_id=entity_id, expected_state=expected_state), timeout=5)
        if default_volume is not None:
            grad_vol.set_volume(data={"volume": default_volume, "duration": 10}, target={"entity_id": entity_id})
            log.info(f"Set {entity_id} to default volume level {default_volume}")
        else:
            log.error(f"No default volume level defined for {entity_id}")

@service
def switch_to_shield():
    """yaml
name: Switch to Shield
description: Turns on the receiver, resets the volume to a known level, and switches to Shield input
"""
    if state.get("media_player.denon_avr_x1300w") != "on":
        media_player.turn_on(entity_id="media_player.denon_avr_x1300w")
        task.wait_until(state_trigger="media_player.denon_avr_x1300w == 'on'", state_hold=2, timeout=15)
        media_player.volume_set(entity_id="media_player.denon_avr_x1300w", volume_level=0.55)
    media_player.select_source(entity_id="media_player.denon_avr_x1300w", source="Shield")

@service
def start_playlist(entity_id="", playlist_uri="", volume_level=None, duration=20):
    """yaml
name: Start Playlist
description: Starts a playlist on the specified device at the specified volume level
fields:
  entity_id:
    description: the name of the media player entity
    example: media_player.living_room_audio
    required: true
  playlist_uri:
    description: the URI of the playlist to play
    example: spotify:playlist:37i9dQZF1DXcBWIGoYBM5M
    required: true
  volume_level:
    description: the volume level to set (0.0 to 1.0)
    example: 0.5
  duration:
    description: duration in seconds for volume fade-in/out
    example: 60
    required: false
"""
    if volume_level is not None:
        log.info(f"Set volume_level {0.01} on {entity_id}")
        media_player.volume_set(entity_id=entity_id, volume_level=0.01)
    media_player.shuffle_set(entity_id=entity_id, shuffle=True)
    music_assistant.play_media(media_id=playlist_uri, enqueue='replace', entity_id=entity_id)
    task.wait_until(state_trigger="{entity_id} == 'playing'".format(entity_id=entity_id), state_hold=2, timeout=15)
    if volume_level is not None:
        script.turn_on(entity_id="script.gradually_set_volume", variables={"volume": volume_level, "duration": duration, "entity_id": entity_id})
        log.info(f"Set volume_level {volume_level} on {entity_id} over {duration} seconds")
        task.sleep(duration)
        set_default_audio_levels(group_name=entity_id)

import requests

@service
def phone_command(key=None, cmd=None):
    """yaml
name: Phone Command
description: Sends an AutoRemote message to tasker using the given API key
fields:
  key:
    description: the API key as given by AutoRemote
    required: true
  cmd:
    description: the command to send
    example: bedtime
    required: true
"""
    url = "https://autoremotejoaomgcd.appspot.com/sendmessage?key=" + key + "&message=" + cmd
    requests.get(url)
from socket import socket

@service
def pc_cmd(cmd=None):
    """yaml
name: PC Command
description: Sends a message to the PC using sockets
fields:
  cmd:
    description: the command to send
    example: shutdown
    required: true
"""
    s = socket()              
    s.connect(('192.168.0.5', 12345))
    s.settimeout(5.0)
    s.send(cmd.encode())
    s.close()
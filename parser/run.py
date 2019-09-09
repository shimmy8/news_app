# -*- coding: utf-8 -*-
import os
import socket

from parser import parse


PARSER_PORT = int(os.getenv('PARSER_PORT', 1111))

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.bind(('', PARSER_PORT))
socket.listen()

while True:
    client, _ = socket.accept()
    while True:
        data = client.recv(255).decode()
        if data:
            if data.strip() == 'parse':
                client.send('started\n'.encode())
                parse()
        break

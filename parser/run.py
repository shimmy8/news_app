# -*- coding: utf-8 -*-
import socket

from parser import parse


socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.bind(('', 1111))
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

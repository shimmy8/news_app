# -*- coding: utf-8 -*-
import os
import socket

from parser import parse


PARSER_PORT = int(os.getenv('PARSER_PORT', 1111))


def run():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('', PARSER_PORT))
    server.listen()

    while True:
        client, _ = server.accept()
        while True:
            data = client.recv(255).decode()
            if data:
                if data.strip() == 'parse':
                    client.send('started\n'.encode())
                    parse()
            break


if __name__ == '__main__':
    run()

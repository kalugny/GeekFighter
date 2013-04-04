"""
keyproxy.py

accepts keystrokes on one computer and transmits to another.

usage: copy this folder to whichever 2 computers and run this
    script on each computer, decide which is the key transmitter
    and which is the key hitter on the printed menu.

NOTE: remember to install SendKeys
NOTE: if you run both server and client on the same computer, it's an infinite loop
    that explodes.
"""

from getch import getch
import SendKeys
import time
import socket

HOST = '169.254.41.165'    # The remote host name or ip address
PORT = 50007              # The port as used by the server


def init_hitter():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_host = '' # any interface
    sock.bind((server_host, PORT))
    sock.listen(1)
    conn, addr = sock.accept()
    print 'Connected by', addr
    return conn
    
def main_hitter():
    conn = init_hitter()
    
    while True:
        data = conn.recv(1)
        SendKeys.SendKeys(data)
        print(data)


def init_transmitter():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    return sock


def main_transmitter():
    sock = init_transmitter()
    while True:
        char = getch()
        print(char)
        sock.send(char)



if __name__ == "__main__":
    print 'Which computer is this?'
    print '1. hitter (this computer needs keys to be hit, start this first)'
    print '2. transmitter (this computer has someone actually hitting the keyboard)'
    choice = getch()
    if choice == '1':
        print 'hitter, starting server'
        main_hitter()
    elif choice == '2':
        print 'transmitter, connecting to server'
        main_transmitter()

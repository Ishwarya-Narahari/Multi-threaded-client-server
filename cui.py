
##
# References:
# https://docs.python.org/3.2/library/socketserver.html#socketserver-udpserver-example
# https://docs.python.org/3.0/library/os.path.html
# https://levelup.gitconnected.com/learn-python-by-building-a-multi-user-group-chat-gui-application-af3fa1017689
#
##

from filewatcher import desync, sync_dirs
import json
import os
import socket
import sys
import threading
import time
import tkinter as tk
from os import stat

import easygui

# globals
HOST, PORT = "localhost", 9999
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
global username
username = ''
local_dirs = []

# Function to log the messages on UI


def log(msg):
    tkDisplay.config(state="normal")
    tkDisplay.insert(tk.END, msg + "\n")
    tkDisplay.config(state="disabled")


def send_command(command, args):
    global username
    send({'command': command, 'args': args, 'username': username})
    print(username)

# Function to send json data


def send(data):
    sock.sendto(bytes(json.dumps(data), "utf-8"), (HOST, PORT))

# Function to receive and parse json data


def rec():
    return json.loads(str(sock.recv(1024), "utf-8"))

# Send Command button handler


def s_c():
    global username
    cmd = entName.get()
    if ('localdir' in cmd):
        local_dirs.append(cmd.split(' ')[1])
        log("directory added for syncing locally")
    elif 'desync' in cmd:
        local_dirs.remove(cmd.split(' ')[1])
        desync(cmd.split(' ')[1], 'cl_'+username)
        log("directory removed")
    elif 'history' in cmd:
        send_command(cmd, '')
    else:
        send_command(cmd.split(' ')[0], cmd.split(' ')[1])


def _exit():
    send_command('exit', username)
    time.sleep(0.5)
    os._exit(0)


# GUI CODE STARTS
window = tk.Tk()
window.title("Client")

topFrame = tk.Frame(window)
lblName = tk.Label(topFrame, text="Command:").pack(side=tk.LEFT)
entName = tk.Entry(topFrame)
entName.pack(side=tk.LEFT)
btnConnect = tk.Button(topFrame, text="Send", command=s_c)
btnConnect.pack(side=tk.LEFT)
btnExit = tk.Button(topFrame, text="Exit", command=lambda: _exit())
btnExit.pack(side=tk.LEFT)
topFrame.pack(side=tk.TOP)

displayFrame = tk.Frame(window)
scrollBar = tk.Scrollbar(displayFrame)
scrollBar.pack(side=tk.RIGHT, fill=tk.Y)
tkDisplay = tk.Text(displayFrame, height=20, width=55)
tkDisplay.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 0))
tkDisplay.tag_config("tag_your_message", foreground="blue")
scrollBar.config(command=tkDisplay.yview)
tkDisplay.config(yscrollcommand=scrollBar.set, background="#F4F6F7",
                 highlightbackground="grey", state="normal")
displayFrame.pack(side=tk.TOP)


bottomFrame = tk.Frame(window)
# GUI CODE ENDS

# Thread to asynchronously log all messages received from server.


# Logic to accept only unique usernames.
while(True):
    username = easygui.enterbox('Enter username:')
    send_command("register", "")
    acc = rec()
    print(acc)
    log('Available home dirs:')
    log(','.join(acc['available dirs']))
    if (acc["res"] == 'accepted'):
        break


def sync():
    [send_command('sync', x) for x in local_dirs]


def _bg_recv():
    while True:
        data = rec()
        if (data['res'] == 'syncData'):
            sync_dirs(data['files'], data['syncDir'], 'cl_'+username)
        elif 'Successful' in data['res']:
            log('Successfully executed')
        elif 'history' in data['res']:
            log('-------------------------------')
            if 'logs' in data.keys():
                log('\n'.join(data['logs']))
            else:
                log(data['res'])
        else:
            log(data['res'])

        time.sleep(0.5)


def _bg():
    while True:
        sync()
        time.sleep(2)


threading.Thread(target=_bg).start()
threading.Thread(target=_bg_recv).start()
window.mainloop()



##
# References:
# https://levelup.gitconnected.com/learn-python-by-building-a-multi-user-group-chat-gui-application-af3fa1017689
#
##

import os
import socketserver
import threading
import tkinter as tk
import server as ss


window = tk.Tk()
window.title("Sever")
window.geometry("500x500")

# Function to log the messages on UI

server = None


def log(msg):
    tkDisplay.config(state="normal")
    tkDisplay.insert(tk.END, msg + "\n")
    tkDisplay.config(state="disabled")


ss.log = log


# Start the server


def _start():
    HOST, PORT = "localhost", 9999
    global server
    server = socketserver.UDPServer((HOST, PORT), ss.Server)
    server.serve_forever()

# Start button handler


def s_s():
    log("Server started")
    t = threading.Thread(target=_start)
    t.setDaemon(True)
    t.start()


# GUI CODE STARTS
topFrame = tk.Frame(window)
btnStart = tk.Button(topFrame, text="Start", command=s_s)
btnStart.pack(side=tk.LEFT)
btnStop = tk.Button(topFrame, text="Stop",
                    command=lambda: os._exit(0))
btnStop.pack(side=tk.LEFT)
topFrame.pack(side=tk.TOP, pady=(5, 0))

clientFrame = tk.Frame(window)
lblLine = tk.Label(
    clientFrame, text="Logs:").pack()
scrollBar = tk.Scrollbar(clientFrame)
scrollBar.pack(side=tk.RIGHT, fill=tk.Y)
tkDisplay = tk.Text(clientFrame, height=30, width=80)
tkDisplay.pack(side=tk.LEFT, fill=tk.X, padx=(2, 0))
scrollBar.config(command=tkDisplay.yview)
tkDisplay.config(yscrollcommand=scrollBar.set, background="#F4F6F7",
                 highlightbackground="grey", state="disabled")
clientFrame.pack(side=tk.BOTTOM, pady=(5, 10))
# GUI CODE ENDS

window.mainloop()

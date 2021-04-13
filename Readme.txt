This project uses Python 3.8 with following dependencies.

- easygui
- json
- socketserver

Run by: python <filename>.py

Files:

sui.py ==> Run this file once to start the server. (Hit start to begin listening for connections.)
cui.py ==> Run this file once for evrey client you want to create.

In every client, 

following commands are supported:

CREATE one/or/many/dirs 
RENAME old,new
MOVE src,dest
LIST ./
LIST dir1/dir2
localdir dir1
desync dir1
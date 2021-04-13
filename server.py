
##
# References:
# https://docs.python.org/3.2/library/socketserver.html#socketserver-udpserver-example
# https://docs.python.org/3.0/library/os.path.html
#
##

import json
import socketserver
import os
import shutil
import filewatcher
from filewatcher import get_dir_files
from oplog import LogNode, OperationLogs

log = None
home_dir_A = 'A'
home_dir_B = 'B'
home_dir_C = 'C'

logs = {}


class Server(socketserver.BaseRequestHandler):

    users = []
    linearCommandLog = []

    # Function to send json data
    def send(self, sock, data):
        sock.sendto(bytes(json.dumps(data), "utf-8"), self.client_address)

    # Function to handle the commands issued by client

    def process_data(self, data):
        print(data)
        user = data['username']
        # When user tries to register, check for duplicate names.
        if data['command'] == 'register':
            if user in self.users:
                return {'res': 'declined'}
            else:
                self.users.append(data['username'])
                logs[data['username']] = OperationLogs(data['username'])
                path = os.path.join('./folders', data['username'])
                if not os.path.exists(path):
                    os.mkdir(path)
                log('client ' + user + ' connected.')
                return {'res': 'accepted', 'available dirs': [home_dir_A, home_dir_B, home_dir_C]}
        elif data['command'] == 'history':
            if user in logs.keys():
                logObj = logs[user]
                t = logObj.get_linear_logs()
                if t == None or len(t) == 0:
                    return {'res': 'No history'}

                return {'res': 'history', 'logs': t}
        elif 'undo' in data['command']:
            if user in logs.keys():
                logObj = logs[user]
                ind, res = logObj.undoIndex(int(data['args']))
                if ind:
                    logObj.store()
                    log('Undo successful')
                else:
                    log('Undo failed')
                return res
        else:
            if user in self.users:
                # Handle all individual commands
                ret = individual_command(data['command'], data['args'], user)
                logs[user].store_command_in_logs(data)
                logs[user].store()
                return ret

    # Function for global client processing by the UDP server.
    def handle(self):
        data = self.request[0].strip()
        if '"sync"' not in str(data):
            log(str(data, "utf-8"))
        data = json.loads(data)

        socket = self.request[1]
        try:
            if (data['command'] == 'exit'):
                log(data['args'] + ' has exited.')
                return
            res = self.process_data(data)

        except Exception as e:
            res = {'res': str(e)}

        # log(json.dumps(res))
        if res != None:
            self.send(socket, res)


def individual_command(command, args, basepath):
    if command == 'create':
        path = os.path.join('./folders/'+basepath, args)
        print(path)
        if os.path.exists(path):
            return {'res': 'Directory already exists'}
        os.makedirs(path)
    elif command == 'delete':
        path = os.path.join('./folders/'+basepath, args)
        os.rmdir(path)
    elif command == 'rename':
        paths = args.split(',')
        if len(paths) != 2:
            return {'res': 'Invalid arg for rename: ' + args}
        src = os.path.join('./folders/'+basepath, paths[0])
        dest = os.path.join('./folders/'+basepath, paths[1])
        os.renames(src, dest)
    elif command == 'move':
        paths = args.split(',')
        if len(paths) != 2:
            return {'res': 'Invalid arg for rename: ' + args}
        src = os.path.join('./folders/'+basepath, paths[0])
        dest = os.path.join('./folders/'+basepath, paths[1])
        shutil.move(src, dest)
    elif command == 'list':
        path = os.path.join('./folders/'+basepath, args)
        li = os.listdir(path)
        return {'res': '\n'.join(li)}
    elif command == 'sync':
        syncDir = args
        resSet = list(get_dir_files(
            os.path.join('./folders', syncDir)))
        print(resSet)
        return {'res': 'syncData', 'syncDir': syncDir, 'files': resSet}
    return {'res': 'Successful'}

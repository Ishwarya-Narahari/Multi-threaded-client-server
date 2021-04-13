import pickle
import os


class LogNode:

    def __str__(self) -> str:
        return self.command_obj['command'] + ' ' + self.command_obj['args']

    def __init__(self, command_obj) -> None:
        self.command_obj = command_obj
        self.mainArg = None
        self.parentCommand = None
        self.dependentLogs = dict()

    def add_dependent(self, new_command):
        currMainArg = self.mainArg
        tmpArg = new_command.get_relevant_mainArg(currMainArg)
        if tmpArg in self.dependentLogs.keys():
            tmpNode = self.dependentLogs[tmpArg]
            tmpNode.add_dependent(new_command)
        else:
            new_command.mainArg = tmpArg
            new_command.parentCommand = self
            self.dependentLogs[tmpArg] = new_command

    def get_relevant_mainArg(self, currentMainArg):
        args = self.command_obj['args']
        if currentMainArg == None:
            return args.split('/')[0]
        else:
            if ',' in args:
                temparr = args.split(',')[0].split('/')
            else:
                temparr = args.split('/')

            if (temparr.index(currentMainArg) == len(temparr)-1):
                return currentMainArg
            else:
                return temparr[temparr.index(currentMainArg)+1:][0]

    def __undo_logic__(self, prefix):
        command = self.command_obj['command']
        oldargs = self.command_obj['args']
        newargs = ''

        if 'create' in command:
            command = 'delete'
            newargs = oldargs

        elif 'delete' in command:
            command = 'create'
            newargs = oldargs

        elif 'rename' in command or 'move' in command:
            t = oldargs.split(',')
            t.reverse()
            newargs = ','.join(t)

        from server import individual_command
        individual_command(command, newargs, prefix)

    def undo(self, prefix) -> list:
        res = []
        print('Undo Called')
        if self.dependentLogs != None:
            for key in list(self.dependentLogs.keys()):
                res += self.dependentLogs[key].undo(prefix)
        self.__undo_logic__(prefix=prefix)
        if self.parentCommand != None:
            self.parentCommand.dependentLogs.pop(self.mainArg)
        res.append(self)
        return res


class OperationLogs:

    def __init__(self, filename_prefix):
        self.linearCommandLog = []
        self.linkedCommandLog = {}
        self.prefix = filename_prefix
        self.load()

    def store(self):
        # if old file exists, delete and create new.
        if os.path.isfile(self.prefix + '_linear.b') and os.path.isfile(self.prefix + '_linked.b'):
            os.remove(self.prefix + '_linear.b')
            os.remove(self.prefix + '_linked.b')

        pickle.dump(self.linearCommandLog,
                    open(self.prefix + '_linear.b', 'wb'))
        pickle.dump(self.linkedCommandLog,
                    open(self.prefix + '_linked.b', 'wb'))

    def load(self):
        # open only if exists
        if os.path.isfile(self.prefix + '_linear.b') and os.path.isfile(self.prefix + '_linked.b'):
            self.linearCommandLog = pickle.load(
                open(self.prefix + '_linear.b', 'rb'))
            self.linkedCommandLog = pickle.load(
                open(self.prefix + '_linked.b', 'rb'))

    def undoIndex(self, ix):
        try:
            if (ix < len(self.linearCommandLog)):
                logNode = self.linearCommandLog.pop(ix)
                ret = logNode.undo(self.prefix)
                if logNode.mainArg in self.linkedCommandLog.keys():
                    self.linkedCommandLog.pop(logNode.mainArg)

                for _, x in enumerate(ret):
                    for i in range(len(self.linearCommandLog)):
                        logNodestr = str(self.linearCommandLog[i])
                        if (str(x) == logNodestr):
                            self.linearCommandLog.pop(i)
                            break
                return True, {'res': 'Undo Result Success', 'message': ''}
        except Exception as ex:
            return False, {'res': 'Undo Result Failed', 'message': str(ex)}

    def get_linear_logs(self):
        return ['Log No: '+str(ind) + ' : ' + str(x) for ind, x in enumerate(self.linearCommandLog)]

    def store_command_in_logs(self, command_obj):
        logNode = LogNode(command_obj)
        tempMainArg = logNode.get_relevant_mainArg(None)

        self.linearCommandLog.append(logNode)
        if tempMainArg not in self.linkedCommandLog.keys():
            self.linkedCommandLog[tempMainArg] = logNode
            logNode.mainArg = tempMainArg
        else:
            tempNode = self.linkedCommandLog[tempMainArg]
            tempNode.add_dependent(logNode)

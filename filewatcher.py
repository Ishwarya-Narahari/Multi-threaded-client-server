import os
import json
import shutil

# Function to get all the files and data in an organized list to create local copies.


def get_dir_files(dir):
    files = os.listdir(dir)
    res = set()
    for f in files:
        working_path = os.path.join(dir, f)
        print(working_path, os.path.isdir(working_path))

        if os.path.isdir(working_path):
            resset = get_dir_files(working_path)
            res = res.union(resset)
            res.add(json.dumps({'path': working_path, 'emptyDir': True}))
        else:
            res.add(json.dumps({'path': working_path, 'emptyDir': False, 'mkdir': working_path.replace(os.path.basename(working_path), ''),
                                'data': open(working_path, 'r').read()}))
    return res

# Function to create the local copies on client side, with input coming from server


def sync_dirs(inputset, sync_dir, base_dir):

    syncPath = os.path.join('.\\local_copies',
                            base_dir, 'folders', sync_dir)
    if os.path.exists(syncPath):
        shutil.rmtree(syncPath, ignore_errors=True)
    for val in inputset:
        print(val)
        vjson = json.loads(val)

        filePath = os.path.join('.\\local_copies', base_dir,   vjson['path'])
        if vjson['emptyDir'] == True:
            if os.path.exists(filePath):
                shutil.rmtree(filePath, ignore_errors=True)
            os.makedirs(filePath)
        else:
            mkdir_path = os.path.join(
                '.\\local_copies', base_dir, vjson['mkdir'])

            if not os.path.exists(mkdir_path):
                os.makedirs(mkdir_path)
            if not os.path.exists(filePath):
                f = open(filePath, 'x')
            else:
                f = open(filePath, 'w')
            f.write(vjson['data'])

# Desync and delete local copy


def desync(dirName, base_dir):
    shutil.rmtree(os.path.join('.\\local_copies',
                               base_dir, 'folders', dirName))

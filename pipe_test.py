import mmap
import win32event
import win32con
import json
import time
import numpy as np


def test():
    shared_mem = mmap.mmap(0,128,'testmap',mmap.ACCESS_READ)
    print('Hello world')
    shared_mem.close()

def test2():
    hWait = win32event.OpenMutex(0x1F0001, False, 'testmapmutex')
    win32event.WaitForSingleObject(hWait, 20000)
    print('Hello world')
    win32event.ReleaseMutex(hWait)

def test3():
    shared_mem = mmap.mmap(0,128,'flag',mmap.ACCESS_WRITE)
    shared_mem.write_byte(1)

def test4():
    shared_mem = mmap.mmap(0,128,'toAgent',mmap.ACCESS_READ)
    print('Hello world')

def test_json():

    now = time.time()

    for i in range(0,6000):
        json_string = '{"State":[[1,10]],"Reward":0,"IsEnded":false,"Info":null}'
        response = json.loads(json_string)
        state = np.asarray(response['State'])
        reward = float(response['Reward'])
        isdone = bool(response['IsEnded'])
        if response['Info'] != None:
            info = dict(response['Info'])
        else:
            info = None

    # m = win32event.OpenMutex(0x1F0001, False, 'cssl_rl_mutex')

    # for i in range(0,6000):
    #     win32event.WaitForSingleObject(m, 2000)
    #     win32event.ReleaseMutex(m)

    dur = time.time() - now
    print('Duration:', dur)

test_json()
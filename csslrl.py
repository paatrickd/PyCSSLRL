import requests
import numpy as np
# import win32event
import mmap
from enum import Enum
import json
import time
import os

class Flag(Enum):
     WAIT = 0
     RESET = 1
     ACT = 2

class rl_layer:

    def __init__(self, path: str):
        self.path = path
        self.mmf_response_length = 1024
        with open(os.path.join(path, 'response')) as fd:
            self.mmf_response = mmap.mmap(fd.fileno(), self.mmf_response_length, access=mmap.ACCESS_READ)
        with open(os.path.join(path, 'action'), 'r+') as fd:
            self.mmf_action = mmap.mmap(fd.fileno(), 4)
        with open(os.path.join(path, 'flag'), 'r+') as fd:
            self.mmf_flag = mmap.mmap(fd.fileno(), 1)
        # self.mmf_action = mmap.mmap(0, 4, 'action', mmap.ACCESS_WRITE)
        # self.mmf_flag = mmap.mmap(0, 1, 'flag', mmap.ACCESS_WRITE)
        # self.mmf_response = mmap.mmap(0, self.mmf_response_length, 'response', mmap.ACCESS_READ)

    def reset(self):
        self.set_flag(Flag.RESET)
        state, reward, isdone, info = self.wait_for_response()
        return state, isdone, info

    def set_flag(self, flag: Flag):
        self.mmf_flag.seek(0)
        self.mmf_flag.write_byte(flag.value)

    def write_action(self, action: int):
        self.mmf_action.seek(0)
        self.mmf_action.write(action.to_bytes(4,'little'))

    def wait_for_response(self):
        while True:
            self.mmf_flag.seek(0)
            flag = self.mmf_flag.read_byte()
            if (flag == Flag.WAIT.value):
                return self.read_response()

    def read_response(self):
        self.mmf_response.seek(0)
        length = self.mmf_response.read_byte()
        if length >= self.mmf_response_length:
            self.mmf_response_length = length + 1
            self.mmf_response = mmap.mmap(0, self.mmf_response_length, 'response', mmap.ACCESS_READ)
            self.mmf_response.seek(1)
        response_raw = self.mmf_response.read(length)
        response = json.loads(response_raw)
        state = np.asarray(response['State'])
        reward = float(response['Reward'])
        isdone = bool(response['IsEnded'])
        if response['Info'] != None:
            info = dict(response['Info'])
        else:
            info = None
        return state, reward, isdone, info

    def act(self, action: int):
        self.write_action(action)
        self.set_flag(Flag.ACT)
        return self.wait_for_response()

    # Web api

    def reset2(self):

        res = requests.get(self.api + '/Reset')
        data = res.json()

        state = np.asarray(data['State'])
        isdone = bool(data['IsEnded'])
        if data['Info'] != None:
            info = dict(data['Info'])
        else:
            info = None

        return state, isdone, info

    def act2(self, action: int):

        # if (type(action) is not int):
        #     raise TypeError(action)
        
        payload = {'action': action}

        res = requests.post(self.api, params=payload)
        data = res.json()

        state = np.asarray(data['State'])
        reward = float(data['Reward'])
        isdone = bool(data['IsEnded'])
        if data['Info'] != None:
            info = dict(data['Info'])
        else: 
            info = None

        return state, reward, isdone, info

    def ping(self):

        res = requests.get(self.api + '/Status')

        return res.ok

    def make(name: str, api_url: str):

        if (type(name) is not str):
            raise TypeError(name)
        elif(type(api_url) is not str):
            raise TypeError(api_url)

        layer = rl_layer('cssl_rl_mutex', 'WINDOWS', api_url)
        return layer

from telegram import bot
import json
import os
from subprocess import Popen, PIPE
import time


class handler:

    __target: bot

    __isListening: bool = False

    __offset: int = 0

    __pipe_path: str = ""

    def __init__(self, target: bot, pipe_path: str, offset: int = 0) -> None:
        self.__target = target
        self.__offset = offset
        self.__pipe_path = pipe_path
        pass

    def listen(self):
        self.__isListening = True
        while self.__isListening:
            updates = self.__target.getUpdates(self.__offset).content.decode()
            updates = json.loads(updates)
            if(bool(updates["ok"])):
                print(updates["result"])    
            pass
        pass

    def stop(self): self.__isListening = False

    def last_update(self): return self.__offset
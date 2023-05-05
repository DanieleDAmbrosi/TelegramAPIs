from telegram import bot
import json
import os
from subprocess import Popen, PIPE
import time
import dotenv, os, threading
import win32pipe, win32file, pywintypes, time
import database

class handler:

    __target: bot

    __isListening: bool = False

    __offset: int = 0

    __pipe_path: str = ""

    __db_handler: database.DatabaseHandler = None

    def __init__(self, target: bot, pipe_path: str, db_handler: database.DatabaseHandler, offset: int = 0) -> None:
        self.__target = target
        self.__offset = offset
        self.__pipe_path = pipe_path
        self.__db_handler = db_handler
        pass

    def listen(self):
        self.__isListening = True

        pipe = self.__create_pipe()

        try:
            while self.__isListening:
                updates = self.__target.getUpdates(self.__offset).content.decode()
                updates = json.loads(updates)
                if(bool(updates["ok"])):
                    self.__print_pipe(pipe, json.dumps(updates["result"]))
                    for update in updates["result"]:
                        if int(update["update_id"]) > self.__offset: self.__offset = int(update["update_id"])
                        
                        pass
                    time.sleep(2)
                pass
        finally:
            self.__close_pipe(pipe)
            self.__isListening = False
        pass

    def stop(self):
        self.__isListening = False
        self.__db_handler.close()

    def last_update(self): return self.__offset

    def __print_pipe(self, pipe, data):
        data = bytes(str.encode(data))
        try:
            win32file.WriteFile(pipe, data)
        except:
            self.__close_pipe(pipe)
        pass

    def __create_pipe(self):
        pipe = win32pipe.CreateNamedPipe(
        self.__pipe_path,
        win32pipe.PIPE_ACCESS_DUPLEX,
        win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
        1, 65536, 65536,
        0,
        None)
        print("waiting for client")
        win32pipe.ConnectNamedPipe(pipe, None)
        print("got client")
        return pipe
    
    def __close_pipe(self, pipe):
         win32file.CloseHandle(pipe)
         pass
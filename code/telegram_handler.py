from telegram import bot
import json
import os
from subprocess import Popen, PIPE
import time
import dotenv, os, threading
import win32pipe, win32file, pywintypes, time
import database

class bot_handler:

    __target: bot

    __isListening: bool = False

    __offset: int = 0

    __pipe_path: str = ""

    __db_handler: database.DatabaseHandler = None

    __chat_handlers: dict = {}

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
                results = self.__get_results()
                if len(results) > 0:
                    threading.Thread(target=self.__handle_results, args=(results)).start()
                self.__print_pipe(pipe, json.dumps(results))
                time.sleep(2)
        finally:
            self.__close_pipe(pipe)
            self.__isListening = False
        pass

    def __get_results(self):
        updates = self.__target.getUpdates(self.__offset).content.decode()
        updates = json.loads(updates)
        if(bool(updates["ok"])):
            for update in updates["result"]:
                if int(update["update_id"]) > self.__offset: self.__offset = int(update["update_id"])
            return updates["result"]
        
    def __handle_results(self, results):
        for result in results:
            message = result["message"]
            id = message["chat"]["id"]
            entities = message.get("entities")
            if entities is None: pass #TO DO:
            else:
                if self.__chat_handlers.get(id) is None:

                    pass
                pass
            pass
        pass

    def __handle_command(self, command):
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
    
class chat_handler():

    pass
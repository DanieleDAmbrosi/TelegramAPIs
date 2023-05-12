from telegram import *
import json
import os
from subprocess import Popen, PIPE
import time
import dotenv, os, threading
import database
import pipe
class bot_handler:

    __target: bot

    __isListening: bool = False

    __offset: int = 0

    __db_handler: database.DatabaseHandler = None

    __out = print
    __consume = lambda: None
    __stop_consume = lambda: None

    __chat_handlers: dict = {}

    def __init__(self, target: bot, pipe_handler: pipe.pipe_handler = None, db_handler: database.DatabaseHandler = None, offset: int = 0) -> None:
        self.__target = target
        self.__offset = offset

        if pipe_handler:
            self.__out = pipe_handler.push_message
            self.__consume = pipe_handler.consume
            self.__stop_consume = pipe_handler.stop #se il pipe handler non esiste scelgo come canale di out la print normale
            
        # self.__pipe_handler.stop = lambda : None
        # self.__pipe_handler.consume = lambda : None
        self.__db_handler = db_handler
        pass

    def listen(self):
        self.__isListening = True
        #threading.Thread(target=self.__pipe_handler.consume).start()
        threading.Thread(target=self.__consume).start()
        try:
            while self.__isListening:
                updates: Update = self.__target.getUpdatesObject(self.__offset)
                for update in updates:
                    if update._update_id > self.__offset: self.__offset = update._update_id
                    #self.__pipe_handler.push_message(repr(update))
                    self.__out(repr(update))
                    self.__handle_update(update)
                    pass
        finally:
            if self.__isListening: self.stop()
        pass

    def __handle_update(self, update: Update):
        message: Message = update._message
        chat: Chat = message._chat
        if chat._id not in self.__chat_handlers:
            self.__chat_handlers[chat._id] = chat_handler(chat._id)
        self.__chat_handlers[chat._id].handle(message)
        pass

    def stop(self):
        self.__stop_consume()
        self.__db_handler.close()
        self.__isListening = False

    def last_update(self): return self.__offset

class chat_handler:
    _chat_id: int

    def __init__(self, chat_id: int) -> None:
        self._chat_id = chat_id
        pass

    def handle(self, message: Message):
        pass
    pass
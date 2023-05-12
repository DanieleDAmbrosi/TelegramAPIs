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

    __pipe_handler: pipe.pipe_handler

    __db_handler: database.DatabaseHandler = None

    __chat_handlers: dict = {}

    def __init__(self, target: bot, pipe_handler: pipe.pipe_handler = None, db_handler: database.DatabaseHandler = None, offset: int = 0) -> None:
        self.__target = target
        self.__offset = offset
        self.__pipe_handler = pipe_handler
        self.__db_handler = db_handler
        pass

    def listen(self):
        self.__isListening = True
        pipe = self.__create_pipe()

        try:
            while self.__isListening:
                updates: Update = self.__target.getUpdatesObject(self.__offset)
                for update in updates:
                    if update._update_id > self.__offset: self.__offset = update._update_id
                    self.__print_pipe(pipe, repr(update))
                    self.__handle_update(update)
                    pass
        finally:
            self.__close_pipe(pipe)
            self.stop()
        pass

    def __handle_update(self, update: Update):
        message: Message = update._message
        chat: Chat = message._chat
        if chat._id not in self.__chat_handlers:
            self.__chat_handlers[chat._id] = chat_handler(chat._id)
        self.__chat_handlers[chat._id].handle(message)
        pass

    def stop(self):
        self.__isListening = False
        self.__db_handler.close()

    def last_update(self): return self.__offset

class chat_handler:
    _chat_id: int

    def __init__(self, chat_id: int) -> None:
        self._chat_id = chat_id
        pass

    def handle(message: Message):
        pass
    pass
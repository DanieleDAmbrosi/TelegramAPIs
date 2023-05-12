from .......users.danie.documents.github.telegramapis.code_test.telegram import Message
from .......users.danie.documents.github.telegramapis.code_test.telegram import Message
from .......users.danie.documents.github.telegramapis.code_test.telegram import Message
from telegram import *
import json
import os
from subprocess import Popen, PIPE
import time
import dotenv, os, threading
import database
import pipe
class BotHandler:

    __target: Bot

    __isListening: bool = False

    __offset: int = 0

    __db_handler: database.DatabaseHandler = None

    __out = print
    __consume = lambda: None
    __stop_consume = lambda: None

    __chat_handlers: dict = {}

    def __init__(self, target: Bot, pipe_handler: pipe.PipeHandler = None, db_handler: database.DatabaseHandler = None, offset: int = 0) -> None:
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
            self.__chat_handlers[chat._id] = ChatHandler(chat._id)
        self.__chat_handlers[chat._id].handle(message)
        pass

    def stop(self):
        self.__stop_consume()
        self.__db_handler.close()
        self.__isListening = False

    def last_update(self): return self.__offset

class ChatHandler():
    _chat_id: int

    def __init__(self, chat_id: int) -> None:
        self._chat_id = chat_id
        pass

    def handle(self, message: Message):
        simple = self.simple_message(message)
        pass
    pass

class Handler():
    def handle(self, message: Message):
        pass
    pass

class ConcreteHandler(Handler):
    def handle(self, message: Message):
        #do something with message
        pass

class Decorator(Handler):
    def __init__(self, handler: Handler) -> None:
        self._handler = handler
        pass

    def handler(self) -> Handler:
        return self._handler
    
    def handle(self, message: Message):
        return self._handler.handle()
    pass

class DecoratorBefore(Decorator):
    def handle(self, message: Message):
        #do something
        return f"DecoratorBefore({self.handler.handle(message)})"
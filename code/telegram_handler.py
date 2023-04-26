from telegram import bot
import json

class handler:

    __target: bot

    __isListening: bool = False

    __offset: int = 0

    def __init__(self, target: bot, offset: int = 0) -> None:
        self.__target = target
        self.__offset = offset
        pass

    def listen(self):
        self.__isListening = True
        while self.__isListening:
            messages = self.__target.getUpdates(self.__offset).content
            #messages = json.load(messages)
            print(messages)
            pass
        pass

    def stop(self): self.__isListening = False
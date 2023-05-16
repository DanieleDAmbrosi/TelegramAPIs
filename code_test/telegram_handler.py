from __future__ import annotations
from telegram import *
from subprocess import Popen, PIPE
from typing import Any
import threading
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
        ans = self.__chat_handlers[chat._id].handle(message)
        self.__target.sendMessage(chat._id, ans)
        pass

    def stop(self):
        self.__stop_consume()
        self.__db_handler.close()
        self.__isListening = False

    def last_update(self): return self.__offset

class ChatHandler():
    _chat_id: int
    _consume: float = None # l/km
    _location: Location = None ##

    def __init__(self, chat_id: int) -> None:
        self._chat_id = chat_id
        cor = CommandHandleStart()
        self._handler = WaitCommandDecorator(BaseDecorator(MessageHandler()), cor)
        pass

    def handle(self, message: Message):
        self._handler, ans = self._handler.handle(message, self)
        print(type(self._handler))
        #self._handler._cor.get_commands([])
        return ans

    pass


from abc import ABC, abstractmethod

class ICommandHandler(ABC):
    @abstractmethod
    def set_next(self, command: ICommandHandler) -> ICommandHandler:
        pass

    @abstractmethod
    def handle(self, request):
        pass

    @abstractmethod
    def get_commands(self, command):
        pass

    @abstractmethod
    def get_last(self):
        pass

    @abstractmethod
    def reset(self):
        pass

class CommandHandler(ICommandHandler):
    _next_handler: ICommandHandler = None
    _command: str = ""

    def set_next(self, command: ICommandHandler) -> CommandHandler:
        self._next_handler = command
        return command

    @abstractmethod
    def handle(self, message: Message, command: str) -> Any:
        if self._next_handler:
            return self._next_handler.handle(message, command)
        return None, "Command not found" #-> next_handler, risposta
    pass

    def get_commands(self, command: list[str] = []) -> list[str]:
        command.append(self._command)
        if self._next_handler:
            return self._next_handler.get_commands(command)
        return command
    pass

    def get_last(self):
        if self._next_handler:
            return self._next_handler.get_last()
        return self
    
    def reset(self):
        if self._next_handler:
            self._next_handler.reset()
        self._next_handler = None

class CommandHandleStart(CommandHandler): #prima di ricevere /start ignora tutto
    _command = "/start"
    def handle(self, message: Message, command: str) -> Any:
        if self._command == command.lower():
            #return WaitName, f"[CommandName] What's your name?"
            return WaitCommandDecorator, "Harry Botter greats you"
        else:
            return super().handle(message, command)
        
class CommandHandleRegisterVehicle(CommandHandler):
    _command = "/register"
    def handle(self, message: Message, command: str) -> Any:
        if self._command == command.lower():
            #return WaitName, f"[CommandName] What's your name?"
            return WaitCarDataDecorator, "Please insert your car consume [l/km]"
        else:
            return super().handle(message, command)
        
class CommandHandleGetServiceStation(CommandHandler):
    _command = "/find"
    def handle(self, message: Message, command: str) -> Any:
        if self._command == command.lower():
            #return WaitName, f"[CommandName] What's your name?"
            return WaitLocationDataDecorator, "TO DO"
        else:
            return super().handle(message, command)
        
class CommandHandleGetPosition(CommandHandler):
    _command = "/locate"
    def handle(self, message: Message, command: str) -> Any:
        if self._command == command.lower():
            #return WaitName, f"[CommandName] What's your name?"
            return WaitLocationDataDecorator, "Please share your position with me"
        else:
            return super().handle(message, command)
        
class CommandHandleGetLivePosition(CommandHandler):
    _command = "/locate_live"
    def handle(self, message: Message, command: str) -> Any:
        if self._command == command.lower():
            #return WaitName, f"[CommandName] What's your name?"
            return WaitLocationDataDecorator, "Please share your live position with me"
        else:
            return super().handle(message, command)
        
command_handlers = [
    CommandHandleStart(),
    CommandHandleGetServiceStation(),
    CommandHandleRegisterVehicle(),
    CommandHandleGetPosition(),
    CommandHandleGetLivePosition()
]

class MessageHandler():
    def handle(message):
        return message

class BaseDecorator():
    def __init__(self, handler: MessageHandler) -> None:
        self._handler = handler
        pass

    def handler(self):
        return self._handler
    
    def handle(self, message):
        return self.handler().handle(message)
    
    pass

class WaitCommandDecorator(BaseDecorator):
    _cor: CommandHandler

    def __init__(self, handler: BaseDecorator, cor: CommandHandler) -> None:
        self._cor = cor
        super().__init__(handler)

    def handle(self, message: Message, chatHandler: ChatHandler) -> BaseDecorator:
        if not message._entities: return self, "Aspettato: comando"#non ci sono comandi
        e = message._entities[0]
        command = message._text[e._offset:e._offset+e._length]
        r, ans = self._cor.handle(message, command)
        #self.handler().handle(ans)
        if r:
            if r == WaitCommandDecorator:
                commands = CommandHandleStart()
                commands.reset()
                print(commands.get_commands())
                for h in command_handlers[1:]:
                    c = h.__class__
                    h = c()
                    commands.get_last().set_next(h)
                print(commands.get_commands())
                return r(self.handler(), commands), ans
            else: return r(WaitGenericDataDecorator(self.handler)), ans
        else: return self, ans

class WaitGenericDataDecorator(BaseDecorator):
    def __init__(self, handler: BaseDecorator) -> None:
        super().__init__(handler)

    def handle(self, data: str) -> BaseDecorator:
        if data:
            self.handler().handle(data)
        return self.handler() #self.handler() = base decorator
    
class WaitCarDataDecorator(WaitGenericDataDecorator):
    def is_float(self, string):
        try:
            float(string)
            return True
        except ValueError:
            return False

    def __init__(self, handler: WaitGenericDataDecorator) -> None:
        super().__init__(handler)

    def handle(self, message: Message, chatHandler: ChatHandler) -> WaitGenericDataDecorator:
        ret = self
        ans = "The data you submitted is not valid"
        if message._text:
            consume = message._text
            if self.is_float(consume):
                commands = CommandHandleStart()
                commands.set_next(CommandHandleGetServiceStation()).set_next(CommandHandleRegisterVehicle())
                ret = WaitCommandDecorator(self.handler(), commands)
                chatHandler._consume = float(consume)
                ans = "The consume ratio was successfully updated"
        else: self.handler().handle(None)
        return ret, ans

    
class WaitLocationDataDecorator(WaitGenericDataDecorator):
    def __init__(self, handler: WaitGenericDataDecorator) -> None:
        super().__init__(handler)

    def handle(self, message: Message, chatHandler: ChatHandler) -> WaitGenericDataDecorator:
        ret = self
        ans = "The data you submitted is not valid"
        if message._location:
            commands = CommandHandleStart()
            commands.set_next(CommandHandleGetServiceStation()).set_next(CommandHandleRegisterVehicle())
            ret = WaitCommandDecorator(self.handler(), commands)
            ans = "The location was successfully updated"
            chatHandler._location = message._location
        else: self.handler().handle(None)
        return ret, ans
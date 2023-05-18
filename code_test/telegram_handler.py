from __future__ import annotations
from telegram import *
from subprocess import Popen, PIPE
from typing import Any
import threading
import database
import pipe
import time


class BotHandler:
    __target: Bot

    __isListening: bool = False

    __offset: int = 0

    __db_handler: database.DatabaseHandler = None

    __out = print
    __consume = lambda: None
    __stop_consume = lambda: None

    __chat_handlers: dict[int, ChatHandler] = {}

    def __init__(
        self,
        target: Bot,
        pipe_handler: pipe.PipeHandler = None,
        db_handler: database.DatabaseHandler = None,
        offset: int = 0,
    ) -> None:
        self.__target = target
        self.__offset = offset

        if pipe_handler:
            self.__out = pipe_handler.push_message
            self.__consume = pipe_handler.consume
            self.__stop_consume = (
                pipe_handler.stop
            )  # se il pipe handler non esiste scelgo come canale di out la print normale

        # self.__pipe_handler.stop = lambda : None
        # self.__pipe_handler.consume = lambda : None
        self.__db_handler = db_handler
        pass

    def listen(self):
        self.__isListening = True
        # threading.Thread(target=self.__pipe_handler.consume).start()
        threading.Thread(target=self.__consume).start()
        try:
            while self.__isListening:
                updates: list[Update] = self.__target.getUpdatesObject(self.__offset)
                for update in updates:
                    if update._update_id > self.__offset:
                        self.__offset = update._update_id
                    # self.__pipe_handler.push_message(repr(update))
                    self.__out(update._message._text)
                    self.__handle_update(update)
                    pass
        finally:
            if self.__isListening:
                self.stop()
        pass

    def __handle_update(self, update: Update):
        message: Message = update._message
        chat: Chat = message._chat
        if chat._id not in self.__chat_handlers.keys():
            self.__chat_handlers[chat._id] = ChatHandler(chat._id, self, 30)
        self.__chat_handlers[chat._id].handle(message)
        pass

    def stop(self):
        self.__stop_consume()
        self.__db_handler.close()
        self.__isListening = False
        for chat in self.__chat_handlers.copy().values():
            chat.stop()

    def last_update(self):
        return self.__offset

    def update(self, chat: ChatHandler):
        if chat._chat_id in self.__chat_handlers.keys():
            if not chat._running:
                self.__target.sendMessage(chat._chat_id, "You have been disconnected")
                self.__chat_handlers.pop(chat._chat_id)
        pass

    def sendMessage(self, chat_id: int, text: str):
        self.__target.sendMessage(chat_id, text)

    def sendLocation(self, chat_id: int, latitude: float, longitude: float):
        self.__target.sendLocation(chat_id, latitude, longitude)

    def setCommands(self, commands):
        self.__target.setCommands(commands)

    def get_db(self):
        return self.__db_handler

class ChatHandler:
    _chat_id: int
    _consume: float = None  # l/km
    _location: Location = None  ##
    _telegram: BotHandler = None
    _running: bool = False
    _last_update: float = 0.0
    AFK_RESET: float = 5 * 60
    STARTING_COMMANDS: dict = {}

    def __init__(
        self, chat_id: int, telegram: BotHandler, AFK_RESET: int = 300
    ) -> None:
        self._chat_id = chat_id
        cor = CommandHandleStart()
        self._handler = WaitCommandDecorator(BaseDecorator(MessageHandler()), cor)
        self._telegram = telegram
        self._running = True
        self._last_update = time.time()
        self.AFK_RESET = AFK_RESET
        threading.Thread(target=self.afk, args=[self._last_update]).start()
        self.STARTING_COMMANDS = {
            "commands": [
                {
                    "command": "start",
                    "description": "Start the bot",
                },
                {
                    "command": "explain",
                    "description": "Describes the bot",
                },
            ],
            "scope": {"type": "chat", "chat_id": self._chat_id},
            "language_code": "",
        }
        self._telegram.setCommands(self.STARTING_COMMANDS)
        pass

    def handle(self, message: Message):
        self._handler = self._handler.handle(message, self)
        if not self._handler:
            self.stop()
        self._last_update = message._date
        try:
            commands = []
            for c in self._handler._cor.get_commands([]):
                if c != "":
                    commands.append({"command": str(c), "description": str(c).replace("/", "")})
            comms = {
                "commands": commands,
                "scope": {"type": "chat", "chat_id": self._chat_id},
                "language_code": "",
            }
            self._telegram.setCommands(comms)
        except AttributeError:
            pass

    def afk(self, last_update: float):
        time.sleep(self.AFK_RESET + self.AFK_RESET * 0.10 - 15)
        if not self._running: return
        self.sendMessage("You will be disconnected in 15 seconds")
        time.sleep(15)
        current_time = time.time()
        if current_time - self._last_update < self.AFK_RESET + self.AFK_RESET * 0.10 and self._running:
            threading.Thread(target=self.afk, args=[self._last_update]).start()
        else:
            self.stop()

    def stop(self):
        self._running = False
        self._telegram.setCommands(self.STARTING_COMMANDS)
        self.notify()
        pass

    def notify(self):
        self._telegram.update(self)
        pass

    def get_impianti(self):
        if not self._location or not self._consume: return None
        db=database.Database("./data/data.db")
        lat = self._location._latitude
        lon = self._location._longitude
        rad = 50
        dbh = self._telegram.get_db()
        dbh.connect(db, ["impianti","prezzi"])
        res = dbh.exec(f"""SELECT *
FROM impianti join prezzi on impianti.idImpianto = prezzi.idImpianto
WHERE descCarburante LIKE '%'
    AND (acos(sin({lat})*sin( Latitudine )+cos({lat})*cos( Latitudine )*cos( Longitudine - {lon}))*6371) < {rad}
ORDER BY (acos(sin({lat})*sin( Latitudine )+cos({lat})*cos( Latitudine )*cos( Longitudine - {lon}))*6371) ASC""")
        return res

    pass

    def sendMessage(self, text: str):
        self._telegram.sendMessage(self._chat_id, text)

    def sendLocation(self, latitude: float, longitude: float):
        self._telegram.sendLocation(self._chat_id, latitude, longitude)

    def setCommands(self, commands):
        self._telegram.setCommands(commands)


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

    @abstractmethod
    def set_next_chain(self):
        pass


class CommandHandler(ICommandHandler):
    def __init__(self) -> None:
        self._next_handler = None

    _next_handler: ICommandHandler = None
    _command: str = ""

    def set_next(self, command: ICommandHandler) -> CommandHandler:
        self._next_handler = command
        return command

    def set_next_chain(self, command: list[ICommandHandler], n=0) -> CommandHandler:
        self._next_handler = None
        if n < len(command):
            self._next_handler = command[n]
            self._next_handler.set_next_chain(command, n + 1)
        # print(f"Settato {self._command}, iter: {n}")

    def handle(self, message: Message, command: str, chat: ChatHandler) -> Any:
        if self._next_handler:
            return self._next_handler.handle(message, command, chat)
        chat.sendMessage("WTF are you saying m' dude")
        return None  # -> next_handler, risposta

    pass

    def get_commands(self, command: list[str] = []) -> list[str]:
        command.append(self._command)
        # print(f"{self}, {len(command)}")
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


class CommandHandleStart(CommandHandler):  # prima di ricevere /start ignora tutto
    def __init__(self) -> None:
        super().__init__()

    _command = "/start"

    def handle(self, message: Message, command: str, chat: ChatHandler) -> Any:
        if self._command == command.lower():
            # return WaitName, f"[CommandName] What's your name?"
            chat.sendMessage("Hey guys we have a gift for you...")
            chat.sendMessage("WAIT, This is not how it looks")
            chat.sendMessage("Welcome to the chamber of secrets")
            return WaitCommandDecorator
        else:
            return super().handle(message, command, chat)


class CommandHandleStop(CommandHandler):  # prima di ricevere /start ignora tutto
    def __init__(self) -> None:
        super().__init__()

    _command = "/stop"

    def handle(self, message: Message, command: str, chat: ChatHandler) -> Any:
        if self._command == command.lower():
            chat.sendMessage("Goodbye my dearest friend")
            chat.stop()
            return None
        else:
            return super().handle(message, command, chat)


class CommandHandleRegisterVehicle(CommandHandler):
    def __init__(self) -> None:
        super().__init__()

    _command = "/register"

    def handle(self, message: Message, command: str, chat: ChatHandler) -> Any:
        if self._command == command.lower():
            # return WaitName, f"[CommandName] What's your name?"
            chat.sendMessage("How much does it take for you broom to fly? [l/km]")
            return WaitCarDataDecorator
        else:
            return super().handle(message, command, chat)


class CommandHandleGetServiceStation(CommandHandler):
    def __init__(self) -> None:
        super().__init__()

    _command = "/find"

    class Impianto:
        prezzi: dict[str, float] = {}
        lat: float
        lon: float
        nome: str
        bandiera: str

        def __str__(self) -> str:
            str_prezzi = ""
            for key, value in self.prezzi.items():
                str_prezzi += f"prezzo {key}: {str(value)}\n\r" 
            return f"Impianto: {self.nome}\n\rBandiera: {self.bandiera}\n\r{str_prezzi}"

    def handle(self, message: Message, command: str, chat: ChatHandler) -> Any:
        if self._command == command.lower():
            # return WaitName, f"[CommandName] What's your name?"
            res = chat.get_impianti()
            if not res: chat.sendMessage("Not all parameters are setted")
            elif len(res) == 0: chat.sendMessage("No results")
            else:
                impianti: dict[int, self.Impianto] = {}
                for r in res:
                    id = r["idImpianto"]
                    if id not in impianti.keys():
                        impianti[id] = self.Impianto()
                        impianti[id].lat = float(r["Latitudine"])
                        impianti[id].lon = float(r["Longitudine"])
                        impianti[id].nome = r["Nome"]
                        impianti[id].bandiera = r["Bandiera"]
                    impianti[id].prezzi[r["descCarburante"]] = float(r["prezzo"])
                for imp in list(impianti.values())[:2]:
                    chat.sendLocation(imp.lat, imp.lon)
                    chat.sendMessage(str(imp))

            return WaitCommandDecorator
        else:
            return super().handle(message, command, chat)


class CommandHandleGetPosition(CommandHandler):
    def __init__(self) -> None:
        super().__init__()

    _command = "/locate"

    def handle(self, message: Message, command: str, chat: ChatHandler) -> Any:
        if self._command == command.lower():
            # return WaitName, f"[CommandName] What's your name?"
            chat.sendMessage("Send me you position baby girl, don't be shy :PPP")
            return WaitLocationDataDecorator
        else:
            return super().handle(message, command, chat)


# class CommandHandleGetLivePosition(CommandHandler):
#     def __init__(self) -> None:
#         super().__init__()
#     _command = "/locate_live"
#     def handle(self, message: Message, command: str) -> Any:
#         if self._command == command.lower():
#             #return WaitName, f"[CommandName] What's your name?"
#             return WaitLocationDataDecorator, "Please share your live position with me"
#         else:
#             return super().handle(message, command)

command_handlers = [
    CommandHandleGetServiceStation,
    CommandHandleRegisterVehicle,
    CommandHandleGetPosition,
    # CommandHandleGetLivePosition,
    CommandHandleStop,
]


class MessageHandler:
    def handle(message):
        return message


class BaseDecorator:
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

    def __init__(self, handler: BaseDecorator, cor: CommandHandler = None) -> None:
        commands = CommandHandler()
        commands.set_next_chain([c() for c in command_handlers])
        self._cor = cor if cor else commands
        super().__init__(handler)

    def handle(self, message: Message, chat: ChatHandler) -> BaseDecorator:
        if not message._entities:
            chat.sendMessage(f"Command expected")
            return self  # non ci sono comandi
        e = message._entities[0]
        command = message._text[e._offset : e._offset + e._length]
        r = self._cor.handle(message, command, chat)
        # self.handler().handle(ans)

        if not r:
            return self
        elif r != WaitCommandDecorator:
            return r(WaitGenericDataDecorator(self.handler()))
        return r(self.handler())


class WaitGenericDataDecorator(BaseDecorator):
    def __init__(self, handler: BaseDecorator) -> None:
        super().__init__(handler)

    def handle(self, data: str) -> BaseDecorator:
        if data:
            self.handler().handle(data)
        return self.handler()  # self.handler() = base decorator


class WaitCarDataDecorator(WaitGenericDataDecorator):
    def is_float(self, string):
        try:
            float(string)
            return True
        except ValueError:
            return False

    def __init__(self, handler: WaitGenericDataDecorator) -> None:
        super().__init__(handler)

    def handle(self, message: Message, chat: ChatHandler) -> WaitGenericDataDecorator:
        ret = self
        ans = "The data you submitted is not valid"
        if message._text:
            consume = message._text
            if self.is_float(consume):
                ret = WaitCommandDecorator(self.handler())
                chat._consume = float(consume)
                ans = "The consume ratio was successfully updated"
        else:
            self.handler().handle(None)
        chat.sendMessage(ans)
        return ret


class WaitLocationDataDecorator(WaitGenericDataDecorator):
    def __init__(self, handler: WaitGenericDataDecorator) -> None:
        super().__init__(handler)

    def handle(self, message: Message, chat: ChatHandler) -> WaitGenericDataDecorator:
        ret = WaitCommandDecorator(self.handler())
        ans = "Fucking whore"
        if message._location:
            ans = "Very good baby, very good"
            chat.sendMessage(ans)
            chat._location = message._location
        else:
            self.handler().handle(None)
        return ret

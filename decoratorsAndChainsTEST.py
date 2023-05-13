from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Optional

class ICommand(ABC):
    @abstractmethod
    def set_next(self, command: ICommand) -> ICommand:
        pass

    @abstractmethod
    def handle(self, request):
        pass

class Command(ICommand):
    _next_handler: Handler = None

    def set_next(self, command: ICommand) -> Command:
        self._next_handler = command
        return command

    @abstractmethod
    def handle(self, request: Any) -> str:
        if self._next_handler:
            return self._next_handler.handle(request)
        return None, "[GenericCommand] Command not found"
    pass

class CommandName(Command):
    def handle(self, request: Any) -> str:
        print("checking 4 name")
        if request == "/name":
            return WaitName, f"[CommandName] What's your name?"
        else:
            return super().handle(request)
        
class CommandAge(Command):
    def handle(self, request: Any) -> str:
        print("checking 4 age")
        if request == "/age":
            return WaitAge, f"[CommandAge] How old are you?"
        else:
            return super().handle(request)

class IHandler():
    def handle(self, message: str):
        pass
    pass

class Handler(IHandler):
    def handle(self, message: str):
        print(message)
        return None

class BaseDecorator(IHandler):
    def __init__(self, handler: IHandler) -> None:
        self._handler = handler
        pass

    def handler(self) -> IHandler:
        return self._handler
    
    def handle(self, message: str):
        return self._handler.handle(message)
    pass

class WaitCommand(BaseDecorator):
    _cor: Command

    def __init__(self, handler: IHandler, cor: Command) -> None:
        self._cor = cor
        super().__init__(handler)

    def handle(self, message: str) -> BaseDecorator:
        # if(message == "/name"):
        #     ans = "What's your name?"
        #     self.handler().handle(ans + f", {self._cor}")
        #     r = WaitName(WaitData(self.handler()))
        # elif (message == "/age"):
        #     ans = "How old are you?"
        #     self.handler().handle(ans + f", {self._cor}")
        #     r = WaitAge(WaitData(self.handler())) #self.handler() = base decorator
        # else: self.handler().handle(ans + f", {self._cor}")
        r, ans = self._cor.handle(message)
        self.handler().handle(ans)
        if r:
            return r(WaitData(self.handler()))
        else: return self

class WaitData(BaseDecorator):
    def handle(self, message: str) -> BaseDecorator:
        ans = f"{message}"
        self.handler().handle(ans)
        return self.handler() #self.handler() = base decorator
    
class WaitAge(WaitData):
    def handle(self, message: str) -> tuple[WaitData, None]:
        ans = f"Wow, you look younger than a {message} year old"
        base = self.handler().handle(ans)
        age = CommandAge()
        name = CommandName()
        name.set_next(age)
        return WaitCommand(base, name) #self.handler() = wait data
    
class WaitName(WaitData):
    def handle(self, message: str) -> tuple[WaitData, None]:
        ans = f"Nice to meet you {message}"
        base = self.handler().handle(ans)
        age = CommandAge()
        name = CommandName()
        name.set_next(age)
        return WaitCommand(base, name) #self.handler() = wait data


age = CommandAge()
name = CommandName()
name.set_next(age)
h = WaitCommand(BaseDecorator(Handler()), age)

messages = ["/age", "18", "/name", "Daniele", "/age", "20", "/ciao"]
for message in messages:
    h = h.handle(message)
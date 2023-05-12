class Handler():
    def handle(self, message: str):
        pass
    pass

class ConcreteHandler(Handler):
    def handle(self, message: str):
        return message

class Decorator(Handler):
    def __init__(self, handler: Handler) -> None:
        self._handler = handler
        pass

    def handler(self) -> Handler:
        return self._handler
    
    def handle(self, message: str):
        return self._handler.handle(message)
    pass

def getOne(decorator: Decorator):
    return Decorator1(decorator)

def getTwo(decorator: Decorator):
    return Decorator2(decorator)

def getThree(decorator: Decorator):
    return Decorator3(decorator)

next = {
    "1": getTwo,
    "2": getThree,
    "3": getOne
}

class Decorator1(Decorator):
    def handle(self, message: str) -> Decorator:
        r = self
        if(message == "1"):
            print("IT'S MY TURN! (1)")
            r = next[message](self.handler())
        else:
            print ("WAITING FOR MY TURN (1)")
        #print("AFTER" + self.handler().handle(message))
        return r


class Decorator2(Decorator):
    def handle(self, message: str) -> Decorator:
        r = self
        if(message == "2"):
            print("IT'S MY TURN! (2)")
            r = next[message](self.handler())
        else:
            print ("WAITING FOR MY TURN (2)")
        #print("AFTER" + self.handler().handle(message))
        return r
    
class Decorator3(Decorator):
    def handle(self, message: str) -> Decorator:
        r = self
        if(message == "3"):
            print("IT'S MY TURN! (3)")
            r = next[message](self.handler())
        else:
            print ("WAITING FOR MY TURN (3)")
        #print("AFTER" + self.handler().handle(message))
        return r
    
a = ConcreteHandler()

b = Decorator(a)

c = Decorator3(b)

messages = ["1", "2", "3", "1", "2", "3"]
for message in messages:
    print(f"Turn: {message}")
    c = c.handle(message)
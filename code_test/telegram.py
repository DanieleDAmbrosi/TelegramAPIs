import requests, json

class Entity:
    __offset: int = 0
    __length: int = 0
    __type: str = ""

    def __init__(self, offset, length, type) -> None:
        self.__offset = offset
        self.__length = length
        self.__type = type
        pass

    # @classmethod
    # def fromJson(self, offset, length, type):
    #     entity = Entity()
    #     entity.__offset = offset
    #     entity.__length = length
    #     entity.__type = type
    #     return entity
    pass

class User:
    __id: int = 0
    __is_bot: bool = False
    __first_name: str = ""
    __last_name: str = ""
    __username: str = ""
    __language_code: str = ""

    def __init__(self, id, is_bot, first_name, last_name, username, language_code) -> None:
        self.__id = id
        self.__is_bot = is_bot
        self.__first_name = first_name
        self.__last_name = last_name
        self.__username = username
        self.__language_code = language_code
        pass

    # @classmethod
    # def fromJson(self, id, is_bot, first_name, last_name, username, language_code):
    #     user = User()
    #     user.__id = id
    #     user.__is_bot = is_bot
    #     user.__first_name = first_name
    #     user.__last_name = last_name
    #     user.__username = username
    #     user.__language_code = language_code
    #     return user
    pass

class Chat:
    __id: int = 0
    __first_name: str = ""
    __last_name: str = ""
    __username: str = ""
    __type: str = ""

    def __init__(self, id, first_name, last_name, username, type):
        self.__id = id
        self.__first_name = first_name
        self.__last_name = last_name
        self.__username = username
        self.__type = type
        pass

    # @classmethod
    # def fromJson(self, id, first_name, last_name, username, type):
    #     chat = Chat()
    #     chat.__id = id
    #     chat.__first_name = first_name
    #     chat.__last_name = last_name
    #     chat.__username = username
    #     chat.__type = type
    #     return chat
    pass

class Message:
    __message_id: int = 0
    __from: User
    __chat: Chat
    __text: str
    __entities: list[Entity]
    __date: int

    def __init__(self, message_id: int, _from: dict, chat: dict, text: str, date: int, entities: list[dict] = []) -> None:
        self.__message_id = message_id
        self.__from = User(**_from)
        self.__chat = Chat(**chat)
        self.__text = text
        self.__entities = [Entity(**entity) for entity in entities]
        self.__date = date
        pass

    # @classmethod
    # def fromJson(self, message_id: int, _from: dict, chat: dict, text: str, date: int, entities: list[dict] = []):
    #     message = Message()
    #     message.__message_id = message_id
    #     message.__from = User.fromJson(**_from)
    #     message.__chat = Chat.fromJson(**chat)
    #     message.__text = text
    #     message.__entities = [Entity(**entity) for entity in entities]
    #     message.__date = date
    #     return message
    pass    

class Update:
    __update_id: int = 0
    __message: Message

    def __init__(self, update_id: int, message: dict) -> None:
        self.__update_id = update_id
        if("from" in message.keys()):
            message["_from"] = message.pop("from")
        self.__message = Message(**message)
        pass

    # @classmethod
    # def fromJson(self, update_id: int, message: dict):
    #     update = Update()
    #     update.__update_id = update_id
    #     message["_from"] = message.pop("from")
    #     update.__message = Message(**message)
    #     print(update.__message)
    #     return update
    pass

class bot:
    def __init__(self, token):
        self.token = token
        self.__link = f"https://api.telegram.org/bot{token}"
        pass

    def link(self) -> str:
        return self.__link
    
    def getMe(self):
        return requests.get(f"{self.__link}/getMe")
    
    def getUpdates(self, offset):
        offset = (0,offset)[offset>0]
        updates = requests.get(f"{self.__link}/getUpdates?offset={offset + 1}").content.decode()
        updates = json.loads(updates)
        if(bool(updates["ok"])):
            return updates["result"]
        else:
            return []
        
    def getUpdatesObject(self, offset) -> list[Update]:
        offset = (0,offset)[offset>0]
        updates = requests.get(f"{self.__link}/getUpdates?offset={offset + 1}").content.decode()
        updates = json.loads(updates)
        if(bool(updates["ok"])):
            return [Update(**update) for update in updates["result"]]
        else:
            return []
    
    def setCommands(self, commands):
        return requests.post(f"{self.__link}/setMyCommands", json=commands)

    def getCommands(self, scope = {"type": "default"}, language_code = ""):
        return requests.get(f"{self.__link}/getMyCommands", json=json.dumps({"scope": scope, "language_code": language_code}))
    
    def sendMessage(self, chat_id, text):
        return requests.post(f"{self.__link}/sendMessage", json={"chat_id": chat_id, "text": text})
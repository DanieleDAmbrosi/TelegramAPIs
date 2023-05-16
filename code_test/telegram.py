import requests, json

class Location:
    _longitude: float = 0.0
    _latitude: float = 0.0
    _horizontal_accuracy: float = None
    _live_period: int = None
    _heading: int = None #1 - 360
    _proximity_alert_radius: int = None

    def __init__(self, longitude: float, latitude: float, horizontal_accuracy: float = None, live_period: int = None, heading: int = None, proximity_alert_radius: int = None) -> None:
        self._longitude = longitude
        self._latitude = latitude
        self._horizontal_accuracy = horizontal_accuracy
        self._live_period = live_period
        self._heading = heading
        self._proximity_alert_radius = proximity_alert_radius
        pass

    pass

class Entity:
    _offset: int = 0
    _length: int = 0
    _type: str = ""

    def __init__(self, offset, length, type) -> None:
        self._offset = offset
        self._length = length
        self._type = type
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
    _id: int = 0
    _is_bot: bool = False
    _first_name: str = ""
    _last_name: str = ""
    _username: str = ""
    _language_code: str = ""

    def __init__(self, id, is_bot, first_name, last_name, username, language_code) -> None:
        self._id = id
        self._is_bot = is_bot
        self._first_name = first_name
        self._last_name = last_name
        self._username = username
        self._language_code = language_code
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
    _id: int = 0
    _first_name: str = ""
    _last_name: str = ""
    _username: str = ""
    _type: str = ""

    def __init__(self, id, first_name, last_name, username, type):
        self._id = id
        self._first_name = first_name
        self._last_name = last_name
        self._username = username
        self._type = type
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
    _message_id: int = 0
    _from: User
    _chat: Chat
    _text: str
    _entities: list[Entity]
    _date: int
    _location: Location

    def __init__(self, message_id: int, _from: dict, chat: dict, date: int, text: str = None, location: dict = None, entities: list[dict] = None) -> None:
        self._message_id = message_id
        self._from = User(**_from)
        self._chat = Chat(**chat)
        self._text = text
        self._entities = [Entity(**entity) for entity in entities] if entities else None
        self._date = date
        self._location = Location(**location) if location else None
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
    _update_id: int = 0
    _message: Message

    def __init__(self, update_id: int, message: dict) -> None:
        self._update_id = update_id
        if("from" in message.keys()):
            message["_from"] = message.pop("from")
        self._message = Message(**message)
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

class Bot:
    def __init__(self, token):
        self.token = token
        self.__link = f"https://api.telegram.org/bot{token}"
        pass

    def link(self) -> str:
        return self.__link
    
    def getMe(self):
        return requests.get(f"{self.__link}/getMe")
        
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
    
    def sendLocation(self, chat_id, latitude, longitude):
        return requests.post(f"{self.__link}/sendLocation", json={"chat_id": chat_id, "latitude": latitude, "longitude": longitude})
import requests, json
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
    
    def setCommands(self, commands):
        return requests.post(f"{self.__link}/setMyCommands", json=commands)

    def getCommands(self, scope = {"type": "default"}, language_code = ""):
        return requests.get(f"{self.__link}/getMyCommands", json=json.dumps({"scope": scope, "language_code": language_code}))
    
    def sendMessage(self, chat_id, text):
        return requests.post(f"{self.__link}/sendMessage", json={"chat_id": chat_id, "text": text})
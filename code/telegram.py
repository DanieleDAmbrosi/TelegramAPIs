import requests
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
        return requests.get(f"{self.__link}/getUpdates?offset={offset + 1}")    
import dotenv, os, threading, time

dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)

token = os.environ["SECRET_TOKEN"]
offset = int(os.environ["LAST_UPDATE"])

from telegram_handler import bot, handler

mybot = bot(token)

print(mybot.getMe().content)

myhandler = handler(mybot)

threading.Thread(target=myhandler.listen).start()

time.sleep(10)

myhandler.stop()

#dotenv.set_key(dotenv_file, "LAST_UPDATE", os.environ["LAST_UPDATE"])
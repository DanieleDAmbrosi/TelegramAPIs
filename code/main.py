import dotenv, os, threading, time
from telegram_handler import bot, bot_handler
import database

def start_terminal(pipe_path):
    import sys
    from subprocess import Popen, PIPE

    print("starting terminal")

    os.environ['TERM'] = 'xterm-256color'

    target = f'{os.getcwd()}/code/server_console.py'

    new_window_command = "cmd.exe /c start".split()

    py = [sys.executable]
    proc = Popen(new_window_command + py + [target, pipe_path])
    print(new_window_command + py + [target, pipe_path])
    proc.wait()
    pass

dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)

token = os.environ["SECRET_TOKEN"]
offset = int(os.environ["LAST_UPDATE"])

mybot = bot(token)

print(mybot.getMe().content)

pipe_path = os.environ["PIPE_PATH"]
start_terminal(pipe_path)

db=database.Database(os.environ["DB_PATH"] + "users.db")

dbhandler = database.DatabaseHandler(db, "users")

bothandler = bot_handler(mybot, pipe_path, dbhandler, offset)

threading.Thread(target=bothandler.listen).start()

time.sleep(3)

inp = ""
while inp != "exit":
    inp = input("Type exit to quit...\n")

bothandler.stop()

dotenv.set_key(dotenv_file, "LAST_UPDATE", str(bothandler.last_update()))
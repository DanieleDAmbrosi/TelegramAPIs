import dotenv, os, threading

def start_terminal(pipe_path):
    import sys
    from subprocess import Popen, PIPE

    target = 'server_console.py'

    new_window_command = "cmd.exe /c start".split()

    py = [sys.executable]
    Popen(new_window_command + py + [target, pipe_path])
    pass

dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)

token = os.environ["SECRET_TOKEN"]
offset = int(os.environ["LAST_UPDATE"])

from telegram_handler import bot, handler

mybot = bot(token)

print(mybot.getMe().content)

pipe_path = os.environ["PIPE_PATH"]
start_terminal(pipe_path)
myhandler = handler(mybot, pipe_path)

threading.Thread(target=myhandler.listen).start()

inp = ""
while inp != "exit":
    inp = input("Type exit to quit...")

myhandler.stop()

dotenv.set_key(dotenv_file, "LAST_UPDATE", str(myhandler.last_update()))
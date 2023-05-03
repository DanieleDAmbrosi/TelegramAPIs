import dotenv, os, threading
import win32pipe, win32file, pywintypes, time
def start_terminal(pipe_path):
    import sys
    from subprocess import Popen, PIPE

    print("starting terminal")

    os.environ['TERM'] = 'xterm-256color'

    target = f'{os.getcwd()}/code/server_console.py'

    new_window_command = "cmd.exe /c start".split()

    py = [sys.executable]
    #pipe_path = "\"{var}\"".format(var = pipe_path)
    # questo funziona: cmd.exe /c start py code/server_console.py
    # MA POPOPEN NO DIO...
    proc = Popen(new_window_command + py + [target, pipe_path])
    print(new_window_command + py + [target, pipe_path])
    proc.wait()
    pass

start_terminal('//./pipe/Foo')

count = 0

pipe = win32pipe.CreateNamedPipe(
        '//./pipe/Foo',
        win32pipe.PIPE_ACCESS_DUPLEX,
        win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
        1, 65536, 65536,
        0,
        None)
try:
    print("waiting for client")
    win32pipe.ConnectNamedPipe(pipe, None)
    print("got client")

    while count < 10:
        print(f"writing message {count}")
        # convert to bytes
        some_data = str.encode(f"{count}")
        win32file.WriteFile(pipe, some_data)
        time.sleep(1)
        count += 1

    print("finished now")
finally:
        win32file.CloseHandle(pipe)
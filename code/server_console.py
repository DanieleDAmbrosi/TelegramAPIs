import win32pipe, win32file, pywintypes, os
import sys, time

def start_pipe(pipe_path):
        quit = False
        while not quit:
            try:
                handle = win32file.CreateFile(
                    pipe_path,
                    win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                    0,
                    None,
                    win32file.OPEN_EXISTING,
                    0,
                    None
                )
                res = win32pipe.SetNamedPipeHandleState(handle, win32pipe.PIPE_READMODE_MESSAGE, None, None)
                if res == 0:
                    print(f"SetNamedPipeHandleState return code: {res}")
                while True:
                    resp = win32file.ReadFile(handle, 64*1024)
                    print(f"{resp}")
            except pywintypes.error as e:
                if e.args[0] == 2:
                    print("retrying in one second...")
                    time.sleep(1)
                    os.system('cls')
                elif e.args[0] == 109:
                    print("fatal error")
                    quit = True


os.system('pause')
if len(sys.argv) < 2:
    print("need the pipe path")
    os.system('pause')
    exit()
start_pipe(str(sys.argv[1]))
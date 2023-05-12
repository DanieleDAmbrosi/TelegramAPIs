import win32pipe, win32file, pywintypes, time
from collections import deque

class pipe_handler():
    __pipe = None
    __message_dequeue: deque[str] = deque()
    __running = False

    def __init__(self, pipe_path: str) -> None:
        self.__pipe = self.__create_pipe(pipe_path)
        pass

    def consume(self):
        self.__running = True
        while self.__running:
            if len(self.__message_dequeue) > 0:
                message = self.__message_dequeue.popleft()
                self.__print_pipe(message=message)
                pass
            pass
        pass

    def push_message(self, message: str):
        self.__message_dequeue.append(message)
        pass

    def __print_pipe(self, message: str):
        data = bytes(str.encode(str(message)))
        try:
            win32file.WriteFile(self.__pipe, data)
        except:
            self.__close_pipe(self.__pipe)
        pass

    def __create_pipe(self, pipe_path):
        pipe = win32pipe.CreateNamedPipe(
        pipe_path,
        win32pipe.PIPE_ACCESS_DUPLEX,
        win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
        1, 65536, 65536,
        0,
        None)
        print("waiting for client")
        win32pipe.ConnectNamedPipe(pipe, None)
        print("got client")
        return pipe
    
    def __close_pipe(self):
        win32file.CloseHandle(self.__pipe)
        pass

    def stop(self):
        self.__running = False
        self.__close_pipe()
    pass
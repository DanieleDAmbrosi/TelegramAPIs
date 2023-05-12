import win32pipe, win32file, pywintypes, time
from queue import Queue

class pipe_handler():
    __pipe_path: str = ""
    __message_queue: Queue = Queue()
    __running = False

    def __init__(self, pipe_path: str) -> None:
        pass

    def consume(self):
        self.__running = True
        pipe = self.create_pipe(self)
        while self.__running:
            if self.__message_queue.empty() == False:
                data = self.__message_queue.get()
                self.__print_pipe(pipe, data)
                self.__message_queue.task_done()
                pass
            pass
        pass

    def push_message(self):
        pass

    def __print_pipe(self, pipe, data: str):
        data = bytes(str.encode(str(data)))
        try:
            win32file.WriteFile(pipe, data)
        except:
            self.__close_pipe(pipe)
        pass

    def __create_pipe(self):
        pipe = win32pipe.CreateNamedPipe(
        self.__pipe_path,
        win32pipe.PIPE_ACCESS_DUPLEX,
        win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
        1, 65536, 65536,
        0,
        None)
        print("waiting for client")
        win32pipe.ConnectNamedPipe(pipe, None)
        print("got client")
        return pipe
    
    def __close_pipe(self, pipe):
        win32file.CloseHandle(pipe)
        pass

    pass
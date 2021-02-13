import socket
import threading

ON_CONNECTED = 0x01
ON_MESSAGE = 0x02


class TCPClient(threading.Thread):
    def __init__(self, ip, port, buffer_size=1024):
        super().__init__()
        self._ip = ip
        self._port = port
        self._buffer_size = buffer_size
        self._socket = self._create_socket()
        self._handlers = {}

    def on(self, event):
        def wrapper(func):
            self._handlers[event] = func
        return wrapper

    def add_handler(self, event, func):
        self._handlers[event] = func

    def connect(self):
        self._socket.connect((self._ip, self._port))

    def send(self, message: str):
        self._socket.send(message.encode("utf-8"))

    def disconnect(self):
        self._socket.close()

    def run(self):
        func = self._handlers.get(ON_CONNECTED)
        if func and callable(func):
            func((self._ip, self._port))
        while True:
            message: bytes = self._socket.recv(self._buffer_size)
            func = self._handlers.get(ON_MESSAGE)
            if func and callable(func):
                func(message.decode("utf-8"))

    @staticmethod
    def _create_socket():
        socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        return socket_

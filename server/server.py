import socket
import threading

NEW_CONNECTION = 0x01
NEW_MESSAGE = 0x02


class TCPServer:
    def __init__(self, ip: str, port: int, buffer_size: int = 1024, max_clients: int = 100):
        """Create a TCP server for listening
        :type max_clients: int
        :type ip: str
        :type port: int
        :type buffer_size: int

        :param ip: address to bind for
        :param port: port to bing for
        :param buffer_size: size of receiving buffer
        :param max_clients: max incoming clients connections
        """
        self._ip = ip
        self._port = port
        self._buffer_size = buffer_size
        self._max_clients = max_clients
        self._socket = self._create_socket()
        self._clients = []
        self._handlers = {}

    def broadcast(self, message: str):
        """Send message to everyone connected

        :param message: message to send
        """
        for client in self._clients:
            try:
                client.send(message.encode("utf-8"))
            except ConnectionResetError:
                self._remove_client(client)

    def on(self, event):
        """Wrapper to get callback when event is triggered

        :param event: event code
        :return: wrapper
        """

        def wrapper(func):
            self._handlers[event] = func

        return wrapper

    def client_receiver(self, conn, addr):
        """Start receiving messages from clients

        :param conn: socket object
        :param addr: address info
        """

        while True:
            try:
                message: bytes = conn.recv(self._buffer_size)
                if message:
                    func = self._handlers.get(NEW_MESSAGE)
                    if func and callable(func):
                        func(addr, message.decode("utf-8"))
            except ConnectionResetError:
                self._remove_client(conn)
                break

    def start(self):
        """Start accepting incoming connections
        """
        threading.Thread(target=self._accept_connections).start()

    def _accept_connections(self):
        while True:
            conn, addr = self._socket.accept()
            self._clients.append(conn)
            threading.Thread(target=self.client_receiver, args=(conn, addr)).start()
            func = self._handlers.get(NEW_CONNECTION)
            if func and callable(func):
                func(addr)

    def _create_socket(self):
        socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_.bind((self._ip, self._port))
        socket_.listen(self._max_clients)
        return socket_

    def _remove_client(self, client):
        if client in self._clients:
            self._clients.remove(client)

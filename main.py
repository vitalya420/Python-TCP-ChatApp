import sys
from queue import Queue

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow

from client import TCPClient, ON_MESSAGE, ON_CONNECTED
from ui import Ui_MainWindow


class TCPConnection(QThread):
    connected = pyqtSignal(bool)
    message = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ip = "127.0.0.1"
        self.port = 4040
        self.username = None
        self.message_queue = Queue()
        self.client = TCPClient(self.ip, self.port, 2048)
        self.client.add_handler(ON_MESSAGE, self.message.emit)

    def connect(self):
        try:
            self.client.connect()
            return True
        except ConnectionRefusedError:
            return False

    def send_message(self, message):
        self.message_queue.put(f"{self.username}: {message}")

    def run(self):
        conn_status = self.connect()
        self.connected.emit(conn_status)
        if conn_status:
            self.client.send(f"{self.username} has joined!")
            self.client.start()
            while True:
                if not self.message_queue.empty():
                    self.client.send(self.message_queue.get())


class ChatWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.connected = False

        self.connection_thread = TCPConnection()
        self.connection_thread.connected.connect(self._connect_status)
        self.connection_thread.message.connect(self._add_message)

        self.ui.button_connect.clicked.connect(self.connect_to_server)
        self.ui.button_send.clicked.connect(self.send_message)
        self.ui.line_message.returnPressed.connect(self.send_message)

    def connect_to_server(self):
        if self.connected and self.connection_thread.isRunning():
            self.connection_thread.terminate()
            self._set_enabled_ui(True)
        name = self._get_name()
        if not name:
            self.ui.status.setText("Bad name!")
            return
        ip, port = self._get_addr()
        if not ip:
            return
        self.connection_thread.username = name
        self.connection_thread.ip = ip
        self.connection_thread.port = port
        self.connection_thread.start()
        self.connected = True

    def send_message(self):
        if self.connected:
            text = self.ui.line_message.text()
            if len(text.strip()) > 1:
                self.connection_thread.send_message(text)
                self.ui.line_message.clear()

    def _get_addr(self):
        ip_port = self.ui.line_ip_port.text()
        if ":" not in ip_port:
            return ()
        ip, port = ip_port.split(":")
        if not port.isdigit():
            return ()
        return ip, port

    def _get_name(self):
        name = self.ui.line_name.text()
        if not (3 <= len(name) <= 9):
            return
        return name

    def _add_message(self, message):
        self.ui.chat.append(message)

    def _set_enabled_ui(self, status):
        ui = [
            self.ui.line_name,
            self.ui.line_ip_port,
        ]
        for ui_element in ui:
            ui_element.setEnabled(status)

    def _connect_status(self, status):
        if status:
            self.ui.status.setText("Connected")
            self._set_enabled_ui(False)
            self.ui.button_connect.setText("Disconnect")
            return
        self.ui.status.setText("Error")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ChatWindow()
    win.show()
    sys.exit(app.exec_())

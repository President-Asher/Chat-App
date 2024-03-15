import sys
import socket
import threading
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QTextBrowser, QLineEdit, QPushButton, QVBoxLayout
import random
import sounddevice as sd
import numpy as np

class ServerGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Server Monitor")
        self.setStyleSheet("QMainWindow { border: 2px solid black; }")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()

        self.log_browser = QTextBrowser()
        self.log_browser.setStyleSheet("background-color: black; color: green; font-size: 16px;")
        self.layout.addWidget(self.log_browser)

        self.message_entry = QLineEdit()
        self.message_entry.setStyleSheet("color: black; font-size: 16px;")
        self.message_entry.returnPressed.connect(self.send_server_message)
        self.layout.addWidget(self.message_entry)

        self.send_button = QPushButton("Send Message")
        self.send_button.clicked.connect(self.send_server_message)
        self.layout.addWidget(self.send_button)

        self.start_call_button = QPushButton("Start Voice Call")
        self.start_call_button.clicked.connect(self.start_voice_call)
        self.layout.addWidget(self.start_call_button)

        self.hang_up_button = QPushButton("Hang Up Call")
        self.hang_up_button.clicked.connect(self.hang_up_call)
        self.hang_up_button.setEnabled(False)
        self.layout.addWidget(self.hang_up_button)

        self.central_widget.setLayout(self.layout)

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(('127.0.0.1', 5555))
        self.server.listen(5)

        self.clients = []

        self.log_browser.append("Server started...")

        self.receive_thread = threading.Thread(target=self.accept_clients)
        self.receive_thread.start()

        self.voice_calling = False

    def accept_clients(self):
        while True:
            client_socket, addr = self.server.accept()
            print(f"Accepted connection from {addr}")

            client_color = "#{:06x}".format(random.randint(0, 0xFFFFFF))

            client_handler = threading.Thread(target=self.handle_client, args=(client_socket, addr, client_color))
            client_handler.start()

    def handle_client(self, client_socket, client_address, client_color):
        def receive():
            while True:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                print(f"\nReceived from {client_address}: {data}")

                # Broadcast the received message to all connected clients
                for client in self.clients:
                    if client != client_socket:
                        try:
                            client.send(data.encode('utf-8'))
                        except Exception as e:
                            print(f"Error broadcasting message to a client: {e}")

                # Update the server log in the GUI with color-coded messages
                message = f"<span style='color:{client_color}'>Received from {client_address}: {data}</span>"
                self.log_browser.append(message)
                self.log_browser.verticalScrollBar().setValue(self.log_browser.verticalScrollBar().maximum())

        receive_thread = threading.Thread(target=receive)
        receive_thread.start()

        # Add the client socket to the list of connected clients
        self.clients.append(client_socket)

    def send_server_message(self):
        message = self.message_entry.text()
        if message:
            for client in self.clients:
                try:
                    client.send(message.encode('utf-8'))
                except Exception as e:
                    print(f"Error sending server message to a client: {e}")

            # Update the server log in the GUI with color-coded server message
            server_message = f"<span style='color:green'>Server Message: {message}</span>"
            self.log_browser.append(server_message)
            self.log_browser.verticalScrollBar().setValue(self.log_browser.verticalScrollBar().maximum())

            self.message_entry.clear()

    def start_voice_call(self):
        self.voice_calling = True
        self.start_call_button.setEnabled(False)
        self.hang_up_button.setEnabled(True)

        def voice_call():
            with sd.InputStream(callback=self.callback):
                sd.sleep(1000000)  # Allow the voice call to continue until the user hangs up

        voice_thread = threading.Thread(target=voice_call)
        voice_thread.start()

    def hang_up_call(self):
        self.voice_calling = False
        self.start_call_button.setEnabled(True)
        self.hang_up_button.setEnabled(False)

    def callback(self, indata, frames, time, status):
        if self.voice_calling and status:
            print(f"Voice call error: {status}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = ServerGUI()
    gui.show()
    sys.exit(app.exec_())
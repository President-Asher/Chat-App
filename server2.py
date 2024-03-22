import sys
import socket
import threading
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QTextBrowser, QLineEdit, QPushButton, QVBoxLayout, QFileDialog
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import random
from PIL import Image
from io import BytesIO

class ServerGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Server Monitor")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()

        self.log_browser = QTextBrowser()
        self.log_browser.setStyleSheet("background-color: black; color: green; font-size: 16px;")
        self.layout.addWidget(self.log_browser)

        self.message_entry = QLineEdit()
        self.message_entry.setStyleSheet("color: white; font-size: 16px;")
        self.message_entry.returnPressed.connect(self.send_server_message)
        self.layout.addWidget(self.message_entry)

        self.send_button = QPushButton("Send Message")
        self.send_button.clicked.connect(self.send_server_message)
        self.layout.addWidget(self.send_button)

        self.upload_button = QPushButton("Upload Photo")
        self.upload_button.clicked.connect(self.upload_photo)
        self.layout.addWidget(self.upload_button)

        self.admin_frame = QWidget()
        self.layout.addWidget(self.admin_frame)

        self.shutdown_button = QPushButton("Emergency Shutdown")
        self.shutdown_button.clicked.connect(self.handle_emergency_shutdown)
        self.layout.addWidget(self.shutdown_button)

        self.central_widget.setLayout(self.layout)

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(('10.200.236.221', 5555))
        self.server.listen(5)

        self.clients = []  # Maintain a list of connected clients

        self.log_browser.append("Server started...")

        self.receive_thread = threading.Thread(target=self.accept_clients)
        self.receive_thread.start()

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

                # Check if the received data is an image
                if data.startswith("IMAGE:"):
                    image_data = data[len("IMAGE:"):]
                    self.show_image(client_color, image_data)
                elif data == "!emergency_shutdown":
                    self.handle_emergency_shutdown(client_color)
                else:
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

    def show_image(self, client_color, image_data):
        try:
            image_bytes = image_data.encode('utf-8')
            image = Image.open(BytesIO(image_bytes))
            image_label = QLabel()
            pixmap = QPixmap(image)
            pixmap = pixmap.scaledToHeight(100)
            image_label.setPixmap(pixmap)
            self.log_browser.append(f"<span style='color:{client_color}'>Received an image:</span>")
            self.log_browser.document().addBlock()  # Add a new line for the image
            self.log_browser.insertHtml(image_label.text())
        except Exception as e:
            print(f"Error displaying image: {e}")

    def handle_emergency_shutdown(self, client_color):
        # Broadcast an emergency shutdown message to all connected clients
        for client in self.clients:
            try:
                client.send("!emergency_shutdown".encode('utf-8'))
            except Exception as e:
                print(f"Error sending emergency shutdown command to a client: {e}")

        # Update the server log in the GUI
        emergency_message = "<span style='color:red'>Emergency Shutdown initiated by admin!</span>"
        self.log_browser.append(emergency_message)
        self.log_browser.verticalScrollBar().setValue(self.log_browser.verticalScrollBar().maximum())

        # Perform any additional actions for emergency shutdown if needed

        # Terminate the server process
        sys.exit()

    def upload_photo(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, 'Upload Photo', '', 'Image Files (*.png *.jpg *.jpeg)')
        if file_path:
            try:
                with open(file_path, 'rb') as file:
                    image_data = file.read()
                    for client in self.clients:
                        try:
                            client.send(f"IMAGE:{image_data.decode('utf-8')}".encode('utf-8'))
                        except Exception as e:
                            print(f"Error sending image to a client: {e}")
            except Exception as e:
                print(f"Error reading image file: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = ServerGUI()
    gui.show()
    sys.exit(app.exec_())

import socket
import threading
from io import BytesIO
from tkinter import simpledialog
from PIL import Image
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel, QFileDialog
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

MAX_MESSAGES = None  # No maximum number of messages in the chat log

class ChatClientUI(QWidget):
    def __init__(self, client_socket, client_name):
        super().__init__()

        self.client_socket = client_socket
        self.client_name = client_name

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Chat Client")

        self.chat_log = QTextEdit(self)
        self.chat_log.setReadOnly(True)

        self.entry_widget = QLineEdit(self)
        self.entry_widget.returnPressed.connect(self.send_message)

        self.send_button = QPushButton("Send", self)
        self.send_button.clicked.connect(self.send_message)

        self.send_image_button = QPushButton("Send Image", self)
        self.send_image_button.clicked.connect(self.send_image)

        layout = QVBoxLayout()
        layout.addWidget(self.chat_log)
        layout.addWidget(self.entry_widget)
        layout.addWidget(self.send_button)
        layout.addWidget(self.send_image_button)

        self.setLayout(layout)

        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.start()

        self.show()

    def send_message(self):
        message = self.entry_widget.text()
        if message:
            full_message = f"{self.client_name}: {message}"
            self.client_socket.send(full_message.encode('utf-8'))
            self.display_message(full_message)
            self.entry_widget.clear()

    def send_image(self):
        file_dialog = QFileDialog()
        image_path, _ = file_dialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.bmp)")
        if image_path:
            with open(image_path, 'rb') as image_file:
                image_data = image_file.read()
                self.client_socket.sendall(image_data)
                self.display_image(image_data)

    def receive_messages(self):
        while True:
            try:
                data = self.client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                if data.startswith("Image:"):
                    image_data = self.client_socket.recv(1024)
                    self.display_image(image_data)
                else:
                    self.display_message(data)
            except Exception as e:
                print(f"Error receiving message: {e}")
                break

    def display_message(self, message):
        self.chat_log.append(message)

    def display_image(self, image_data):
        try:
            image = Image.open(BytesIO(image_data))
            pixmap = QPixmap(image)
            pixmap = pixmap.scaledToHeight(100)

            # Create a label for the image and display it in the client's log
            image_label = QLabel()
            image_label.setPixmap(pixmap)
            self.chat_log.append("Received an image:")
            self.chat_log.document().addBlock()  # Add a new line for the image
            self.chat_log.insertHtml(image_label.text())

        except Exception as e:
            print(f"Error displaying image: {e}")

def main():
    # Get client's name using simpledialog
    app = QApplication([])
    client_name = simpledialog.askstring("Client Name", "Enter your name:")

    # Continue with the chat only if the client entered a name
    if client_name:
        server_address = ('10.200.236.220', 5555)

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(server_address)

        # Send client's name to the server
        client.send(client_name.encode('utf-8'))

        # Start the GUI
        chat_ui = ChatClientUI(client, client_name)

        app.exec_()
        client.close()

if __name__ == "__main__":
    main()
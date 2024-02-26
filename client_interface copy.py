import sys
import socket
import threading
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QTextBrowser, QLineEdit, QPushButton, QVBoxLayout, QLabel, QFileDialog, QMessageBox
from PyQt5.QtGui import QTextCursor, QPixmap
from PyQt5.QtCore import Qt
import random
from PIL import Image
from io import BytesIO

class ClientGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Chat Client")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()

        self.log_browser = QTextBrowser()
        self.log_browser.setStyleSheet("background-color: white; color: black; font-size: 14px;")
        self.layout.addWidget(self.log_browser)

        self.username_entry = QLineEdit()
        self.username_entry.setStyleSheet("color: black; font-size: 14px;")
        self.username_entry.setPlaceholderText("Enter your username")
        self.layout.addWidget(self.username_entry)

        self.message_entry = QLineEdit()
        self.message_entry.setStyleSheet("color: black; font-size: 14px;")
        self.message_entry.setPlaceholderText("Type your message here...")
        self.message_entry.returnPressed.connect(self.send_message)
        self.layout.addWidget(self.message_entry)

        self.send_button = QPushButton("Send Message")
        self.send_button.clicked.connect(self.send_message)
        self.layout.addWidget(self.send_button)

        self.upload_button = QPushButton("Upload Photo")
        self.upload_button.clicked.connect(self.upload_photo)
        self.layout.addWidget(self.upload_button)

        self.central_widget.setLayout(self.layout)

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(('10.200.236.224', 5555))

        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.start()

        self.username = None  # To store the username

    def receive_messages(self):
        while True:
            try:
                data = self.client_socket.recv(1024).decode('utf-8')
                if not data:
                    break

                # Check if the received data is an image
                if data.startswith("IMAGE:"):
                    image_data = data[len("IMAGE:"):]
                    self.show_image(image_data)
                else:
                    # Update the client log in the GUI with received messages
                    self.log_browser.append(data)
                    self.log_browser.verticalScrollBar().setValue(self.log_browser.verticalScrollBar().maximum())
            except Exception as e:
                print(f"Error receiving message: {e}")
                break

    def send_message(self):
        if not self.username:
            entered_username = self.username_entry.text().strip()
            if not entered_username:
                self.show_error_message("No Username", "Please enter a username.")
                return

            if not self.is_valid_username(entered_username):
                self.show_error_message("Invalid Username", "Please enter a valid username without inappropriate content.")
                return

            self.username = entered_username
            self.username_entry.setReadOnly(True)
            self.show_info_message("Welcome", f"Welcome, {self.username}!")

        message = self.message_entry.text()
        if message:
            try:
                self.client_socket.send(f"{self.username}: {message}".encode('utf-8'))
            except Exception as e:
                print(f"Error sending message: {e}")

            self.message_entry.clear()

    def is_valid_username(self, username):
        # List of common bad words
        bad_words = ["badword1", "badword2", "badword3", "example"]

        # Check if the username contains any bad words
        return all(bad_word not in username.lower() for bad_word in bad_words)

    def show_image(self, image_data):
        try:
            image_bytes = image_data.encode('utf-8')
            image = Image.open(BytesIO(image_bytes))
            image_label = QLabel()
            pixmap = QPixmap(image)
            pixmap = pixmap.scaledToHeight(100)
            image_label.setPixmap(pixmap)
            self.log_browser.append("Received an image:")
            self.log_browser.document().addBlock()  # Add a new line for the image
            self.log_browser.insertHtml(image_label.text())
        except Exception as e:
            print(f"Error displaying image: {e}")

    def upload_photo(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, 'Upload Photo', '', 'Image Files (*.png *.jpg *.jpeg)')
        if file_path:
            try:
                with open(file_path, 'rb') as file:
                    image_data = file.read()
                    self.client_socket.send(f"IMAGE:{image_data.decode('utf-8')}".encode('utf-8'))
            except Exception as e:
                print(f"Error reading image file: {e}")

    def show_error_message(self, title, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec_()

    def show_info_message(self, title, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    client_gui = ClientGUI()
    client_gui.show()
    sys.exit(app.exec_())
import cv2
import socket
import pickle
import struct
import socket

# Get the client's IP address
client_ip = socket.gethostbyname(socket.gethostname())

# Create a socket connection to the server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('10.200.236.221', 8080))

# Start capturing from the webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()

    # Serialize the frame and send it to the server
    data = pickle.dumps(frame)
    size = struct.pack("L", len(data))
    client_socket.sendall(size + data)

    # Send the client's IP address to the server
    client_socket.sendall(client_ip.encode())

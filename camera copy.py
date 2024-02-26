import cv2
import socket
import pickle
import struct

# Create a socket connection to the server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('10.200.236.221', 8888))

# Start capturing from the client's webcam
cap = cv2.VideoCapture(0)

while True:
    # Read a frame from the client's webcam
    ret, frame = cap.read()

    # Serialize the frame and send it to the server
    data = pickle.dumps(frame)
    size = struct.pack("L", len(data))
    client_socket.sendall(size + data)

    # Receive and display the server's webcam footage
    data = b""
    payload_size = struct.calcsize("L")

    while len(data) < payload_size:
        data += client_socket.recv(4096)

    packed_size = data[:payload_size]
    data = data[payload_size:]
    msg_size = struct.unpack("L", packed_size)[0]

    while len(data) < msg_size:
        data += client_socket.recv(4096)

    frame_data = data[:msg_size]
    data = data[msg_size:]

    # Deserialize the frame and display it
    server_frame = pickle.loads(frame_data)
    cv2.imshow('Server Webcam', server_frame)
    cv2.waitKey(1)

    # Display the client's own webcam footage
    cv2.imshow('Client Webcam', frame)
    cv2.waitKey(1)

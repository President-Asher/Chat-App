import socket
import time
import pyautogui

def receive_and_move_mouse(server_host, server_port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_host, server_port))

    try:
        while True:
            # Receive mouse position from the server
            mouse_position = client_socket.recv(1024).decode()
            print(mouse_position)

            # Extract X and Y coordinates from the received data
            _, x_str, y_str = mouse_position.split()
            x, y = int(x_str), int(y_str)

            # Move the mouse to the received position
            pyautogui.moveTo(x, y)

            # Wait for 0.1 seconds before moving to the next position
            time.sleep(0.1)

    except KeyboardInterrupt:
        print('Program terminated by user.')
        client_socket.close()

if __name__ == "__main__":
    server_host = 'localhost'  # Replace with the server's host
    server_port = 12345        # Replace with the server's port

    receive_and_move_mouse(server_host, server_port)

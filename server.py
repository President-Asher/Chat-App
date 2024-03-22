import socket
import threading

def handle_client(client_socket, client_address):
    
    def receive():
        while True:
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                break
            print(f"\nReceived from {client_address}: {data}")

    def send():
        while True:
            response = input("Enter a message to send back to the client: ")
            client_socket.send(response.encode('utf-8'))

    receive_thread = threading.Thread(target=receive)
    send_thread = threading.Thread(target=send)

    receive_thread.start()
    send_thread.start()

    receive_thread.join()
    send_thread.join()

    client_socket.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('10.200.236.221', 5555))
    server.listen(5)

    print("Server listening on port 5555")

    while True:
        client_socket, addr = server.accept()
        print(f"Accepted connection from {addr}")

        client_handler = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_handler.start()

if __name__ == "__main__":
    start_server()

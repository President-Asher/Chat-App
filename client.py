import socket
import threading
def run_time():
    try:
        # Create a socket connection to an external server
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Connect to Google's public DNS server
        local_ip = s.getsockname()[0]  # Get the local IP address
        s.close()
        return local_ip
    except Exception as e:
        print(f"Error getting local IP: {e}")
        return None

if __name__ == "__main__":
    runtime = run_time()


def receive(client_socket):
    while True:
        data = client_socket.recv(1024).decode('utf-8')
        if not data:
            break
        print(f"\nReceived from server: {data}")

def send(client_socket):
    while True:
        message = input(f"{runtime} - Enter a message to send to the server: ")
        client_socket.send(message.encode('utf-8'))

server_address = ('10.200.236.221', 5555)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(server_address)

receive_thread = threading.Thread(target=receive, args=(client,))
send_thread = threading.Thread(target=send, args=(client,))

receive_thread.start()
send_thread.start()

receive_thread.join()
send_thread.join()

client.close()

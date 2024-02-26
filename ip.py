import socket

def get_ip_address():
    try:
        # Create a socket connection to the server
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ("10.200.236.221", 8080)  # Replace with the server's IP address
        s.connect(server_address)

        # Receive and print the server's response (client's IP address)
        data = s.recv(1024)
        print(f"Server says: {data.decode()}")
    except socket.error:
        print("Unable to connect to the server")
    finally:
        s.close()

if __name__ == "__main__":
    get_ip_address()

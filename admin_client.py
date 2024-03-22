import socket
import threading
import tkinter as tk
from tkinter import simpledialog

MAX_MESSAGES = None  # No maximum number of messages in the chat log

def get_client_name():
    return simpledialog.askstring("Client Name", "Enter your name:")

def receive(client_socket, chat_log):
    while True:
        try:
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                break
            chat_log.config(state=tk.NORMAL)
            chat_log.insert(tk.END, f"{data}\n")
            chat_log.config(state=tk.DISABLED)
            chat_log.yview(tk.END)  # Auto-scroll to the end
        except Exception as e:
            print(f"Error receiving message: {e}")
            break

def send(event, client_socket, entry_widget, chat_log, client_name):
    message = entry_widget.get()
    if message:
        full_message = f"{client_name}: {message}"
        client_socket.send(full_message.encode('utf-8'))
        chat_log.config(state=tk.NORMAL)
        chat_log.insert(tk.END, f"{client_name}: {message}\n")
        chat_log.config(state=tk.DISABLED)
        chat_log.yview(tk.END)  # Auto-scroll to the end
        entry_widget.delete(0, tk.END)

def start_gui(client_socket, client_name):
    root = tk.Tk()
    root.title("Chat Client")

    chat_log = tk.Text(root, height=15, width=50, state=tk.DISABLED, wrap=tk.WORD)
    chat_log.pack()

    scrollbar = tk.Scrollbar(root, command=chat_log.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    chat_log.config(yscrollcommand=scrollbar.set)

    entry_widget = tk.Entry(root, width=50)
    entry_widget.pack()
    entry_widget.bind("<Return>", lambda event: send(event, client_socket, entry_widget, chat_log, client_name))

    send_button = tk.Button(root, text="Send", command=lambda: send(None, client_socket, entry_widget, chat_log, client_name))
    send_button.pack()

    # Admin buttons
    admin_frame = tk.Frame(root)
    admin_frame.pack(pady=10)

    emergency_shutdown_button = tk.Button(admin_frame, text="Emergency Shutdown", command=lambda: emergency_shutdown(client_socket))
    emergency_shutdown_button.pack()

    receive_thread = threading.Thread(target=receive, args=(client_socket, chat_log))
    receive_thread.start()

    root.protocol("WM_DELETE_WINDOW", lambda: root.destroy())

    # Disable resizing (including maximizing)
    root.resizable(False, False)

    root.mainloop()

def emergency_shutdown(client_socket):
    # Send an emergency shutdown command to the server
    client_socket.send("!emergency_shutdown".encode('utf-8'))

    # Additional actions on the client side if needed

def main():
    # Get client's name using simpledialog
    client_name = get_client_name()

    # Continue with the chat only if the client entered a name
    if client_name:
        server_address = ('10.200.236.220', 5555)

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(server_address)

        # Send client's name to the server
        client.send(client_name.encode('utf-8'))

        # Start the GUI in a separate thread
        gui_thread = threading.Thread(target=start_gui, args=(client, client_name))
        gui_thread.start()

        gui_thread.join()
        client.close()

if __name__ == "__main__":
    main()

import socket
import threading
import tkinter as tk
from tkinter import simpledialog  # Import simpledialog for getting user input

MAX_MESSAGES = None  # No maximum number of messages in the chat log

def get_client_name():
    # Use simpledialog to get user input for the client's name
    return simpledialog.askstring("Client Name", "Enter your name:")

def receive(client_socket, chat_log, client_name):
    while True:
        data = client_socket.recv(1024).decode('utf-8')
        if not data:
            break
        chat_log.config(state=tk.NORMAL)
        if data.startswith("Client:"):
            chat_log.insert(tk.END, f"{client_name}: {data.split(': ', 1)[1]}\n", 'client_tag')
        else:
            chat_log.insert(tk.END, f"Server: {data}\n", 'server_tag')
        chat_log.config(state=tk.DISABLED)
        chat_log.yview(tk.END)  # Auto-scroll to the end


def send(event, client_socket, entry_widget, chat_log, client_name):
    message = entry_widget.get()
    if message:
        full_message = f"{client_name}: {message}"
        client_socket.send(full_message.encode('utf-8'))
        chat_log.config(state=tk.NORMAL)
        chat_log.insert(tk.END, f"{client_name}: {message}\n", 'client_tag')
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

    # Configure tags for text color
    chat_log.tag_configure('client_tag', foreground='blue')
    chat_log.tag_configure('server_tag', foreground='red')

    entry_widget = tk.Entry(root, width=50)
    entry_widget.pack()
    entry_widget.bind("<Return>", lambda event: send(event, client_socket, entry_widget, chat_log, client_name))

    send_button = tk.Button(root, text="Send", command=lambda: send(None, client_socket, entry_widget, chat_log, client_name))
    send_button.pack()

    receive_thread = threading.Thread(target=receive, args=(client_socket, chat_log, client_name))
    receive_thread.start()

    root.protocol("WM_DELETE_WINDOW", lambda: root.destroy())

    # Disable resizing (including maximizing)
    root.resizable(False, False)

    root.mainloop()

def main():
    # Get client's name using simpledialog
    client_name = get_client_name()

    # Continue with the chat only if the client entered a name
    if client_name:
        server_address = ('10.200.236.224', 5555)

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(server_address)

        gui_thread = threading.Thread(target=start_gui, args=(client, client_name))
        gui_thread.start()

        gui_thread.join()
        client.close()

if __name__ == "__main__":
    main()
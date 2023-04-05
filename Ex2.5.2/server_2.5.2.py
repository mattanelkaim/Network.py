"""
A server that receives commands from client
and sends back a response accordingly
"""
import socket
import time
from random import randint

SERVER_ADDRESS = ("0.0.0.0", 8220)
NAME_ENC = b"CAPYBARA"
QUIT_MSG_ENC = b"BYE"
NO_CMD_ENC = b"ILLEGAL COMMAND"
COMMANDS = {
    "Quit": QUIT_MSG_ENC,
    "NAME": NAME_ENC,
    "TIME": time.strftime("%H:%M:%S", time.localtime()).encode(),
    "RAND": str(randint(1, 10)).encode()
}

# Initialize server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(SERVER_ADDRESS)

# Listen to client's socket
server_socket.listen()
client_socket, client_address = server_socket.accept()
print(f"Client {client_address} connected")

data = ""
while data != "Quit":
    data = client_socket.recv(1024).decode()
    response = COMMANDS.get(data, NO_CMD_ENC)  # Encoded
    client_socket.send(response)

# Close sockets
client_socket.close()
server_socket.close()

"""
Connects to a server, sends data and prints the received data
"""
import socket

SERVER_ADDRESS = ("127.0.0.1", 8220)
MSG = "im not angry"

# Create a TCP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(SERVER_ADDRESS)

# Exchange data with server, then print it
client_socket.send(MSG.encode())
data = client_socket.recv(1024).decode()
print(data)

client_socket.close()

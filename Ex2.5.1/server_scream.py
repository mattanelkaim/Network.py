"""
A server that receives data from client and
sends it back with uppercase chars and 3 '!'
"""
import socket

SERVER_ADDRESS = ("0.0.0.0", 8220)

# Create a TCP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(SERVER_ADDRESS)

server_socket.listen()
client_socket, client_address = server_socket.accept()
print(f"Client {client_address} connected")

# Send back to client an angry message
data = client_socket.recv(1024).decode()
data = f"{data.upper()}!!!"

client_socket.send(data.encode())
server_socket.close()

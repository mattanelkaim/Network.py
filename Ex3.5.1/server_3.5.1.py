"""
Get messages from a user until they lose hope
"""
import socket

IP, PORT = "0.0.0.0", 8821
BUFFER_SIZE = 1024

# Create a UDP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((IP, PORT))

data = ""
while data != "EXIT":
    # Read messages from client
    client_msg, _ = server_socket.recvfrom(BUFFER_SIZE)
    data = client_msg.decode()
    print(f"Client sent: {data}")

server_socket.close()

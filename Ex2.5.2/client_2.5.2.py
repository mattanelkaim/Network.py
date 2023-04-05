"""
Connects to a server, sends data from
user and prints the received data
"""
import socket

SERVER_ADDRESS = ("127.0.0.1", 8220)
END_MSG = "BYE"

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(SERVER_ADDRESS)

data = ""
while data != END_MSG:
    data = input("Enter your message\n")
    client_socket.send(data.encode())
    data = client_socket.recv(1024).decode()
    print(f"Server sent: {data}")

client_socket.close()

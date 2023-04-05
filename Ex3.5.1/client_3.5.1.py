"""
Send messages to a UDP server until you lose hope
"""
import socket

IP, PORT = "127.0.0.1", 8821
BUFFER_SIZE = 1024

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

msg = ""
while msg != "EXIT":
    # Get message from user and send to server
    msg = input("Enter your message\n")
    client_socket.sendto(msg.encode(), (IP, PORT))

client_socket.close()

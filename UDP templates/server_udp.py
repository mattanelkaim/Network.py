import socket

IP, PORT = "0.0.0.0", 8821
BUFFER_SIZE = 1024

# Create a UDP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((IP, PORT))

# Receive messages and decode
client_msg, client_addr = server_socket.recvfrom(BUFFER_SIZE)
data = client_msg.decode()
print(f"Client sent: {data}")

# Send a message back to client
response = f"I love {data}"
server_socket.sendto(response.encode(), client_addr)

server_socket.close()
